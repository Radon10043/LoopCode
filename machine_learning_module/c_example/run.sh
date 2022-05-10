export AFL_PATH=/home/yagol/PycharmProjects/LoopCode/afl
export BASE_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example
export TEMP_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example/temp
export PY_PATH=/home/yagol/anaconda3/envs/LoopCode/bin/python
export PY_MAIN_PATH=/home/yagol/PycharmProjects/LoopCode/machine_learning_module/src/main.py
#sudo netstat -ap | grep 12012
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
$PY_PATH $PY_MAIN_PATH True $TEMP_PATH/BBFile.txt & $AFL_PATH/afl-fuzz -p -t 5000 -i testcase -o /home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example/temp/out /home/yagol/PycharmProjects/LoopCode/machine_learning_module/c_example/a.out