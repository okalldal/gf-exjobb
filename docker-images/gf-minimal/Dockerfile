FROM ubuntu

RUN apt-get update && \
    apt-get install -y --no-install-recommends autoconf automake libtool make vim haskell-platform git libghc-haskeline-dev python3 python3-dev

# Clone gf repo
RUN git clone --depth 1 --single-branch git@github.com:GrammaticalFramework/GF.git


# Install C runtime
WORKDIR $HOME/GF/src/runtime/c
RUN autoreconf -i && \
    ./configure && \
    make && \
    make install
ENV LD_LIBRARY_PATH=/usr/local/lib


# Install GF
WORKDIR $HOME/GF
RUN git pull && \
    cabal update && \
    cabal install -fserver -fc-runtime
ENV PATH=$PATH:/root/.cabal/bin


# Install python bindings
WORKDIR $HOME/GF/src/runtime/python
RUN python setup.py build && \
    python setup.py install

ENV PATH=$PATH:$HOME/.cabal/bin \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
WORKDIR $HOME