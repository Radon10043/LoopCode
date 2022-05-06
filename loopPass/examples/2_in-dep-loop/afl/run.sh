
export AFL=~/Documents/project_vscode/cpp/llvm/5_LoopCode/afl

if [ -d "temp/" ]; then
    rm -r temp
fi

mkdir temp;

cd ..
export SUBJECT=$PWD; export TMP_DIR=$PWD/afl/temp
export CC=$AFL/afl-clang-fast; export CXX=$AFL/afl-clang-fast++
export ADDITIONAL="-outdir=$TMP_DIR"

$CC loop.c $ADDITIONAL -g -o loop.out

$CC loop.c -bbfile=$TMP_DIR/BBFile.txt -g -o loop.out

cd afl/temp; mkdir in; echo "" > in/in; echo "" > in/in2
$AFL/afl-fuzz -m none -i in -o out ../../loop.out
