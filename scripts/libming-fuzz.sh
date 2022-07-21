###
# @Author: Radon
# @Date: 2022-05-16 14:23:19
# @LastEditors: Radon
# @LastEditTime: 2022-07-21 15:43:45
# @Description: Hi, say something
###

###
# @description: 下载libming
# @return {*}
###
download() {
  git clone https://github.com/libming/libming.git LIBMING-SRC

  cp -r LIBMING-SRC libming-0.4.8

  cd libming-0.4.8/
  git checkout b72cc2f # version 0.4.8
}

###
# @description: 使用afl进行模糊测试
# @param: $1 数字, 重复测试多少次
# @return {*}
###
afl() {
  mkdir obj-afl
  mkdir obj-afl/temp

  # AFL Path
  export AFL=/path/to/afl

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-afl/temp
  export CC=$AFL/afl-clang-fast
  export CXX=$AFL/afl-clang-fast++
  export LDFLAGS=-lpthread

  ./autogen.sh

  cd obj-afl
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean
  make

  mkdir in
  wget -P in http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf

  for ((i = 1; i <= $1; i++)); do
    # timeout?
    $AFL/afl-fuzz -m none -i in -o out ./util/swftophp @@
  done
}

###
# @description: 使用afl进行模糊测试
# @param: $1 数字, 重复测试多少次
# @return {*}
###
model() {
  mkdir obj-model
  mkdir obj-model/temp

  # AFL-model Path
  export AFLM=/path/to/afl

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-model/temp
  export CC=$AFLM/afl-clang-fast
  export CXX=$AFLM/afl-clang-fast++
  export LDFLAGS=-lpthread
  export ADDITIONAL="-outdir=$TMP_DIR"

  ./autogen.sh

  # 1st build
  cd obj-model
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean
  make

  # Get max line
  line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

  # 2nd build
  CFLAGS="-bbfile=$TMP_DIR/BBFile.txt" CXXFLAGS="-bbfile=$TMP_DIR/BBFile.txt" ../configure --disable-shared --prefix=$(pwd)
  make clean
  make

  if [ -d "in/" ]; then
    rm -r in
  fi

  mkdir in
  wget -P in http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf

  for ((i = 1; i <= $1; i++)); do
    # timeout? -p?
    $AFLM/afl-fuzz -l $line -m none -i in -o out ./util/swftophp @@
  done
}

#Entry
# $1: 表示用哪个fuzzer进行测试
# $2: 数字, 表示重复fuzz多少次
if ! [[ "$2" =~ ^[0-9]+$ ]]; then
  echo "$2 is not a number."
  exit
fi
echo "$2 is a number, yeah!"

download

if [ "$1" == "afl" ]; then
  afl $2
elif [ "$1" == "model" ]; then
  model $2
else
  echo "Unsupported fuzzer: $1."
  echo "Supported fuzzers: afl, model(afl-model)."
fi
