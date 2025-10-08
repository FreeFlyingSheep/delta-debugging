#!/bin/bash
# This script installs the delta debugging environment on a local machine.
# It is just for reference and not intended to be run on a production system.
set -ex

src_dir=~
dst_dir=/opt
jobs=$(nproc)

pushd ${src_dir}

    # Install necessary packages
    sudo apt-get update
    sudo apt-get install -y build-essential bison flex texinfo git automake libc6-dbg curl

    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source .bashrc

    # Download binutils
    if [ ! -d "binutils-gdb" ]; then
        git clone https://sourceware.org/git/binutils-gdb.git
    fi

    # Download Valgrind
    if [ ! -d "valgrind" ]; then
        git clone https://sourceware.org/git/valgrind.git
    fi

    # Build and install binutils from source
    pushd binutils-gdb
        git checkout -f 2870b1ba83fc0e0ee7eadf72d614a7ec4591b169
        mkdir build-2870b1b
        cd build-2870b1b
        ../configure --prefix=${dst_dir}/binutils-2870b1b --target=x86_64-mingw32 --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f 53f7e8ea7fad1fcff1b58f4cbd74e192e0bcbc1d
        mkdir build-53f7e8e
        cd build-53f7e8e
        ../configure --prefix=${dst_dir}/binutils-53f7e8e --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f a6c21d4a553de184562fd8409a5bcd3f2cc2561a
        mkdir build-a6c21d4
        cd build-a6c21d4
        ../configure --prefix=${dst_dir}/binutils-a6c21d4 --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f be8e83130996a5300e15b415ed290de1af910361
        mkdir build-be8e831
        cd build-be8e831
        ../configure --prefix=${dst_dir}/binutils-be8e831 --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    # Build and install valgrind from source
    pushd valgrind
        git checkout -f VALGRIND_3_22_0
        ./autogen.sh
        ./configure --prefix=${dst_dir}/valgrind-3_22_0
        make -j"${jobs}"
        sudo make install
    popd

    # Download the project
    if [ ! -d "delta-debugging" ]; then
        git clone https://github.com/FreeFlyingSheep/delta-debugging.git
    fi

    # Install the project
    pushd delta-debugging
        uv sync --all-extras
    popd

popd
