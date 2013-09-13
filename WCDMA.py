#!/usr/bin/env python
# For Agilent8960 WCDMA measurement
# Using PyVisa and Python 2.7.5
# William Chang

from visa import *
import time
import sys
from decimal import *
from WCDMA_attributes import *
from Agilent8960 import *
from Anritsu8820C import *

def main():
	if len(sys.argv) == 3:
		test_item = sys.argv[1].lower()
		test_band = sys.argv[2].upper()
		if ((test_item not in ("txp", "sens")) or (test_band not in ("B1", "B2", "B4", "B5", "B8"))):
			print("usage: python {0} (txp/sens) (B1/B2/B4/B5/B8)".format(sys.argv[0]))
			exit()
	else:
		print("usage: python {0} (txp/sens) (B1/B2/B4/B5/B8)".format(sys.argv[0]))
		exit()
	
	"""
		initial instrument
	"""
	#get instrument and distinguish Agilent and Anritsu
	gpib_addr = "GPIB::{0}".format(Instrument_GPIB)
	callbox = instrument(gpib_addr)
	s = callbox.ask("*IDN?")
	print(s)
	callbox.close()
	callbox = None
	if "ANRITSU" in s:
		callbox = Anritsu8820C(gpib_addr)
	else:
		callbox = Agilent8960(gpib_addr)
	callbox.timeout = 10
	
	#switch to WCDMA mode
	if (callbox.switch_to_WCDMA() == 1):
		print("switch format fail")
		exit()

	#preset instrument
	callbox.preset()

	#set path loss
	callbox.update_path_loss()

	#set call parameters
	callbox.update_link_settings()
	#IMSI = '001010123456789'
	callbox.set_IMSI(IMSI)

	#set DL channel
	callbox.set_DL_channel(Band_DL_ch_map[test_band][1])
	print(Band_DL_ch_map[test_band][1])
	#set DL power
	callbox.set_DL_power(-70)

	#set Tx power to 0dBm
	callbox.set_UL_power(0)

	#setup call
	if (callbox.call_connected() == 1):
		callbox.setup_call(100)

	if(test_item == "txp"):
		callbox.sweep_LMH_Txp_ACLR(test_band)
	elif(test_item == "sens"):
		callbox.sweep_LMH_BER_search(test_band)
	
	callbox.close()
	
main()



