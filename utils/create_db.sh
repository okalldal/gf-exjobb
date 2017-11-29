#!/bin/bash
FILES=$@

for f in $FILES; do
  if [ ! -f $f ]; then
    echo "$f does not exist"
    exit 1
  fi

  name=${f##*/}
  name=${name%.*}
  cols='prob NUM, child TEXT'
  icols='child'

  if [[ $name != *"uni"* ]]; then
    cols="$cols, head TEXT"
    icols="$icols, head"
  fi
  if [[ $name != *"nodep"* ]]; then
    cols="$cols, deprel TEXT"
    icols="$icols, deprel"
  fi
  
  echo "DROP TABLE IF EXISTS $name;"
  echo "CREATE TABLE $name($cols);"
  echo "CREATE UNIQUE INDEX lookup_$name ON $name($icols);"
  echo ".mode tabs"
  echo ".import $f $name"
  echo "CREATE TABLE IF NOT EXISTS total_probs(name TEXT UNIQUE, total NUM);"
  echo "DELETE FROM total_probs WHERE name='$name'"
  echo "INSERT INTO total_probs(name, total) " \
       "SELECT '$name' AS name, SUM(prob) AS total FROM $name;"
  echo ".schema $name"
done
