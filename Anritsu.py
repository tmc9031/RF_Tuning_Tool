#!/usr/bin/env python
# For Anritsu8820C WCDMA measurement
# Using PyVisa and Python 2.7.5
# William Chang

from visa import *
import time
from decimal import *
from WCDMA_attributes import *

class Anritsu8820C(Instrument):
	"""
		class for Anritsu8820C
	"""
	def __init__(self, resource_name, **keyw):
		super(Anritsu8820C, self).__init__(resource_name, **keyw)
		self.s = None	#temporary string
		self.__path_loss = {700: -0.35, 1200: -0.35, 1700: -0.6, 2200: -0.6}		#initiate path loss table (using dict)
	
	def __repr__(self):
		return "Anritsu8820C(\"%s\")".format(self.resource_name)
		
	def switch_to_WCDMA(self):
		"""
			switch to WCDMA mode
			switch ok => return 0
			switch fail => return 1
		"""
		s = self.ask("STDSEL?")	#WCDMA|GSM|LTE
		print("Current Function: "+s)
		if s == "WCDMA":
			print("Already WCDMA mode")
			return 0
		else:
			self.write("STDSEL WCDMA")		#switch to WCDMA
			time.sleep(1)
			if (self.ask("STDSEL?") == "WCDMA"):
				print("Switch to WCDMA mode OK")
				return 0
			else:
				print("Switch to WCDMA mode fail")
				return 1

	def switch_to_GSM(self):
		"""
			switch to GSM mode
			switch ok => return 0
			switch fail => return 1
		"""
		s = self.ask("STDSEL?")	#WCDMA|GSM|LTE
		print("Current Format: "+s)
		if s == "GSM":
			print("Already GSM mode")
			return 0
		else:
			self.write("STDSEL GSM")		#switch to GSM
			time.sleep(1)
			if (self.ask("STDSEL?") == "GSM"):
				print("Switch to GSM mode OK")
				return 0
			else:
				print("Switch to GSM mode fail")
				return 1
	
	def switch_to_LTE(self):
		"""
			switch to LTE mode
			switch ok => return 0
			switch fail => return 1
		"""
		s = self.ask("STDSEL?")	#WCDMA|GSM|LTE
		print("Current Format: "+s)
		if s == "LTE":
			print("Already LTE mode")
			return 0
		else:
			self.write("STDSEL LTE")		#switch to LTE
			time.sleep(1)
			if (self.ask("STDSEL?") == "LTE"):
				print("Switch to LTE mode OK")
				return 0
			else:
				print("Switch to LTE mode fail")
				return 1
	
	def preset(self):
		"""
			preset Anritsu 8820C
		"""
		print("Preset Anritsu 8820C")
		s = self.ask("STDSEL?")	#WCDMA|GSM|LTE
		if s == "WCDMA":
			self.preset_3GPP()
		else:
			self.write("*RST")	#this command changes measurement count to "single"
		self.write("*CLS")
		
	def preset_3GPP(self):
		"""
			preest to 3GPP spec (for WCDMA)
		"""
		self.write("PRESET_3GPP")
		
	def update_path_loss(self):
		"""
			update path loss to Anritsu 8820C
			need to add other function to edit path loss
		"""
		freq = self.__path_loss.keys()
		freq.sort()
		#print(freq)
		str1 = "LOSSTBLVAL"
		str2 = ""
		self.write("DELLOSSTBL")	#delete loss table first
		for keys in freq:
			str2 = "{0} {1}MHz, {2}, {2}, {2}".format(str1, str(keys), str(abs(self.__path_loss[keys])))
			print(str2)
			self.write(str2)
		#self.write(str1)
		#self.write(str2)
	
	def update_link_settings(self):
		"""
			update Anritsu 8820C setting for link mode RF test
		"""
		if integrity == 1:
			self.write("INTEGRITY ON")
		else:
			self.write("INTEGRITY OFF")
		self.write("OLVL -75")		#set Output power to -75dBm (same as 8960)
		self.write("DRXCYCLNG 64")
		self.write("CALLPROC ON")	#ON|OFF
	
	def set_FDD_test_mode(self):
		# For Anritsu8820C, turn off "Call Processing"
		self.write("CALLPROC OFF")	#ON|OFF
	
	def set_FDD_UL_channel(self, UL_ch):
		"""
			Use this function only in FDD test mode
			For Anritsu8820C, it could be used in link mode
		"""
		s = "ULCHAN "+str(UL_ch)	# set UL ch
		self.write(s)
	
	def set_IMSI(self, IMSI):
		#set IMSI
		s = "IMSI {0}".format(IMSI)
		self.write(s)
	
	def set_DL_channel(self, DL_ch):
		s = "DLCHAN "+str(DL_ch)
		self.write(s)

	def handover_to_DL_ch(self, DL_ch):
		#for Anritsu8820C, direct set DL channel
		self.set_DL_channel(DL_ch)

	def set_DL_power(self, DL_power):
		s = "OLVL "+str(DL_power)	# Set output level
		self.write(s)
		#print("Set DL power to "+str(DL_power)+" dBm")
	
	def set_UL_power(self, UL_power):
		"""
			set UL Tx power and change to active bit mode
		"""
		self.write("TPCPAT ILPC")	# ALL1|ALL0|ALT|ILPC|UCMD
		s = "ILVL "+str(UL_power)	# Set input level
		self.write(s)
	
	def	set_UL_power_FTM(self, UL_power):
		"""
			set UL Tx power for tuning
		"""
		s = "ILVL "+str(UL_power)
		self.write(s)
	
	def set_all_up_bit(self):
		"""
			set all up bit and target 23dBm
		"""
		self.write("ILVL 23")	#set UE target power to 23dBm
		self.write("TPCPAT ALL1")	# ALL1|ALL0|ALT|ILPC|UCMD

	def call_connected(self):
		"""
			if idle => return 1
			if connected => return 0
		"""
		conn_stat = self.ask("CALL:CONN?")
		if conn_stat == "1":
			print("Phone connected")
			return 0
		else:
			print("Idle")
			return 1
	
	def setup_call(self, times=100):
		"""
			try to setup call for "times" times
			if connected => return 0
			if cannot setup call => return 1
		"""
		count = 0
		while True:
			if (count < times):
				conn_stat = self.ask("CALL:CONN?")
				print("conn_stat:"+conn_stat)
				if conn_stat == "1":
					print("Phone connected")
					return 0
				else:
					count += 1
					print("Paging count:"+str(count))
					self.write("CALL:ORIG")	#call UE
					time.sleep(3)
			else:
				print("UE not connected")
				return 1
	
	def setup_channel_power_mea(self, count = 20, RRC = "ON"):
		"""
			channel power measurement settings
			count: measure count
			RRC: RRC filter ON/OFF (ON for 3GPP sepc)
		"""
		#Tx power setting
		#agilent.write("SET:WCP:COUN:STAT ON")	#multi measurement ON
		self.write("SET:WCP:CONT OFF")	#Measure Single
		self.write("SET:WCP:TIM 1S")	#set time-out 1S in case the measurement cannot be made
		s = "SET:WCP:COUN "+str(count)	#multi-measurement ON and set measure count
		self.write(s)	
		self.write("SET:WCP:INTerval:TIME 666.7US")	#measurement interval for 1 timeslot (666.7us)
		self.write("SET:WCP:TRIGger:SOURce AUTO")	#set trigger source auto
		s = "SET:WCP:FILT:RRC "+RRC
		self.write(s)	#set RRC filter ON to meet 3GPP spec

	def setup_ACLR_mea(self, count = 20):
		"""
			ACLR measurement settings
			count: measure count
		"""
		#ACLR setting
		self.write("SET:WACL:CONT OFF")
		self.write("SET:WACL:TIM 3S")	#set time-out 1S in case the measurement cannot be made
		s = "SET:WACL:COUN "+str(count)
		self.write(s)	#multi-measurement ON and count = 10
		self.write("SET:WACL:TRIGger:SOURce AUTO")	#set trigger source auto

	def init_mea(self, command):
		s = "INIT:"+";".join(command)
		self.write(s)
	
	def init_TXP_ACLR(self):
		self.write("INIT:WCP;WACL")
	
	def init_TXP(self):
		self.write("INIT:WCP")
	
	def init_ACLR(self):
		self.write("INIT:WACL")
		
	def read_TXP(self):
		"""
			read channel power measurement
			if integrity is fail, return None and print error message
			if integrity is ok, return tx power in Decimal()
			
			"FETC:WCP?" data format
			+0,+4.21111100E-001
			int, channel power
		"""
		#read tx power
		s = self.ask("FETC:WCP?")
		s = s.split(",")
		Integrity = int(s[0])
		Txp = Decimal(s[1])
		if not Integrity:
			#print("Integrity ok")
			#print("Tx Power:"+str(Txp))
			return Txp
		else:
			print("Tx Power integrity fail: "+str(Integrity))
			return None

	def read_ACLR(self):
		"""
			read ACLR measurement (average)
			if integrity is fail, return None and print error message
			if integrity is ok, return ACLR in [-5MHz, +5MHz, -10MHz, +10MHz] fromat
			
			Reading format:
			"FETC:WACL?" (Max)
			ACLR:+0,-4.21932800E+001,-4.20209700E+001,-5.74313000E+001,-5.52463200E+001
				int, -5Mhz, +5Mhz, -10M, +10M	
			"FETC:WACL:AVER?" (average)
			ACLR:-4.21932800E+001,-4.20209700E+001,-5.74313000E+001,-5.52463200E+001
				 -5Mhz, +5Mhz, -10M, +10M	
		"""
		#check ACLR integrity
		Integrity = int(self.ask("FETC:WACL:INT?"))
		if not Integrity:
			s = self.ask("FETC:WACL:AVER?")
			s = s.split(",")
			ACLR = []
			for value in s:
				#ACLR.append((Decimal(value)).quantize(Decimal('.01')))
				ACLR.append((Decimal(value)))
			return ACLR
		else:
			print("ALCR integrity fail: "+str(Integrity))
			return None
	
	def sweep_LMH_Txp_ACLR(self, Band):
		"""
			sweep LMH channel Max Tx power and ACLR
		"""
		self.setup_channel_power_mea(20, "ON")	#Tx power measurement setting
		self.setup_ACLR_mea(count = 20)			#ACLR measurement setting
		self.set_all_up_bit()					#set all up bit
		#title string
		print("{0:8}, {1:8}, {2:6}, {3:6}, {4:6}, {5:6}".format("channel", "Tx Power", "-5MHz", "+5MHz", "-10MHz", "+10MHz"))
		for DL_ch in Band_DL_ch_map[Band]:
			self.handover_to_DL_ch(DL_ch)	#handover
			self.init_TXP_ACLR()	#start channel power & ACLR measurement
			time.sleep(2)	#wait for stable reading
			self.init_TXP_ACLR()	#start channel power & ACLR measurement again
			#read tx power
			txp = self.read_TXP()
			#read ACLR
			aclr = self.read_ACLR()
			print("{0:^8d}, {1:^8,.2f}, {2:6,.2f}, {3:6,.2f}, {4:6,.2f}, {5:6,.2f}".format(DL_ch, txp, aclr[0], aclr[1], aclr[2], aclr[3]))
	
	def setup_BER_mea(self, count=50000):
		"""
			BER measurement settings
			count: number of bits to test
		"""
		s = "SET:WBER:COUN "+str(count)	#set number of bits to test
		self.write(s)
		self.write("SET:WBER:CONT OFF")	#set trigger arm to single
	
	def init_BER(self):
		self.write("INIT:WBER")
	
	def read_BER(self):
		"""
			read BER measurement
			if integrity is fail, return None and print error message
			if integrity is ok, return BER(%) in Decimal
		"""
		#read BER
		s = self.ask("FETC:WBER:ALL?" )
		s = s.split(",")
		Integrity = int(s[0])
		BER = Decimal(s[1])
		if not Integrity:
			#print("BER(%): "+str(BER))
			return BER
		else:
			print("BER integrity fail: "+str(Integrity))
			return None

	def BER_GO(self, count=50000, start=-107, target=0.1):
		"""
			BER Go-No Go
			count: number of bits to test
			start: DL power level
			target: target BER
			
			PASS => return True
			FAIL => return False
		"""
		self.setup_BER_mea(count)
		self.set_DL_power(start)
		time.sleep(0.1)
		self.init_BER()
		ber = self.read_BER()
		if (ber <= target):
			return True
		else:
			return False
		
	def BER_search(self, count=50000, start=-107, step=0.5, target=0.1):
		"""
			BER search
			count: number of bits to test
			start: start DL power level
			step: step power level
			target: target BER
			
			return DL power level
		"""
		count = int(count)
		if (count <= 0):
			print("BER count error: "+str(count))
			count = 50000
		
		start = Decimal(start)
		if (start > -50):
			print("DL power level error: "+str(start))
			start = Decimal(-107)
		
		step = Decimal(step)
		
		self.setup_BER_mea(count)
		touch = 0	#flag if 0: reduce power, if 1: increase power
		while True:
			self.set_DL_power(start)
			time.sleep(0.1)
			self.init_BER()
			ber = self.read_BER()
			if (touch == 0):
				if (ber <= target):
					start -= step
				else:
					touch = 1
					start += step
			else:
				if (ber <= target):
					break
				else:
					start += step
		return start

			
	def sweep_LMH_BER_search(self, band, count=50000, start=-107, step=0.5, target=0.1):
		"""
			sweep LMH channel sensitivity
		"""
		#title string
		print("{0:8}, {1:18}".format("channel", "Sensitivity(dBm)"))
		for DL_ch in Band_DL_ch_map[band]:
			self.set_DL_power(-75)	#set DL power to -75dBm for handover
			time.sleep(0.1)
			self.handover_to_DL_ch(DL_ch)	#handover
			sens = self.BER_search(count, start, step, target)
			print("{0:^8d}, {1:^18,.1f}".format(DL_ch, sens))

if __name__ == "__main__":
	
	anritsu = Anritsu8820C("GPIB::14")
	anritsu.timeout = 10
	print("*IDN?")
	print(anritsu.ask("*IDN?"))
	
	# could use this to judge if Agilent or Anritsu
	s = anritsu.ask("*IDN?")
	if "ANRITSU" in s:
		print("YES")
	
	
	print("*OPC?")
	print(anritsu.ask("*OPC?"))
	
	
	
	
	anritsu.switch_to_WCDMA()
	#anritsu.switch_to_GSM()
	anritsu.preset()
	
	print(anritsu.ask("LOSSTBLVAL? 1"))
	anritsu.update_path_loss()
	
	anritsu.write("DLCHAN 10600")
	anritsu.set_IMSI(IMSI)
	
	print(anritsu.ask("CALLSTAT?"))