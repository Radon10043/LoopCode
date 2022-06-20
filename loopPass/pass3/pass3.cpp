/*
 * @Author: Radon
 * @Date: 2022-03-30 11:30:24
 * @LastEditors: Radon
 * @LastEditTime: 2022-06-20 18:02:33
 * @Description: Hi, say something
 */
#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <set>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "llvm/IR/Function.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

#include "llvm/ADT/Statistic.h"
#include "llvm/Analysis/CFGPrinter.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/FileSystem.h"

#include "llvm/Analysis/CFG.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Use.h"
#include "llvm/IR/Value.h"

#include "llvm/Analysis/LoopInfo.h"
using namespace llvm;


cl::opt<std::string> OutDirectory(
    "outdir",
    cl::desc("Output directory where txt files are generated."),
    cl::value_desc("outdir"));


namespace {
  class MyPass : public FunctionPass {
  public:
    static char ID;
    MyPass()
        : FunctionPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const override;
    bool runOnFunction(Function &F) override;
  };

  class AFLGoPass : public ModulePass {
  public:
    static char ID;
    AFLGoPass()
        : ModulePass(ID) {}

    bool runOnModule(Module &M) override;
  };
} // namespace


char MyPass::ID = 1;
char AFLGoPass::ID = 0;


/**
 * @brief 获取指令的所在位置:"文件名:行号"
 *
 * @param I
 * @param Filename
 * @param Line
 */
static void getDebugLoc(const Instruction *I, std::string &Filename, unsigned &Line) {
#ifdef LLVM_OLD_DEBUG_API
  DebugLoc Loc = I->getDebugLoc();
  if (!Loc.isUnknown()) {
    DILocation cDILoc(Loc.getAsMDNode(M.getContext()));
    DILocation oDILoc = cDILoc.getOrigLocation();

    Line = oDILoc.getLineNumber();
    Filename = oDILoc.getFilename().str();

    if (filename.empty()) {
      Line = cDILoc.getLineNumber();
      Filename = cDILoc.getFilename().str();
    }
  }
#else
  if (DILocation *Loc = I->getDebugLoc()) {
    Line = Loc->getLine();
    Filename = Loc->getFilename().str();

    if (Filename.empty()) {
      DILocation *oDILoc = Loc->getInlinedAt();
      if (oDILoc) {
        Line = oDILoc->getLine();
        Filename = oDILoc->getFilename().str();
      }
    }
  }
#endif /* LLVM_OLD_DEBUG_API */
}


static bool isBlacklisted(const Function *F) {
  static const SmallVector<std::string, 8> Blacklist = {
      "asan.",
      "llvm.",
      "sancov.",
      "__ubsan_handle_",
      "free",
      "malloc",
      "calloc",
      "realloc"};

  for (auto const &BlacklistFunc : Blacklist) {
    if (F->getName().startswith(BlacklistFunc)) {
      return true;
    }
  }

  return false;
}


void MyPass::getAnalysisUsage(AnalysisUsage &AU) const {
  AU.setPreservesCFG();
  AU.addRequired<LoopInfoWrapperPass>();
}


// 分支和基本块的深度都是相对于函数而言的, 所以都写在runOnFunction就行了
bool MyPass::runOnFunction(Function &F) {

  if (isBlacklisted(&F)) {
    return false;
  }

  LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
  std::stack<BasicBlock *> stk;   // 栈, 辅助计算分支深度
  std::set<std::string> st;       // 集合, 记录分支下的循环块

  for (auto &BB : F) {

    if (!stk.empty() && &BB == stk.top())
      stk.pop();

    std::string bbname;

    for (auto &I : BB) {

      std::string filename;
      unsigned line;
      getDebugLoc(&I, filename, line);

      /* 仅保留文件名与行号 */
      std::size_t found = filename.find_last_of("/\\");
      if (found != std::string::npos)
        filename = filename.substr(found + 1);

      /* 设置基本块名称 */
      if (bbname.empty() && !filename.empty() && line) {
        bbname = filename + ":" + std::to_string(line);
        break;
      }
    }

    bool isLoopHeader = LI.isLoopHeader(&BB);  // 检查该BB是否是循环的入口
    bool isLoop = LI.getLoopFor(&BB);          // 检查该BB是否是循环
    unsigned loopDepth = LI.getLoopDepth(&BB); // 该BB所处的循环深度, 0表示不在循环, 1表示在1层循环, 2表示在2层...

    // 如果这个基本块是循环头, 查看是否在分支里
    // TODO: 目前无法识别最外层else下的循环块
    if (isLoopHeader) {
      if (stk.size()) // 在分支里的话, 加入集合, 否则就跳过, 避免将循环深度与分支深度搞混
        st.insert(bbname);
      continue;
    }

    for (auto &I : BB) {

    // 如果这个基本块中的指令可以转换为分支指令, 输出其所在基本块的T,F分支基本块并判断深度 (深度没找到现成的方法, 目前用的栈)
      if (BranchInst *BI = dyn_cast<BranchInst>(&I)) {

        if (!BI->isConditional())
          break;

        BasicBlock *BBT = BI->getSuccessor(0);
        BasicBlock *BBF = BI->getSuccessor(1);

        // F分支的基本块加入栈, 以计算分支深度
        stk.push(BBF);

      } else if (SwitchInst *SI = dyn_cast<SwitchInst>(&I)) {

        // 根据观察, 0一般是跳出switch-case后要经过的基本块或default基本块, 1至n-1一般是按照case顺序来的基本块
        int n = SI->getNumSuccessors();

        // 将default或跳出switch后的第一个基本块加入栈
        stk.push(SI->getSuccessor(0));
        }
      }

    std::ofstream fout(OutDirectory + "/BBnames.txt", std::ofstream::out | std::ofstream::app);
    fout << bbname << "\n";

    }

  // 参数中有 -mllvm -outdir=XXX的话, 就将集合内容输出到XXX下的loopInBranchBBs.txt中
  if (!OutDirectory.empty()) {
    std::ofstream fout(OutDirectory + "/loopInBranchBBs.txt", std::ofstream::out | std::ofstream::app);
    for (auto &&bb : st)
      if (!bb.empty())
        fout << bb << "\n";
  }

  return false;

}


/* 注册Pass */
static void registerPass3(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new MyPass());
}
static RegisterStandardPasses RegisterMyPass(PassManagerBuilder::EP_OptimizerLast, registerPass3);
static RegisterStandardPasses RegisterMyPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerPass3);