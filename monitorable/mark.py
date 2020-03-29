from .utils import safeify

_read = None # dist
def mark_read(target, prop):
	global _read
	if not _read:
		return
	if not target in _read:
		_read[target] = set()
	_read[target].add(prop)

def observe(fn, map, **options):
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

_watchList = dict() # TODO: WeakMap


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

def postpone(f, priority = False):
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
		_watchList[target] = dict() # TODO: WeakMap
	list = _watchList[target]
	if not prop in list:
		list[prop] = set()
	watch = list[prop]
	safeifyCb = safeify(cb)
	watch.add(safeifyCb)
	removed = False
	def remove():
		if removed:
			return
		if not safeifyCb in watch:
			return
		watch.remove(safeifyCb)
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