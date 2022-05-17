/*
 * @Author: Radon
 * @Date: 2022-03-30 11:30:24
 * @LastEditors: Radon
 * @LastEditTime: 2022-05-17 15:01:49
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


/* 全局变量 */
std::map<std::string, unsigned> loopMap; // 记录循环基本块及其所处循环深度的map
std::map<std::string, char> typeMap;     // 记录基本块及其类型的map, <基本块名, 基本块类型(循环or分支)>
                                         // 'L': 循环基本块, 'B': 分支基本块, 'H': 循环头基本块


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

  return "empty?";
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
  // std::ofstream fout("./LOOPINFO.txt", std::ofstream::out | std::ofstream::app);

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

      /* 获取基本块名称 */
      if (bbname.empty() && !filename.empty() && line) {
        bbname = filename + ":" + std::to_string(line);
        break;
      }
    }

    /* 不对名字为空的基本块进行分析 */
    if (bbname.empty())
      continue;

    bool isLoopHeader = LI.isLoopHeader(&BB);  // 检查该BB是否是循环的入口
    bool isLoop = LI.getLoopFor(&BB);          // 检查该BB是否在循环中
    unsigned loopDepth = LI.getLoopDepth(&BB); // 该BB所处的循环深度, 0表示不在循环, 1表示在1层循环, 2表示在2层...

    /* 如果这个基本块不在循环里, 跳过 */
    if (!isLoop)
      continue;

    /* loopMap记录循环基本块及其深度 */
    loopMap[bbname] = loopDepth;

    /*  如果是循环头, 标记其为 'H' (Header) */
    if (isLoopHeader) {

      typeMap[bbname] = 'H';

    } else {

      /* 若基本块不是循环头并处于循环中, 查看这个基本块是分支基本块还是循环基本块 */
      bool isBranch = false;

      for (auto &I : BB) {

        /* 若该基本块中有指令可以转为BranchInst, 证明这个基本块中可能包含 if 语句 */
        if (BranchInst *BI = dyn_cast<BranchInst>(&I)) {
          if (BI->getNumSuccessors() > 1) {		// 若后继者数量多于1, 证明这个基本块中包含了 if
            isBranch = true;
            break;
          }
        }

        /* 若该基本块中有指令可以转为SwitchInst, 证明这个基本块中可能包含 switch 语句 */
        if (SwitchInst *SI = dyn_cast<SwitchInst>(&I)) {
          if (SI->getNumSuccessors() > 1) {		// 若后继者数量多于1, 证明这个基本块中包含了 switch. Tips: 若switch中只有一个default, 后继者数量是1
            isBranch = true;
            break;
          }
        }
      }

      if (isBranch)
        typeMap[bbname] = 'B'; // 分支基本块用 'B' 表示 (Branch)
      else
        typeMap[bbname] = 'L'; // 循环基本块用 'L' 表示 (Loop)
    }
  }
  return false;
}


bool AFLGoPass::runOnModule(Module &M) {

#if 1
  /* Debugging start ... */

  outs() << "loopMap:\n";
  for (auto &psu : loopMap)
    outs() << psu.first << "," << psu.second << "\n";

  outs() << "\ntypeMap:\n";
  for (auto &psc : typeMap)
    outs() << psc.first << "," << psc.second << "\n";

  /* Debugging end   ... */
#endif

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
  }

  return false;
}


/* 注册Pass */
static void registerPass3(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
  PM.add(new MyPass());
  PM.add(new AFLGoPass());
}
static RegisterStandardPasses RegisterMyPass(PassManagerBuilder::EP_OptimizerLast, registerPass3);
static RegisterStandardPasses RegisterMyPass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerPass3);