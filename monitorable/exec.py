from contextlib import contextmanager
from .utils import safeify
from .mark import observe, watch_prop
from .encase import recover

def _run(this_read, trigger, cb):
	if len(this_read) == 0:
		cb(False)
		return
	list = []
	for (target, props) in dict(this_read).items():
		for (p, m) in dict(props).items():
			if m:
				cb(True)
				return
			list.append((target, p))
	cancel_list = []
	for (o, p) in list:
		cancel_list.append(watch_prop(recover(o), p, trigger))
	return cancel_list

@contextmanager
def __with__exec(cb, **options):
	safeify_cb = safeify(cb)
	cancel_list = None
	# 取消监听
	def cancel():
		nonlocal cancel_list
		if not cancel_list:
			return False
		list = cancel_list
		cancel_list = None
		for f in list:
			f()
		return True
	def trigger():
		if not cancel():
			return
		safeify_cb(True)
	this_read = dict()
	with observe(this_read, postpone = options.get('postpone')):
		yield cancel
	_run(this_read, trigger, safeify_cb)

def exec(cb, fn = None, **options):
	if not callable(fn):
		return __with__exec(cb, **options)
	safeify_cb = safeify(cb)
	cancel_list = None
	# 取消监听
	def cancel():
		nonlocal cancel_list
		if not cancel_list:
			return False
		list = cancel_list
		cancel_list = None
		for f in list:
			f()
		return True
	def trigger():
		if not cancel():
			return
		safeify_cb(True)
	this_read = dict()
	result = observe(this_read, fn, postpone = options.get('postpone'))
	_run(this_read, trigger, safeify_cb)
	if options.get('result_only'):
		return result
	def stop():
		if not cancel():
			return
		safeify_cb(False)
	return 	dict(result = result, stop = stop)
