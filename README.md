# A language independent probabilistic model for word sense disambiguation

This project aims to develop a probabilistic model for disambiguating word senses in natural language through unsupervised parameter estimation methods using linguistic data for multiple languages. The main application is to improve the parsing of language independent abstract syntax trees in [Grammatical Framework](https://github.com/GrammaticalFramework/GF), and emphasis is put on developing a model that is as language independent as possible. The main approach involves using Expectation Maximization to estimate parameters using data from [UD-treebanks](https://github.com/UniversalDependencies).

## Running the code
To run the code you need to download the appropriate [UD-treebanks](https://github.com/UniversalDependencies) and put them in a folder named data in the project directory. You will then need to generate feature count files by running 'python possibility_dictionary_generation.py' from the work directory. Then you can run 'python main.py' to run the main pipeline that will compute bigram probabilities and run analysis on those probabilities. By default the code uses English, Swedish and Bulgarian to estimate probabilities, but more languages can easily be added in the main.py script.

To generate new possibility dictionaris you need the GF C-runtime with python bindings installed or run the code through docker by running 'make build' to build the docker image and then 'make console', to automatically run the image and mount the needed directories.
