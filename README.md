# A context sensitive probabilistic model for natural language abstract syntax trees

This project aims to develop a probabilistic model for disambiguating abstract syntax trees for natural language in [Grammatical Framework](https://github.com/GrammaticalFramework/GF). The main approach involves using Expectation Maximization to estimate parameters using data from [UD-treebanks](https://github.com/UniversalDependencies).

## Running the code
To run the code you need GF C-runtime with python bindings installed or run the code through docker by running 'make build' to build the docker image and then 'make console' to automatically run the image and mount the needed directories.
