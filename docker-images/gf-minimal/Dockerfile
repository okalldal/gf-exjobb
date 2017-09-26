FROM ubuntu

RUN apt-get update && \
    apt-get install -y autoconf automake libtool make vim haskell-platform git libghc-haskeline-dev python3 python3-dev

WORKDIR /
# Clone gf repo
RUN git clone --depth 1 --single-branch http://github.com/GrammaticalFramework/GF.git


# Install C runtime
WORKDIR /GF/src/runtime/c
RUN autoreconf -i && \
    ./configure && \
    make && \
    make install
ENV LD_LIBRARY_PATH=/usr/local/lib


# Install GF
WORKDIR /GF
RUN git pull && \
    cabal update && \
    cabal install -fserver -fc-runtime
ENV PATH=$PATH:/root/.cabal/bin


# Install python bindings
WORKDIR /GF/src/runtime/python
RUN python3 setup.py build && \
    python3 setup.py install

ENV PATH=$PATH:$HOME/.cabal/bin
WORKDIR /
