/*
  Copyright 2015 Google LLC All rights reserved.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

/*
   american fuzzy lop - LLVM-mode instrumentation pass
   ---------------------------------------------------

   Written by Laszlo Szekeres <lszekeres@google.com> and
              Michal Zalewski <lcamtuf@google.com>

   LLVM integration design comes from Laszlo Szekeres. C bits copied-and-pasted
   from afl-as.c are Michal's fault.

   This library is plugged into LLVM when invoking clang through afl-clang-fast.
   It tells the compiler to add code roughly equivalent to the bits discussed
   in ../afl-as.h.
*/

#define AFL_LLVM_PASS

#include "../config.h"
#include "../debug.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <list>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <algorithm>
#include <set>
#include <unordered_set>
#include <map>

#include "llvm/Analysis/LoopInfo.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/Debug.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Analysis/CFGPrinter.h"

#if defined(LLVM34)
#include "llvm/DebugInfo.h"
#else
#include "llvm/IR/DebugInfo.h"
#endif

#if defined(LLVM34) || defined(LLVM35) || defined(LLVM36)
#define LLVM_OLD_DEBUG_API
#endif

using namespace llvm;

cl::opt<std::string> BBFile(
    "bbfile",
    cl::desc("Input file containing all bbs."),
    cl::value_desc("bbfile"));

cl::opt<std::string> OutDirectory(
    "outdir",
    cl::desc("Output directory where bbfile.txt is generated."),
    cl::value_desc("outdir"));

namespace {

  class AFLCoverage : public ModulePass {

    public:

      static char ID;
      AFLCoverage() : ModulePass(ID) { }

      bool runOnModule(Module &M) override;

      // StringRef getPassName() const override {
      //  return "American Fuzzy Lop Instrumentation";
      // }

  };

}


char AFLCoverage::ID = 0;


static void getDebugLoc(const Instruction *I, std::string &Filename,
                        unsigned &Line) {
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
    "realloc"
  };

  for (auto const &BlacklistFunc : Blacklist) {
    if (F->getName().startswith(BlacklistFunc)) {
      return true;
    }
  }

  return false;
}


bool AFLCoverage::runOnModule(Module &M) {

  bool is_preprocessing = false;
  std::vector<std::string> bbvec;

  /* -bbfile 与 -outdir 不能同时存在 */
  if (!BBFile.empty() && !OutDirectory.empty()) {
    FATAL("-bbfile and -outdir can't coexist.");
    return false;
  }

  /* 如果 -outdir 不为空的话, 证明是预处理; 否则是程序插桩 */
  if (!OutDirectory.empty())
    is_preprocessing = true;

  /* 如果BBFile不为空的话, 证明是程序插桩阶段, 读取文件并将内容存入map */
  if (!BBFile.empty()) {

    std::ifstream fin(BBFile);
    std::string bbname;

    /* 读取文件, 并根据行号当作id, 存入map中 */
    if (fin.is_open()) {

      while (getline(fin, bbname)) {
        bbvec.emplace_back(bbname);
      }

    } else {

      outs() << "I can't find bbfile, use AFL instrumentation method.\n";

    }

  }

  /* Show a banner */

  char be_quiet = 0;

  if (isatty(2) && !getenv("AFL_QUIET")) {

    SAYF(cCYA "afl-llvm-pass " cBRI VERSION cRST " %s mode modified by Radon\n",
        (is_preprocessing ? "preprocessing" : "instrumentation"));

  } else be_quiet = 1;

  /* Decide instrumentation ratio */

  char* inst_ratio_str = getenv("AFL_INST_RATIO");
  unsigned int inst_ratio = 100;

  if (inst_ratio_str) {

    if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || !inst_ratio ||
        inst_ratio > 100)
      FATAL("Bad value of AFL_INST_RATIO (must be between 1 and 100)");

  }

  /* 预处理阶段, 基本上照搬的AFLGo, 根据需求进行了一些删减 */
  if (is_preprocessing) {

    std::ofstream bbfile(OutDirectory + "/BBFile.txt", std::ofstream::out | std::ofstream::app);

    for (auto& F : M) {

      /* Black list of function names */
      if (isBlacklisted(&F)) {
        continue;
      }

      for (auto &BB : F) {

        std::string bbname;
        std::string filename;
        unsigned line = 0;

        for (auto &I : BB) {
          getDebugLoc(&I, filename, line);

          /* Don't worry about external libs */
          static const std::string Xlibs("/usr/");
          if (filename.empty() || line == 0 || !filename.compare(0, Xlibs.size(), Xlibs))
            continue;

          if (bbname.empty()) {

            std::size_t found = filename.find_last_of("/\\");
            if (found != std::string::npos)
              filename = filename.substr(found + 1);

            bbname = filename + ":" + std::to_string(line);

          }

        }

        /* 将基本块名字输出到文件中 */
        // TODO: BB名可能会有重复, 需要改进
        if (!bbname.empty()) {
          bbfile << bbname << "\n";
        }

      }

    }

  /* 程序插桩 */
  } else {
    LLVMContext &C = M.getContext();

    IntegerType *Int8Ty  = IntegerType::getInt8Ty(C);
    IntegerType *Int32Ty = IntegerType::getInt32Ty(C);
    IntegerType *Int64Ty = IntegerType::getInt64Ty(C);

#ifdef __x86_64__
    IntegerType *LargestType = Int64Ty;
#else
    IntegerType *LargestType = Int32Ty;
#endif

    /* TODO: Radon: I dont think it's a good way. */

    std::vector<ConstantInt*> bitValue(8);
    for (int i = 0; i < 8; i++) {
      bitValue[i] = ConstantInt::get(Int8Ty, 128 >> i);
    }

    /* Get globals for the SHM region and the previous location. Note that
      __afl_prev_loc is thread-local. */

    GlobalVariable *AFLMapPtr =
        new GlobalVariable(M, PointerType::get(Int8Ty, 0), false,
                          GlobalValue::ExternalLinkage, 0, "__afl_area_ptr");

    GlobalVariable *AFLPrevLoc = new GlobalVariable(
        M, Int32Ty, false, GlobalValue::ExternalLinkage, 0, "__afl_prev_loc",
        0, GlobalVariable::GeneralDynamicTLSModel, 0, false);

    /* Instrument all the things! */

    int inst_blocks = 0;

    for (auto &F : M)
      for (auto &BB : F) {

        std::string bbname;

        for (auto &I : BB) {

          std::string filename;
          unsigned line;
          getDebugLoc(&I, filename, line);

          if (filename.empty() || line == 0)
            continue;
          std::size_t found = filename.find_last_of("/\\");
          if (found != std::string::npos)
            filename = filename.substr(found + 1);

          bbname = filename + ":" + std::to_string(line);

          break;

        }

        BasicBlock::iterator IP = BB.getFirstInsertionPt();
        IRBuilder<> IRB(&(*IP));

        if (AFL_R(100) >= inst_ratio) continue;

        /* Make up cur_loc */

        unsigned int cur_loc = AFL_R(MAP_SIZE);

        ConstantInt *CurLoc = ConstantInt::get(Int32Ty, cur_loc);

        /* Load prev_loc */

        LoadInst *PrevLoc = IRB.CreateLoad(AFLPrevLoc);
        PrevLoc->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *PrevLocCasted = IRB.CreateZExt(PrevLoc, IRB.getInt32Ty());

        /* Load SHM pointer */

        LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
        MapPtr->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *MapPtrIdx =
            IRB.CreateGEP(MapPtr, IRB.CreateXor(PrevLocCasted, CurLoc));

        /* Update bitmap */

        LoadInst *Counter = IRB.CreateLoad(MapPtrIdx);
        Counter->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *Incr = IRB.CreateAdd(Counter, ConstantInt::get(Int8Ty, 1));
        IRB.CreateStore(Incr, MapPtrIdx)
            ->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        /* Set prev_loc to cur_loc >> 1 */

        StoreInst *Store =
            IRB.CreateStore(ConstantInt::get(Int32Ty, cur_loc >> 1), AFLPrevLoc);
        Store->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        /* 在BB中插入指定内存区域至1的指令, 即覆盖了这个BB的话就把共享内存中的指定区域变为1 */
        int idx = std::find(bbvec.begin(), bbvec.end(), bbname) - bbvec.begin();
        if (idx < bbvec.size()) {

          // 目前的step是1bit, 不知道是否写对了
          ConstantInt *MapCovLoc = ConstantInt::get(LargestType, MAP_SIZE + idx / 8);

          Value *MapCovPtr = IRB.CreateBitCast(
              IRB.CreateGEP(MapPtr, MapCovLoc), Int8Ty->getPointerTo());
          LoadInst *MapCov = IRB.CreateLoad(MapCovPtr);
          MapCov->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

          Value *OrCov = IRB.CreateOr(MapCov, bitValue[idx % 8]);
          IRB.CreateStore(OrCov, MapCovPtr)
              ->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        }

        inst_blocks++;

      }
    /* Say something nice. */

    if (!be_quiet) {

      if (!inst_blocks) WARNF("No instrumentation targets found.");
      else OKF("Instrumented %u locations (%s mode, ratio %u%%).",
              inst_blocks, getenv("AFL_HARDEN") ? "hardened" :
              ((getenv("AFL_USE_ASAN") || getenv("AFL_USE_MSAN")) ?
                "ASAN/MSAN" : "non-hardened"), inst_ratio);

    }
  }

  return true;

}


static void registerAFLPass(const PassManagerBuilder &,
                            legacy::PassManagerBase &PM) {

  PM.add(new AFLCoverage());

}


static RegisterStandardPasses RegisterAFLPass(
    PassManagerBuilder::EP_ModuleOptimizerEarly, registerAFLPass);

static RegisterStandardPasses RegisterAFLPass0(
    PassManagerBuilder::EP_EnabledOnOptLevel0, registerAFLPass);
