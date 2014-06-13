#!/usr/bin/env python
"""
	For Agilent8960 WCDMA/LTE GPIB commands
	Using PyVisa and Python 2.7.5
	
	 This file is part of RF_Tuning_Tool.

	:copyright: (c) 2013 by the A-mao Chang (maomaoto@gmail.com)
	:license: MIT, see COPYING for more details.

"""

from visa import *
import time
from decimal import *
from WCDMA_attributes import *

class Agilent8960(Instrument):
	"""
		class for Agilent8960
		Agilent info: Agilent Technologies,8960 Series 10 E5515C,MY50266677,A.13.07
	"""
	def __init__(self, resource_name, **keyw):
		super(Agilent8960, self).__init__(resource_name, **keyw)
		self.s = None	#temporary string
		#self.__path_loss = {700: -0.35, 1200: -0.35, 1700: -0.6, 2200: -0.6}		#initiate path loss table (using dict)
	
	def __repr__(self):
		return "Agilent8960(\"%s\")".format(self.resource_name)
		
	def switch_to_WCDMA(self):
		"""
			switch to WCDMA mode
			switch ok => return 0
			switch fail => return 1
		"""
		s = self.ask("SYSTem:APPL?")	#ask application => Fast Switch Test App
		print("System application: "+s)
		s = self.ask("SYST:APPL:FORMat?")	#WCDMA|GSM/GPRS
		print("Current Format: "+s)
		if s == "\"WCDMA\"":
			print("Already WCDMA mode")
			return 0
		else:
			self.write("SYST:APPL:FORM 'WCDMA'")		#switch to WCDMA
			time.sleep(1)
			if (self.ask("SYST:APPL:FORMat?") == "\"WCDMA\""):
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
		s = self.ask("SYSTem:APPL?")	#ask application
		print("System application: "+s)
		s = self.ask("SYST:APPL:FORMat?")	#WCDMA|GSM/GPRS
		print("Current Format: "+s)
		if s == "\"GSM/GPRS\"":
			print("Already GSM/GPRS mode")
			return 0
		else:
			self.write("SYST:APPL:FORM 'GSM/GPRS'")		#switch to GSM
			time.sleep(1)
			if (self.ask("SYST:APPL:FORMat?") == "\"GSM/GPRS\""):
				print("Switch to GSM mode OK")
				return 0
			else:
				print("Switch to GSM mode fail")
				return 1
		
	
	def switch_to_C2k(self):
		"""
			switch to CDMA2000 mode
			switch ok => return 0
			switch fail => return 1
		"""
		s = self.ask("SYSTem:APPL?")	#ask application
		print("System application: "+s)
		s = self.ask("SYST:APPL:FORMat?")	#WCDMA|GSM/GPRS
		print("Current Format: "+s)
		if s == "\"IS-2000/IS-95/AMPS\"":
			print("Already C2k mode")
			return 0
		else:
			self.write("SYST:APPL:FORM 'IS-2000/IS-95/AMPS'")		#switch to CDMA
			time.sleep(1)
			if (self.ask("SYST:APPL:FORMat?") == "\"IS-2000/IS-95/AMPS\""):
				print("Switch to C2k mode OK")
				return 0
			else:
				print("Switch to C2k mode fail")
				return 1
		
	
	def preset(self):
		"""
			preset Agilent 8960
		"""
		print("Preset Agilent 8960")
		self.write("*RST")	#this command changes measurement count to "single"
		self.write("*CLS")
	
	def update_path_loss(self):
		"""
			update path loss to Agilent8960
			need to add other function to edit path loss
		"""
		freq = path_loss.keys()
		freq.sort()
		#print(freq)
		str1 = "SYST:CORR:FREQ "
		str2 = "SYST:CORR "
		
		for keys in freq:
			str1 += str(keys)+"MHz, "
			str2 += str(path_loss[keys])+", "
		print(str1)
		print(str2)
		self.write(str1)
		self.write(str2)
	
	def update_link_settings(self):
		"""
			update 8960 setting for link mode RF test
		"""
		#set cell-off mode for change parameter
		self.write("CALL:OPER:MODE OFF")	#CALL|CW|FDDT|OFF
		#Cell Parameters:
		#BCCH update page: Inhibit
		#self.write("CALL:BCCHannel:UPDAtepage INH")	#AUTO|INHibit
		#PS Domain Information: Present
		self.write("CALL:PSD PRES")	#ABSent|PRESent
		#ATT (IMSI Attach) Flag State: Set
		self.write("CALL:ATTFlag ON")	#ON|OFF
		#Security Operations: None
		self.write("CALL:SECurity:OPERation NONE")	#NONE|AUTHONLY|AUTHINT|AIC
		#RLC Reestablish: Off
		self.write("CALL:RLC:REEStablish OFF")	#AUTO|OFF
		#set frequency band indicator
		#self.write("CALL:BCCHannel:FBIN:STAT ON")	#1|ON|0|OFF
		#set Band Arbitrator
		self.write("CALL:BARBitrator BAND5")		#BAND5|BAND6
		# set back to Active Cell
		self.write("CALL:OPER:MODE CALL")	#CALL|CW|FDDT|OFF
	
	def set_FDD_test_mode(self):
		"""
			GSM: BCH+TCH mode
			WCDMA: FDD Test mode
			C2k: IS-2000 Test mode
		"""
		s = self.ask("SYST:APPL:FORMat?")	#WCDMA|GSM/GPRS
		if s == "\"GSM/GPRS\"":
			# Set 8960 to GSM BCH+TCH test mode
			self.write("CALL:OPER:MODE GBTTest")
		elif s == "\"WCDMA\"":
			# Set 8960 to FDD test mode for WCDMA
			self.write("CALL:OPER:MODE FDDT")	#CALL|CW|FDDT|OFF
		elif s == "\"IS-2000/IS-95/AMPS\"":
			# Set 8960 to IS-2000 Test mode for C2k (same result as Active Cell)
			self.write("CALL:OPER:MODE D2KT")	#AVCTest|CALL|D2KTest|CW|OFF
		else:
			print("Set FDD test mode fail")
	
	def set_FDD_UL_channel(self, UL_ch):
		"""
			Use this function only in FDD test mode
		"""
		s = self.ask("SYST:APPL:FORMat?")
		if s == "\"WCDMA\"":
			#set UL chan atuo OFF
			self.write("CALL:UPL:CHAN:CONT:AUTO OFF")	#1|ON|0|OFF
			s1 = "CALL:UPL:CHAN:CHAN "+str(UL_ch)	# set UL ch
			self.write(s1)
		elif s == "\"IS-2000/IS-95/AMPS\"":
			self.set_C2k_FTM_channel(UL_ch)
		
	
	def set_IMSI(self, IMSI):
		#set IMSI
		s = "CALL:PAG:IMSI \"{0}\"".format(IMSI)
		self.write(s)
	
	def set_DL_channel(self, DL_ch):
		#set cell-off mode for change parameter
		self.write("CALL:OPER:MODE OFF")	#CALL|CW|FDDT|OFF
		s = "CALL:CHAN "+str(DL_ch)
		self.write(s)
		#set UL chan atuo
		self.write("CALL:UPLink:CHANnel:CONTrol:AUTO ON")	#1|ON|0|OFF
		# set back to Active Cell
		self.write("CALL:OPER:MODE CALL")	#CALL|CW|FDDT|OFF
	
	def handover_to_DL_ch(self, DL_ch):
		#self.write("CALL:HANDoff:TCReconfig:CHANnel:STATe ON")	#set Transport channel reconfig-> UARFCN state ON
		s = "CALL:SET:CHAN:DOWN "+str(DL_ch)	# set DL ch
		self.write(s)	
		self.write("CALL:SETup:CHANnel:UPLink:CONTrol:AUTO ON")	#UL ch AUTO
		self.write("CALL:HANDoff:PCReconfig:RBTest:LMESsaging:STATe ON")	#set PCR RB loopback mode ON for BER test 
		self.write("CALL:HANDoff:PCReconfig")	#execute handover

	def set_DL_power(self, DL_power):
		s = "CALL:POW "+str(DL_power)
		self.write(s)
		#print("Set DL power to "+str(DL_power)+" dBm")
	
	def set_UL_power(self, UL_power):
		"""
			set UL Tx power and change to active bit mode
		"""
		self.write("CALL:CLPC:UPL:MODE ACT")	#ACTive|UDOWn (alternating bits) |UP (all up bits)|DOWN (all down bits)|UDOWn10 (ten up/ten down bits)
		s = "CALL:MS:POW:TARG "+str(UL_power)
		self.write(s)
	
	def	set_UL_power_FTM(self, UL_power):
		"""
			set UL Tx power for tuning
		"""
		#self.write("CALL:CLPC:UPL:MODE ACT")	#ACTive|UDOWn (alternating bits) |UP (all up bits)|DOWN (all down bits)|UDOWn10 (ten up/ten down bits)
		s = "CALL:MS:POW:TARG "+str(UL_power)
		self.write(s)
	
	def get_UL_power(self):
		"""
			get UL power (callbox setting)
		"""
		s = self.ask("SYST:APPL:FORMat?")
		if s == "\"WCDMA\"":
			UL_level = Decimal(self.ask("CALL:MS:POW:TARG?"))
		elif s == "\"IS-2000/IS-95/AMPS\"":
			UL_level = Decimal(self.ask("RFANalyzer:MANual:POWer?"))
		return UL_level
	
	def set_all_up_bit(self):
		"""
			set all up bit and target 23dBm
		"""
		self.write("CALL:MS:POW:TARG:AMPL 23")	#set UE target power to 23dBm
		self.write("CALL:CLPC:UPL:MODE UP")		#ACTive|UDOWn (alternating bits) |UP (all up bits)|DOWN (all down bits)|UDOWn10 (ten up/ten down bits)

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
	
	def setup_channel_power_mea(self, count = 20, RRC = "OFF"):
		"""
			channel power measurement settings
			count: measure count
			RRC: RRC filter ON/OFF (ON for 3GPP sepc)
		"""
		#Tx power setting
		#agilent.write("SET:WCP:COUN:STAT ON")	#multi measurement ON
		self.write("SET:WCP:CONT OFF")	#Measure Single
		self.write("SET:WCP:TIM 10S")	#set time-out 10S in case the measurement cannot be made
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
		self.write("SET:WACL:TIM 10S")	#set time-out 10S in case the measurement cannot be made
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
			if integrity is fail, return tx power and print error message
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
		elif Integrity == 5:	# Over Range
			print("Tx Power over range, integrity: "+str(Integrity))
			return 999999		# temp solution, 8960 still get a value if over range, translate to 8820c type of value
		elif Integrity == 6:	# Under Range
			print("Tx Power under range, integrity: "+str(Integrity))
			return -999999		# temp solution, 8960 still get a value if under range, return a very small value for distinction
		else:
			print("Tx Power integrity fail: "+str(Integrity))
			return Txp

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
			if integrity is fail, return BER(%) and print error message
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
		
	def set_GSM_channel(self, ch):
		"""
			Set GSM channel
			GSM TCH setting need to be verified with two kinds of command
			CALL:TCHannel[:ARFCn][:SELected]
			CALL:TCHannel[:ARFCn]:(DCS|EGSM|GSM450|GSM480|GSM750|GSM850|PCS|PGSM|RGSM|TGSM810) 
		"""
		s = "CALL:TCH "+str(ch)	# set UL ch
		self.write(s)
		
	def set_GSM_band(self, band):
		"""
			Set GSM TCH band
			CALL:TCHannel:BAND
			Range: PGSM | DCS | EGSM | GSM450 | GSM480 | GSM750 | GSM850 | PCS | RGSM | TGSM810
			Set Band Indicator
			CALL[:CELL]:BINDicator
			Range: DCS | PCS
		"""
		if band == "EGSM":
			self.write("CALL:TCH:BAND EGSM")
		elif band == "GSM850":
			self.write("CALL:TCH:BAND GSM850")
		elif band == "DCS":
			self.write("CALL:TCH:BAND DCS")
			self.write("CALL:BIND DCS")	#Set band indicator to DCS
		elif band == "PCS":
			self.write("CALL:TCH:BAND PCS")
			self.write("CALL:BIND PCS")	#Set band indicator to PCS

	def set_GSM_power_mea(self, count = 20):
		"""
			GSM Tx power measurement setting
			count: measure count
		"""
		self.write("SETUP:TXPOWER:CONTINUOUS OFF")
		s = "SET:TXP:COUN:NUMB "+str(count)	# set measure counts
		self.write(s)
		self.write("SETup:TXPower:TRIGger:SOURce AUTO")	# Trigger source: AUTO
		self.write("CALL:MS:TXL 0")	# Set PCL0 for QB
	
	def set_GSM_TSC(self):
		# This command is for Anritsu8820C only
		# Agilent 8960 default: AS_BCC
		# Measured value difference < 0.1dB
		self.write("CALL:SETup:TCHannel:TSCode TSC5")
		
	
	def init_GSM_power(self):
		self.write("INIT:TXP")
		
	def read_GSM_power(self):
		"""
			read channel power measurement
			if integrity is fail, return tx power and print error message
			if integrity is ok, return tx power in Decimal()
		"""
		#read tx power
		s = self.ask("FETC:TXP:ALL?")
		s = s.split(",")
		Integrity = int(s[0])
		Txp = Decimal(s[1])
		if not Integrity:
			#print("Integrity ok")
			#print("Tx Power:"+str(Txp))
			return Txp
		else:
			print("Tx Power integrity fail: "+str(Integrity))
			return Txp		
	

	def set_C2k_band(self, band):
		"""
			Set C2k band
			CALL:BAND
			Range: IMT2000|JCDMa|KPCS |NMT450|CELLular700|SECondary800|USCellular|USPCs|USPCs1900|AWService|PAMR400 |
					PAMR800 | PSAFety700 |CLOWer700 | TACS | DCS1800 | CCELlular | IMT2500 | US2500 |USFLink2500
		"""
		if band == "BC0":
			self.write("CALL:BAND USC")
		elif band == "BC1":
			self.write("CALL:BAND USPC")
		elif band == "BC10":
			self.write("CALL:BAND SEC800")

	def set_C2k_FTM_channel(self, ch):
		"""
			Set C2k channel
			CALL:CHAN
		"""
		s = "CALL:CHAN "+str(ch)	# set UL ch
		self.write(s)
	
	def	set_C2k_UL_power_FTM(self, UL_power):
		"""
			Set C2k UL Tx power for tuning
			Set "Recv Power Ctrl" to Manual
			Then set "Receiver Power"
		"""
		self.write("RFANalyzer:CONTrol:POWer:AUTO 0")	# Range: 1|ON|0|OFF
		s = "RFANalyzer:MANual:POWer "+str(UL_power)
		self.write(s)
	
	def set_C2k_RC(self, RC=1):
		"""
			Set C2k Radio Config
			Range: F1R1|F2R2|F3R3|F4R3|F5R4|F11R8
			Use F1R1 as default
		"""
		RC_dict = {1:'F1R1', 2:'F2R2', 3:'F3R3', 4:'F4R3', 5:'F5R4', 6:'F11R8'}
		self.write("CALL:RCONfig {0}".format(RC_dict[RC]))
	
	def setup_C2k_channel_power_mea(self, count = 20):
		"""
			C2k channel power measurement settings
			count: measure count
		"""
		#Tx power setting
		self.write("SET:CPOW:CONT OFF")	#Measure Single
		self.write("SET:CPOW:TIM 10S")	#set time-out 10S in case the measurement cannot be made
		s = "SET:CPOW:COUN "+str(count)	#multi-measurement ON and set measure count
		self.write(s)	

	def setup_C2k_ACLR_mea(self, count = 10):
		"""
			C2k Tx Spurious Emissions measurement settings
			count: measure count
			set default count to 10, 20 times is too slow
		"""
		#ACLR setting
		self.write("SET:CTXS:CONT OFF")
		self.write("SET:CTXS:TIM 10S")	#set time-out 10S in case the measurement cannot be made
		s = "SET:CTXS:COUN "+str(count)
		self.write(s)	#multi-measurement ON and count = 10
	
	def init_C2k_TXP_ACLR(self):
		self.write("INIT:CPOW;CTXS")
	
	def init_C2k_TXP(self):
		self.write("INIT:CPOW")
	
	def init_C2k_ACLR(self):
		self.write("INIT:CTXS")
	
	def read_C2k_TXP(self):
		"""
			read C2k channel power measurement
			if integrity is fail, return tx power and print error message
			if integrity is ok, return tx power in Decimal()
			
			"FETC:CPOW?" data format
			+0,+4.21111100E-001
			int, channel power
		"""
		#read tx power
		s = self.ask("FETC:CPOW?")
		s = s.split(",")
		Integrity = int(s[0])
		Txp = Decimal(s[1])
		if not Integrity:
			#print("Integrity ok")
			#print("Tx Power:"+str(Txp))
			return Txp
		elif Integrity == 5:	# Over Range
			print("Tx Power over range, integrity: "+str(Integrity))
			return 999999		# temp solution, 8960 still get a value if over range, translate to 8820c type of value
		elif Integrity == 6:	# Under Range
			print("Tx Power under range, integrity: "+str(Integrity))
			return -999999		# temp solution, 8960 still get a value if under range, return a very small value for distinction
		else:
			print("Tx Power integrity fail: "+str(Integrity))
			return Txp

	def read_C2k_ACLR(self):
		"""
			read C2k ACLR measurement (average)
			if integrity is fail, return ACLR and print error message
			if integrity is ok, return ACLR in [-0.885MHz, +0.885MHz, -1.980MHz, +1.980MHz] fromat
			
			Reading format:
			"FETC:CTXS?" (average)
			+0,+0.00000000E+000,-5.30425600E+001,-5.38219900E+001,-6.54417000E+001,-6.31073600E+001
			int, 0/PASS/1/FAIL, -0.885MHz, +0.885MHz, -1.980MHz, +1.980MHz
		"""
		#check ACLR integrity
		s = self.ask("FETC:CTXS?")
		s = s.split(",")
		Integrity = int(s[0])
		s = s[2:]
		ACLR = []
		for value in s:
			#ACLR.append((Decimal(value)).quantize(Decimal('.01')))
			ACLR.append((Decimal(value)))
		if not Integrity:
			return ACLR
		else:
			print("ALCR integrity fail: "+str(Integrity))
			return ACLR
	
if __name__ == "__main__":
	
	#get instrument
	agilent = Agilent8960("GPIB::14")
	agilent.timeout = 10
	agilent.write("*IDN?")
	print(agilent.read())
	"""
		Agilent Technologies,8960 Series 10 E5515C,MY48360201,A.10.12
		System application: "Fast Switch Test App"	
	"""

	#switch to WCDMA mode
	if (agilent.switch_to_C2k() == 1):
		print("switch format fail")
		exit()

	
	#preset instrument
	agilent.preset()
	print("preset")


	#set path loss
	agilent.update_path_loss()
	print("path loss")

	agilent.set_FDD_test_mode()
	
	agilent.set_C2k_band("BC0")
	agilent.set_C2k_FTM_channel(384)
	agilent.set_C2k_UL_power_FTM(23)
	agilent.set_C2k_RC()
	
	agilent.setup_C2k_channel_power_mea()
	agilent.setup_C2k_ACLR_mea()
	agilent.init_C2k_TXP_ACLR()
	txp = agilent.read_C2k_TXP()
	aclr = agilent.read_C2k_ACLR()
	print("txp"+str(txp))
	print("aclr"+str(aclr))
	
	"""
	#set call parameters
	agilent.update_link_settings()
	#IMSI = '001010123456789'
	agilent.set_IMSI(IMSI)
	print(IMSI)
	#set DL channel

	agilent.set_DL_channel(WCDMA_B2_DL_ch[1])
	print("DL channel")

	#set DL power
	agilent.set_DL_power(-70)

	#set Tx power to 0dBm
	agilent.set_UL_power(5)


	#setup call
	if (agilent.call_connected() == 1):
		agilent.setup_call(100)

	#agilent.sweep_LMH_Txp_ACLR("B2")
	agilent.sweep_LMH_BER_search("B2", count=15000, start=-108, step=0.5, target=0.1)
	"""
