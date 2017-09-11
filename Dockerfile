from "jupyter/scipy-notebook"

# the docker runs in a restricted user mode
USER root

# install stuff 

# nltk
RUN conda install --quiet --yes \
    'nltk'

# java
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre curl && \
    rm -rf /var/lib/apt/lists/*

# stanford parser
RUN curl -SL -o stanford.zip https://nlp.stanford.edu/software/stanford-parser-full-2017-06-09.zip
RUN unzip -d /usr/lib/ stanford.zip && rm stanford.zip

# change back to notebook user
USER $NB_USER