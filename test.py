import monitorable

print(monitorable)

a = monitorable.value(1)
b = monitorable.value(1)

def get_c():
	print('get_c')
	return a() + b()

c = monitorable.computed(get_c)


print('run')
print('c', c())
a(2)
print('a', a())
b(3)
print('b', b())
print('c', c())
a(4)
print('a', a())
print('c', c())
print('c', c())
print('c', c())
