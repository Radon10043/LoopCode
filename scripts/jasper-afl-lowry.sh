# Jasper
rm -rf SRC
rm -rf jasper-3.0.3
rm -rf jasper-3.0.3-gcc
rm -rf obj-loop
proxychains git clone https://github.com/mdadams/jasper.git SRC
echo "run gcc first"
./jasper-afl-gcc-version-ya.sh

cp -r SRC jasper-3.0.3
cd jasper-3.0.3
git checkout 020ec588 # version-3.0.3

mkdir obj-loop
mkdir obj-loop/temp

# AFL path
export AFL=/home/lowry/Documents/LoopCode/afl-yagol
export SUBJECT=$PWD
export TMP_DIR=$PWD/obj-loop/temp
export PY_OUTPUT_DIR_PATH=$TMP_DIR/py.out
export CC=$AFL/afl-clang-fast
export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"
# py module path
export PY_PATH=/home/lowry/anaconda3/bin/python
export PY_MAIN_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/main.py
export KEEP_SHOWMAP_THREAD_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/keep_showmap_thread.py
export PY_OUTPUT_DIR_PATH=$PWD/obj-loop/temp/py.log
export PRE_TRAIN_AFL_OUT_DIR_NAME=out_afl_pre_train
export MODEL_PATH=$PWD/obj-loop/temp/jasper.model.lowry
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

# 第一次afl，用于生成模型的初始测试用例
#$AFL/afl-fuzz -k 1 -l $line -m none -i in -o /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out_afl_origin.jpg --input @@
## 第一次py，预训练模型
#$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --pre-train --model-save-path $MODEL_PATH --pre-train-testcase /home/lowry/Documents/LoopCode/scripts/jasper_in2 --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3-gcc/obj-loop/src/app/jasper --append-args "--output /tmp/out_afl_origin.jpg --input"
## 正式运行afl-model
#$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --model-load-path $MODEL_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3-gcc/obj-loop/src/app/jasper --append-args "--output /tmp/out_afl_origin.jpg --input" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
#sleep 5s
#$AFL/afl-fuzz -p -y -k 360 -l $line -t 1000+ -e 0 -m none -i /home/lowry/Documents/LoopCode/scripts/jasper_in2 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@

# 独立运行原版afl
#$AFL/afl-fuzz -k 1 -l $line -m none -i in -o /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out_afl_origin.jpg --input @@
$PY_PATH -u $KEEP_SHOWMAP_THREAD_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --model-load-path $MODEL_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/jasper-3.0.3-gcc/obj-loop/src/app/jasper --append-args "--output /tmp/out_afl_origin.jpg --input" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
sleep 5s
$AFL/afl-fuzz -k 360 -l $line -t 1000+ -e 0 -m none -i /home/lowry/Documents/LoopCode/scripts/jasper_in2 -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@
