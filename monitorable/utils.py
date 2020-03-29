def safeify(cb):
	return lambda *p, **o: cb(*p, **o)
