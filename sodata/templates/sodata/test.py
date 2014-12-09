def recursion(n):
	print(n)
	if n == 10:
		return
	recursion(n+1)

recursion(5)

def fib(n):

	if n == 0:
		return 1
	elif n == 1:
		return 1

	return fib(n-1) + fib(n-2)

def fib_loop(n):
	i = 0
	f1 = 0
	f2 = 1

	while i < n:
		

fib(8)
# 0 1 1 2 3 5 8 13