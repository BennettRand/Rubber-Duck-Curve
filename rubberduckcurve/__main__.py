import datetime

from . import model

def main():
	p = model.ProductionModel(100, 400)
	c = model.ConsumptionModel(200, 240)

	for x in xrange(24):
		curr_t = datetime.time(x)
		print c.get_power(curr_t), c.get_net_power(curr_t),
		print p.get_power(curr_t), p.get_net_power(curr_t)

	return

if __name__ == "__main__":
	main()
