# Jasper

cp -r SRC jasper-3.0.3-gcc
cd jasper-3.0.3-gcc
git checkout 020ec588 # version-3.0.3

mkdir obj-loop
mkdir obj-loop/temp

export AFL=/home/yagol/LoopCode/afl-yagol
export SUBJECT=$PWD
export CC=$AFL/afl-gcc
export CXX=$AFL/afl-g++
export LDFLAGS=-lpthread
# 1st build
cd obj-loop
cmake ..
make all
exit