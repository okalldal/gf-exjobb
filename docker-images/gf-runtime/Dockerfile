FROM ubuntu

RUN apt-get update
RUN apt-get install -y haskell-platform git libghc-haskeline-dev autoconf automake libtool make python python-dev

RUN git clone --depth 1 --single-branch https://github.com/GrammaticalFramework/GF.git

# Install GF
WORKDIR /GF
RUN cabal update
RUN cabal install

# Install C runtime
WORKDIR /GF/src/runtime/c
RUN autoreconf -i
RUN ./configure
RUN make
RUN make install

# Install python bindings
WORKDIR /GF/src/runtime/python
RUN python setup.py build
RUN python setup.py install

ENV PATH=$PATH:/root/.cabal/bin
ENV LD_LIBRARY_PATH=/usr/local/lib

WORKDIR /GF