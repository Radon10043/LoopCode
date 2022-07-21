###
# @Author: Radon
# @Date: 2022-05-20 18:28:34
# @LastEditors: Radon
# @LastEditTime: 2022-07-21 15:47:49
# @Description: jasper fuzz script
###

###
# @description: 下载jasper
# @return {*}
###
download() {
  git clone https://github.com/mdadams/jasper.git JASPER-SRC

  rm -rf jasper-3.0.3
  cp -r JASPER-SRC jasper-3.0.3
  cd jasper-3.0.3
  git checkout 020ec588 # version-3.0.3
}

###
# @description: 使用afl进行模糊测试
# @param: $1 数字, 重复多少次测试
# @return {*}
###
afl() {
  mkdir obj-afl
  mkdir obj-afl/temp

  # AFL path
  export AFL=/path/to/afl

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-afl/temp
  export CC=$AFL/afl-clang-fast
  export CXX=$AFL/afl-clang-fast++
  export LDFLAGS=-lpthread

  cd obj-afl
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
  make clean all

  mkdir in
  # cp $AFL/testcases/images/jp2/not_kitty.jp2 in/
  echo "" >in/in.jp2

  for ((i = 1; i <= $1; i++)); do
    # timeout [x] $AFL/afl-fuzz ?
    $AFL/afl-fuzz -m none -i in -o out$i src/app/jasper --output /tmp/out.jpg --input @@
  done
}

###
# @description: 使用afl-model对jasper进行模糊测试
# @param: $1 数字, 重复多少次测试
# @return {*}
###
model() {
  mkdir obj-model
  mkdir obj-model/temp

  # AFL-model path
  export AFLM=/path/to/afl

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-model/temp
  export CC=$AFLM/afl-clang-fast
  export CXX=$AFLM/afl-clang-fast++
  export LDFLAGS=-lpthread
  export ADDITIONAL="-outdir=$TMP_DIR"

  # 1st build
  cd obj-model
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
  make clean all

  # Get max line
  line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

  # 删掉obj-loop文件夹, 重新建一个, 因为继续在这个文件夹make的话会延续第一次build的命令行参数
  # 不知道是什么原因
  cd $SUBJECT
  mkdir obj-loop2
  cp -r obj-model/temp obj-loop2/temp
  rm -rf obj-model
  mv obj-loop2 obj-model
  cd obj-model

  # 2nd build
  export ADDITIONAL="-bbfile=$TMP_DIR/BBFile.txt"
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" cmake ..
  make clean all

  mkdir in
  # cp $AFLM/testcases/images/jp2/not_kitty.jp2 in/
  echo "" >in/in.jp2

  for ((i = 1; i <= $1; i++)); do
    # timeout? -p?
    $AFLM/afl-fuzz -l $line -m none -i in -o out$i src/app/jasper --output /tmp/out.jpg --input @@
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
