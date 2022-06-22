/*
 * @Author: Radon
 * @Date: 2022-03-30 11:30:24
 * @LastEditors: Radon
 * @LastEditTime: 2022-06-22 20:06:08
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
} // namespace


char MyPass::ID = 1;


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

/**
 * @brief 获取基本块的名字
 *
 * @param BB
 * @return std::string
 */
static std::string getBasicBlockName(BasicBlock *BB) {
  std::string bbname, filename;
  unsigned line = 0;

  for (auto &I : *BB) {

    getDebugLoc(&I, filename, line);

    if (!filename.empty() && line) {

      size_t found = filename.find_last_of("\\/");
      if (found != std::string::npos)
        filename = filename.substr(found + 1);

      bbname = filename + ":" + std::to_string(line);
      return bbname;
    }
  }

  return "";
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
  std::set<std::string> st;     // 集合, 记录分支下的循环块
  std::map<BasicBlock *, bool> mp;

  for (auto &BB : F) {

    mp[&BB] = true;

    std::string bbname = getBasicBlockName(&BB);

    if (!bbname.empty())
      BB.setName(bbname);

    bool isLoopHeader = LI.isLoopHeader(&BB);  // 检查该BB是否是循环的入口

    // 如果这个基本块是循环头, 查看是否在分支里
    if (isLoopHeader) {

      for (auto &pBb : mp) {
        if (!pBb.second) {
          st.insert(bbname);
          break;
        }
      }

      continue;
    }

    for (auto &I : BB) {

      // 如果这个基本块中的指令可以转换为分支指令, 输出其所在基本块的T,F分支基本块并判断深度 (深度没找到现成的方法, 目前用的栈)
      if (BranchInst *BI = dyn_cast<BranchInst>(&I)) {

        int n = BI->getNumSuccessors();
        for (int i = 0; i < n; i++) {
          mp[BI->getSuccessor(i)];
        }

      } else if (SwitchInst *SI = dyn_cast<SwitchInst>(&I)) {

        // 根据观察, 0一般是跳出switch-case后要经过的基本块或default基本块, 1至n-1一般是按照case顺序来的基本块
        int n = SI->getNumSuccessors();

        for (int i = 0; i < n; i++) {
          mp[SI->getSuccessor(i)];
        }
      }
    }
  }

  for (auto& name : st)
    outs() << name << "\n";

  return false;
}


/* 注册Pass */
static void registerPass3(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new MyPass());
}
static RegisterStandardPasses RegisterMyPass(PassManagerBuilder::EP_OptimizerLast, registerPass3);
static RegisterStandardPasses RegisterMyPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerPass3);