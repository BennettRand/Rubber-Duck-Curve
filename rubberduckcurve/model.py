import datetime

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
