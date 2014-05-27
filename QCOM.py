#!/usr/bin/env python
"""
	Control Qualcomm based phone via QMSL lib
	
	 This file is part of RF_Tuning_Tool.

	:copyright: (c) 2013 by the A-mao Chang (maomaoto@gmail.com)
	:license: MIT, see COPYING for more details.

"""
import time
from ctypes import *
from WCDMA_attributes import *

truth_dict = {True:"Yes",False:"No"}
pass_dict = {True:"Pass",False:"Fail"}

		
class QCOM_phone:
	def __init__(self):
		self.g_hResourceContext = c_void_p()
		self.qdll = None
		self.qBW = RFCOM_BW_LTE_5MHz	# BW corresponds to QMSL defined const
	
	def initial_QMSL(self, bUseQPST):
		# Import dll
		self.qdll = CDLL("QMSL_MSVC10R")

		#Set the library mode--QPST or QPHONEMS
		# bUseQPST = true to use QPST, FALSE to use QPHONEMS 
		# move bUseQPST to WCDMA_attributes.py
		self.qdll.QLIB_SetLibraryMode( bUseQPST )

		#Get the library version
		# Return: QLIB VXX.xx, <MODE>
		sLibraryVersion = create_string_buffer(50);
		self.qdll.QLIB_GetLibraryVersion(sLibraryVersion);
		print (sLibraryVersion.value)
		#return "b'QLIB V6.0.1,QPHONEMS'" @home(py 3.3.2 + win7)
		#return "QLIB V6.0.1,QPHONEMS" @office(py 2.7.5 + win7)

		#These will get filled in by the library interface
		_bSupportsDiag = c_bool(0)
		_bSupportsEFS = c_bool(0)
		_bSupportsSwDownload = c_bool(0)
		_bUsingQPST = c_bool(0)
		# Get the capabilities
		self.qdll.QLIB_GetLibraryCapabilities(byref(_bSupportsDiag), byref(_bSupportsEFS), byref(_bSupportsSwDownload), byref(_bUsingQPST))

		# Print the results
		print("Supports DIAG: {0}".format(truth_dict[bool(_bSupportsDiag)]))
		#print("Supports EFS: {0}".format(truth_dict[bool(_bSupportsEFS)]))
		#print("Supports SW Download: {0}".format(truth_dict[bool(_bSupportsSwDownload)]))
		print("Using QPST: {0}".format(truth_dict[bool(_bUsingQPST)]))
		
	def get_phone_port_list(self):
		"""
			Return a list containing available phone ports
			If no port found, return a empty list
		"""
		iNumPorts = c_ushort(16)	# as an input: max length of aPortList
									# as an output: number of ports found
		UShortList = c_ushort * 16
		aPortList = UShortList()	# output: array of ports available
		iNumIgnorePorts = c_ushort(0)	# number of ports to ignore
		aIgnorePortList = pointer(c_ushort())	# list of ports to ignore
		bOK = self.qdll.QLIB_GetAvailablePhonesPortList(byref(iNumPorts), byref(aPortList), iNumIgnorePorts, aIgnorePortList)
		PhoneList = []
		if (bOK):
			print("NumPorts: {0}".format(iNumPorts))
			print("Port:")
			for i in range(iNumPorts.value):
				print(aPortList[i])
				PhoneList.append(aPortList[i])
		else:
			print("no port found")
		
		return PhoneList

	def connect_phone(self, iComPort):
		#iComPort = c_uint(40)	# move to WCDMA_attributes
		self.qdll.QLIB_ConnectServerWithWait.restype = c_void_p
		self.qdll.QLIB_ConnectServer.restype = c_void_p
		self.g_hResourceContext = self.qdll.QLIB_ConnectServerWithWait(iComPort)
		#iComPort = QLIB_COM_AUTO_DETECT
		#self.g_hResourceContext = self.qdll.QLIB_ConnectServerWithWait(iComPort, c_int(3000))
		#print("QCOM Handle: {0}".format(self.g_hResourceContext))
		print("Phone Connected: {0}".format(truth_dict[bool(self.qdll.QLIB_IsPhoneConnected(self.g_hResourceContext))]))

		#Get COM port number
		#self.qdll.QLIB_GetComPortNumber( self.g_hResourceContext, byref(c_ushort(iComPort)) )
		self.qdll.QLIB_GetComPortNumber( self.g_hResourceContext, byref(iComPort) )
		print("Port Number: {0}".format(iComPort))

		#Get SW version info
		comp_date = create_string_buffer(11)	#compile date
		comp_time = create_string_buffer(8)		#compile time
		rel_date = create_string_buffer(11)		#release date
		rel_time = create_string_buffer(8)		#release time
		ver_dir = create_string_buffer(8)		#version directory
		scm = c_ubyte()				#Station class mark
		mob_cai_rev = c_ubyte()		#CAI rev
		mob_model = c_ubyte()		#Mobile model
		mob_firm_rev = c_ushort()	#Firmware rev.
		slot_cycle_index = c_ubyte()#slot cycle index
		voc_maj = c_ubyte()			#Vocoder major version
		voc_min = c_ubyte()			#Vocoder minor version
		bOK = self.qdll.QLIB_DIAG_VERNO_F  ( self.g_hResourceContext, comp_date, comp_time, rel_date, rel_time, ver_dir, \
			byref(scm), byref(mob_cai_rev), byref(mob_model), byref(mob_firm_rev), byref(slot_cycle_index), \
			byref(voc_maj), byref(voc_min))  

		if (bool(bOK) == True):
			print("Mobile version report:")
			#print("Compile Date: {0}".format(comp_date.value))
			#print("Compile Time: {0}".format(comp_time.value))
			#print("Release Date: {0}".format(rel_date.value))
			#print("Release Time: {0}".format(rel_time.value))
			#print("Version Dir: {0}".format(ver_dir.value))
			#print("Station Class Mark: {0}".format(scm.value))
			#print("CAI Rev: {0}".format(mob_cai_rev.value))
			#print("Mobile Model: {0}".format(mob_model.value))
			#print("Firmware Rev.: {0}".format(mob_firm_rev.value))
			#print("Slot Cycle Index: {0}".format(slot_cycle_index.value))
			#print("Vocoder major version: {0}".format(voc_maj.value))
			#print("Vocoder minor version: {0}".format(voc_min.value))
		else:
			print("Mobile version fail")

		#Get extended version info
		_iMSM_HW_Version = c_ulong(0)
		_iMobModel = c_ulong(0)
		_sMobSwRev = create_string_buffer(512)
		_sModelStr = create_string_buffer(512)
		bOK = self.qdll.QLIB_DIAG_EXT_BUILD_ID_F( self.g_hResourceContext, byref(_iMSM_HW_Version),
			byref(_iMobModel), _sMobSwRev, _sModelStr )

		if (bool(bOK) == True):
			print("Ext MSM HW Version: {0}".format(hex(_iMSM_HW_Version.value)))
			print("Ext Mobile Model: {0}".format(hex(_iMobModel.value)))
			print("Ext Mobile Mobile SW Rev: {0}".format(_sMobSwRev.value))
			print("Ext Model ID: {0}".format(_sModelStr.value))
		else:
			print("Extended Mobile version fail")
	
	def set_online_mode(self):
		# Set online mode
		bOK = self.qdll.QLIB_DIAG_CONTROL_F(self.g_hResourceContext, MODE_ONLINE_F)
		print("change to Online mode: {0}".format(pass_dict[bool(bOK)]))
	
	def set_FTM_mode(self):
		# Set FTM mode
		bOK = self.qdll.QLIB_DIAG_CONTROL_F(self.g_hResourceContext, MODE_FTM_F)
		print("change to FTM mode: {0}".format(pass_dict[bool(bOK)]))
		bFTMMode = c_ubyte()
		bOK = self.qdll.QLIB_IsFTM_Mode(self.g_hResourceContext, byref(bFTMMode))
		if (bool(bOK) == True):
			print("Is FTM Mode: {0}".format(truth_dict[bool(bFTMMode)]))
		else:
			print("Is FTM Mode function fail")
		# Set Calibration State for latest device
		self.set_calibration_state()
	
	def set_calibration_state(self):
		# Set Calibration state for latest device
		bOK = self.qdll.QLIB_FTM_SET_CALIBRATION_STATE(self.g_hResourceContext,1)   

	
	def set_band(self, eModeId, eNewMode):	
		"""
			Set technology/band
			eModeId: technology  
			eNewMode: band
		"""
		bOK = self.qdll.QLIB_FTM_SET_MODE_ID(self.g_hResourceContext, eModeId)  
		if (bool(bOK) == False): 
			print("Set FTM tech {0}: {1}".format(eModeId, pass_dict[bool(bOK)]))
		bOK = self.qdll.QLIB_FTM_SET_MODE(self.g_hResourceContext, eNewMode)
		if (bool(bOK) == False): 
			print("Set Band mode {0}: {1}".format(eNewMode, pass_dict[bool(bOK)]))
	
	def set_channel(self, iChannel):
		bOK = self.qdll.QLIB_FTM_SET_CHAN(self.g_hResourceContext,iChannel)
		if (bool(bOK) == False): 
			print("Set UL channel {0}: {1}".format(iChannel, pass_dict[bool(bOK)]))
		
	def set_Tx_ON(self):
		#Set Tx ON
		bOK = self.qdll.QLIB_FTM_SET_TX_ON( self.g_hResourceContext)
		if (bool(bOK) == False): 
			print("Set Tx ON: {0}".format(pass_dict[bool(bOK)]))
		
	def set_waveform(self):
		# Set WCDMA waveform
		if (bSet_WCDMA_Waveform == 1):
			bSelectCW = 0 	# Set 0 for de-select CW 
			bOK = self.qdll.QLIB_FTM_CDMA_CW_WAVEFORM(self.g_hResourceContext,bSelectCW)
			if (bool(bOK) == False): 
				print("Set WCDMA waveform: {0}".format(pass_dict[bool(bOK)]))
		
	def set_PA_range(self, iPArange):
		# Set PA range
		bOK = self.qdll.QLIB_FTM_SET_PA_RANGE(self.g_hResourceContext, iPArange)  
		if (bool(bOK) == False): 
			print("Set PA range {0}: {1}".format(iPArange, pass_dict[bool(bOK)]))
	
	def set_PDM(self, iPDMvalue):
		"""
		WCDMA mode values
		2 - Tx AGC Adjust PDM
		4 - Trk Lo Adjust PDM

		GSM mode values
		0 - Trk Lo Adjust PDM

		CDMA mode values
		2 - Tx AGC Adjust PDM
		4 - Trk Lo Adjust PDM
		"""
		iPDMtype = 2	#Tx AGC Adj PDM
		#iPDMvalue = 210	# 6285 Max:255
		bOK = self.qdll.QLIB_FTM_SET_PDM(self.g_hResourceContext, iPDMtype, iPDMvalue)  
		if (bool(bOK) == False): 
			print("Set Tx PDM value {0}: {1}".format(iPDMvalue, pass_dict[bool(bOK)]))

	def set_PA_BIAS_override(self, iOnOff):
		"""
			need to test
			seems iOnOff = 1/0
		"""
		bOK = self.qdll.QLIB_FTM_SET_SMPS_PA_BIAS_OVERRIDE(self.g_hResourceContext, iOnOff)  
		if (bool(bOK) == False): 
			print("Set PA BIAS override: {0}".format(pass_dict[bool(bOK)]))
		
	def set_PA_BIAS_value(self, iPA_Bias_Value):
		"""
			need to test
		"""
		bOK = self.qdll.QLIB_FTM_SET_SMPS_PA_BIAS_VAL(self.g_hResourceContext, iPA_Bias_Value)
		if (bool(bOK) == False): 
			print("Set PA BIAs value {0}: {1}".format(iPA_Bias_Value, pass_dict[bool(bOK)]))

	def set_Tx_off(self):
		bOK = self.qdll.QLIB_FTM_SET_TX_OFF( self.g_hResourceContext)
		if (bool(bOK) == False): 
			print("Set Tx OFF: {0}".format(pass_dict[bool(bOK)]))
	
	def set_LTE_Tx_BW(self, BW=5):
		"""
			Set LTE Tx BW
		"""
		if BW == 1:
			self.qBW = RFCOM_BW_LTE_1P4MHz
		elif BW == 3:
			self.qBW = RFCOM_BW_LTE_3MHz
		elif BW == 5:
			self.qBW = RFCOM_BW_LTE_5MHz
		elif BW == 10:
			self.qBW = RFCOM_BW_LTE_10MHz
		elif BW == 15:
			self.qBW = RFCOM_BW_LTE_15MHz
		elif BW == 20:
			self.qBW = RFCOM_BW_LTE_20MHz
		else:
			self.qBW = RFCOM_BW_LTE_5MHz	# Set 5MHz as default
			print("Wrong Tx BW input: {0}MHz, set BW as 5MHz".format(BW))
		bOK = self.qdll.QLIB_FTM_LTE_SET_TX_BANDWIDTH( self.g_hResourceContext, self.qBW)
		if (bool(bOK) == False): 
			print("Set Tx BW {0}MHz: {1}".format(BW, pass_dict[bool(bOK)]))
	
	def set_LTE_Tx_QPSK(self):
		# Set Tx Modulation to QPSK
		# Need to find QMSL doc
		bOK = self.qdll.QLIB_FTM_LTE_SET_TX_MODULATION_TYPE(self.g_hResourceContext,0) #0-QPSK, 1-16QAM, 2-64QAM
		#bOK = True
		if (bool(bOK) == False): 
			print("Set Tx Modulation: {0}".format(pass_dict[bool(bOK)]))
			
	def set_LTE_Rx_BW(self, BW=5):
		"""
			Set LTE Rx BW
		"""
		if BW == 1:
			self.qBW = RFCOM_BW_LTE_1P4MHz
		elif BW == 3:
			self.qBW = RFCOM_BW_LTE_3MHz
		elif BW == 5:
			self.qBW = RFCOM_BW_LTE_5MHz
		elif BW == 10:
			self.qBW = RFCOM_BW_LTE_10MHz
		elif BW == 15:
			self.qBW = RFCOM_BW_LTE_15MHz
		elif BW == 20:
			self.qBW = RFCOM_BW_LTE_20MHz
		else:
			self.qBW = RFCOM_BW_LTE_5MHz	# Set 5MHz as default
			print("Wrong Rx BW input: {0}MHz, set BW as 5MHz".format(BW))
		bOK = self.qdll.QLIB_FTM_LTE_SET_RX_BANDWIDTH( self.g_hResourceContext, self.qBW)
		if (bool(bOK) == False): 
			print("Set Rx BW {0}MHz: {1}".format(BW, pass_dict[bool(bOK)]))
	
	def set_LTE_Tx_waveform(self):
		"""
			Set LTE Tx waveform to Full RB PUSCH
		"""
		fRB = None
		if self.qBW == RFCOM_BW_LTE_1P4MHz:
			fRB = 6
		elif self.qBW == RFCOM_BW_LTE_3MHz:
			fRB = 15
		elif self.qBW == RFCOM_BW_LTE_5MHz:
			fRB = 25
		elif self.qBW == RFCOM_BW_LTE_10MHz:
			fRB = 50
		elif self.qBW == RFCOM_BW_LTE_15MHz:
			fRB = 75
		elif self.qBW == RFCOM_BW_LTE_20MHz:
			fRB = 100
		iTxWaveform = 1	# 0-CW, 1- PUSCH, 2- PUCCH, 3 - PRACH, 4 - SRS, 5 - UpPTS 
		inumRBsPUSCH = fRB
		inumRBsPUCCH = 0
		iPUSCHStartRBIndex = 0
		bOK = self.qdll.QLIB_FTM_LTE_SET_TX_WAVEFORM( self.g_hResourceContext, iTxWaveform, inumRBsPUSCH, inumRBsPUCCH, iPUSCHStartRBIndex)
		if (bool(bOK) == False): 
			print("Set Tx waveform: {0}".format(pass_dict[bool(bOK)]))
	
	def set_LTE_PDM(self, iTxGainIndex):
		"""
			LTE Tx PDM function is different with WCDMA
		"""
		bOK = self.qdll.QLIB_FTM_SET_TX_GAIN_INDEX(self.g_hResourceContext, iTxGainIndex)
		if (bool(bOK) == False): 
			print("Set Tx PDM value {0}: {1}".format(iTxGainIndex, pass_dict[bool(bOK)]))
	
	def disconnect(self):
		self.qdll.QLIB_DisconnectServer( self.g_hResourceContext )

	def set_GSM_Tx_burst(self):
		"""
			Set GSM Tx burst parameters (fixed)
			According to QCOM reference, it is "Set Tx Burst".
			But it may change to "Set Tx Continue" depends on tuning experience
		"""
		iSlotNum = 0
		iDataSource = FTM_GSM_TX_DATA_SOURCE_PSDRND
		iTSCindex = 5
		iNumBursts = 0
		bIsInfiniteDuration = 1
		bOK = self.qdll.QLIB_FTM_SET_TRANSMIT_BURST(self.g_hResourceContext, iSlotNum, iDataSource, iTSCindex, iNumBursts, bIsInfiniteDuration)  
		if (bool(bOK) == False): 
			print("Set GSM Tx Burst: {0}".format(pass_dict[bool(bOK)]))
	
	def set_TCXO_Adj_PDM(self, iPDMvalue = 0):
		"""
			For GSM tuning
			Set TCXO Adj PDM to 0
		"""
		iPDMtype = 0	#GSM mode 0: Trk Lo Adjust PDM
		iPDMvalue = 0	#Set TXCO Adj PDM to 0
		bOK = self.qdll.QLIB_FTM_SET_PDM_signed( self.g_hResourceContext, iPDMtype, iPDMvalue)
		if (bool(bOK) == False): 
			print("Set GSM TCXO Adj PDM {0}: {1}".format(iPDMvalue, pass_dict[bool(bOK)]))
			
	def set_GSM_Linear_PA_range(self, iPaRange = 0):
		"""
			Set GSM Linear PA range
			Slot: 0
			Range: 0
		"""
		iSlotNum = 0
		bOK = self.qdll.QLIB_FTM_SET_GSM_LINEAR_PA_RANGE( self.g_hResourceContext, iSlotNum, iPaRange)
		if (bool(bOK) == False): 
			print("Set GSM Linear PA range: {0}".format(pass_dict[bool(bOK)]))
	
	def set_GSM_Linear_RGI(self, iRgiIndex = 31):
		"""
			Set GSM Linear RGI
			For tuning, it sets to 31 by default
		"""
		iSlotNum = 0
		iModType = 1	#GSM
		bOK = self.qdll.QLIB_FTM_GSM_SET_LINEAR_RGI(self.g_hResourceContext, iSlotNum, iRgiIndex, iModType)
		if (bool(bOK) == False): 
			print("Set GSM Linear RGI {0}: {1}".format(iRgiIndex, pass_dict[bool(bOK)]))

	
if __name__ == "__main__":
	
	phone = QCOM_phone()
	
	phone.initial_QMSL(bUseQPST)
	pl = phone.get_phone_port_list()
	for i in pl: print(i)
	
	"""
	phone.connect_phone(Phone_Com_Port)
	
	phone.set_online_mode()
	
	phone.set_FTM_mode()
	
	#set mode/band
	#eModeId = FTM_MODE_ID_WCDMA
	#eNewMode = PHONE_MODE_WCDMA_IMT
	eModeId = FTM_MODE_ID_LTE
	eNewMode = PHONE_MODE_LTE_B7
	phone.set_band(eModeId, eNewMode)
	
	# Set LTE BW
	phone.set_LTE_Tx_BW(5)
	phone.set_LTE_Rx_BW(5)
	
	#Set channel
	#iChannel = WCDMA_B1_UL_ch[0]
	iChannel = LTE_B7_UL_ch_5M[1]
	phone.set_channel(iChannel)

	# Set Tx ON
	phone.set_Tx_ON()
	# Set LTE waveform
	phone.set_LTE_Tx_waveform()
	# Set PA range @ WCDMA_attributes
	phone.set_PA_range(iPArange_high)
	# Set PDM
	phone.set_LTE_PDM(PDM_init)
	
	time.sleep(10)

	#Set Tx OFF
	phone.set_Tx_off()
	
	# Disconnect phone
	phone.disconnect()
	"""
	

"""
QRCT log:

07:24:59  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:24:59  Helper_CalculateFrequency(PHONE_MODE_WCDMA_IMT,9612)
RxUHF = 2112.4, TxUHF = 1922.4
07:24:59  QLIB_FTM_SET_CHAN(9612)

07:24:59  Helper_IsValidULChannel(PHONE_MODE_WCDMA_IMT,9612)

07:25:30  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:30  Helper_CalculateFrequency(PHONE_MODE_WCDMA_IMT,9612)
RxUHF = 2112.4, TxUHF = 1922.4
07:25:30  QLIB_FTM_SET_CHAN(9612)

07:25:30  Helper_IsValidULChannel(PHONE_MODE_WCDMA_IMT,9612)

07:25:34  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:34  QLIB_FTM_CDMA_CW_WAVEFORM(0)

07:25:40  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:40  QLIB_FTM_SET_PA_RANGE(3)

07:25:48  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:48  QLIB_FTM_SET_PDM(TX_AGC_ADJUST,210)

07:25:52  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:52  QLIB_FTM_SET_TX_ON()

07:25:55  QLIB_FTM_SET_MODE_ID(WCDMA_RF)

07:25:55  QLIB_FTM_SET_TX_OFF()

"""
