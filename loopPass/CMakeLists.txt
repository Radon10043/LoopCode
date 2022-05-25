cmake_minimum_required(VERSION 3.0.0)
project(demo VERSION 0.1.0)

# support C++14 features used by LLVM 10.0.0
set(CMAKE_CXX_STANDARD 14)

find_package(LLVM REQUIRED CONFIG)
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})

add_subdirectory(pass1)
add_subdirectory(pass2)
add_subdirectory(pass3)
add_subdirectory(pass4)