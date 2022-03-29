/*
 * @Author: Radon
 * @Date: 2022-03-20 12:14:46
 * @LastEditors: Radon
 * @LastEditTime: 2022-03-29 15:27:27
 * @Description: Hi, say something
 */
#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <set>
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


/* 全局变量 */
std::unordered_set<std::string> loopHeaderUSet;


namespace {
  class LoopPass : public FunctionPass {
  public:
    static char ID;
    LoopPass()
        : FunctionPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const override;
    bool runOnFunction(Function &F) override;
  };

  class BranchPass : public ModulePass {
  public:
    static char ID;
    BranchPass()
        : ModulePass(ID) {}

    bool runOnModule(Module &M) override;
  };
} // namespace


char LoopPass::ID = 1;
char BranchPass::ID = 0;


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


void LoopPass::getAnalysisUsage(AnalysisUsage &AU) const {
  AU.setPreservesCFG();
  AU.addRequired<LoopInfoWrapperPass>();
}


bool LoopPass::runOnFunction(Function &F) {

  if (isBlacklisted(&F)) {
    return false;
  }

  LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();

  for (auto &BB : F) {

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
        bbname = filename + ":" + std::to_string(line) + ":";
        break;
      }
    }

    bool isLoopHeader = LI.isLoopHeader(&BB); // 检查该BB是否是循环的入口
    bool isLoop = LI.getLoopFor(&BB);         // 检查该BB是否是循环

    if (isLoopHeader && !bbname.empty()) // 如果是循环的入口, 加入集合, 在后续的识别分支操作中, 忽略掉循环入口BB
      loopHeaderUSet.insert(bbname);
  }
  return false;
}


bool BranchPass::runOnModule(Module &M) {
  for (auto &F : M) {
    /* Black list of function names */
    if (isBlacklisted(&F)) {
      continue;
    }

    /* AFLGo的预处理部分过程, 直接复制过来的 */
    for (auto &BB : F) {

      std::string bb_name("");
      std::string filename;
      unsigned line;

      for (auto &I : BB) {
        getDebugLoc(&I, filename, line);

        /* Don't worry about external libs */
        static const std::string Xlibs("/usr/");
        if (filename.empty() || line == 0 || !filename.compare(0, Xlibs.size(), Xlibs))
          continue;

        if (bb_name.empty()) {

          std::size_t found = filename.find_last_of("/\\");
          if (found != std::string::npos)
            filename = filename.substr(found + 1);

          bb_name = filename + ":" + std::to_string(line);
        }
      }

      if (!bb_name.empty()) {

        BB.setName(bb_name + ":");
        if (!BB.hasName()) {
          std::string newname = bb_name + ":";
          Twine t(newname);
          SmallString<256> NameData;
          StringRef NameRef = t.toStringRef(NameData);
          MallocAllocator Allocator;
          BB.setValueName(ValueName::Create(NameRef, Allocator));
        }
      }
    }

    /* My process*/
    for (auto &BB : F) {
      std::string filename;
      unsigned line = 0;

      for (auto &I : BB) {
        std::string loc;
        getDebugLoc(&I, filename, line);

        if (!filename.empty() && line) { // 获取当前指令所对应的位置
          size_t found = filename.find_last_of("/\\");
          if (found != std::string::npos)
            filename = filename.substr(found + 1);
          loc = filename + ":" + std::to_string(line);
        }

        if (loc.empty())
          continue;

        /* 通过BranchInst与SwitchInst对分支进行分析 */
        if (BranchInst *BI = dyn_cast<BranchInst>(&I)) { // 若当前指令能转换为BranchInst, 证明它是一个IF-ELSE分支?
          if (!BI->isConditional())                      // 若这个指令没有条件, 则跳过
            continue;
          if (loopHeaderUSet.find(BB.getName().str()) != loopHeaderUSet.end())
            continue;

          outs() << "IF-ELSE:" << loc << "\n";

          int n = BI->getNumSuccessors(); // 获取后继者数量, 并进行遍历
          for (int i = 0; i < n; i++) {
            outs() << BI->getSuccessor(i)->getName() << ",";
          }
          outs() << "\n\n";

        } else if (SwitchInst *SI = dyn_cast<SwitchInst>(&I)) { // 若当前指令能转换为SwitchInst, 证明它是一个SWITCH-CASE分支?
          outs() << "SWITCH-CASE:" << loc << "\n";

          int n = SI->getNumSuccessors();
          for (int i = 0; i < n; i++) {
            outs() << SI->getSuccessor(i)->getName() << ",";
          }
          outs() << "\n";
        }
      }
    }
  }
  return false;
}


/* 注册Pass */
static void registerPass2(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new LoopPass());
  PM.add(new BranchPass());
}
static RegisterStandardPasses RegisterRnDuPass(PassManagerBuilder::EP_OptimizerLast, registerPass2);
static RegisterStandardPasses RegisterRnDuPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerPass2);