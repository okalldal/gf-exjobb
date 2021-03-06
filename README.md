# A language independent probabilistic model for disambiguation of abstract syntax trees

This project aims to develop a probabilistic model for disambiguating abstract syntax trees in natural language through unsupervised parameter estimation methods using linguistic data for multiple languages. Applications include parsing abstract syntax trees in [Grammatical Framework](https://github.com/GrammaticalFramework/GF) and using the disambiguated trees to extract word sense information and doing macine translations. Emphasis is put on developing a model that is as language independent as possible. The main approach involves using Expectation Maximization to estimate parameters using data from [UD-treebanks](https://github.com/UniversalDependencies) and automatically parsed UD-trees from various text corpora.

## Directory structure
- src - main script files for estimating probabilities
- evaluation - scripts for evaluation of estimated probabilities
- data/feature_counts/{name}/{lang} - raw syntactic n-gram data from (parsed) corpora
- data/possibility_dictionaries/{gf/wn}/{lang} - dictionaries describing possible latent representations for each vocabulary item, currently featuring gf based dictionaries and wordnet based dictionaries

## Running the code
To run the estimations you first need to preprocess data for the estimation by running src/make_all_em_data.sh, estimation can then be done by running src/run_em.sh. Depending on the type of probabilities you are intrested in you might want to add autoparsed data in the data/feature_counts/autoparsed directory and you might want to make a combined wordnet/GF possibility dictionary by running data/possibility_dictionaries/combine_gf_wn.sh.
