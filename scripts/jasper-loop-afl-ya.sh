# Jasper
git clone https://github.com/mdadams/jasper.git SRC

rm -rf jasper-3.0.3
cp -r SRC jasper-3.0.3
cd jasper-3.0.3; git checkout 020ec588      # version-3.0.3

mkdir obj-loop; mkdir obj-loop/temp

# AFL path
export AFL=/home/yagol/LoopCode/afl
export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-loop/temp
export CC=$AFL/afl-clang-fast; export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"

# 1st build
cd obj-loop; CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
make clean all

# Get max line
line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

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
echo "f**k!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >> in/testcase.txt
#原版, 非bb输入
#$AFL/afl-fuzz -m none -i in -o /home/yagol/PycharmProjects/LoopCode/scripts/jasper-3.0.3/obj-loop/out /home/yagol/PycharmProjects/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@
#非模型, 原版
$AFL/afl-fuzz -k 30 -l $line -m none -i in -o /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/out /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@
# 模型
#$AFL/afl-fuzz -p -k 30 -l $line -m none -i in -o /home/yagol/PycharmProjects/LoopCode/scripts/jasper-3.0.3/obj-loop/out /home/yagol/PycharmProjects/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@