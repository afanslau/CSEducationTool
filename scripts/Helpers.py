
def ensurePrefix(base, prefix): 
	if base is None:
		return None
	elif prefix is None:
		return None
	''' Example 
	# make this url absolute without duplicating http://
	old_s = http://example.com
	new_s = ensurePrefix(old_s, 'http://')
	# output: 
	# http://example.com

	old_s = example.com
	new_s = ensurePrefix(old_s, 'http://')
	# output: 
	# http://example.com
	'''

	# Return the base if you find the prefix at position 0. Otherwise
	if base.find(prefix) == 0:
		return base  
	else:
		return prefix + base


