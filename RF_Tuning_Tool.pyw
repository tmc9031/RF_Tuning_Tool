#!/usr/bin/env python
"""
	To facilitate WCDMA/LTE Tx tuning with GUI
	
	 This file is part of RF_Tuning_Tool.

	:copyright: (c) 2013 by the A-mao Chang (maomaoto@gmail.com)
	:license: MIT, see COPYING for more details.

"""
import sys
import time
from PySide.QtCore import *
from PySide.QtGui import *
from WCDMA_attributes import *
from QCOM import *
from Agilent8960 import *
from Anritsu8820C import *

import mainGui

__appname__ = "RF Tuning Tool"

class MainDialog(QDialog, mainGui.Ui_mainDialog):
	
	# variables
	test_band = ""
	UL_ch = 0
	PDM = PDM_init
	SMPS_ON = SMPS_ON_init	#SMPS ON/OFF
	SMPS_value = SMPS_init		#SMPS value
	txp = None
	aclr = None
	tx_on_flag = 0			#ON(1)/OFF(0)
	PArange = iPArange_high	#set to high gain mode as default
	
	gpib_addr = ""
	callbox = None
	phone = None
	eModeId = None
	eNewMode = None
	
	# for tableWidget
	current_edit_row = -1
	
	def __init__(self, parent = None):
		super(MainDialog, self).__init__(parent)
		self.setupUi(self)
		
		# Setup instrument and phone
		self.setupInstrument()
		self.setupPhone()
		
		
		self.comboBoxTech.addItems(("LTE", "WCDMA", "GSM"))
		self.comboBoxTech.activated[unicode].connect(self.comboBoxTechSelected)
		self.comboBoxBand.activated[unicode].connect(self.comboBoxBandSelected)
		
		self.qlMessage.clear()
		self.print_message("<font color=red> Select LTE/WCDMA first, then select Band. </color>")
		
		self.spinBoxPDMStart.setRange(PDM_min, PDM_max)
		self.spinBoxPDMStart.setValue(PDM_start)
		self.spinBoxPDMEnd.setRange(PDM_min, PDM_max)
		self.spinBoxPDMEnd.setValue(PDM_end)
		self.btnStartSweep.clicked.connect(self.startSweep)
		
		self.btnHPM.clicked.connect(self.setHPM)
		self.btnLPM.clicked.connect(self.setLPM)
		self.btnTxOn.clicked.connect(self.setTxOn)
		self.btnTxOff.clicked.connect(self.setTxOff)
		self.btnPDMPlus.clicked.connect(self.increasePDM)
		self.btnPDMMinus.clicked.connect(self.decreasePDM)
		self.btnChPlus.clicked.connect(self.increaseChannel)
		self.btnChMinus.clicked.connect(self.decreaseChannel)
		
		self.tableWidget.customContextMenuRequested.connect(self.tableWidgetMenu)
		self.tableWidget.addAction(self.actionCopy)
		
		self.actionCopy.triggered.connect(self.copySelectCells)
		
	def setupInstrument(self):
		self.print_message("Setup Instrument")
		self.qlGPIB.setText(unicode(Instrument_GPIB))
		# initial instrument and distinguish Agilent and Anritsu
		self.gpib_addr = "GPIB::{0}".format(Instrument_GPIB)
		self.callbox = instrument(self.gpib_addr)
		s = self.callbox.ask("*IDN?")
		self.print_message(s)
		self.callbox.close()
		self.callbox = None
		if "ANRITSU" in s:
			self.callbox = Anritsu8820C(self.gpib_addr)
		else:
			self.callbox = Agilent8960(self.gpib_addr)
		
		self.callbox.timeout = 10
		
	
	def setupPhone(self):
		self.print_message("Setup Phone")
		self.qlCOM.setText(unicode(Phone_Com_Port))
		# initial phone
		self.phone = QCOM_phone()
		self.phone.initial_QMSL(bUseQPST)
		Phone_Com_Port_c = c_int(Phone_Com_Port)
		self.phone.connect_phone(Phone_Com_Port_c)
		self.phone.set_online_mode()
		self.phone.set_FTM_mode()
	
	def comboBoxTechSelected(self, tech):
		if tech == "LTE":
			self.comboBoxBand.clear()
			self.comboBoxBand.addItems(sorted(LTE_Band_QMSL_map.keys(), key=lambda x: int(x[1:])))
			self.qlBW.setText("5MHz")
		elif tech == "WCDMA":
			self.comboBoxBand.clear()
			self.comboBoxBand.addItems(sorted(Band_QMSL_map.keys(), key=lambda x: int(x[1:])))
			self.qlBW.setText("--")
		elif tech == "GSM":
			self.comboBoxBand.clear()
			self.comboBoxBand.addItems(sorted(GSM_Band_QMSL_map.keys()))
			self.qlBW.setText("--")
		else:
			QMessageBox.warning(self, "Error", "comboBoxTech Error")
		self.print_title()
	
	def comboBoxBandSelected(self, band):
		#print("Band selected, need to setup display and start first measurement")
		if self.comboBoxTech.currentText() == "LTE":
			# Set Variable values
			self.test_band = band
			self.UL_ch = LTE_Band_UL_ch_map_5M[self.test_band][1]
			
			# Set PA range
			if (self.test_band in PA_range_map):
				self.PArange = PA_range_map[self.test_band][0]
			else:
				self.PArange = iPArange_high
			self.btnHPM.setChecked(True)
			#switch Anritsu to LTE mode
			if (self.callbox.switch_to_LTE() == 1):
				self.print_message("<font color=red> Switch Instrument format fail.</color>")
				sys.exit()
			#preset instrument
			self.callbox.preset()
			self.callbox.update_path_loss()
			# Set FDD test mode
			self.callbox.set_FDD_test_mode()
			# Set UL channel
			self.callbox.set_FDD_UL_channel(self.UL_ch)
			self.displayChannel()
			# Setup TxP and ACLR setting
			self.callbox.set_LTE_BW()		# Set BW to 5MHz (default)
			self.callbox.set_LTE_TXP_ACLR()	# Set LTE Txp ACLR 
			
			# Phone setting
			self.eModeId = FTM_MODE_ID_LTE
			self.eNewMode = LTE_Band_QMSL_map[self.test_band]
			self.set_phone_LTE_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
			
		elif self.comboBoxTech.currentText() == "WCDMA":
			# Set Variable values
			self.test_band = band
			self.UL_ch = Band_UL_ch_map[self.test_band][1]
			# Set PA range
			if (self.test_band in PA_range_map):
				self.PArange = PA_range_map[self.test_band][0]
			else:
				self.PArange = iPArange_high
			self.btnHPM.setChecked(True)
			#switch Instrument to WCDMA mode
			if (self.callbox.switch_to_WCDMA() == 1):
				self.print_message("<font color=red> Switch Instrument format fail.</color>")
				sys.exit()
			#preset instrument
			self.callbox.preset()
			self.callbox.update_path_loss()
			# Set FDD test mode
			self.callbox.set_FDD_test_mode()
			# Set UL channel
			self.callbox.set_FDD_UL_channel(self.UL_ch)
			self.displayChannel()
			# Setup TxP and ACLR setting
			self.callbox.setup_channel_power_mea(Average_times, "OFF")	#Tx power measurement setting
			self.callbox.setup_ACLR_mea(count = Average_times)			#ACLR measurement setting
			self.callbox.set_UL_power_FTM(23)							#set 8960 UL power
			
			# Phone setting
			self.eModeId = FTM_MODE_ID_WCDMA
			self.eNewMode = Band_QMSL_map[self.test_band]
			self.set_phone_WCDMA_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
			
		elif self.comboBoxTech.currentText() == "GSM":
			"""
				For GSM, just scan all channel max power and show on table
				May need to deactive all other buttons 
			"""
			# Set variable values
			self.test_band = band
			self.UL_ch = GSM_Band_UL_ch_map[self.test_band][1]
			#preset instrument
			self.callbox.preset()
			self.callbox.update_path_loss()
			# Set FDD test mode
			self.callbox.set_FDD_test_mode()
			
			
		
		# measure one time
		self.measure()
		
		# print result
		#self.print_title()
		self.print_result()
	
	
	def startSweep(self):
		print("Start Sweep")
		ch_list = []
		if self.comboBoxTech.currentText() == "LTE":
			ch_list = LTE_Band_UL_ch_map_5M[self.test_band]
		elif self.comboBoxTech.currentText() == "WCDMA":
			ch_list = Band_UL_ch_map[self.test_band]
		
		PDM_start = 0
		PDM_end = 0
		if self.spinBoxPDMStart.value() > self.spinBoxPDMEnd.value():
			PDM_start = self.spinBoxPDMEnd.value()
			PDM_end = self.spinBoxPDMStart.value()
		else:
			PDM_start = self.spinBoxPDMStart.value()
			PDM_end = self.spinBoxPDMEnd.value()
		
		for ch in ch_list:
			self.UL_ch = ch
			self.phone.set_Tx_off()	# Set Tx OFF
			self.tx_on_flag = 0
			self.btnTxOff.setChecked(True)
			self.callbox.set_FDD_UL_channel(self.UL_ch)		# Set instrument to new channel
			if self.comboBoxTech.currentText() == "LTE":
				self.set_phone_LTE_on()
			elif self.comboBoxTech.currentText() == "WCDMA":
				self.set_phone_WCDMA_on()
			self.btnTxOn.setChecked(True)
			# Set SMPS
			self.set_SMPS()
			for PDM_sweep in range(PDM_start, PDM_end+1, 1):
				self.PDM = PDM_sweep
				if self.comboBoxTech.currentText() == "LTE":
					self.phone.set_LTE_PDM(self.PDM)
				elif self.comboBoxTech.currentText() == "WCDMA":
					self.phone.set_PDM(self.PDM)
				self.qlPDM.setText(unicode(self.PDM))
				self.measure()
				self.print_result()
		
	def setHPM(self):
		print("set HPM")
		
		#set to low gain mode
		if (self.test_band in PA_range_map):
			self.PArange = PA_range_map[self.test_band][0]
		else:
			self.PArange = iPArange_high
		self.PDM = PDM_init
		self.qlPDM.setText(unicode(self.PDM))
		self.SMPS_value = SMPS_init
		self.callbox.set_UL_power_FTM(23)	#set Instrument UL power
		if self.comboBoxTech.currentText() == "LTE":
			self.set_phone_LTE_on()
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.set_phone_WCDMA_on()
		# Set SMPS
		self.set_SMPS()
		self.measure()
		self.print_result()
		
		
	def setLPM(self):
		print("set LPM")
		
		if (self.test_band in PA_range_map):
			self.PArange = PA_range_map[self.test_band][1]
		else:
			self.PArange = iPArange_low
		#PArange = iPArange_low	#set to low gain mode
		self.PDM = PDM_low
		self.qlPDM.setText(unicode(self.PDM))
		self.SMPS_value = SMPS_low
		if self.comboBoxTech.currentText() == "LTE":
			self.set_phone_LTE_on()
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.set_phone_WCDMA_on()
		# Set SMPS
		self.set_SMPS()
		self.callbox.set_UL_power_FTM(-20)		# Set 8960 UL power
		self.measure()
		self.print_result()
		
		
	def setTxOn(self):
		self.print_message("set Tx ON")
		
		if self.comboBoxTech.currentText() == "LTE":
			self.set_phone_LTE_on()
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.set_phone_WCDMA_on()
		self.qlPDM.setText(unicode(self.PDM))
		# Set SMPS
		self.set_SMPS()
		self.measure()
		self.print_result()
		
		
	def setTxOff(self):
		self.print_message("set Tx OFF")
		
		self.phone.set_Tx_off()
		self.tx_on_flag = 0
		
		
	def increasePDM(self):
		print("increase PDM")
		
		if (self.PDM < PDM_max):
			self.PDM += 1
		if self.comboBoxTech.currentText() == "LTE":
			self.phone.set_LTE_PDM(self.PDM)
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.phone.set_PDM(self.PDM)
		self.qlPDM.setText(unicode(self.PDM))
		self.measure()
		self.print_result()
		
		
	def decreasePDM(self):
		print("decrease PDM")
		
		if (self.PDM > PDM_min):
			self.PDM -= 1
		if self.comboBoxTech.currentText() == "LTE":
			self.phone.set_LTE_PDM(self.PDM)
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.phone.set_PDM(self.PDM)
		self.qlPDM.setText(unicode(self.PDM))
		self.measure()
		self.print_result()
		
		
	def increaseChannel(self):
		print("increase channel")
		#self.print_result()
		
		if self.comboBoxTech.currentText() == "LTE":
			i = LTE_Band_UL_ch_map_5M[self.test_band].index(self.UL_ch)
			if (i<2):
				i += 1
				self.UL_ch = LTE_Band_UL_ch_map_5M[self.test_band][i]
			# Set Phone on again
			self.phone.set_Tx_off()	# Set Tx OFF
			self.tx_on_flag = 0
			self.btnTxOff.setChecked(True)
			self.callbox.set_FDD_UL_channel(self.UL_ch)		# Set instrument to new channel
			self.set_phone_LTE_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
		elif self.comboBoxTech.currentText() == "WCDMA":
			i = Band_UL_ch_map[self.test_band].index(self.UL_ch)
			if (i<2):
				i += 1
				self.UL_ch = Band_UL_ch_map[self.test_band][i]
			# Set Phone on again
			self.phone.set_Tx_off()	# Set Tx OFF
			self.tx_on_flag = 0
			self.btnTxOff.setChecked(True)
			self.callbox.set_FDD_UL_channel(self.UL_ch)		# Set instrument to new channel
			self.set_phone_WCDMA_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
		self.displayChannel()
		self.measure()
		self.print_result()
		
		
	def decreaseChannel(self):
		print("decrease channel")
		
		if self.comboBoxTech.currentText() == "LTE":
			i = LTE_Band_UL_ch_map_5M[self.test_band].index(self.UL_ch)
			if (i>0):
				i -= 1
				self.UL_ch = LTE_Band_UL_ch_map_5M[self.test_band][i]
			# Set Phone on again
			self.phone.set_Tx_off()	# Set Tx OFF
			self.tx_on_flag = 0
			self.btnTxOff.setChecked(True)
			self.callbox.set_FDD_UL_channel(self.UL_ch)		# Set instrument to new channel
			self.set_phone_LTE_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
		elif self.comboBoxTech.currentText() == "WCDMA":
			i = Band_UL_ch_map[self.test_band].index(self.UL_ch)
			if (i>0):
				i -= 1
				self.UL_ch = Band_UL_ch_map[self.test_band][i]
			# Set Phone on again
			self.phone.set_Tx_off()	# Set Tx OFF
			self.tx_on_flag = 0
			self.btnTxOff.setChecked(True)
			self.callbox.set_FDD_UL_channel(self.UL_ch)		# Set instrument to new channel
			self.set_phone_WCDMA_on()
			self.qlPDM.setText(unicode(self.PDM))
			# Set SMPS
			self.set_SMPS()
		self.displayChannel()
		self.measure()
		self.print_result()
		
		
	def set_SMPS(self):
		self.phone.set_PA_BIAS_override(self.SMPS_ON)	# Set SMPS override ON
		self.phone.set_PA_BIAS_value(self.SMPS_value)
		self.qlSMPS.setText(unicode(self.SMPS_value))
		
	def set_phone_LTE_on(self):
		print("seet_phone_lte_on")
		
		# Set band/mode
		self.phone.set_band(self.eModeId, self.eNewMode)
		# Set LTE BW -> fixed at 5MHz
		self.phone.set_LTE_Tx_BW()
		self.phone.set_LTE_Rx_BW()
		# Set channel
		self.phone.set_channel(self.UL_ch)
		# Set Tx modulation QPSK
		self.phone.set_LTE_Tx_QPSK()
		# Set Tx ON
		self.phone.set_Tx_ON()
		self.tx_on_flag = 1
		self.btnTxOn.setChecked(True)
		# Set LTE waveform
		self.phone.set_LTE_Tx_waveform()
		# Set PA range @ WCDMA_attributes
		self.phone.set_PA_range(self.PArange)
		# Set PDM
		self.phone.set_LTE_PDM(self.PDM)
		
		
	def set_phone_WCDMA_on(self):
		print("set phone wcdma on")
		
		# Set band/mode
		self.phone.set_band(self.eModeId, self.eNewMode)
		# Set channel
		self.phone.set_channel(self.UL_ch)
		# Set Tx ON
		self.phone.set_Tx_ON()
		self.tx_on_flag = 1
		self.btnTxOn.setChecked(True)
		# Set waveform
		self.phone.set_waveform()
		# Set PA range @ WCDMA_attributes
		self.phone.set_PA_range(self.PArange)
		# Set PDM
		self.phone.set_PDM(self.PDM)
		
	
	def measure(self):
		print("measure")
		
		if self.comboBoxTech.currentText() == "LTE":
			#start channel power & ACLR measurement again
			self.callbox.init_LTE_TXP_ACLR()
			#read tx power
			self.txp = self.callbox.read_LTE_TXP()
			#read ACLR
			self.aclr = self.callbox.read_LTE_ACLR()
		elif self.comboBoxTech.currentText() == "WCDMA":
			#start channel power & ACLR measurement again
			self.callbox.init_TXP_ACLR()	
			#read tx power
			self.txp = self.callbox.read_TXP()
			#read ACLR
			self.aclr = self.callbox.read_ACLR()
		
		
	def print_message(self, param):
		self.qlMessage.setText(unicode(param))
	
	def print_title(self):
		print("print title")
		#print title 
		if self.comboBoxTech.currentText() == "LTE":
			self.tableWidget.setHorizontalHeaderLabels(["channel", "Tx Power", "PDM", "Max curr", "min curr", "Current", "UTRA-1", "UTRA+1", "EUTRA-1", "EURTA+1"])
			#self.textBrowser.append("{0:7}, {1:8}, {2:4}, {3:7}, {4:7}, {5:7}, {6:7}, {7:7}, {8:7}".format("channel", "Tx Power", "PDM", "UTRA-1", "UTRA+1", "EUTRA-1", "EURTA+1", "PArange", "SMPS"))
		elif self.comboBoxTech.currentText() == "WCDMA":
			self.tableWidget.setHorizontalHeaderLabels(["channel", "Tx Power", "PDM", "Max curr", "min curr", "Current","-5MHz", "+5MHz", "", ""])
			#self.textBrowser.append("{0:8}, {1:8}, {2:4}, {3:6}, {4:6}, {5:7}, {6:7}".format("channel", "Tx Power", "PDM", "-5MHz", "+5MHz", "PArange", "SMPS"))
			
	def print_result(self):
		self.current_edit_row += 1
		
		if self.comboBoxTech.currentText() == "LTE":
			print("current row: {0}".format(self.current_edit_row))
			print("row count: {0}".format(self.tableWidget.rowCount()))
			if (self.current_edit_row == self.tableWidget.rowCount()):
				self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
			self.tableWidget.setCurrentCell(self.current_edit_row, 0)
			"""
			# for test only
			self.UL_ch = 24300
			self.txp = 23.4
			self.PDM = 90
			self.aclr = ["-41", "-40", "-43", "-42"]
			"""
			itemULCh = QTableWidgetItem(unicode(self.UL_ch))
			itemTxp = QTableWidgetItem("{0:.2f}".format(self.txp))
			itemPDM = QTableWidgetItem(unicode(self.PDM))
			itemAclrUTRAM = QTableWidgetItem("{0:.2f}".format(self.aclr[2]))
			itemAclrUTRAP = QTableWidgetItem("{0:.2f}".format(self.aclr[3]))
			itemAclrEUTRAM = QTableWidgetItem("{0:.2f}".format(self.aclr[0]))
			itemAclrEUTRAP = QTableWidgetItem("{0:.2f}".format(self.aclr[1]))
			
			self.tableWidget.setItem((self.current_edit_row), 0, itemULCh)
			self.tableWidget.setItem((self.current_edit_row), 1, itemTxp)
			self.tableWidget.setItem((self.current_edit_row), 2, itemPDM)
			self.tableWidget.setItem((self.current_edit_row), 6, itemAclrUTRAM)
			self.tableWidget.setItem((self.current_edit_row), 7, itemAclrUTRAP)
			self.tableWidget.setItem((self.current_edit_row), 8, itemAclrEUTRAM)
			self.tableWidget.setItem((self.current_edit_row), 9, itemAclrEUTRAP)
			
			
		elif self.comboBoxTech.currentText() == "WCDMA":
			print("current row: {0}".format(self.current_edit_row))
			print("row count: {0}".format(self.tableWidget.rowCount()))
			if (self.current_edit_row == self.tableWidget.rowCount()):
				self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
			self.tableWidget.setCurrentCell(self.current_edit_row, 0)
			"""
			# for test only
			self.UL_ch = 24300
			self.txp = 23.4
			self.PDM = 90
			self.aclr = ["-41", "-40", "-43", "-42"]
			"""
			itemULCh = QTableWidgetItem(unicode(self.UL_ch))
			itemTxp = QTableWidgetItem("{0:.2f}".format(self.txp))
			itemPDM = QTableWidgetItem(unicode(self.PDM))
			itemAclrUTRAM = QTableWidgetItem("{0:.2f}".format(self.aclr[0]))
			itemAclrUTRAP = QTableWidgetItem("{0:.2f}".format(self.aclr[1]))
			
			self.tableWidget.setItem((self.current_edit_row), 0, itemULCh)
			self.tableWidget.setItem((self.current_edit_row), 1, itemTxp)
			self.tableWidget.setItem((self.current_edit_row), 2, itemPDM)
			self.tableWidget.setItem((self.current_edit_row), 6, itemAclrUTRAM)
			self.tableWidget.setItem((self.current_edit_row), 7, itemAclrUTRAP)
	
	def displayChannel(self):
		if self.comboBoxTech.currentText() == "LTE":
			i = LTE_Band_UL_ch_map_5M[self.test_band].index(self.UL_ch)
			self.qlULch.setText(unicode(self.UL_ch))
			self.qlDLch.setText(unicode(LTE_Band_DL_ch_map_5M[self.test_band][i]))
		elif self.comboBoxTech.currentText() == "WCDMA":
			i = Band_UL_ch_map[self.test_band].index(self.UL_ch)
			self.qlULch.setText(unicode(self.UL_ch))
			self.qlDLch.setText(unicode(Band_DL_ch_map[self.test_band][i]))
	
	def copySelectCells(self):
		print("copy")
		print(self.tableWidget.selectedRanges())
		selectedRanges = self.tableWidget.selectedRanges()[0]
		print("Top row: {0}".format(selectedRanges.topRow()))
		print("Buttom row: {0}".format(selectedRanges.bottomRow()))
		print("Left column: {0}".format(selectedRanges.leftColumn()))
		print("Right column: {0}".format(selectedRanges.rightColumn()))
		print("Row count: {0}".format(selectedRanges.rowCount()))
		print("Column count: {0}".format(selectedRanges.columnCount()))
		copyString = unicode()
		for selectedRanges in self.tableWidget.selectedRanges():
			for row in range(selectedRanges.topRow(), selectedRanges.topRow() + selectedRanges.rowCount()):	
				print("row: {0}".format(row))
				for column in range(selectedRanges.leftColumn(), selectedRanges.leftColumn()+ selectedRanges.columnCount()):
					try:
						print("column: {0}".format(column))
						print("itme text: {0}".format(self.tableWidget.item(row, column).text()))
						print("itme text: {0}".format(self.tableWidget.item(row, column)))
						if column == selectedRanges.leftColumn()+ selectedRanges.columnCount() -1:
							copyString += "{0}".format(self.tableWidget.item(row, column).text())
						else:
							copyString += "{0}\t".format(self.tableWidget.item(row, column).text())
						#print(copyString)
					except AttributeError as e:
						copyString += "\t"
				copyString += "\n"
		print(copyString)
		QApplication.clipboard().setText(copyString)
		
	def tableWidgetMenu(self, pos):
		print("custom context menu requested: {0}".format(pos))
		menu = QMenu(self)
		menu.addAction(self.actionCopy)
		menu.exec_(self.tableWidget.mapToGlobal(pos))
	
	def closeEvent(self, event):
		print("closing")
		
		#Set Tx OFF
		self.phone.set_Tx_off()
		# Disconnect phone
		self.phone.disconnect()
		self.callbox.close()
		
		event.accept()
	
	def keyPressEvent(self, event):
		# Re-direct ESC key to closeEvent
		#print(event)
		if event.key() == Qt.Key_Escape:
			self.close()
		
def main():
	app = QApplication(sys.argv)
	form = MainDialog()
	form.show()
	app.exec_()

if __name__ == '__main__':
    main()
