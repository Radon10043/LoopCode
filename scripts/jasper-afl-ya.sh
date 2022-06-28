# Jasper
git clone https://github.com/mdadams/jasper.git SRC

rm -rf jasper-3.0.3
cp -r SRC jasper-3.0.3
cd jasper-3.0.3
git checkout 020ec588 # version-3.0.3

mkdir obj-loop
mkdir obj-loop/temp

# AFL path
export AFL=/home/yagol/LoopCode/afl-yagol
export SUBJECT=$PWD
export TMP_DIR=$PWD/obj-loop/temp
export PY_OUTPUT_DIR_PATH=$TMP_DIR/py.out
export CC=$AFL/afl-clang-fast
export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"
# py module path
export PY_PATH=/home/yagol/anaconda3/envs/LoopCode/bin/python
export PY_MAIN_PATH=/home/yagol/LoopCode/machine_learning_module/src/main.py
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
#cp $AFL/testcases/images/jp2/not_kitty.jp2 in/
echo "" >in/in.jp2

# echo core >/proc/sys/kernel/core_pattern

# 第一次afl，用于生成模型的初始测试用例
$AFL/afl-fuzz -k 1 -l $line -m none -i in -o /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out_afl_origin.jpg --input @@
# 第一次py，预训练模型
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --pre-train --model-save-path $MODEL_PATH --pre-train-testcase /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME
# 正式运行afl-model
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --model-load-path $MODEL_PATH & # 后台运行py
sleep 5s
$AFL/afl-fuzz -p -y -k 240 -l $line -e 10 -m none -i /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME/seed -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/src/app/jasper --output /tmp/out.jpg --input @@

# 独立运行原版afl
#$AFL/afl-fuzz -k 60 -l $line -m none -i in_afl_origin -o /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/out_afl_origin /home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/src/app/jasper --output /tmp/out_afl_origin.jpg --input @@
