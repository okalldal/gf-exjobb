from "jupyter/scipy-notebook"

# the docker runs in a restricted user mode
USER root

# install stuff
RUN conda install --quiet --yes \
    'nltk'

# change back to notebook user
USER $NB_USER