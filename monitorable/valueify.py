from .value import value, computed, is_value

def _create_value(props, key, defa = None, set = None):
	def cb(value, setted):
		if callable(set):
			set(value, setted)
	def get_value():
		if not props.has(key):
			return defa()
		p = props[key]
		if is_value(p):
			return p()
		return p
	def set_value(v):
		if not props.has(key):
			defa(v)
			cb(v, False)
			return
		p = props[key]
		if is_value(p):
			p(v)
			cb(v, True)
			return
		cb(v, False)
	return computed(get_value, set_value)

def valueify(props, key = None, defa = None, set= None):
	if (key != None):
		return _create_value(props, key, defa, set)
	def valueify_props(k, d = None, s = None):
		return _create_value(props, k, d, s)
	return valueify_props
