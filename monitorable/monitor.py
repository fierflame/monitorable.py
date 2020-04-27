from .utils import safeify
from .mark import observe, watch_prop
from .encase import recover

class monitor:
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
	def __run(self, this_read):
		if len(this_read) == 0:
			self.__cb(False)
			return
		list = []
		for (target, props) in dict(this_read).items():
			for (p, m) in dict(props).items():
				if m:
					self.__cb(True)
					return
				list.append((target, p))
		cancel_list = []
		trigger = self.__trigger
		for (o, p) in list:
			cancel_list.append(watch_prop(recover(o), p, trigger))
		self.___cancel_list = cancel_list
	def __call__(self, *p, **pp):
		self.__cancel()
		this_read = dict()
		result = observe(
			this_read,
			lambda: self.__fn(*p, **pp),
			**self.__options
		)
		self.__run(this_read)
		return result
	def stop(self):
		if self.__cancel():
			self.__cb(False)
