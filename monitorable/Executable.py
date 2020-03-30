from .utils import safeify
from .mark import observe, watch_prop
from .encase import recover

class Executable:
	__cancel_list = None
	def __init__(self, fn, cb, **options):
		self.__options = options
		self.__fn = fn
		self.__cb = safeify(cb)
	def __trigger(self):
		if self.__cancel():
			self.__cb(True)
	def __cancel(self):
		if self.__cancel_list == None:
			return False
		list = self.__cancel_list
		self.__cancel_list = None
		for f in set(list):
			f()
		return True
	def __call__(self):
		self.__cancel()
		thisRead = dict()
		ok = False
		try:
			result = observe(thisRead, self.__fn, **self.__options)
			ok = True
			return result
		finally:
			if ok and len(thisRead):
				cancel_list = self.__cancel_list = []
				for (target, props) in dict(thisRead).items():
					for prop in set(props):
						cancel_list.append(
							watch_prop(
								recover(target),
								prop,
								self.__trigger
							)
						)
			else:
				self.__cb(False)
		pass
	def stop(self):
		if self.__cancel():
			self.__cb(False)
