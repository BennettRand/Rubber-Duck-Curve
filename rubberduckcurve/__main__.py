import datetime
import matplotlib.pyplot as plt

from . import model

def main():
	cs = [model.ConsumptionResidential(5.0, 20) for _ in xrange(100)]
	ps = [model.SolarPV(4.0, 90.0, 0.1, True, 0.0) for _ in xrange(75)]
	r = model.Noise(-0.01, 0.01)

	n = model.NetPower(cs + ps)

	ts = n.get_timeseries(datetime.timedelta(minutes=5))
	plt.plot([x[0] for x in ts], [x[1] for x in ts])
	plt.show()

	# n = model.NetPower(*cs)
	#
	# ts = n.get_timeseries(datetime.timedelta(minutes=5))
	# plt.plot([x[0] for x in ts], [x[1] for x in ts])
	# plt.show()

	return

if __name__ == "__main__":
	main()
