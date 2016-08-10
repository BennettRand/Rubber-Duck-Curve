import datetime
import random

from .math_ import *

class Direction(object):
	Production = -1
	Consumption = 1

class Model(object):
	def __init__(self, k_watt_peak, direction):
		self.direction = direction
		self.k_watt_peak = k_watt_peak

	@staticmethod
	def time_to_minutes(time_):
		mins = (time_.hour * 60.0) + time_.minute + (time_.second / 60.0)
		mins += time_.microsecond / (1000000.0 * 60.0)
		return mins

	def _get_power_normalized(self, time_):
		return 0.5

	def get_power(self, time_):
		return self._get_power_normalized(time_) * self.k_watt_peak

	def get_net_power(self, time_):
		return self.get_power(time_) * self.direction

	def get_timeseries(self, step=datetime.timedelta(minutes=15)):
		current = datetime.datetime(2000,1,1)
		ts_list = []
		while current.day == 1:
			ts_list.append((current, self.get_power(current.time())))
			current += step

		return ts_list

class ConsumptionModel(Model):
	def __init__(self, k_watt_peak):
		super(ConsumptionModel, self).__init__(k_watt_peak,
			Direction.Consumption)

	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return (1.0 / 720.0) * min(1440.0 - mins, mins)

class ProductionModel(Model):
	def __init__(self, k_watt_peak):
		super(ProductionModel, self).__init__(k_watt_peak,
			Direction.Production)

	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return (1.0 / 1440.0) * min(1440.0 - mins, mins)

class ConsumptionDepartmentStore(ConsumptionModel):
	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return 1.27444801678829*max(0.826182364981405,cos(5.36116494335841 +\
			0.00126747469986732*mins +0.0692808118897491*\
			cos(0.00744373589903713*mins))) - 0.245652006327247

class ConsumptionDepartmentStore2(ConsumptionModel):
	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return 1.13002853743606*max(cos(5.5350162766485 +0.000973397877250573*\
			mins +0.171470532079154*cos(3.9993028535514 -0.00378658770491399*\
			mins)), 0.767364206122888)- 0.10878458249177 -0.00580866769680088*\
			cos(-0.0153972638843874*mins)

class ConsumptionBigBoxStore(ConsumptionModel):
	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return 0.668661562226531 + 1.12066846186571e-10*mins +\
			0.000333194390074274*mins*greater(mins, 552.758831497753) -\
			1.71925108391698e-10*mins**3*greater(mins, 552.758831497753)

class ConsumptionSchool(ConsumptionModel):
	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		if mins == 887.0:
			mins += 0.0001
		return (119.0 - if_(185.0 - mins, 1.0, if_(330.0 - mins, 185.0 - mins,\
			if_(896.0 - mins, -377.0, 3611.0 / (887.0 - mins))))) / 496.0

class ConsumptionResidential(ConsumptionModel):
	def __init__(self, k_watt_peak, usage_spikes=0):
		super(ConsumptionResidential, self).__init__(k_watt_peak)
		self.usage_spikes = usage_spikes

		self.spike_map = [random.uniform(0.0, 1.0) for _ in xrange(37)]

	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		mean = .256
		ret = 0.851361191446212 + 0.000108310047298587*mins*\
			sin(5.54574851559184 + 0.0133582566114846*mins) -\
			0.000764501665482085*mins - 0.55759590992875*\
			cos(-0.00206579208712526*mins) - 6.57555322579598e-8*mins**2*\
			sin(5.54574851559184 + 0.0133582566114846*mins)

		expected = ret / mean

		tot = 0.0
		z = 0.0
		while self.spike_map[int(mins / 40)] > tot:
			tot += poisson_pdf(expected, z)
			z += 1.0


		ret = (z * mean)

		ret = max(ret, 0.0)
		ret = min(ret, 1.0)

		return ret

class SolarPV(ProductionModel):
	def __init__(self, k_watt_peak, sun_elevation=90.0, cloud_coverage=0.0,
		reduce_peak=False, over_power=0.0, optical_depth=0.56, nominal_v=400.0):
		super(SolarPV, self).__init__(k_watt_peak)
		self.sun_elevation = (sun_elevation / 90.0)
		self.cloud_coverage = cloud_coverage
		self.reduce_peak = reduce_peak
		self.over_power = over_power
		self.optical_depth = optical_depth
		self.nominal_v = nominal_v

		self.cloud_coverage_map = [True] * int(self.cloud_coverage * 360)
		self.cloud_coverage_map += [False] *\
			(360 - len(self.cloud_coverage_map))

		random.shuffle(self.cloud_coverage_map)

	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		ret = max(sin(((mins / 720.0) * pi) - pi/2.0) -\
			(1.0 - self.sun_elevation) , 0.0) * (1.0 / self.sun_elevation)

		ret = min(ret * (1.0 + self.over_power), 1.0)

		if self.reduce_peak:
			ret *= self.sun_elevation

		if self.cloud_coverage_map[int(mins)/4]:
			ret *= self.optical_depth

		return ret

	def get_iv(self, time_):
		power = self.get_power(time_)
		v = (self.nominal_v / (pi / 2.0)) * atan(100*power)
		if v == 0: v = 0.00000000000001
		i = power / v

		return i,v

class NetPower(Model):
	def __init__(self, models, export=True):
		super(NetPower, self).__init__(1, Direction.Consumption)
		self.models = models
		self.export = export

	def get_power(self, time_):
		if not self.export:
			return max(sum([x.get_net_power(time_) for x in self.models]), 0.0)
		else:
			return sum([x.get_net_power(time_) for x in self.models])

class Noise(Model):
	def __init__(self, k_watt_min, k_watt_peak):
		super(Noise, self).__init__(k_watt_peak, Direction.Consumption)
		self.k_watt_min = k_watt_min

	def _get_power_normalized(self, time_):
		return (self.k_watt_min / self.k_watt_peak) +\
			((self.k_watt_peak - self.k_watt_min) / self.k_watt_peak) * \
			random.uniform(0.0,1.0)
