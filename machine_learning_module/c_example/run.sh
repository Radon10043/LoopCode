export AFL_PATH=/home/yagol/PycharmProjects/LoopCode/afl
export BASE_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example
export TEMP_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example/temp

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
export ADDITIONAL="-outdir=$TEMP_PATH"
cd $BASE_PATH
$CXX e.c $ADDITIONAL -g -o a.out
$CXX e.c -bbfile=$TEMP_PATH/BBFile.txt -g -o a.out
cd temp
$AFL_PATH/afl-fuzz -t 5000 -i testcase -o out ../a.out
