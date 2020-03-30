print_error = print
def safeify(cb):
	def safeify_cb(*p, **o):
		try:
			cb(*p, **o)
		except BaseException as e:
			print_error(e)
	return safeify_cb

def set_print_error(cb):
	global print_error
	print_error = cb
