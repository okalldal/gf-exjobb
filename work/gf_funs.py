
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

FILE = 'UD_functions'
functions = list(functions_from_file(FILE))

if __name__ == "__main__":
	import pgf
	gr = pgf.readPGF('Dictionary.pgf')
	print('Writing to file: ' + FILE)
	functions_to_file(FILE, functions_from_grammar(gr))