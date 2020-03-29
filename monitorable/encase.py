from .mark import mark_change, mark_read

class encase:
	def __init__(self, target: dict = None, nest: int = 0):
		self.__dict = target or dict()
		self.__nest = nest
	def __getitem__(self, k):
		mark_read(self.__dict, k)
		value = self.__dict.get(k)
		nest = self.__nest
		if self.__nest <= 0 or not isinstance(value, dict):
			return value
		return encase(value, nest - 1)
	def __setitem__(self, k, v):
		mark_change(self.__dict, k)
		if (isinstance(v, encase)):
			v = v()
		self.__dict[k] = v
	def __delitem__(self, k):
		has = k in self.__dict
		if has:
			mark_change(self.__dict, True)
		del self.__dict[k]
	def __contains__(self, k):
		mark_read(self.__dict, True)
		return k in self.__dict
	def __call__(self):
		return self.__dict


def recover(v):
	if (isinstance(v, encase)):
		return v()
	return v
