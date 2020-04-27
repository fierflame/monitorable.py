from .value import computed, is_value

def _create_value(props, key):
	def get_value():
		p = props[key]
		if is_value(p):
			return p()
		return p
	def set_value(v):
		p = props[key]
		if is_value(p):
			p(v)
		else:
			props[key] = v
	return computed(get_value, set_value)

def as_value(props, key = None):
	if key != None:
		return _create_value(props, key)
	return lambda k: _create_value(props, k)
