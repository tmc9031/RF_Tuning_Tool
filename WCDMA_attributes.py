#!/usr/bin/env python
# for instrument/phone setting
# William Chang

#Instrument setting
Instrument_GPIB = 14		#GPIB
Average_times = 20		# average times for Txp and ACLR measurement
IMSI = '001010123456789'
path_loss = {700: -0.3, 1200: -0.3, 1700: -0.6, 2200: -0.6}		#initiate path loss table (using dict)
#Anritsu 8820C setting
Integrity = 1			# Integrity ON|OFF
#Phone settings
bUseQPST = 1			# bUseQPST = true to use QPST, FALSE to use QPHONEMS 
Phone_Com_Port = 3		# Phone COM port
bSet_WCDMA_Waveform = 0	# For GLU(MSM8974),  not to set WCDMA waveform
PDM_init = 88			# Start PDM (High gain mode default PDM) (RTR6285:210, WTR1605:90)
PDM_low = 50			# PDM for -20dBm (Low gain mode PDM) (RTR6285:140, WTR1605:60)
PDM_max = 255			# PDM Max (RTR6285:255, WTR1605:127)
PDM_min = 0
iPArange_high = 2			# for high gain mode (RTR6285:3, WTR1605:0)
iPArange_low = 3			# for low gain mode (RTR6285:0, WTR1605:3)
PA_range_map = dict(B7=(0,1), # for different Band-PA setting => Band=(HPM,LPM)
					B20=(0,3), 
					)
"""
	0 - R0 = 0, R1 = 0,
	1 - R0 = 1, R1 = 0,
	2 - R0 = 0, R1 = 1,
	3 - R0 = 1, R1 = 1
"""

SMPS_ON_init = 1	#SMPS ON(1)/OFF(0)
SMPS_init = 3400	#SMPS value (for High gain mode) (MSM8x25/RTR6285:380/511, MSM8x30/WTR1605:780, MSM8974/WTR1605:1000)
SMPS_low = 1000		#SMPS value for -20dBm (for Low gain mode) (MSM8x25/RTR6285:95, MSM8x30/WTR1605:230, MSM8974/WTR1605:1000)
# Tuning sweep
TARGET_PWR = 23.5
PDM_start = 80
PDM_end = 90


# WCDMA attributes
#channel list
WCDMA_B1_DL_ch = [10562, 10700, 10838]
WCDMA_B1_UL_ch = [9612, 9750, 9888]
WCDMA_B2_DL_ch = [9662, 9800,9938]
WCDMA_B2_UL_ch = [9262, 9400, 9538]
WCDMA_B4_DL_ch = [1537, 1675, 1738]
WCDMA_B4_UL_ch = [1312, 1450, 1513]
WCDMA_B5_DL_ch = [4357, 4400, 4458]
WCDMA_B5_UL_ch = [4132, 4175, 4233]
WCDMA_B8_DL_ch = [2937, 3013, 3088]
WCDMA_B8_UL_ch = [2712, 2788, 2863]
WCDMA_B9_DL_ch = [9237, 9312, 9387]
WCDMA_B9_UL_ch = [8762, 8837, 8912]
WCDMA_B19_DL_ch = [712, 738, 763]
WCDMA_B19_UL_ch = [312, 338, 363]

#band-channel mapping
Band_DL_ch_map = dict(B1=WCDMA_B1_DL_ch, B2=WCDMA_B2_DL_ch,
				B4=WCDMA_B4_DL_ch, B5=WCDMA_B5_DL_ch,
				B8=WCDMA_B8_DL_ch, B9=WCDMA_B9_DL_ch, B19=WCDMA_B19_DL_ch)
Band_UL_ch_map = dict(B1=WCDMA_B1_UL_ch, B2=WCDMA_B2_UL_ch,
				B4=WCDMA_B4_UL_ch, B5=WCDMA_B5_UL_ch,
				B8=WCDMA_B8_UL_ch, B9=WCDMA_B9_UL_ch, B19=WCDMA_B19_UL_ch)

# LTE attributes
# channel list
LTE_B1_DL_ch_5M = [25, 300, 575]
LTE_B1_UL_ch_5M = [18025, 18300, 18575]
LTE_B2_DL_ch_5M = [625, 900, 1175]
LTE_B2_UL_ch_5M = [18625, 18900, 19175]
LTE_B3_DL_ch_5M = [1225, 1575, 1925]
LTE_B3_UL_ch_5M = [19225, 19575, 19925]
LTE_B7_DL_ch_5M = [2775, 3100, 3425]
LTE_B7_UL_ch_5M = [20775, 21100, 21425]
LTE_B8_DL_ch_5M = [3475, 3625, 3775]
LTE_B8_UL_ch_5M = [21475, 21625, 21775]
LTE_B11_DL_ch_5M = [4775, 4850, 4925]
LTE_B11_UL_ch_5M = [22775, 22850, 22925]
LTE_B13_DL_ch_5M = [5205, 5230, 5255]
LTE_B13_UL_ch_5M = [23205, 23230, 23255]
LTE_B19_DL_ch_5M = [6025, 6075, 6125]
LTE_B19_UL_ch_5M = [24025, 24075, 24125]
LTE_B20_DL_ch_5M = [6175, 6300, 6425]
LTE_B20_UL_ch_5M = [24175, 24300, 24425]
LTE_B21_DL_ch_5M = [6475, 6525, 6575]
LTE_B21_UL_ch_5M = [24475, 24525, 24575]
LTE_B26_DL_ch_5M = [8715, 8865, 9015]
LTE_B26_UL_ch_5M = [26715, 26865, 27015]
LTE_B28A_DL_ch_5M = [9235, 9335, 9434]
LTE_B28A_UL_ch_5M = [27235, 27335, 27434]
LTE_B28B_DL_ch_5M = [9435, 9535, 9635]
LTE_B28B_UL_ch_5M = [27435, 27535, 27635]

# band-channel mapping
LTE_Band_DL_ch_map_5M = dict(B1=LTE_B1_DL_ch_5M, B2=LTE_B2_DL_ch_5M, B3=LTE_B3_DL_ch_5M, B7=LTE_B7_DL_ch_5M,
						B8=LTE_B8_DL_ch_5M, B11=LTE_B11_DL_ch_5M, B13=LTE_B13_DL_ch_5M, 
						B19=LTE_B19_DL_ch_5M, B20=LTE_B20_DL_ch_5M, B21=LTE_B21_DL_ch_5M, 
						B26=LTE_B26_DL_ch_5M, B281=LTE_B28A_DL_ch_5M, B282=LTE_B28B_DL_ch_5M)
LTE_Band_UL_ch_map_5M = dict(B1=LTE_B1_UL_ch_5M, B2=LTE_B2_UL_ch_5M, B3=LTE_B3_UL_ch_5M, B7=LTE_B7_UL_ch_5M,
						B8=LTE_B8_UL_ch_5M, B11=LTE_B11_UL_ch_5M, B13=LTE_B13_UL_ch_5M, 
						B19=LTE_B19_UL_ch_5M, B20=LTE_B20_UL_ch_5M, B21=LTE_B21_UL_ch_5M, 
						B26=LTE_B26_UL_ch_5M, B281=LTE_B28A_UL_ch_5M, B282=LTE_B28B_UL_ch_5M)
					

# Below is QMSL defined variable

# Definition of the COM port value that will be used to "auto detect" the COM port
QLIB_COM_AUTO_DETECT  = 0xFFFF

# Phone modes
MODE_OFFLINE_A_F = 0  #Go to offline analog
MODE_OFFLINE_D_F = 1  #Go to offline digital 
MODE_RESET_F = 2      #Reset. Only exit from offline 
MODE_FTM_F = 3        #FTM mode
MODE_ONLINE_F = 4     #Go to Online 
MODE_LPM_F = 5        #Low Power Mode (if supported)
MODE_POWER_OFF_F = 6  #Power off (if supported)
MODE_MAX_F = 7        #Last (and invalid) mode enum value

# Phone logging settings
LOG_NOTHING = 0x0000	# log nothing
LOG_C_HIGH_LEVEL_START = 0x0200	# High level C function start, indicates the begining of a high level C function, which
								# calls other low level C functions internal to the library
LOG_C_HIGH_LEVEL_STOP = 0x4000	# High level C function stop
LOG_IO = 0x0001		# data IO (data bytes)
LOG_FN = 0x0002		# function calls with parameters
LOG_RET = 0x0004	# function return data
LOG_INF = 0x0008	# general information (nice to know)--do not use this one, as
					# this space needs to be reserved for async messages
LOG_ASYNC = 0x0008	# asynchronous messages
LOG_ERR = 0x0010	# critical error information
LOG_IO_AHDLC = 0x0020	# HDLC IO tracing (data bytes)
LOG_FN_AHDLC = 0x0040	# HDLC layer function calls
LOG_RET_AHDLC = 0x0080	# HDLC function return data
LOG_INF_AHDLC = 0x0100	# HDLC general information
LOG_ERR_AHDLC = LOG_INF_AHDLC	# HDLC Error info merged with LOG_INF_AHDLC, to free up the log bit
LOG_IO_DEV = 0x0400	# device IO tracing (data bytes)
LOG_FN_DEV = 0x0800	# device layer function calls
LOG_RET_DEV = 0x1000	# device function return data
LOG_INF_DEV = 0x2000	# device general information
LOG_ERR_DEV = LOG_INF_DEV		# device error information, merged with LOG_INF_DEV to free up the log bit
LOG_DEFAULT	= (LOG_C_HIGH_LEVEL_START|LOG_C_HIGH_LEVEL_STOP|LOG_FN|LOG_IO|LOG_RET|LOG_ERR|LOG_ASYNC) #  default settings
LOG_ALL = 0xFFFF	# everything

# Set FTM Mode
FTM_MODE_ID_CDMA_1X     = 0
FTM_MODE_ID_WCDMA       = 1
FTM_MODE_ID_GSM         = 2
FTM_MODE_ID_CDMA_1X_RX1 = 3
FTM_MODE_ID_BLUETOOTH   = 4
FTM_MODE_ID_CDMA_1X_CALL= 7
FTM_MODE_ID_LOGGING     = 9
FTM_MODE_ID_AGPS        = 10
FTM_MODE_ID_PMIC        = 11
FTM_MODE_GSM_BER        = 13
FTM_MODE_ID_AUDIO       = 14
FTM_MODE_ID_CAMERA      = 15
FTM_MODE_WCDMA_BER      = 16
FTM_MODE_ID_GSM_EXTENDED_C = 17
FTM_MODE_CDMA_API_V2    = 18
FTM_MODE_ID_MF_C        = 19
FTM_MODE_RF_COMMON      = 20
FTM_MODE_WCDMA_RX1      = 21
FTM_MODE_ID_LTE        = 29	# LTE FTM Calibration
FTM_MODE_LTE_NS        = 30	# LTE FTM Non-Signaling
FTM_MODE_CDMA_C2        = 32
FTM_MODE_CDMA_C3        = 40
FTM_MODE_CDMA_C4        = 45
FTM_MODE_ID_PRODUCTION  = 0x8000
FTM_MODE_ID_LTM         = 0x8001	# LTM


# For FTM Mode/Band setting
PHONE_MODE_FM        = 1      #(FM)
PHONE_MODE_GPS       = 3      #(GPS)
PHONE_MODE_GPS_SINAD = 4      #(GPS SINAD)
PHONE_MODE_CDMA_800  = 5      #(CDMA 800)
PHONE_MODE_CDMA_1900 = 6      #(CDMA 1900)
PHONE_MODE_CDMA_1800 = 8      #(CDMA 1800)
PHONE_MODE_J_CDMA    = 14     #(JCDMA)
PHONE_MODE_CDMA_450  = 17     #(CDMA 450)
PHONE_MODE_CDMA_IMT  = 19     #(CDMA IMT)

PHONE_MODE_WCDMA_IMT   =9      #(WCDMA IMT, Band I)
PHONE_MODE_GSM_900     =10     #(GSM 900)
PHONE_MODE_GSM_1800    =11     #(GSM 1800)
PHONE_MODE_GSM_1900    =12     #(GSM 1900)
PHONE_MODE_WCDMA_1900A =15     #(WCDMA 1900 A, Band II Add)
PHONE_MODE_WCDMA_1900B =16     #(WCDMA 1900 B, Band II Gen)
PHONE_MODE_GSM_850     =18     #(GSM 850)
PHONE_MODE_WCDMA_800   =22     #(WCDMA 800, Band V Gen)
PHONE_MODE_WCDMA_800A  =23     #(WCDMA 800, Band V Add)
PHONE_MODE_WCDMA_1800  =25     #(WCDMA 1800, Band III)
PHONE_MODE_WCDMA_BC4   =28     #(WCDMA BC4-used for both Band IV Gen and Band IV Add)
PHONE_MODE_WCDMA_BC8   =29     #(WCDMA BC8, Band VIII)
PHONE_MODE_MF_700      =30     #(MediaFLO)
PHONE_MODE_WCDMA_BC9   =31     #(WCDMA BC9 (1750MHz & 1845MHz), Band IX)
PHONE_MODE_CDMA_BC15   =32     #(CDMA Band Class 15)

PHONE_MODE_LTE_B1     =34    #(LTE Band Class 1)
PHONE_MODE_LTE_B7     =35    #(LTE Band Class 7)
PHONE_MODE_LTE_B13    =36    #(LTE Band Class 13)
PHONE_MODE_LTE_B17    =37    #(LTE Band Class 17)
PHONE_MODE_LTE_B38    =38    #(LTE Band Class 38)
PHONE_MODE_LTE_B40    =39    #(LTE Band Class 40)
PHONE_MODE_WCDMA_1500 =40             

PHONE_MODE_LTE_B11 = 41

PHONE_MODE_LTE_B2=43 
PHONE_MODE_LTE_B3=44 
PHONE_MODE_LTE_B5=45 
PHONE_MODE_LTE_B6=46 
PHONE_MODE_LTE_B8=47 
PHONE_MODE_LTE_B9=48 
PHONE_MODE_LTE_B10=49 
PHONE_MODE_LTE_B12=50 
PHONE_MODE_LTE_B14=51 
PHONE_MODE_LTE_B15=52 
PHONE_MODE_LTE_B16=53 
PHONE_MODE_LTE_B18=54 
PHONE_MODE_LTE_B19=55 
PHONE_MODE_LTE_B20=56 
PHONE_MODE_LTE_B21=57 
PHONE_MODE_LTE_B22=58 
PHONE_MODE_LTE_B23=59 
PHONE_MODE_LTE_B24=60 
PHONE_MODE_LTE_B25=61 
PHONE_MODE_LTE_B26=62 
PHONE_MODE_LTE_B27=63 
PHONE_MODE_LTE_B28=64 
PHONE_MODE_LTE_B29=65 
PHONE_MODE_LTE_B30=66 
PHONE_MODE_LTE_B31=67 
PHONE_MODE_LTE_B32=68 
PHONE_MODE_LTE_B33=69 
PHONE_MODE_LTE_B34=70 
PHONE_MODE_LTE_B35=71 
PHONE_MODE_LTE_B36=72 
PHONE_MODE_LTE_B37=73 
PHONE_MODE_LTE_B39=74 
PHONE_MODE_WCDMA_BC19=75      
PHONE_MODE_LTE_B41=76 

#TDSCDMA reserves 90 - 99
PHONE_MODE_TDSCDMA_B34=90 
PHONE_MODE_TDSCDMA_B39=91 
PHONE_MODE_TDSCDMA_B40=92 
PHONE_MODE_MAX         =255    #(Last possible value, not a valid mode)

# LTE Bandwidth 
RFCOM_BW_LTE_1P4MHz = 0
RFCOM_BW_LTE_3MHz = 1
RFCOM_BW_LTE_5MHz = 2 
RFCOM_BW_LTE_10MHz = 3
RFCOM_BW_LTE_15MHz = 4
RFCOM_BW_LTE_20MHz = 5

#Band-QMSL variable mapping
Band_QMSL_map = dict(B1=PHONE_MODE_WCDMA_IMT, B2=PHONE_MODE_WCDMA_1900B,
				B4=PHONE_MODE_WCDMA_BC4, B5=PHONE_MODE_WCDMA_800, B8=PHONE_MODE_WCDMA_BC8, 
				B9=PHONE_MODE_WCDMA_BC9,B19=PHONE_MODE_WCDMA_BC19)
LTE_Band_QMSL_map = dict(B1=PHONE_MODE_LTE_B1, B2=PHONE_MODE_LTE_B2, B3=PHONE_MODE_LTE_B3, B7=PHONE_MODE_LTE_B7, 
					B8=PHONE_MODE_LTE_B8, B11=PHONE_MODE_LTE_B11, B13=PHONE_MODE_LTE_B13,
					B19=PHONE_MODE_LTE_B19, B20=PHONE_MODE_LTE_B20, B21=PHONE_MODE_LTE_B21,
					B26=PHONE_MODE_LTE_B26, B281=PHONE_MODE_LTE_B28, B282=PHONE_MODE_LTE_B28)
				
#Anritsu 8820C CALL Status
ANRITSU_OFF = 0		#Call processing function set to Off
ANRITSU_IDLE = 1	#Idle state
ANRITSU_IDLE_REGIST = 2		#Idle( Regist ) Idle state (location registered)
ANRITSU_REGIST = 3			# Under location registration
ANRITSU_ORIGIN = 4			# Origination from a terminal
ANRITSU_TERMIN = 5			# Origination from the MT8815B/MT8820B (network)
ANRITSU_COMMUN = 6			# Under communication
ANRITSU_LOOP_1 = 7			# Loopback mode 1
ANRITSU_LOOP_1_OPEN = 8		# Loopback mode 1 open
ANRITSU_LOOP_1_CLOSE = 9	# Loopback mode 1 close
ANRITSU_LOOP_2 = 10			# Loopback mode 2
ANRITSU_LOOP_2_OPEN = 11	# Loopback mode 2 open
ANRITSU_LOOP_2_CLOSE = 12	# Loopback mode 2 close
ANRITSU_HAND = 13			# Under handover
ANRITSU_NW_RELEASE = 14		# Release by the MT8815B/MT8820B (network)
ANRITSU_UE_RELEASE = 15		# Release by a terminal
ANRITSU_OTHER = 16			# Other
