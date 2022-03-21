/*
 * @Author: Radon
 * @Date: 2022-03-20 12:14:46
 * @LastEditors: Radon
 * @LastEditTime: 2022-03-21 16:29:26
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

namespace {
  class BranchPass : public ModulePass {
  public:
    static char ID;
    BranchPass()
        : ModulePass(ID) {}

    bool runOnModule(Module &M) override;
  };
} // namespace


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


bool BranchPass::runOnModule(Module &M) {
  for (auto &F : M) {
    for (auto &BB : F) {
      std::string bbOriginName = BB.getName().str();
      std::string bbname, filename;
      unsigned line = 0;

      for (auto &I : BB) {
        getDebugLoc(&I, filename, line);
        if (!filename.empty() && line) {
          size_t found = filename.find_last_of("/\\");
          if (found != std::string::npos)   // 只保留文件名
            filename = filename.substr(found + 1);
          bbname = filename + ":" + std::to_string(line);
          break;
        }
      }

      size_t found = bbOriginName.find("if.");
      if (found != std::string::npos && !bbname.empty()) {
        outs() << "I found \"if\" in " << bbname << "!\n";
      }
    }
  }
  return false;
}


/* 注册Pass */
static void registerBranchPass(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new BranchPass());
}
static RegisterStandardPasses RegisterRnDuPass(PassManagerBuilder::EP_OptimizerLast, registerBranchPass);
static RegisterStandardPasses RegisterRnDuPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerBranchPass);