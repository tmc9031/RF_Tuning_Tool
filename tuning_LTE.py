#!/usr/bin/env python
# For facilitate LTETx tuning
# William Chang

import msvcrt
import sys
from WCDMA_attributes import *
from QCOM import *
from Agilent8960 import *
from Anritsu8820C import *

ON_dict = {True:"ON",False:"OFF"}

def main():
	
	# variables
	test_band = "B7"
	UL_ch = LTE_Band_UL_ch_map_5M[test_band][1]
	PDM = PDM_init
	SMPS_ON = SMPS_ON_init	#SMPS ON/OFF
	SMPS = SMPS_init		#SMPS value
	txp = None
	aclr = None
	tx_on_flag = 0			#ON(1)/OFF(0)
	PArange = iPArange_high	#set to high gain mode as default
	
	# Set default band at begining
	if len(sys.argv) == 2:
		test_band = sys.argv[1].upper()
		if (test_band not in LTE_Band_UL_ch_map_5M):
			print("usage: python {0} {1}".format(sys.argv[0], LTE_Band_UL_ch_map_5M.keys()))
			exit()
	else:
		print("usage: python {0} {1}".format(sys.argv[0], LTE_Band_UL_ch_map_5M.keys()))
		exit()
	
	UL_ch = LTE_Band_UL_ch_map_5M[test_band][1]
	
	# Set PA range
	if (test_band in PA_range_map):
		PArange = PA_range_map[test_band][0]
	else:
		PArange = iPArange_high
	
	# initial instrument and distinguish Agilent and Anritsu
	gpib_addr = "GPIB::{0}".format(Instrument_GPIB)
	callbox = instrument(gpib_addr)
	s = callbox.ask("*IDN?")
	print(s)
	callbox.close()
	callbox = None
	if "ANRITSU" in s:
		callbox = Anritsu8820C(gpib_addr)
	else:
		#callbox = Agilent8960(gpib_addr)
		print("Only support Anrtisu 8820C for LTE tuning")
		exit()
	
	callbox.timeout = 10
	
	#switch Anritsu to LTE mode
	if (callbox.switch_to_LTE() == 1):
		print("switch format fail")
		exit()
	#preset instrument
	callbox.preset()
	callbox.update_path_loss()
	# Set FDD test mode
	callbox.set_FDD_test_mode()
	# Set UL channel
	callbox.set_FDD_UL_channel(UL_ch)
	# Setup TxP and ACLR setting
	callbox.set_LTE_BW()		# Set BW to 5MHz (default)
	callbox.set_LTE_TXP_ACLR()	# Set LTE Txp ACLR 
	
	# initial phone
	phone = QCOM_phone()
	phone.initial_QMSL(bUseQPST)
	Phone_Com_Port_c = c_int(Phone_Com_Port)
	phone.connect_phone(Phone_Com_Port_c)
	phone.set_online_mode()
	phone.set_FTM_mode()
	# Set band/mode
	eModeId = FTM_MODE_ID_LTE
	eNewMode = LTE_Band_QMSL_map[test_band]
	phone.set_band(eModeId, eNewMode)
	# Set LTE BW -> fixed at 5MHz
	phone.set_LTE_Tx_BW(5)
	phone.set_LTE_Rx_BW(5)
	# Set channel
	phone.set_channel(UL_ch)
	# Set Tx modulation QPSK
	phone.set_LTE_Tx_QPSK()
	# Set Tx ON
	phone.set_Tx_ON()
	tx_on_flag = 1
	# Set LTE waveform
	phone.set_LTE_Tx_waveform()
	# Set PA range @ WCDMA_attributes
	phone.set_PA_range(PArange)
	# Set PDM
	phone.set_LTE_PDM(PDM_init)
	# Set SMPS
	set_SMPS(phone, SMPS_ON, SMPS)
	
	# measure one time
	(txp, aclr) = measure(callbox)
	
	#print control key, title, and result
	print_command()
	print_title()
	print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
	
	
	while True:
		
		chr = msvcrt.getch()
		#print(chr)
		if(chr in b'Qq'):
			print("Quit")
			break
		elif (chr in b'Aa\r'):	# enter to measure again
			#measure
			#print("measure")
			(txp, aclr) = measure(callbox)
			print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
		elif(chr in b'Ll'):	#Low gain mode
			if (test_band in PA_range_map):
				PArange = PA_range_map[test_band][1]
			else:
				PArange = iPArange_low
			#PArange = iPArange_low	#set to low gain mode
			PDM = PDM_low
			SMPS = SMPS_low
			#print("{0}, {1}".format(PArange, SMPS))
			phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
			phone.set_LTE_PDM(PDM)	# Set PDM
			# Set SMPS
			set_SMPS(phone, SMPS_ON, SMPS)
			callbox.set_UL_power_FTM(-20)		# Set 8960 UL power
			(txp, aclr) = measure(callbox)
			print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
		elif(chr in b'Hh'):
			if (test_band in PA_range_map):
				PArange = PA_range_map[test_band][0]
			else:
				PArange = iPArange_high
			#PArange = iPArange_high	#set to low gain mode
			PDM = PDM_init
			SMPS = SMPS_init
			callbox.set_UL_power_FTM(23)	#set 8960 UL power
			#print("{0}, {1}".format(PArange, SMPS))
			phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
			phone.set_LTE_PDM(PDM)	# Set PDM
			# Set SMPS
			set_SMPS(phone, SMPS_ON, SMPS)
			(txp, aclr) = measure(callbox)
			print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
		elif(chr in b'Oo'):
			tx_on_flag = not tx_on_flag
			if tx_on_flag:
				phone.set_Tx_ON()
				print("Tx: ON")
				tx_on_flag = 1
				phone.set_LTE_Tx_waveform()	# Set waveform
				phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
				phone.set_LTE_PDM(PDM)	# Set PDM
				# Set SMPS
				set_SMPS(phone, SMPS_ON, SMPS)
				(txp, aclr) = measure(callbox)
				print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
			else:
				phone.set_Tx_off()
				print("Tx: OFF")
		elif(chr in b'Ss'):
			phone.set_Tx_off()
			tx_on_flag = 0
			if (test_band in PA_range_map):
				PArange = PA_range_map[test_band][0]
			else:
				PA_range = iPArange_high
			PDM = PDM_init
			SMPS = SMPS_init
			callbox.set_UL_power_FTM(23)	#set 8960 UL power
			print_title()
			for UL_ch in LTE_Band_UL_ch_map_5M[test_band]:		# Set ch to new band Mid ch
				callbox.set_FDD_UL_channel(UL_ch)		# Set 8960 to new channel
				# Set LTE BW -> fixed at 5MHz
				phone.set_LTE_Tx_BW(5)
				phone.set_LTE_Rx_BW(5)
				phone.set_channel(UL_ch)				# Set phone to new channel
				phone.set_LTE_Tx_QPSK()	# Set Tx modulation QPSK
				phone.set_Tx_ON()	# Set Tx ON
				tx_on_flag = 1
				phone.set_LTE_Tx_waveform()	# Set waveform
				phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
				phone.set_LTE_PDM(PDM)	# Set PDM
				# Set SMPS
				set_SMPS(phone, SMPS_ON, SMPS)
				
				txp1 = None		# store txp > TARGET_PWR
				aclr1 = None
				PDM1 = None
				txp2 = None		# store txp < TARGET_PWR
				alcr2 = None
				PDM2 = None
				(txp, aclr) = measure(callbox)
				if (txp > TARGET_PWR):
					while (txp > TARGET_PWR):
						txp1 = txp
						aclr1 = aclr
						PDM1 = PDM
						if (PDM>PDM_min):
							PDM -= 1
						else: break
						phone.set_LTE_PDM(PDM)
						(txp, aclr) = measure(callbox)
						txp2 = txp
						aclr2 = aclr
						PDM2 = PDM
				else:
					while (txp < TARGET_PWR):
						txp2 = txp
						aclr2 = aclr
						PDM2 = PDM
						if (PDM>PDM_min):
							PDM += 1
						else: break
						phone.set_LTE_PDM(PDM)
						(txp, aclr) = measure(callbox)
						txp1 = txp
						aclr1 = aclr
						PDM1 = PDM
				print_result(UL_ch, txp1, PDM1, aclr1, PArange, SMPS_ON, SMPS)
				print_result(UL_ch, txp2, PDM2, aclr2, PArange, SMPS_ON, SMPS)
		elif(chr == b'\xe0'):
			chr = msvcrt.getch()
			#print(chr)
			if (chr in b'Hh'):
				# PDM+1
				#print("UP key")
				if (PDM<PDM_max):
					PDM +=1
				#print("PDM: {0}".format(PDM))
				phone.set_LTE_PDM(PDM)
				(txp, aclr) = measure(callbox)
				print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
			elif (chr in b'Pp'):
				#PDM-1
				#print("Down key")
				if (PDM>PDM_min):
					PDM -=1
				phone.set_LTE_PDM(PDM)
				(txp, aclr) = measure(callbox)
				print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)	
			elif (chr in b'Kk'):
				#-ch
				#print("Left key")
				i = LTE_Band_UL_ch_map_5M[test_band].index(UL_ch)
				if (i>0):
					i -= 1
					UL_ch = LTE_Band_UL_ch_map_5M[test_band][i]
				#print(UL_ch)
				phone.set_Tx_off()	# Set Tx OFF
				tx_on_flag = 0
				phone.set_band(eModeId, eNewMode)		# eModeId is always LTE
				# Set LTE BW -> fixed at 5MHz
				phone.set_LTE_Tx_BW(5)
				phone.set_LTE_Rx_BW(5)
				callbox.set_FDD_UL_channel(UL_ch)		# Set 8960 to new channel
				phone.set_channel(UL_ch)				# Set phone to new channel
				phone.set_LTE_Tx_QPSK()	# Set Tx modulation QPSK
				phone.set_Tx_ON()	# Set Tx ON
				tx_on_flag = 1
				phone.set_LTE_Tx_waveform()	# Set waveform
				phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
				phone.set_LTE_PDM(PDM)	# Set PDM
				# Set SMPS
				set_SMPS(phone, SMPS_ON, SMPS)
				(txp, aclr) = measure(callbox)
				print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
			elif (chr in b'Mm'):
				#+ch
				#print("Right key")
				i = LTE_Band_UL_ch_map_5M[test_band].index(UL_ch)
				if (i<2):
					i += 1
					UL_ch = LTE_Band_UL_ch_map_5M[test_band][i]
				phone.set_Tx_off()	# Set Tx OFF
				tx_on_flag = 0
				phone.set_band(eModeId, eNewMode)		# eModeId is always LTE
				# Set LTE BW -> fixed at 5MHz
				phone.set_LTE_Tx_BW(5)
				phone.set_LTE_Rx_BW(5)
				callbox.set_FDD_UL_channel(UL_ch)		# Set 8960 to new channel
				phone.set_channel(UL_ch)				# Set phone to new channel
				phone.set_LTE_Tx_QPSK()	# Set Tx modulation QPSK
				phone.set_Tx_ON()	# Set Tx ON
				tx_on_flag = 1
				phone.set_LTE_Tx_waveform()	# Set waveform
				phone.set_PA_range(PArange)	# Set PA range @ WCDMA_attributes
				phone.set_LTE_PDM(PDM)	# Set PDM
				# Set SMPS
				set_SMPS(phone, SMPS_ON, SMPS)
				(txp, aclr) = measure(callbox)
				print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS)
		else:
			print_command()
			print_title()
			
	#Set Tx OFF
	phone.set_Tx_off()
	
	# Disconnect phone
	phone.disconnect()
	callbox.close()
	exit()		
	
def print_title():
	#print title & result
	print("{0:7}, {1:8}, {2:4}, {3:7}, {4:7}, {5:7}, {6:7}, {7:7}, {8:7}".format("channel", "Tx Power", "PDM", "UTRA-1", "UTRA+1", "EUTRA-1", "EURTA+1", "PArange", "SMPS"))

def print_result(UL_ch, txp, PDM, aclr, PArange, SMPS_ON, SMPS):
	print("{0:^7d}, {1:^8,.2f}, {2:4}, {3:7,.2f}, {4:7,.2f}, {5:7,.2f}, {6:7,.2f}, PAr:{7:3}, {8:3}:{9:3d}".format(UL_ch, txp, PDM, aclr[2], aclr[3], aclr[0], aclr[1], PArange, ON_dict[bool(SMPS_ON)], SMPS))

def print_command():
	print("----------------------------------------------------------")
	print("[^]+PDM  [v]-PDM  [<]-ch  [>]+ch")
	print("[L]GM    [H]GM  me[A]sure")
	print("[S]weep  [O]NOFF  [Q]uit")
	print("----------------------------------------------------------")
	
def measure(callbox):
	#callbox.init_TXP_ACLR()	#start channel power & ACLR measurement
	#time.sleep(0.1)	#wait for stable reading
	callbox.init_LTE_TXP_ACLR()	#start channel power & ACLR measurement again
	#read tx power
	txp = callbox.read_LTE_TXP()
	#read ACLR
	aclr = callbox.read_LTE_ACLR()
	return (txp, aclr)

def set_SMPS(phone, SMPS_ON, SMPS_value):
	phone.set_PA_BIAS_override(SMPS_ON)	# Set SMPS override ON
	phone.set_PA_BIAS_value(SMPS_value)

main()
