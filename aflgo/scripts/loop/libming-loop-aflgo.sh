git clone https://github.com/libming/libming.git libming-CVE-2018-8962
cd libming-CVE-2018-8962/; git checkout b72cc2f # version 0.4.8

if [ -d "obj-loop/" ]; then
    rm -r obj-loop
fi
mkdir obj-loop; mkdir obj-loop/temp

export AFLGO=~/Documents/project_vscode/cpp/llvm/5_LoopCode/aflgo

export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-loop/temp
export CC=$AFLGO/afl-clang-fast; export CXX=$AFLGO/afl-clang-fast++
export LDFLAGS=-lpthread
export ADDITIONAL="-targets=$TMP_DIR/LoopBBs.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"

echo $'decompile.c:398' > $TMP_DIR/BBtargets.txt
# cp /home/radon/Documents/fuzzing/libming/LoopBBs.txt $TMP_DIR/BBtargets.txt
./autogen.sh;

cd obj-loop; CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=`pwd`
make clean; make

cat $TMP_DIR/BBnames.txt | rev | cut -d: -f2- | rev | sort | uniq > $TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/BBnames.txt
cat $TMP_DIR/BBcalls.txt | sort | uniq > $TMP_DIR/BBcalls2.txt && mv $TMP_DIR/BBcalls2.txt $TMP_DIR/BBcalls.txt
# cat $TMP_DIR/LoopBBs.txt | rev | cut -d: -f2- | rev | sort | uniq >$TMP_DIR/LoopBBs2.txt && mv $TMP_DIR/LoopBBs2.txt $TMP_DIR/LoopBBs.txt

cd util; $AFLGO/scripts/genDistance.sh $SUBJECT/obj-loop $TMP_DIR swftophp

cd -; CFLAGS="-loopfile=$TMP_DIR/LoopBBs.txt -distance=$TMP_DIR/distance.cfg.txt" CXXFLAGS="-loopfile=$TMP_DIR/LoopBBs.txt -distance=$TMP_DIR/distance.cfg.txt" ../configure --disable-shared --prefix=`pwd`
make clean; make
mkdir in; wget -P in http://condor.depaul.edu/sjost/hci430/flash-examples/swf/bumble-bee1.swf
$AFLGO/afl-fuzz -k 1440 -m none -z exp -c 45m -i in -o out ./util/swftophp @@
