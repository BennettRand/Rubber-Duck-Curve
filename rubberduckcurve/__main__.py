import datetime

from . import model

def main():

	print "Consumption"
	c = model.ConsumptionDepartmentStore(100, 240)

	for x in c.get_timeseries(datetime.timedelta(minutes=10)):
		print x[1]

	print "Production"
	p = model.SolarPV(80, 400)

	for x in p.get_timeseries(datetime.timedelta(minutes=10)):
		print x[1]

	return

if __name__ == "__main__":
	main()
