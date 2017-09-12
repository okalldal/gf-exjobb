FROM ubuntu

# Clone gf repo
RUN apt-get update
RUN apt-get install -y git
RUN git clone --depth 1 --single-branch https://github.com/GrammaticalFramework/GF.git

# Install GF
RUN apt-get install -y haskell-platform git libghc-haskeline-dev
WORKDIR /GF
RUN git pull
RUN cabal update
RUN cabal install
ENV PATH=$PATH:/root/.cabal/bin

# Install C runtime
RUN apt-get install -y autoconf automake libtool make 
WORKDIR /GF/src/runtime/c
RUN autoreconf -i
RUN ./configure
RUN make
RUN make install
ENV LD_LIBRARY_PATH=/usr/local/lib

# Install python bindings
RUN apt-get install -y python python-dev python3 python3-dev
WORKDIR /GF/src/runtime/python
RUN python setup.py build
RUN python setup.py install

# Install python3 bindings 
RUN apt-get install -y python3 python3-dev
RUN python3 setup.py build
RUN python3 setup.py install

# Install ud2gf
WORKDIR /
RUN git clone --depth 1 --single-branch https://github.com/GrammaticalFramework/gf-contrib.git
WORKDIR /gf-contrib/ud2gf
RUN ln -s /GF/lib/src/ gflibsrc
RUN mkdir /ud-treebanks
RUN ln -s /ud-treebanks treebanks

# Download english UD-treebank v1.3
RUN apt-get install -y curl
WORKDIR /ud-treebanks
RUN curl -SL https://github.com/UniversalDependencies/UD_English/archive/r1.3.tar.gz | tar xz

WORKDIR /GF
RUN cabal install -fserver -fc-runtime
