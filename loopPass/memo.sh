# 调用共享库
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libIdtfyPass.so examples/1_ezloop/loop.c -o examples/1_ezloop/loop.ll
clang -g -S -emit-llvm -Xclang -load -Xclang build/idtfyloop/libIdtfyPass.so examples/2_in-dep-loop/loop.c -o examples/2_in-dep-loop/loop.ll

# 获得mjs的循环BB
cd ~/Documents/fuzzing/mjs/mjs-issues-78
clang -Xclang -load -Xclang ~/Documents/project_vscode/cpp/llvm/5_LoopCode/loopPass/build/idtfyloop/libIdtfyPass.so -DMJS_MAIN mjs.c -ldl -g -o temp