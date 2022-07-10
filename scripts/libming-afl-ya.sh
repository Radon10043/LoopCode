# libming:swftophp
rm -rf SRC
rm -rf LOOP-libming-gcc
rm -rf LOOP-libming

git clone https://github.com/libming/libming.git SRC
echo "run gcc first"
./libming-afl-gcc-version-ya.sh
cp -r SRC LOOP-libming

cd LOOP-libming
git checkout b72cc2f # version 0.4.8

mkdir obj-loop
mkdir obj-loop/temp

# AFL Path
export AFL=/home/yagol/LoopCode/afl-yagol
# Py path
export PY_PATH=/home/yagol/anaconda3/envs/LoopCode/bin/python
export PY_MAIN_PATH=/home/yagol/LoopCode/machine_learning_module/src/main.py
export PY_OUTPUT_DIR_PATH=$PWD/obj-loop/temp/py.log
export PRE_TRAIN_AFL_OUT_DIR_NAME=out_afl_pre_train
export MODEL_PATH=$PWD/obj-loop/temp/libming.model.lowry
export SUBJECT=$PWD
export TMP_DIR=$PWD/obj-loop/temp
export CC=$AFL/afl-clang-fast
export CXX=$AFL/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-outdir=$TMP_DIR"

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

## 第一次afl，用于生成模型的初始测试用例
$AFL/afl-fuzz -k 1 -l $line -m none -i in -o /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/util/swftophp @@
## 第一次py，预训练模型
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --pre-train --model-save-path $MODEL_PATH --pre-train-testcase /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME
## 正式运行afl-model
$PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --model-load-path $MODEL_PATH --gcc-version-bin /home/yagol/LoopCode/scripts/LOOP-libming-gcc/obj-loop/util/swftophp --append-args "" --testcase-dir-path $SUBJECT/obj-loop/out & # 后台运行py
sleep 5s
$AFL/afl-fuzz -p -y -k 240 -l $line -t 1000+ -e 0 -m none -i /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/$PRE_TRAIN_AFL_OUT_DIR_NAME/seed -o $SUBJECT/obj-loop/out $SUBJECT/obj-loop/util/swftophp @@

# 独立运行原版afl
#$AFL/afl-fuzz -k 60 -l $line -m none -i in_afl_origin -o /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/out_afl_origin /home/yagol/LoopCode/scripts/LOOP-libming/obj-loop/util/swftophp @@
