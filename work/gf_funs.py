
def functions_from_grammar(grammar):
	"""Generate tuples with functions names and category"""
	for cat in grammar.categories:
		for fun in grammar.functionsByCat(cat):
			yield (fun, cat)


def functions_to_file(out_path, funs_tuples):
	with open(out_path, 'w+') as f:
		for fun, cat in funs_tuples:
			f.write('{}\t{}\n'.format(fun, cat))


def functions_from_file(file_path):
	for line in open(file_path):
		fun, cat = line.strip().split('\t')
		yield (fun, cat)


if __name__ == "__main__":
	import pgf
	gr = pgf.readPGF('Dictionary.pgf')
	file = 'UD_functions'
	print('Writing to file: ' + file)
	functions_to_file(file, functions_from_grammar(gr))