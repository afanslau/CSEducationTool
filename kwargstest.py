#Alter value for kwarg Test code

def testfn1(**kwargs):
	print type(kwargs)
	print kwargs
	for k,v in kwargs.iteritems():
		print "1111", k, v

	kwargs['kw1'] = 'replace'
	testfn2(**kwargs)


def testfn2(**kwargs):
	print type(kwargs)
	print kwargs
	for k,v in kwargs.iteritems():
		print "2222", k, v

testfn1(kw1='hello', kw2='world')