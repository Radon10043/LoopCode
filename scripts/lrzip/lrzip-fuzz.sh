###
# @Author: Radon
# @Date: 2023-01-03 16:13:23
 # @LastEditors: Radon
 # @LastEditTime: 2023-01-03 17:01:33
# @Description: Hi, say something
###

###
# @description: 下载lrzip
# @return {*}
###
download() {
  git clone https://github.com/ckolivas/lrzip.git LRZIP-SRC

  rm -rf lrzip-ed51e14
  cp -r LRZIP-SRC lrzip-ed51e14

  cd lrzip-ed51e14/
  git checkout ed51e14
}

###
# @description: 使用afl-model进行模糊测试
# @return {*}
###
model() {
  mkdir obj-model
  mkdir obj-model/temp

  # AFL-model Path
  export AFLM=/home/radon/Documents/project_vscode/cpp/llvm/5_LoopCode/afl-yagol

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-model/temp
  export CC=$AFLM/afl-clang-fast
  export CXX=$AFLM/afl-clang-fast++
  export LDFLAGS=-lpthread
  export ADDITIONAL="-outdir=$TMP_DIR"
  export BBNAMES="BBFile.txt"

  ./autogen.sh
  make distclean

  # 1st build
  cd obj-model
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean
  make

  # Get max line
  cat $TMP_DIR/$BBNAMES | sort | uniq >$TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/$BBNAMES
  line=$(wc -l $TMP_DIR/$BBNAMES | cut -d ' ' -f 1)

  # 2nd build
  CFLAGS="-bbfile=$TMP_DIR/$BBNAMES" CXXFLAGS="-bbfile=$TMP_DIR/$BBNAMES" ../configure --disable-shared --prefix=$(pwd)
  make clean
  make

  if [ -d "in/" ]; then
    rm -r in
  fi

  mkdir in
  cp $AFLM/testcases/archives/exotic/lrzip/small_archive.lrz in/

  for ((i = 1; i <= $1; i++)); do
    $AFLM/afl-fuzz -l $line -m none -i in -o out$i ./lrzip -t @@
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
