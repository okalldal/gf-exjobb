#!/usr/bin/env python3

from collections import Counter, defaultdict
from operator import itemgetter 
import itertools as it 
import logging
import argparse
import sys

#curl -Ls https://www.dropbox.com/s/e7maoa4cq7ljxdk/news.all.en.clean.udparsednew.conllu.bz2?dl=1 | pv -cN dl | gzcat | pv -cN uncompress | python work/conllu_parser.py - test.txt

# zcat /Volumes/corpus-resources/corpora/conll-shared-tasks/\[2017\]\ Multilingual\ Parsing\ from\ Raw\ Text\ to\ Universal\ Dependencies/auto_parsed/English/en-wikipedia-000.conllu.xz | pypy3 conllu_parser.py | sort | uniq -c | sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | sort -k1,1nr --stable -t$'\t' 


# Parse graps from a connlu file, a graph is a list of UDNode objects in order of UD id
def parse_conllu_file(filestream):
  '''
    Reads a conllu_file and gives an iterator of all graphs in the file, each graph is
    given as a list of its nodes sorted by id.
    :param file_path:
    :return:
  '''
  current = []
  failed_parses = 0
  successful_parses = 0
  for line in filestream:
    if line == "\n":
      try:
        yield parse_graph(current)
        successful_parses = successful_parses + 1
      except Exception as ex:
        logging.debug(ex)
        failed_parses = failed_parses+1
      current = []
      #if successful_parses > 20000: return;
    elif not line.startswith('#'):
      current.append(line)
  logging.info('Parsed {} graphs successfully.'.format(successful_parses))
  if failed_parses > 0:
    logging.warning('Error with parsing {} of {} graphs.'.format(failed_parses, failed_parses+successful_parses))


def parse_graph(node_lines):
  return [UDNode(node_line) for node_line in node_lines]


# Count unique occurences of features
def count_features(graphs):
  counter = Counter()
  for graph in graphs:
    counter.update(bigram_features(graph))
  return counter


# Generate features for each node in graph
def bigram_features(graph):
  for node in graph:
    if node.head == -1:
      #yield (node.lemma, node.form, node.upostag, node.deprel)
      yield (node.lemma, node.upostag, node.form, node.feats, node.deprel)
    else:
      head = graph[node.head]
      #yield (node.lemma, node.form, node.upostag, node.deprel, head.lemma, head.form, head.upostag)
      yield (node.lemma, node.upostag, node.form, node.feats, node.deprel, head.lemma, head.upostag, head.form, head.feats);

def print_feature_counts(feature_counts, filestream):
  for feature, count in dict(feature_counts).items():
    print('\t'.join(list(feature)+[str(count)]), file=filestream)

def read_feature_counts(filestream):
  for l in filestream:
    l_split = l.split('\t')
    yield (tuple(l_split[:-1]), int(l_split[-1]))

def get_feature_counts(instream, outstream):
  conllu_sents = parse_conllu_file(instream); 
  bigrams_list = map(bigram_features, conllu_sents);
  bigrams = it.chain.from_iterable(bigrams_list);
  for feat in bigrams:
    print('\t'.join(feat), file=outstream);
  return ;

def read_feature_counts_new(instream, outstream, sel_fields=('node.lemma', 'node.upostag', 'node.deprel', 'head.lemma', 'head.upostag'), threshold=100):
  '''
    Reads a tsv table and gives a counter of edges with selected fields in the table 
    :param filestream: an iterator over the file object
    :param sel_fields: fields of interest over which to collect counts 
    :return:
  '''
  # these are the fields that are included in the tsv files
  fields = ('node.lemma', 'node.upostag', 'node.form', 'node.feats', 'node.deprel', 'head.lemma', 'head.upostag', 'head.form', 'head.feats');
  sel_indices = [];  # indices to be selected to collect statistics
  for f in sel_fields:
    try:
      sel_indices.append(fields.index(f))
    except ValueError:
      print("Can not understand field: {0}".format(f), file=sys.stderr)
  sel_indices = tuple(sel_indices);   # (0, 1, 4, 5, 6) by default
  key_indices = [defaultdict(lambda: it.count(1).__next__) for _ in sel_indices] # a list of hash table for each key # magically generates unique id for each key
  
  freqtable = dict();  #Counter()  # using native dict is faster (maybe because of pypy)
  getter    = freqtable.get
  for idx, line in enumerate(instream, start=1):
    if not (idx%10000000): print(idx, file=sys.stderr)
    fields = line.strip('\n').split('\t')
    freq, entry = int(fields[0]), fields[1:]
    sel_entry = tuple(key_indices[colidx][entry[idx]] for colidx, idx in enumerate(sel_indices) if idx < len(entry))
    freqtable[sel_entry] = getter(sel_entry, 0) + freq; 


  """
  lines = (l for l in instream);
  lines = (l.strip('\n').split('\t') for l in lines);  
  entries = ((int(fields[0]), tuple(fields[1:])) for fields in lines);
  sel_entries = ((freq, \
         tuple(fields[idx] for idx in sel_indices if idx < len(fields))) \
      for freq, fields in entries);
  sel_entries = ((freq, '\t'.join(entry)) for freq, entry in sel_entries);
  freqtable = Counter()  # using native dict is faster (maybe because of pypy)
  for freq, entry in sel_entries:
    counter[entry] += freq ;
  """
  
  reduced_dict = iter(sorted((item for item in freqtable.items() if item[1] >= threshold), key=itemgetter(1), reverse=True))
  inv_key_indices = [dict((value,key) for key,value in hash_table.items())
      for hash_table in key_indices]
  lines = ('{0}\t{1}'.format(item[1],'\t'.join(inv_key_indices[colidx][val] for colidx,val in enumerate(item[0]))) for item in reduced_dict);
  for l in lines:
    print(l, file=outstream)
  return 

#CONLLU_FIELD_NAMES = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
class UDNode:
  def __init__(self, conllu_node_line):
    field_values = conllu_node_line.split('\t')
    self.id = int(field_values[0]) - 1
    self.form = field_values[1]
    self.lemma = field_values[2]
    self.upostag = field_values[3]
    self.xpostag = field_values[4]
    self.feats = field_values[5]
    self.head = int(field_values[6]) - 1
    self.deprel = field_values[7]
    self.deps = field_values[8]
    self.misc = field_values[9]
    
  def __str__(self):
    return 'UDNode ' + self.form + ' (' + str(self.head) + ')'
  def __repr__(self):
    return self.__str__()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', nargs='?', type=argparse.FileType(mode='r', encoding='utf-8'), default=sys.stdin)
  parser.add_argument('outfile', nargs='?', type=argparse.FileType(mode='w', encoding='utf-8'), default=sys.stdout)
  args = parser.parse_args()
  #graphs = parse_conllu_file(args.infile)
  #feature_counts = count_features(graphs)
  #print_feature_counts(feature_counts, args.outfile)
  #get_feature_counts(args.infile, args.outfile)
  read_feature_counts_new(args.infile, args.outfile)
