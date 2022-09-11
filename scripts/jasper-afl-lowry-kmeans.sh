# Jasper
rm -rf SRC
rm -rf jasper-2.0.21
rm -rf jasper-2.0.21-gcc
rm -rf obj-loop
proxychains git clone https://github.com/mdadams/jasper.git SRC
echo "run gcc first"
./jasper-afl-gcc-version-ya.sh

cp -r SRC jasper-2.0.21
cd jasper-2.0.21
git checkout version-2.0.21 # version-2.0.21

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
export FUZZER_STATS=/home/lowry/Documents/LoopCode/scripts/jasper-2.0.21/obj-loop/out/fuzzer_stats
# 1st build
cd obj-loop
CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
make clean all

# Get max line
line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

cd $SUBJECT
mkdir obj-loop2
cp -r obj-loop/temp obj-loop2/temp
rm -rf obj-loop
mv obj-loop2 obj-loop
cd obj-loop

# 2nd build
export ADDITIONAL="-bbfile=$TMP_DIR/BBFile.txt"
CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
make clean all

mkdir in
cp $AFL/testcases/images/jp2/not_kitty.jp2 in/
#echo "" >in/in.jp2

# echo core >/proc/sys/kernel/core_pattern

# 运行afl-model
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --fuzzer-stats $FUZZER_STATS --out-path $TMP_DIR --good-seeds-path $GOOD_SEEDS_PATH --skip-log-stdout --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/jasper-2.0.21-gcc/obj-loop/src/app/jasper --append-args "--output /tmp/out_afl_origin.jpg --input" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
sleep 5s
$AFL/afl-fuzz -p -y -k 180 -l $line -t 1000+ -e 1 -m none -i /home/lowry/Documents/LoopCode/scripts/jasper_in2 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/appl/jasper --output /tmp/out.jpg --input @@

# 独立运行原版afl
#$AFL/afl-fuzz -k 1 -l $line -m none -i in -o /home/lowry/Documents/LoopCode/scripts/jasper-2.0.21/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME /home/lowry/Documents/LoopCode/scripts/jasper-2.0.21/obj-loop/src/appl/jasper --output /tmp/out_afl_origin.jpg --input @@
#$PY_PATH -u $KEEP_SHOWMAP_THREAD_PATH --kmeans T --fuzzer-stats $FUZZER_STATS --log-path $PY_OUTPUT_DIR_PATH --out-path $TMP_DIR --skip-log-stdout --good-seeds-path $GOOD_SEEDS_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/jasper-2.0.21-gcc/obj-loop/src/app/jasper --append-args "--output /tmp/out_afl_origin.jpg --input" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
#sleep 5s
#$AFL/afl-fuzz -p -y -k 180 -l $line -t 1000+ -e 0 -m none -i /home/lowry/Documents/LoopCode/scripts/jasper_in2 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/appl/jasper --output /tmp/out.jpg --input @@

#$AFL/afl-fuzz -k 180 -l $line -t 1000+ -e 0 -m none -i /home/lowry/Documents/LoopCode/scripts/jasper_in2 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/appl/jasper --output /tmp/out.jpg --input @@
