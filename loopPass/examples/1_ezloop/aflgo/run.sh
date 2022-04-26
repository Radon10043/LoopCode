export AFLGO=~/Documents/project_vscode/cpp/llvm/5_LoopCode/aflgo

if [ -d "temp/" ]; then
    rm -r temp
fi

mkdir temp; cp LoopBBs.txt temp/

cd ..
export SUBJECT=$PWD; export TMP_DIR=$PWD/aflgo/temp
export CC=$AFLGO/afl-clang-fast; export CXX=$AFLGO/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-targets=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"

echo $'loop.c:8' > $TMP_DIR/BBtargets.txt
$CC loop.c $ADDITIONAL -ldl -g -o loop.out
$AFLGO/scripts/genDistance.sh $SUBJECT $TMP_DIR loop.out
$CC loop.c -loopfile=$TMP_DIR/LoopBBs.txt -distance=$TMP_DIR/distance.cfg.txt -ldl -g -o loop.out
cd aflgo/temp; mkdir in; echo "" > in/in
# $AFLGO/afl-fuzz -k 1 -m none -z exp -c 45m -i in -o out ../../loop.out
# mkdir out; for i in {1..10}; do timeout -sHUP 180m $AFLGO/afl-fuzz -m none -z exp -c 45m -i in -o "out/out_$i" ../mjs-bin -f @@ > /dev/null 2>&1 & done