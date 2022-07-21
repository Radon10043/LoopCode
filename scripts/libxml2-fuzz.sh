###
# @Author: Radon
# @Date: 2022-06-14 11:38:30
# @LastEditors: Radon
# @LastEditTime: 2022-07-21 15:47:42
# @Description: libxml2, afl
###

###
# @description: 下载libxml2
# @return {*}
###
download() {
  git clone https://gitlab.gnome.org/GNOME/libxml2 SRC

  rm -rf libxml2-2.9.14
  cp -r SRC libxml2-2.9.14
  cd libxml2-2.9.14
  git checkout v2.9.14
}

afl() {
  mkdir obj-afl
  mkdir obj-afl/temp

  export AFL=/path/to/afl
  export CC=$AFL/afl-clang-fast
  export CXX=$AFL/afl-clang-fast++

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-afl/temp
  export ADDITIONAL="-outdir=$TMP_DIR"

  ./autogen.sh
  make distclean

  cd obj-afl
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean all

  mkdir in
  cp $AFL/testcases/others/xml/small_document.xml in/

  for ((i = 1; i <= $1; i++)); do
    # timeout?
    $AFL/afl-fuzz -l $line -m none -i in -o out$i ./xmllint --valid --recover @@
  done
}

###
# @description: 使用afl-model进行模糊测试
# @return {*}
###
model() {
  mkdir obj-model
  mkdir obj-model/temp

  export AFLM=/path/to/afl-model
  export CC=$AFLM/afl-clang-fast
  export CXX=$AFLM/afl-clang-fast++

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-model/temp
  export ADDITIONAL="-outdir=$TMP_DIR"

  ./autogen.sh
  make distclean

  # 1st build
  cd obj-model
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean all

  # Get max line
  line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

  # 2nd build
  export ADDITIONAL="-bbfile=$TMP_DIR/BBFile.txt"
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean all

  mkdir in
  cp $AFLM/testcases/others/xml/small_document.xml in/

  for ((i = 1; i <= $1; i++)); do
    # timeout? -p?
    $AFLM/afl-fuzz -l $line -m none -i in -o out$i ./xmllint --valid --recover @@
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
