FROM arm64v8/ubuntu:plucky

# Install necessary packages
RUN apt-get update && apt-get install -y build-essential bison flex texinfo git automake libc6-dbg

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /root

# Download binutils
RUN git clone https://sourceware.org/git/binutils-gdb.git

# Download valgrind
RUN git clone https://sourceware.org/git/valgrind.git

# Build and install binutils from source
RUN cd binutils-gdb \
    && git checkout -f 2870b1ba83fc0e0ee7eadf72d614a7ec4591b169 \
    && mkdir build-2870b1b \
    && cd build-2870b1b \
    && ../configure --prefix=/opt/binutils-2870b1b --target=x86_64-mingw32 --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror \
    && make -j$(nproc) \
    && make install

RUN cd binutils-gdb \
    && git checkout -f 53f7e8ea7fad1fcff1b58f4cbd74e192e0bcbc1d \
    && mkdir build-53f7e8e \
    && cd build-53f7e8e \
    && ../configure --prefix=/opt/binutils-53f7e8e --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror \
    && make -j$(nproc) \
    && make install

RUN cd binutils-gdb \
    && git checkout -f a6c21d4a553de184562fd8409a5bcd3f2cc2561a \
    && mkdir build-a6c21d4 \
    && cd build-a6c21d4 \
    && ../configure --prefix=/opt/binutils-a6c21d4 --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror \
    && make -j$(nproc) \
    && make install

RUN cd binutils-gdb \
    && git checkout -f be8e83130996a5300e15b415ed290de1af910361 \
    && mkdir build-be8e831 \
    && cd build-be8e831 \
    && ../configure --prefix=/opt/binutils-be8e831 --target=x86_64-linux --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim --disable-gprofng --disable-werror \
    && make -j$(nproc) \
    && make install

# Build and install valgrind from source
RUN cd valgrind \
    && git checkout -f d97fed7c3e4aa7c910dfa0b6c5de12fd6cf08155 \
    && ./autogen.sh \
    && ./configure --prefix=/opt/valgrind-d97fed7 \
    && make -j$(nproc) \
    && make install

RUN cd valgrind \
    && git checkout -f bd4db67b1d386c352040b1d8fab82f5f3340fc59 \
    && ./autogen.sh \
    && ./configure --prefix=/opt/valgrind-bd4db67 \
    && make -j$(nproc) \
    && make install

RUN cd valgrind \
    && git checkout -f 49dccafc3b661692de2d14ce14cf807940bd2d8c \
    && ./autogen.sh \
    && ./configure --prefix=/opt/valgrind-49dccaf \
    && make -j$(nproc) \
    && make install

RUN cd valgrind \
    && git checkout -f fcdaa474260a54af9c4b241bac9c1e9775081f78 \
    && ./autogen.sh \
    && ./configure --prefix=/opt/valgrind-fcdaa47 \
    && make -j$(nproc) \
    && make install

# Copy the project
COPY . /root/delta-debugging

# Install the project
WORKDIR /root/delta-debugging
RUN uv sync --all-extras

# Run tests
RUN uv run pytest -s -v

# Uncomment the following line to run an example by default
# CMD ["uv", "run", "examples/basic.py"]
# CMD ["uv", "run", "examples/benchmark.py"]
# CMD ["uv", "run", "examples/binutils_gdb.py"]
# CMD ["uv", "run", "examples/valgrind.py"]
