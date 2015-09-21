#~/usr/bin/bash

cmake -G "Eclipse CDT4 - Ninja"\
 -D CMAKE_BUILD_TYPE=Debug\
 -D CMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT=TRUE\
 -D _ECLIPSE_VERSION=4.3\
 ../coda
