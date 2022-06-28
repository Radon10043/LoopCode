###
# @Author: Radon
# @Date: 2022-06-14 11:38:30
# @LastEditors: Radon
# @LastEditTime: 2022-06-14 12:21:33
# @Description: libxml2, afl-model
###

main() {
  rm -rf SRC
  git clone https://gitlab.gnome.org/GNOME/libxml2 SRC

  rm -rf libxml2-2.9.14
  cp -r SRC libxml2-2.9.14
  cd libxml2-2.9.14
  git checkout v2.9.14

  mkdir obj-afl
  mkdir obj-afl/temp

  export AFL=/home/lowry/Documents/LoopCode/afl-yagol
  export CC=$AFL/afl-clang-fast
  export CXX=$AFL/afl-clang-fast++

  if [ ! -f $CC ] || [! -f $CXX ]; then
    echo -e "\033[1;47;31mError\033[0m: Hum? I cant find afl-clang-fast in $AFL."
    exit
  fi

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-afl/temp
  export PY_OUTPUT_DIR_PATH=$TMP_DIR/py.out
  export ADDITIONAL="-outdir=$TMP_DIR"

  export PY_PATH=/home/lowry/anaconda3/bin/python
  export PY_MAIN_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/main.py
  export PY_OUTPUT_DIR_PATH=$PWD/obj-afl/temp/py.log

  ./autogen.sh
  make distclean

  # 1st build
  cd obj-afl
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean all

  # Get max line
  line=$(wc -l $TMP_DIR/BBFile.txt | cut -d ' ' -f 1)

  # 2nd build
  export ADDITIONAL="-bbfile=$TMP_DIR/BBFile.txt"
  CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=$(pwd)
  make clean all

  mkdir in
  cp $AFL/testcases/others/xml/small_document.xml in/

#  for ((i = 1; i <= $1; i++)); do
#    $AFL/afl-fuzz -k 720 -l $line -m none -i in -o out$i ./xmllint --valid --recover @@
#  done

  # -p 启动python, -k fuzz多长时间
  for ((i = 1; i <= $1; i++)); do
    $PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout & # 后台运行py
    $AFL/afl-fuzz -p -k 720 -l $line -m none -i in -o $SUBJECT/obj-afl/out$i ./xmllint --valid --recover @@
  done
}

# Entry
# 第一个参数是数字, 表示重复fuzz多少次
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
  echo "$1 is not a number."
  exit
fi

echo "$1 is a number, yeah!"

main $1
