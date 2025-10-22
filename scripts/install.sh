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
    if uv --version >/dev/null 2>&1; then
        echo "Updating uv..."
        uv self update
    else
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source .bashrc
    fi

    # Download binutils
    if [ -d "binutils-gdb" ]; then
        echo "binutils-gdb directory already exists, pulling latest changes..."
        pushd binutils-gdb
            git checkout -f master
            git pull --rebase
        popd
    else
        echo "Cloning binutils-gdb repository..."
        git clone https://sourceware.org/git/binutils-gdb.git
    fi

    # Download Valgrind
    if [ -d "valgrind" ]; then
        echo "Valgrind directory already exists, pulling latest changes..."
        pushd valgrind
            git checkout -f master
            git pull --rebase
        popd
    else
        echo "Cloning Valgrind repository..."
        git clone https://sourceware.org/git/valgrind.git
    fi

    # Build and install binutils from source
    pushd binutils-gdb
        git checkout -f 2870b1ba83fc0e0ee7eadf72d614a7ec4591b169
        rm -rf build-2870b1ba
        mkdir build-2870b1ba
        cd build-2870b1ba
        ../configure --prefix=${dst_dir}/binutils-2870b1ba --target=x86_64-mingw32 --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f 53f7e8ea7fad1fcff1b58f4cbd74e192e0bcbc1d
        rm -rf build-53f7e8ea
        mkdir build-53f7e8ea
        cd build-53f7e8ea
        ../configure --prefix=${dst_dir}/binutils-53f7e8ea --target=aarch64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f a6c21d4a553de184562fd8409a5bcd3f2cc2561a
        rm -rf build-a6c21d4a
        mkdir build-a6c21d4a
        cd build-a6c21d4a
        ../configure --prefix=${dst_dir}/binutils-a6c21d4a --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    pushd binutils-gdb
        git checkout -f be8e83130996a5300e15b415ed290de1af910361
        rm -rf build-be8e8313
        mkdir build-be8e8313
        cd build-be8e8313
        ../configure --prefix=${dst_dir}/binutils-be8e8313 --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror
        make -j"${jobs}"
        sudo make install
    popd

    # Build and install valgrind from source
    pushd valgrind
        git checkout -f d97fed7c3e4aa7c910dfa0b6c5de12fd6cf08155
        ./autogen.sh
        ./configure --prefix=${dst_dir}/valgrind-d97fed7c
        make -j"${jobs}"
        sudo make install
    popd

    pushd valgrind
        git checkout -f bd4db67b1d386c352040b1d8fab82f5f3340fc59
        ./autogen.sh
        ./configure --prefix=${dst_dir}/valgrind-bd4db67b
        make -j"${jobs}"
        sudo make install
    popd

    pushd valgrind
        git checkout -f 49dccafc3b661692de2d14ce14cf807940bd2d8c
        ./autogen.sh
        ./configure --prefix=${dst_dir}/valgrind-49dccafc
        make -j"${jobs}"
        sudo make install
    popd

    pushd valgrind
        git checkout -f fcdaa474260a54af9c4b241bac9c1e9775081f78
        ./autogen.sh
        ./configure --prefix=${dst_dir}/valgrind-fcdaa474
        make -j"${jobs}"
        sudo make install
    popd

    # Download the project
    if [ -d "delta-debugging" ]; then
        echo "delta-debugging directory already exists, pulling latest changes..."
        pushd delta-debugging
            git checkout -f main
            git pull --rebase
        popd
    else
        echo "Cloning delta-debugging repository..."
        git clone https://github.com/FreeFlyingSheep/delta-debugging.git
    fi

    # Install the project
    pushd delta-debugging
        uv sync --all-extras
    popd

popd
