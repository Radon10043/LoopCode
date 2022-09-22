# Jasper

#cp -r SRC jasper-2.0.21-gcc
#cd jasper-2.0.21-gcc
#git checkout v2.0.21
cp -r SRC jasper-3.0.3-gcc
cd jasper-3.0.3-gcc
git checkout 020ec588 # version-3.0.3

mkdir obj-loop
mkdir obj-loop/temp

export AFL=/home/lowry/Documents/LoopCode/afl-lowry
export SUBJECT=$PWD
export CC=$AFL/afl-gcc
export CXX=$AFL/afl-g++
export LDFLAGS=-lpthread
# 1st build
cd obj-loop
cmake ..
make all
exit