import datetime

from .math_ import *

class Direction(object):
	Production = -1
	Consumption = 1

class Model(object):
	def __init__(self, k_watt_peak, nominal_voltage, direction):
		self.direction = float(direction)
		self.k_watt_peak = float(k_watt_peak)
		self.nominal_voltage = float(nominal_voltage)

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
		current = datetime.datetime(1,1,1)
		ts_list = []
		while current.day == 1:
			ts_list.append((current.time(), self.get_power(current.time())))
			current += step

		return ts_list

class ConsumptionModel(Model):
	def __init__(self, k_watt_peak, nominal_voltage):
		super(ConsumptionModel, self).__init__(k_watt_peak, nominal_voltage,
			Direction.Consumption)

	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return (1.0 / 720.0) * min(1440.0 - mins, mins)

class ProductionModel(Model):
	def __init__(self, k_watt_peak, nominal_voltage):
		super(ProductionModel, self).__init__(k_watt_peak, nominal_voltage,
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

class SolarPV(ProductionModel):
	def _get_power_normalized(self, time_):
		mins = self.time_to_minutes(time_)
		return max(min(sin(0.00317108474160941*mins)*sin(4.81530850995063 +\
			0.00333398054600191*mins), sin(0.00317057738375734*mins)), 0)
