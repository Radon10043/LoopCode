export AFL=~/Documents/project_vscode/cpp/llvm/5_LoopCode/afl

if [ -d "temp/" ]; then
    rm -r temp
fi

mkdir temp; cp LoopBBs.txt temp/

cd ..
export SUBJECT=$PWD; export TMP_DIR=$PWD/afl/temp
export CC=$AFLGO/afl-clang-fast; export CXX=$AFLGO/afl-clang-fast++

$CC loop.c $ADDITIONAL -g -o loop.out
cd afl/temp; mkdir in; echo "5" > in/in
$AFL/afl-fuzz -m none -i in -o out ../../loop.out
