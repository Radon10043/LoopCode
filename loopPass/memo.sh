###
# @Author: Radon
# @Date: 2022-02-20 16:43:09
 # @LastEditors: Radon
 # @LastEditTime: 2022-05-17 14:41:08
# @Description: Hi, say something
###

# 调用共享库
# Pass1: 识别循环
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libPass1.so examples/1_ezloop/loop.c -o examples/1_ezloop/loop.ll
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libPass1.so examples/2_in-dep-loop/loop.c -o examples/2_in-dep-loop/loop.ll

# Pass2: 识别分支
clang -g -S -emit-llvm -fno-discard-value-names -Xclang -load -Xclang build/idtfybranch/libPass2.so examples/2_in-dep-loop/loop.c -o examples/2_in-dep-loop/loop.ll
clang -g -S -emit-llvm -fno-discard-value-names -Xclang -load -Xclang build/idtfybranch/libPass2.so examples/3_loopBranch/lb.c -o examples/3_loopBranch/lb.ll

# Pass3: 识别循环与分支
clang -g -S -emit-llvm -fno-discard-value-names -Xclang -load -Xclang build/pass3/libPass3.so examples/3_loopBranch/lb.c -o examples/3_loopBranch/lb.ll

# Pass4: 识别处于循环中的基本块类型
clang -g -S -emit-llvm -Xclang -load -Xclang build/pass4/libPass4.so examples/3_loopBranch/lb.c -o examples/3_loopBranch/lb.ll

# 获得mjs的循环BB
cd ~/Documents/fuzzing/mjs/mjs-issues-78
clang -Xclang -load -Xclang ~/Documents/project_vscode/cpp/llvm/5_LoopCode/loopPass/build/idtfyloop/libPass1.so -DMJS_MAIN mjs.c -ldl -g -o temp
