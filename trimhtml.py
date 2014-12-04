import sys
if __name__=='__main__':
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		outs = ''
		for line in f:
			outs+=line.strip()
		print outs