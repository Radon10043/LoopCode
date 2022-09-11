###
# @Author: Radon
# @Date: 2022-06-14 11:38:30
# @LastEditors: Radon
# @LastEditTime: 2022-06-14 12:21:33
# @Description: libxml2, afl-model
###

main() {
  rm -rf SRC
  proxychains git clone https://gitlab.gnome.org/GNOME/libxml2.git SRC

  rm -rf libxml2-2.9.10-gcc-version
  ./libxml2-afl-gcc-version.sh

  rm -rf libxml2-2.9.10
  cp -r SRC libxml2-2.9.10
  cd libxml2-2.9.10
  git checkout v2.9.10

  mkdir obj-afl
  mkdir obj-afl/temp

  export AFL=/home/lowry//Documents/LoopCode/afl-yagol
  export CC=$AFL/afl-clang-fast
  export CXX=$AFL/afl-clang-fast++

  if [ ! -f $CC ] || [! -f $CXX ]; then
    echo -e "\033[1;47;31mError\033[0m: Hum? I cant find afl-clang-fast in $AFL."
    exit
  fi

  export SUBJECT=$PWD
  export TMP_DIR=$PWD/obj-afl/temp
  export ADDITIONAL="-outdir=$TMP_DIR"

  export PY_PATH=/home/lowry/anaconda3/bin/python
  export PY_MAIN_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/main.py
  export PY_OUTPUT_DIR_PATH=$PWD/obj-afl/temp/py.log
  export PRE_TRAIN_AFL_OUT_DIR_NAME=out_afl_pre_train
  export MODEL_PATH=$PWD/obj-afl/temp/xmllint.model.lowry
  export KEEP_SHOWMAP_THREAD_PATH=/home/lowry/Documents/LoopCode/machine_learning_module/src/keep_showmap_thread.py


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

# 第一次py，预训练模型
#  $PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --pre-train --model-save-path $MODEL_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14-gcc/obj-afl/xmllint --pre-train-testcase /home/lowry/Documents/LoopCode/scripts/libxml_in --append-args "--valid --recover"
#  # 正式运行afl-model
#  $PY_PATH -u $PY_MAIN_PATH --log-path $PY_OUTPUT_DIR_PATH --log-level DEBUG --skip-log-stdout --model-load-path $MODEL_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14-gcc/obj-afl/xmllint --append-args "--valid --recover" --testcase-dir-path $SUBJECT/obj-afl/out & # 后台运行py
#  sleep 5s
#  $AFL/afl-fuzz -p -y -k 180 -l $line -t 1000+ -e 0 -m none -i /home/lowry/Documents/LoopCode/scripts/libxml_in -o $SUBJECT/obj-afl/out $SUBJECT/obj-afl/xmllint --valid --recover @@

  # 独立运行原版afl
  $PY_PATH -u $KEEP_SHOWMAP_THREAD_PATH --log-path $PY_OUTPUT_DIR_PATH --skip-log-stdout --model-load-path $MODEL_PATH --gcc-version-bin /home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14-gcc/obj-afl/xmllint --append-args "--valid --recover" --testcase-dir-path $SUBJECT/obj-afl/out & # 后台运行py
  sleep 5s
  $AFL/afl-fuzz -k 180 -l $line -m none -i /home/lowry/Documents/LoopCode/scripts/libxml_in -o /home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/out /home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/xmllint --valid --recover @@
}

main
