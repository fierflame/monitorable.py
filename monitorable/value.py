from .utils import safeify
from .mark import mark_read, mark_change
from .encase import recover, encase
from .monitor import monitor
from weakref import WeakSet

class Trigger:
	__callbacks = None
	__value = None
	__clear_callbacks = None
	def _init(self, value, callbacks, clear_callbacks):
		self.__value = value
		self.__callbacks = callbacks
		self.__clear_callbacks = clear_callbacks
	def __call__(self):
		callbacks = self.__callbacks
		if callbacks == None:
			return
		mark_change(self.__value, 'value')
		for cb in set(callbacks):
			cb(value, False)
	def has(self):
		callbacks = self.__callbacks
		return bool(callbacks and len(callbacks))
	def stop(self):
		callbacks = self.__callbacks
		if callbacks == None:
			return
		clear_callbacks = self.__clear_callbacks
		if clear_callbacks == None:
			clear_callbacks()
		for cb in set(callbacks):
			cb(value, True)

class Value:
	__trigger = None
	__stopped = False
	@property
	def value(self):
		return self.__get()
	@value.setter
	def value(self, value):
		return self.__set(value)
	def __init__(self,
		get,
		set = None,
		stop = lambda: None,
		change = lambda: None,
		trigger = None,
	):
		if trigger == None:
			trigger = Trigger()
		def getValue():
			mark_read(self, 'value')
			return get()
		self.__get = getValue
		def setValue(v, marked = False):
			if set == None:
				return
			def mark():
				nonlocal marked
				marked = True
			try:
				set(v, mark)
			finally:
				if marked and trigger:
					trigger()
		self.__set = setValue
		self.__stop = stop
		self.__change = change
		self.__callbacks = []
		def clear_callbacks():
			self.__callbacks = None
		self.__trigger = trigger
		trigger._init(self, self.__callbacks, clear_callbacks)
	def __call__(self, *p):
		if len(p) > 2:
			self.__set(p[0], p[1])
			return p[0]
		if len(p):
			self.__set(p[0])
			return p[0]
		return self.__get()
	def watch(self, cb):
		callbacks = self.__callbacks
		if callbacks == None:
			return lambda: None
		safeify_cb = safeify(cb)
		callbacks.append(safeify_cb)
		self.__change()
		cancelled = False
		def cancel():
			nonlocal cancelled, callbacks, safeify_cb
			if cancelled:
				return
			cancelled = True
			if callbacks == None:
				return
			if safeify_cb not in callbacks:
				return
			callbacks.remove(safeify_cb)
			self.__change()
		return cancel
	def stop(self):
		if self.__stopped:
			return
		self.__stopped = True
		self.__stop()
		trigger = self.__trigger
		if trigger == None:
			return
		trigger.stop()

def is_value(x):
	return isinstance(x, Value)

def value(default, **options):
	proxy = options.get('proxy')
	source = None
	proxyValue = None
	def set(v, mark):
		nonlocal proxyValue, source, proxy
		if proxy:
			v = recover(v)
		if v == source:
			return
		source = v
		proxyValue = encase(source) if proxy else source
		mark()
	value = Value( lambda : proxyValue, set)
	value(default)
	return value

def computed(getter, setter = None, **options):
	setValue = setter
	proxy = options.get('proxy')
	postpone = options.get('postpone')
	source = None
	proxyValue = None
	stopped = False
	computed = False
	trigger = Trigger()
	def value_changed(changed):
		nonlocal computed, trigger
		computed = not changed
		if changed and trigger:
			trigger()
	executable = monitor(getter, value_changed, postpone=postpone)
	def run():
		nonlocal computed, stopped, source, proxyValue
		computed = True
		has_error = True
		try:
			source = executable()
			has_error = False
			if proxy:
				source = recover(source)
			proxyValue = encase(source) if proxy else source
			return proxyValue
		finally:
			if has_error and not stopped:
				computed = False
	def stop():
		nonlocal stopped, computed
		if stopped:
			return
		stopped = True
		if computed:
			return
		run()
	return Value(
		lambda : proxyValue if computed or stopped else run(),
		setValue and (lambda v: setValue(recover(v) if proxy else v)),
		stop,
	)
