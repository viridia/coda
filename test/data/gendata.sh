#!/usr/bin/env bash
HERE=$(dirname $(pwd)/$0)
ROOT=$(dirname $(dirname ${HERE}))
LIBS=$ROOT/libs:$ROOT/third-party/python/ply-3.4
if [ -n "$PYTHONPATH" ]
then
  LIBPATH="${PYTHONPATH}:$LIBS"
else
  LIBPATH="$LIBS"
fi
PYTHONPATH=$LIBPATH python3 $HERE/gendata.py ${HERE}/sample.coda\
    --out="text:${HERE}/sample.txt"\
    --out="bin:${HERE}/sample.dat"
