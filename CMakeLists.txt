# CMake build file for Coda

cmake_minimum_required(VERSION 2.8.4)
project(CODA)

set(CODA_VERSION 0)
set(CODA_MAJOR_REVISION 1)
set(CODA_MINOR_REVISION 0)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake_modules/")

# Macros we'll need
include(CheckIncludeFile)
include(CheckIncludeFileCXX)
include(CheckFunctionExists)
include(CheckCXXSourceCompiles)
include(CheckTypeSize)
include(TestBigEndian)

# Report an error if a required header file is not found.
macro(check_required_include_file_cxx INCLUDE VARIABLE)
  check_include_file_cxx(${INCLUDE} ${VARIABLE} -std=c++11)
  if(NOT ${VARIABLE})
    message(FATAL_ERROR "Header '${INCLUDE}' not found.")
  endif()
endmacro()

# Check for the existence of include files.
#check_include_file(assert.h HAVE_ASSERT_H)
#check_include_file(stdio.h HAVE_STDIO_H)
check_include_file(math.h CODA_HAVE_MATH_H)
check_include_file(stdint.h CODA_HAVE_STDINT_H)
#check_include_file(stddef.h HAVE_STDDEF_H)
#check_include_file(stdlib.h HAVE_STDLIB_H)
#check_include_file(string.h HAVE_STRING_H)
#check_include_file(stdbool.h HAVE_STDBOOL_H)
#check_include_file(stdarg.h HAVE_STDARG_H)
#check_include_file(malloc.h HAVE_MALLOC_H)
#check_include_file(unistd.h HAVE_UNISTD_H)
#check_include_file(fcntl.h HAVE_FCNTL_H)
#check_include_file(inttypes.h HAVE_INTTYPES_H)
#check_include_file(errno.h HAVE_ERRNO_H)
#check_include_file(execinfo.h HAVE_EXECINFO_H)
#check_include_file(sys/stat.h HAVE_SYS_STAT_H)
#check_include_file(sys/time.h HAVE_SYS_TIME_H)
#check_include_file(sys/types.h HAVE_SYS_TYPES_H)
#check_include_file(sys/resource.h HAVE_SYS_RESOURCE_H)
#check_include_file(libkern/OSAtomic.h HAVE_LIBKERN_OSATOMIC_H)
check_include_file(intrin.h HAVE_INTRIN_H)
check_required_include_file_cxx(bitset CODA_HAVE_BITSET)
check_required_include_file_cxx(functional CODA_HAVE_FUNCTIONAL)
check_required_include_file_cxx(functional CODA_HAVE_MEMORY)
check_required_include_file_cxx(unordered_map CODA_HAVE_UNORDERED_MAP)
check_required_include_file_cxx(unordered_set CODA_HAVE_UNORDERED_SET)
#check_include_file_cxx(new HAVE_NEW)
#check_include_file_cxx(ctime HAVE_CTIME)
#check_include_file_cxx(cxxabi.h HAVE_CXXABI_H)
#check_include_file_cxx(dlfcn.h HAVE_DLFCN_H)
#check_include_file_cxx(unwind.h HAVE_UNWIND_H)
#check_include_file_cxx(libunwind.h HAVE_LIBUNWIND_H)

# Endian conversions.
test_big_endian(CODA_BIG_ENDIAN)
if (CODA_HAVE_INTRIN_H)
set(CMAKE_REQUIRED_INCLUDES intrin.h)
check_function_exists(_byteswap_ushort CODA_HAVE_BYTESWAP_SHORT)
check_function_exists(_byteswap_ulong CODA_HAVE_BYTESWAP_ULONG)
check_function_exists(_byteswap_uuint64 CODA_HAVE_BYTESWAP_UINT64)
endif (CODA_HAVE_INTRIN_H)

# GCC's __builtin_bswap* should be checked individually 
# because some of them can be missing depends on the GCC version.
check_cxx_source_compiles("
  int main() {
    __builtin_bswap16(0);
    return 0; 
  }
" CODA_HAVE_GCC_BYTESWAP_16)

check_cxx_source_compiles("
  int main() {
    __builtin_bswap32(0);
    return 0; 
  }
" CODA_HAVE_GCC_BYTESWAP_32)

check_cxx_source_compiles("
  int main() {
    __builtin_bswap64(0);
    return 0; 
  }
" CODA_HAVE_GCC_BYTESWAP_64)

#if (CMAKE_USE_PTHREADS_INIT)
#    set (HAVE_PTHREADS ON)
#endif (CMAKE_USE_PTHREADS_INIT)

# Check for LLVM
#find_package(LLVM REQUIRED)
#find_program(LLVM_LLC llc PATHS ${LLVM_BIN_DIR})
#find_program(LLVM_LD llvm-ld PATHS ${LLVM_BIN_DIR})
#find_program(LLVM_OPT opt PATHS ${LLVM_BIN_DIR})
#find_program(LLVM_AS llvm-as PATHS ${LLVM_BIN_DIR})
find_program(PYTHON3 python3)

# Include directory paths
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/support/cpp/include)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/support/cpp/include)
include_directories(third-party/cpp/googletest/googletest/include)
include_directories(third-party/cpp/googletest/googlemock/include)
#include_directories(${LLVM_INCLUDE_DIR})

# Definitions needed by LLVM headers
add_definitions(
    -D__STDC_LIMIT_MACROS
    -D__STDC_CONSTANT_MACROS
    -D_GNU_SOURCE)

# Extra flags for GCC (C++ only)
if (CMAKE_COMPILER_IS_GNUCXX)
  set(CMAKE_CXX_FLAGS
      -pipe
      -Wall -Wextra -Werror -Wcast-align -Wpointer-arith -Wno-sign-compare
      -Wno-deprecated -Wno-unused
      -fmessage-length=0
      -std=c++11
  )
endif (CMAKE_COMPILER_IS_GNUCXX)

# Extra flags for clang (C++ only)
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  add_compile_options(
    -Wall
    -Wextra
    -Werror
    -Wcast-align
    -Wpointer-arith
    -Wno-deprecated
    -Wno-unused-parameter
    -Wno-sign-compare # googletest won't build without this
    -fno-rtti
    -fPIC
    -std=c++11)
  set(CMAKE_EXE_LINKER_FLAGS -lstdc++)
endif ()

# Extra flags for MSVC (C only)
if (MSVC)
  add_definitions(
      -D_CRT_SECURE_NO_WARNINGS
      -DUNICODE -D_UNICODE
      -wd4146 -wd4503 -wd4996 -wd4800 -wd4244 -wd4624
      -wd4355 -wd4715 -wd4180 -wd4345 -wd4224
  )
endif (MSVC)

# Add the check-build target
#add_custom_target(check)

# Subdirs to compile
add_subdirectory(support/cpp)
add_subdirectory(third-party/cpp)
add_subdirectory(test/cpp)

add_test(unittest test/cpp/unittest)

#add_subdirectory(doc/api)

# Make sure we don't destroy PyDev nature.
set_property(GLOBAL APPEND PROPERTY ECLIPSE_EXTRA_NATURES "org.python.pydev.pythonNature")
