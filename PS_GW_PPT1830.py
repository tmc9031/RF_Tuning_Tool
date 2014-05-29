#!/usr/bin/env python
"""
	For power supply GW Instek PPT1830 GPIB commands
	Using PyVisa and Python 2.7.5
	
	 This file is part of RF_Tuning_Tool.

	:copyright: (c) 2013 by the A-mao Chang (maomaoto@gmail.com)
	:license: MIT, see COPYING for more details.

"""

from visa import *
import time
from decimal import *
from WCDMA_attributes import *

class PS_GW_PPT1830(Instrument):
	"""
		class for PS_GW_PPT1830
	"""
	def __init__(self, resource_name, **keyw):
		super(PS_GW_PPT1830, self).__init__(resource_name, **keyw)
	
	def __repr__(self):
		return "PS_GW_PPT1830({0})".format(self.resource_name)
		
	def identity(self):
		"""
			return instrument name
		"""
		s = self.ask("*IDN?")
		return s
		
	def read_current(self, count=10):
		"""
			return output current in mA (int)
		"""
		current = 0
		for i in range(count):
			temp = float(self.ask("MEASure:CURRent?"))
			current += temp
			#print("current:{0}".format(temp))
		
		current = int(current/count*1000)
		
		return current
	
		
if __name__ == "__main__":
	
	power_supply = PS_GW_PPT1830("GPIB::8")
	power_supply.timeout = 10
	print("*IDN?")
	print(power_supply.ask("*IDN?"))
	
	print(power_supply.identity())
	
	a = 0
	
	print("average:{0}".format(power_supply.read_current()))
	"""
	for i in range(10):
		current = power_supply.read_current()
		a += current
		print("current:{0}".format(current))
	
	print("average:{0:.3f}".format(a/10))
	print("average:{0}".format(a/10))
	"""
	
	
