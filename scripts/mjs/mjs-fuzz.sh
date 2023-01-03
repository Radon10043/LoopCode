###
# @Author: Radon
# @Date: 2023-01-03 16:43:03
 # @LastEditors: Radon
 # @LastEditTime: 2023-01-03 16:57:07
# @Description: Hi, say something
###

###
# @description: 下载mjs
# @return {*}
###
download() {
  git clone https://github.com/cesanta/mjs.git MJS-SRC

  rm -rf mjs-9eae0e6
  cp -r MJS-SRC mjs-9eae0e6

  cd mjs-9eae0e6/
  git checkout 9eae0e6
}

###
# @description: 使用afl-model进行模糊测试
# @return {*}
###
model() {
  mkdir obj-model
  mkdir obj-model/temp

  # AFL-model Path
  export AFLM=/path/to/afl-model

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-model/temp
  export CC=$AFLM/afl-clang-fast
  export CXX=$AFLM/afl-clang-fast++
  export LDFLAGS=-lpthread
  export ADDITIONAL="-outdir=$TMP_DIR"
  export BBNAMES="BBFile.txt"

  # 1st build
  $CC -DMJS_MAIN mjs.c $ADDITIONAL -ldl -g -o mjs-bin

  # Get max line
  cat $TMP_DIR/$BBNAMES | sort | uniq >$TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/$BBNAMES
  line=$(wc -l $TMP_DIR/$BBNAMES | cut -d ' ' -f 1)

  # 2nd build
  $CC -DMJS_MAIN mjs.c -bbfile=$TMP_DIR/$BBNAMES -ldl -g -o mjs-bin

  if [ -d "in/" ]; then
    rm -r in
  fi

  cd obj-model
  mkdir in
  cp $AFLM/testcases/others/js/small_script.js in/

  for ((i = 1; i <= $1; i++)); do
    $AFLM/afl-fuzz -l $line -m none -i in -o out$i ../mjs-bin -f @@
  done
}

# Entry
# $1: 表示用哪个fuzzer进行测试
# $2: 数字, 表示重复fuzz多少次
if ! [[ "$2" =~ ^[0-9]+$ ]]; then
  echo "$2 is not a number."
  exit
fi
echo "$2 is a number, yeah!"

download

if [ "$1" == "model" ]; then
  model $2
else
  echo "Unsupported fuzzer: $1."
  echo "Supported fuzzers: model(afl-model)."
fi
