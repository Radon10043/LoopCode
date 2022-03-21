###
# @Author: Radon
# @Date: 2022-02-20 16:43:09
 # @LastEditors: Radon
 # @LastEditTime: 2022-03-20 12:53:43
# @Description: Hi, say something
###

# 调用共享库
# LoopPass
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libLoopPass.so examples/1_ezloop/loop.c -o examples/1_ezloop/loop.ll
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libLoopPass.so examples/2_in-dep-loop/loop.c -o examples/2_in-dep-loop/loop.ll

# BranchPass
clang -g -S -emit-llvm -fno-discard-value-names -Xclang -load -Xclang build/idtfybranch/libBranchPass.so examples/2_in-dep-loop/loop.c -o examples/2_in-dep-loop/loop.ll

# 获得mjs的循环BB
cd ~/Documents/fuzzing/mjs/mjs-issues-78
clang -Xclang -load -Xclang ~/Documents/project_vscode/cpp/llvm/5_LoopCode/loopPass/build/idtfyloop/libLoopPass.so -DMJS_MAIN mjs.c -ldl -g -o temp
