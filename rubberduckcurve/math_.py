import math

cos = math.cos
sin = math.sin
pi = math.pi
e_ = math.e
atan = math.atan

def if_(condition, then, else_val):
	if condition > 0:
		return then
	else:
		return else_val

def greater(a, b):
	if a>b:
		return 1.0
	else:
		return 0.0

def less(a, b):
	if a<b:
		return 1.0
	else:
		return 0.0

def poisson_pdf(expected, idx):
	return ((expected ** idx) * (e_ ** -expected)) / float(math.factorial(idx))
