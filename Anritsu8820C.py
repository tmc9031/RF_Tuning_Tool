#!/usr/bin/env python
"""
	For Anritsu8820C WCDMA/LTE GPIB commands
	Using PyVisa and Python 2.7.5
	
	 This file is part of RF_Tuning_Tool.

	:copyright: (c) 2013 by the A-mao Chang (maomaoto@gmail.com)
	:license: MIT, see COPYING for more details.

"""

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
		#self.__path_loss = {700: -0.35, 1200: -0.35, 1700: -0.6, 2200: -0.6}		#initiate path loss table (using dict)
	
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
		self.write("ALLMEASITEMS_OFF")	# Set all measurements to off
		
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
		freq = path_loss.keys()
		freq.sort()
		#print(freq)
		str1 = "LOSSTBLVAL"
		str2 = ""
		self.write("DELLOSSTBL")	#delete loss table first
		for keys in freq:
			str2 = "{0} {1}MHz, {2}, {2}, {2}".format(str1, str(keys), str(abs(path_loss[keys])))
			print(str2)
			self.write(str2)
		s = self.ask("STDSEL?")	#WCDMA|GSM|LTE
		print("Current Format: "+s)
		if s == "LTE":
			self.write("EXTLOSSW COMMON")	
		elif s == "WCDMA":
			self.write("DLEXTLOSSW COMMON")		# Set DL external loss to COMMON
            self.write("ULEXTLOSSW COMMON")		# Set UL external loss to COMMON
            self.write("AUEXTLOSSW COMMON")		# Set AUX external loss to COMMON
		elif s == "GSM":
			self.write("EXTLOSSW COMMON")
	
	def update_link_settings(self):
		"""
			update Anritsu 8820C setting for link mode RF test
		"""
		if WCDMA_attributes.integrity == 1:
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
		conn_stat = self.ask("CALLSTAT?")
		if int(conn_stat) == ANRITSU_LOOP_1:
			print("Phone connected")
			return 0
		elif int(conn_stat) == ANRITSU_IDLE:
			print("Idle")
			return 1
		elif int(conn_stat) == ANRITSU_IDLE_REGIST:
			print("Idle(Regist)")
			return 1
		else:
			print("Other status")
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
				conn_stat = self.ask("CALLSTAT?")
				print("conn_stat:"+conn_stat)
				if int(conn_stat) == ANRITSU_LOOP_1:
					print("Phone connected")
					return 0
				else:
					count += 1
					print("Paging count:"+str(count))
					self.write("CALLSA")	#call UE
					time.sleep(5)
			else:
				print("UE not connected")
				return 1
	
	def setup_channel_power_mea(self, count = 20, RRC = "OFF"):
		"""
			channel power measurement settings
			count: measure count
			RRC: RRC filter ON/OFF (ON for 3GPP sepc)
		"""
		#Tx power setting
		self.write("PWR_MEAS ON")		# Set [Power Measurement] to [On]
		s = "PWR_AVG "+str(count)		# Set [Average Count] to [count] times
		self.write(s)	
		# RRC filter is no need to set in Anritsu 8820C
		# Filtered and non-filterd power is acquired by different command

	def setup_ACLR_mea(self, count = 20):
		"""
			ACLR measurement settings
			count: measure count
		"""
		#ACLR setting
		self.write("ADJ_MEAS ON")
		s = "ADJ_AVG "+str(count)
		self.write(s)	#multi-measurement ON and count = 20

	def init_mea(self, command):
		self.write("SWP")
		# Anritsu uses only "SWP" to trigger measure
	
	def init_TXP_ACLR(self):
		self.write("SWP")
	
	def init_TXP(self):
		self.write("SWP")
	
	def init_ACLR(self):
		self.write("SWP")
		
	def read_TXP(self):
		"""
			read channel power measurement
		"""
		#read tx power
		s = self.ask("AVG_POWER?")
		Txp = Decimal(s)
		return Txp

	def read_ACLR(self):
		"""
			read ACLR measurement (average)
			return ACLR in [-5MHz, +5MHz, -10MHz, +10MHz] fromat
		"""
		ACLR = []
		ACLR.append((Decimal(self.ask("AVG_MODPWR? LOW5"))))
		ACLR.append((Decimal(self.ask("AVG_MODPWR? UP5"))))
		ACLR.append((Decimal(self.ask("AVG_MODPWR? LOW10"))))
		ACLR.append((Decimal(self.ask("AVG_MODPWR? UP10"))))
		return ACLR
	
	def sweep_LMH_Txp_ACLR(self, Band):
		"""
			sweep LMH channel Max Tx power and ACLR
		"""
		self.setup_channel_power_mea(20, "OFF")	#Tx power measurement setting
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
		self.write("BER_MEAS ON")
		s = "BER_SAMPLE "+str(count)	#set number of bits to test
		self.write(s)
	
	def init_BER(self):
		self.write("SWP")
	
	def read_BER(self):
		"""
			read BER measurement
			return BER(%) in Decimal
		"""
		#read BER
		s = self.ask("BER?" )
		BER = Decimal(s)*Decimal(100)	# convert BER to %
		return BER

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

	def set_LTE_BW(self, BW = 5):
		s = "BANDWIDTH {0}MHZ".format(str(BW))
		self.write(s)
	
	def set_LTE_TXP_ACLR(self):
		self.write("ILVL 23")	#set UE target power to 23dBm
		#self.write("TESTPRM TX_MAXPWR_Q_F")		# Set Test Parameter to Tx1 - Max Power(QPSK/FullRB)
		self.write("ALLMEASITEMS_OFF")	# Set all measurements to off
		self.write("PWR_MEAS ON")	# Set TxP measurement ON
		self.write("PWR_AVG 20")	# Set average count to 20
		self.write("ACLR_MEAS ON")	# Set ACLR measurement ON
		self.write("ACLR_AVG 20")	# Set average count to 20
		
	
	def init_LTE_TXP_ACLR(self):
		self.write("SWP")
	
	def read_LTE_TXP(self):
		# Read LTE tx power
		s = self.ask("POWER? AVG")
		Txp = Decimal(s)
		return Txp
	
	def read_LTE_ACLR(self):
		"""
			Read LTE ACLR
			return in [EUTRA-1, EUTRA+1, UTRA-1, URTA+1] fromat
		"""
		ACLR = []
		ACLR.append((Decimal(self.ask("MODPWR? E_LOW1,AVG"))))
		ACLR.append((Decimal(self.ask("MODPWR? E_UP1,AVG"))))
		ACLR.append((Decimal(self.ask("MODPWR? LOW1,AVG"))))
		ACLR.append((Decimal(self.ask("MODPWR? UP1,AVG"))))
		return ACLR

	def set_GSM_channel(self, ch):
		"""
			Set GSM channel
			In order to reduce querry command, separate GSM channel command
		"""
		s = "CHAN "+str(ch)	# set UL ch
		self.write(s)
		
	def set_GSM_band(self, band):
		"""
			Set GSM band
			Anritsu 8820c only cares DCS/PCS, but Agilent8960 needs different setting for QB
		"""
		if band == "DCS":
			self.write("SYSCMB DCS1800")	#Set system combination to GSM/DCS1800
			self.write("BANDIND DCS1800")	#Set band indicator to DCS
		elif band == "PCS":
			self.write("SYSCMB PCS1900")	#Set system combination to GSM/PCS1900
			self.write("BANDIND PCS1900")	#Set band indicator to PCS
	
	def set_GSM_power_mea(self, count = 20):
		"""
			GSM Tx power measurement setting
			count: measure count
		"""
		#Set GSM mode
		self.write("OPEMODE GSM")
		#Tx power setting
		self.write("PWR_MEAS ON")		# Set [Power Measurement] to [On]
		s = "PWR_COUNT "+str(count)		# Set [Average Count] to [count] times
		self.write(s)
		self.write("MSPWR 0")			#Set PCL0 (for all bands)
		self.write("ILVLCTRL MANUAL")	#Set input level according to Manual
		self.write("ILVL 34")			#Set input level 34dBm, may change after test
	
	def init_GSM_power(self):
		self.write("SWP")
		
	def read_GSM_power(self):
		"""
			return GSM average tx power
		"""
		s = self.ask("AVG_TXPWR? DBM")
		Txp = Decimal(s)
		return Txp
		
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
