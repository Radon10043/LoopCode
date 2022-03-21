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

namespace {
  class LoopPass : public FunctionPass {
  public:
    static char ID;
    LoopPass()
        : FunctionPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const override;
    bool runOnFunction(Function &F) override;
  };
} // namespace


char LoopPass::ID = 0;


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


void LoopPass::getAnalysisUsage(AnalysisUsage &AU) const {
  AU.setPreservesCFG();
  AU.addRequired<LoopInfoWrapperPass>();
}


bool LoopPass::runOnFunction(Function &F) {

  std::set<std::string> loopBBSet; // 存储循环BB的集合
  LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
  std::ofstream fout("/home/radon/Documents/LoopBBs.txt", std::ofstream::out | std::ofstream::app);

  for (auto &BB : F) {

    std::string bbName;

    for (auto &I : BB) {

      std::string filename;
      unsigned line;
      getDebugLoc(&I, filename, line);

      /* 仅保留文件名与行号 */
      std::size_t found = filename.find_last_of("/\\");
      if (found != std::string::npos)
        filename = filename.substr(found + 1);

      /* 设置基本块名称 */
      if (bbName.empty() && !filename.empty() && line) {
        bbName = filename + ":" + std::to_string(line);
      }
    }

    bool isLoop = LI.getLoopFor(&BB);
    if (isLoop && !bbName.empty())
      loopBBSet.insert(bbName);

    /* 将集合中的内容写入文件 */
    for (auto loopBB : loopBBSet)
      fout << loopBB << "\n";
    errs() << "Hi, I found " << loopBBSet.size() << " loopBBs in " << F.getName() << ", and I have written to ~/Documents/LoopBBs.txt.\n";
  }
  return false;
}


/* 注册Pass */
static void registerLoopPass(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new LoopPass());
}
static RegisterStandardPasses RegisterRnDuPass(PassManagerBuilder::EP_OptimizerLast, registerLoopPass);
static RegisterStandardPasses RegisterRnDuPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerLoopPass);