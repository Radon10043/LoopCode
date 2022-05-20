
# Jasper

git clone https://github.com/mdadams/jasper.git SRC

rm -rf jasper-3.0.3
cp -r SRC jasper-3.0.3
cd jasper-3.0.3; git checkout 020ec588      # version-3.0.3

mkdir obj-loop; mkdir obj-loop/temp

# AFL path
export AFL=/path/to/afl

export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-loop/temp
export CC=$AFL/afl-clang-fast; export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"

# 1st build
cd obj-loop; CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
make clean all

# Get max line
line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

# 删掉obj-loop文件夹, 重新建一个, 因为继续在这个文件夹make的话会延续第一次build的命令行参数
# 不知道是什么原因
cd $SUBJECT; mkdir obj-loop2
cp -r obj-loop/temp obj-loop2/temp
rm -rf obj-loop; mv obj-loop2 obj-loop
cd obj-loop

# 2nd build
export ADDITIONAL="-bbfile=$TMP_DIR/BBFile.txt"
CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
make clean all

mkdir in
cp $AFL/testcases/images/jp2/not_kitty.jp2 in/

$AFL/afl-fuzz -l $line -m none -i in -o out src/app/jasper --output /tmp/out.jpg --input @@