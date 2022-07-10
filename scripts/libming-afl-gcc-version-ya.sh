# libming:swftophp
cp -r SRC LOOP-libming-gcc

cd LOOP-libming-gcc
git checkout b72cc2f # version 0.4.8

mkdir obj-loop
mkdir obj-loop/temp

# AFL Path
export AFL=/home/yagol/LoopCode/afl-yagol
export CC=$AFL/afl-gcc
export CXX=$AFL/afl-g++
export LDFLAGS=-lpthread

./autogen.sh

# 1st build
cd obj-loop
../configure --disable-shared --disable-freetype --prefix=$(pwd)
make clean
make