# libming:swftophp
rm -rf SRC
rm -rf LOOP-libming-gcc
rm -rf LOOP-libming

proxychains git clone https://github.com/libming/libming.git SRC
echo "run gcc first"
./libming-afl-gcc-version-ya.sh
cp -r SRC LOOP-libming

cd LOOP-libming
git checkout b72cc2f # version 0.4.8

mkdir obj-loop
mkdir obj-loop/temp

# AFL path
export AFL=/home/lowry/Documents/LoopCode/afl-lowry
export SUBJECT=$PWD
export TMP_DIR=$PWD/obj-loop/temp
export PY_OUTPUT_DIR_PATH=$TMP_DIR/py.out
export CC=$AFL/afl-clang-fast
export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"
# py module path
export PY_PATH=/home/lowry/anaconda3/bin/python
export PY_MAIN_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/k_means_main.py
export KEEP_SHOWMAP_THREAD_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/keep_showmap_thread.py
export PY_OUTPUT_DIR_PATH=$PWD/obj-loop/temp/py.log
export GOOD_SEEDS_PATH=$PWD/obj-loop/temp/good_seeds.txt
export FUZZER_STATS=$PWD/obj-loop/out/fuzzer_stats

./autogen.sh

# 1st build
cd obj-loop
CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --disable-freetype --prefix=$(pwd)
make clean
make

# Get max line
line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

# 2nd build
CFLAGS="-bbfile=$TMP_DIR/BBFile.txt" CXXFLAGS="-bbfile=$TMP_DIR/BBFile.txt" ../configure --disable-shared --disable-freetype --prefix=$(pwd)
make clean
make

if [ -d "in/" ]; then
  rm -r in
fi

mkdir in
wget -P in http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf
mkdir in_afl_origin
wget -P in_afl_origin http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf

# 运行
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --fuzzer-stats $FUZZER_STATS --out-path $TMP_DIR --good-seeds-path $GOOD_SEEDS_PATH --skip-log-stdout --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/LOOP-libming-gcc/obj-afl/util/swftophp --append-args "" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
sleep 5s
$AFL/afl-fuzz -p -y -k 180 -l $line -t 1000+ -e 3 -m none -i /home/lowry/Documents/LoopCode/scripts/libming_in3 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/util/swftophp @@

# 独立运行原版afl
#$PY_PATH -u $KEEP_SHOWMAP_THREAD_PATH --kmeans F --fuzzer-stats $FUZZER_STATS --out-path $TMP_DIR --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/LOOP-libming-gcc/obj-afl/util/swftophp --append-args "" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
#sleep 5s
#$AFL/afl-fuzz -k 180 -l $line -m none -i /home/lowry/Documents/LoopCode/scripts/libming_in3 -o /home/lowry/Documents/LoopCode/scripts/LOOP-libming/obj-loop/out /home/lowry/Documents/LoopCode/scripts/LOOP-libming/obj-loop/util/swftophp @@
