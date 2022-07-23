cp -r SRC libxml2-2.9.14-gcc-version

cd libxml2-2.9.14-gcc-version
git checkout v2.9.14
mkdir ob
mkdir obj-afl
mkdir obj-afl/temp

export AFL=/home/yagol/LoopCode/afl-yagol
export CC=$AFL/afl-gcc
export CXX=$AFL/afl-g++
./autogen.sh
make distclean
cd obj-afl
../configure --disable-shared --prefix=$(pwd)
make all
exit
