FROM jupyter/scipy-notebook

# the docker runs in a restricted user mode
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends git autoconf automake libtool make vim default-jre curl graphviz tk tcl haskell-platform git libghc-haskeline-dev

# Clone gf repo
RUN git clone --depth 1 --single-branch https://github.com/GrammaticalFramework/GF.git


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
#RUN apt-get install -y python3 python3-dev
WORKDIR $HOME/GF/src/runtime/python
RUN python setup.py build && \
    python setup.py install

# nltk
RUN conda install --quiet --yes \
    'nltk' \
    'graphviz'

# stanford parser
RUN curl -SL -o stanford.zip https://nlp.stanford.edu/software/stanford-parser-full-2017-06-09.zip
RUN unzip -d /usr/lib/ stanford.zip && rm stanford.zip
ENV CLASSPATH=/usr/lib/stanford-parser-full-2017-06-09:$CLASSPATH


# Install ud2gf
#WORKDIR /
#RUN git clone --depth 1 --single-branch https://github.com/GrammaticalFramework/gf-contrib.git
#WORKDIR /gf-contrib/ud2gf
#RUN ln -s /GF/lib/src/ gflibsrc
#RUN mkdir /ud-treebanks
#RUN ln -s /ud-treebanks treebanks

# Download english UD-treebank v1.3
#RUN apt-get install -y curl
#WORKDIR /ud-treebanks
#RUN curl -SL https://github.com/UniversalDependencies/UD_English/archive/r1.3.tar.gz | tar xz

ENV PATH=$PATH:$HOME/.cabal/bin \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
WORKDIR $HOME

# change back to notebook user
# USER $NB_USER