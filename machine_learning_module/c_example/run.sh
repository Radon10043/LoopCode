export AFL_PATH=/home/yagol/PycharmProjects/LoopCode/afl
export BASE_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example

cd $BASE_PATH

if [ -d "temp/" ]; then
  rm -r temp
fi

mkdir temp
cd temp
mkdir testcase
cd testcase
echo "0" >tc0

export CC=$AFL_PATH/afl-gcc

export CXX=$AFL_PATH/afl-g++

cd $BASE_PATH
$CC e.c -o a.out
cd temp
$AFL_PATH/afl-fuzz -i testcase -o out ../a.out @@
