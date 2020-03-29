from weakref import WeakKeyDictionary
from contextlib import contextmanager
from .utils import safeify

_read = None # dist
def mark_read(target, prop):
	global _read
	if not _read:
		return
	if not target in _read:
		_read[target] = set()
	_read[target].add(prop)

class _with_observe:
	__old = []
	def __enter__(self):
		global _read
		self.__old.append(_read)
		_read = map
	def __exit__(self, *p):
		global _read
		_read = self.__old.pop()

@contextmanager
def _with_observe(map, **options):
	global _read
	oldread = _read
	_read = map
	try:
		postpone_priority = options.get('postpone')
		if not postpone_priority:
			yield
		else:
			with _with_postpone(postpone_priority == 'priority'):
				yield
	finally:
		_read = oldread

def observe(map, fn = None, **options):
	if not callable(fn):
		return _with_observe(**options)
	global _read
	oldread = _read
	_read = map
	try:
		postpone_priority = options.get('postpone')
		if not postpone_priority:
			return fn()
		return postpone(fn, postpone_priority == 'priority')
	finally:
		_read = oldread

_watchList = WeakKeyDictionary()


def _exec_watch(target, prop):
	global _watchList
	watches = _watchList.get(target)
	if not watches:
		return
	watches = watches.get(prop)
	if not watches:
		return
	for w in watches:
		w()

_waitList = None

def _run(list):
	for (target, set) in list.items():
		for prop in set:
			_exec_watch(target, prop)

@contextmanager
def _with_postpone(priority = False):
	global _waitList
	list = not priority and _waitList or dict()
	old = _waitList
	_waitList = list
	try:
		yield
	finally:
		_waitList = old
		if list != _waitList:
			_run(list)


def postpone(f = None, priority = False):
	if not callable(f):
		return _with_postpone(priority = priority)
	global _waitList
	list = not priority and _waitList or dict()
	old = _waitList
	_waitList = list
	try:
		return f()
	finally:
		_waitList = old
		if list != _waitList:
			_run(list)


_old = []
_list = None
def _postpone_enter():
	global _waitList
	global _old
	global _list
	list = _waitList or dict()
	_old.append(_waitList)
	_waitList = list

def _postpone_exit():
	global _waitList
	global _old
	global _list
	list = _list
	_waitList = _old.pop()
	if list != _waitList:
		_run(list)

postpone.__enter__ = _postpone_enter
postpone.__exit__ = _postpone_exit


def _wait(target, prop):
	global _waitList
	if not _waitList:
		return False
	list = _waitList.get(target)
	if not list:
		list = set()
		_waitList[target] = list
	list.add(prop)
	return True


def mark_change(target, prop):
	if _wait(target, prop):
		return
	_exec_watch(target, prop)

def watch_prop(target, prop, cb):
	global _watchList
	if not target in _watchList:
		_watchList[target] = WeakKeyDictionary()
	list = _watchList[target]
	if not prop in list:
		list[prop] = set()
	watch = list[prop]
	safeify_cb = safeify(cb)
	watch.add(safeify_cb)
	removed = False
	def remove():
		if removed:
			return
		if not safeify_cb in watch:
			return
		watch.remove(safeify_cb)
		if len(watch):
			return
		if not prop in list:
			return
		if list[prop] != watch:
			return
		del list[prop]
		if len(list):
			return
		if not target in _watchList:
			return
		if _watchList[target] != list:
			return
		del _watchList[target]

	return remove
