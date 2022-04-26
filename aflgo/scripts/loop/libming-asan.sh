cd libming-CVE-2018-8962/

if [ -d "obj-asan/" ]; then
    rm -r obj-asan
fi

mkdir obj-asan; mkdir obj-asan/temp

export AFL=~/Documents/fuzzing/afl

export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-asan/temp
export CC=$AFL/afl-clang-fast; export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-g -fsanitize=address -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"

./autogen.sh;
cd obj-asan; CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=`pwd`
make clean; make

# for f in `ls | grep id`; do echo -e "\n${f:0:10}" >> 0.txt | /home/radon/Documents/fuzzing/libming/libming-CVE-2018-8962/obj-asan/util/swftophp $f 2>&1 | grep SUMMARY | tee -a 0.txt; done
