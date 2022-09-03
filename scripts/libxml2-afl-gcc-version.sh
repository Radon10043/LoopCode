# libxml2

cp -r SRC libxml2-2.9.14-gcc
cd libxml2-2.9.14-gcc
git checkout v2.9.14

mkdir obj-afl
mkdir obj-afl/temp

export AFL=/home/lowry/Documents/LoopCode/afl-yagol
export SUBJECT=$PWD
export CC=$AFL/afl-gcc
export CXX=$AFL/afl-g++
export LDFLAGS=-lpthread
# 1st build
cd obj-afl
cmake ..
make all
exit