git clone https://github.com/libming/libming.git SRC

cp -r SRC LOOP

cd LOOP/; git checkout b72cc2f # version 0.4.8

mkdir obj-loop; mkdir obj-loop/temp

# AFL Path
export AFL=/home/yagol/PycharmProjects/LoopCode/afl
export PY_PATH=/home/yagol/anaconda3/envs/LoopCode/bin/python
export PY_MAIN_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/src/main.py
export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-loop/temp
export CC=$AFL/afl-clang-fast; export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"

./autogen.sh

# 1st build
cd obj-loop; CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --disable-freetype --prefix=`pwd`
make clean; make

# Get max line
line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

# 2nd build
CFLAGS="-bbfile=$TMP_DIR/BBFile.txt" CXXFLAGS="-bbfile=$TMP_DIR/BBFile.txt" ../configure --disable-shared --disable-freetype --prefix=`pwd`
make clean; make

if [ -d "in/" ]; then
    rm -r in
fi

mkdir in; wget -P in http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf

#$AFL/afl-fuzz -k 30 -l $line -m none -i in -o out ./util/swftophp @@
#
#$PY_PATH $PY_MAIN_PATH True $TMP_DIR/BBFile.txt &$AFL/afl-fuzz -p -k 600 -l $line -m none -i in -o out /home/yagol/PycharmProjects/LoopCode/scripts/LOOP/obj-loop/util/swftophp @@
#
$AFL/afl-fuzz -p -k 30 -l $line -m none -i in -o /home/yagol/PycharmProjects/LoopCode/scripts/LOOP/obj-loop/out /home/yagol/PycharmProjects/LoopCode/scripts/LOOP/obj-loop/util/swftophp @@