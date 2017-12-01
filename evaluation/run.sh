#!/bin/bash

NUM=1000
RUN=true
DB=""

usage () {
  echo "usage: $(basename "$0") [-hnd] [-n NUM] FILES";
  echo "  -h      show this help"
  echo "  -t      dry run"
  echo "  -d FILE use database"
  echo "  -n NUM  run NUM evaluation sentences"
}

while getopts ':htd:n:' flag; do
  case "${flag}" in 
    h) usage; exit;;
    n) NUM="${OPTARG}" ;;
    t) RUN=false ;;
    d) DB="--database ${OPTARG}" ;;
    \?) echo "Unexpected option ${flag}" >&2; exit 1 ;;
    :) echo "Missing option argument for -$OPTARG" >&2; exit 1 ;;
  esac
done

shift $(($OPTIND - 1))

FILES="$@"

for f in $FILES
do
  name=$(basename $f)
  echo $name

  args=''
  sense_file='../../trainomatic/en_egs.tsv'
  data_file='../../trainomatic/en.conllu'

  if [[ $name == *"clust"* ]]; then
    sense_file='../../trainomatic/wnids_clust5'
    dict='wn'
    possdict='wn_clust'
  elif [[ $name == *"wn"* ]]; then
    dict='wn'
    possdict='wn_gf'
  elif [[ $name == *"gf"* ]]; then
    dict='gf'
    possdict='gf'
  elif [[ $name == *"kras"* ]]; then
    dict='wn'
    possdict='wn_gf'
  fi

  args="$DB $args"
  args="--num $NUM $args"
  args="--sentence-data $data_file --sentence-answer $sense_file $args"
  args="--dict $dict $args"
  args="--possdict ../data/possibility_dictionaries/$possdict/eng.txt $args"
  args="--probs $f $args"

  if [[ $name != *"nodep"* ]]; then
    args="--deprel $args"
  fi

  if [[ $name == *"uni"* ]]; then
    command="python unigram.py $args"
  else
    command="python quantitative.py $args"
  fi

  if $RUN; then
    $command
  else
    echo $command
  fi
done
