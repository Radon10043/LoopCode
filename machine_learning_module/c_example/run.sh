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
echo "1+1=" >tc0

export CC=$AFL_PATH/afl-clang-fast

export CXX=$AFL_PATH/afl-clang-fast++

cd $BASE_PATH
$CXX e.c -o a.out
cd temp
$AFL_PATH/afl-fuzz -t 5000 -i testcase -o out ../a.out
