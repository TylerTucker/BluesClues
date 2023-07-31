from time import time, sleep
import logging
import sqlite3
import pandas as pd
from binascii import unhexlify, hexlify
log = logging.getLogger("btctl")
LLID_LMP = 3

EXT_OPCODE = 0x100

# LMP opcodes
LMP_NAME_REQ                     = 1
LMP_NAME_RES                     = 2
LMP_ACCEPTED                     = 3
LMP_NOT_ACCEPTED                 = 4
LMP_CLKOFFSET_REQ                = 5
LMP_CLKOFFSET_RES                = 6
LMP_DETACH                       = 7
LMP_IN_RAND                      = 8
LMP_COMB_KEY                     = 9
LMP_UNIT_KEY                     = 10
LMP_AU_RAND                      = 11
LMP_SRES                         = 12
LMP_TEMP_RAND                    = 13
LMP_TEMP_KEY                     = 14
LMP_ENCRYPTION_MODE_REQ          = 15
LMP_ENCRYPTION_KEY_SIZE_REQ      = 16
LMP_START_ENCRYPTION_REQ         = 17
LMP_STOP_ENCRYPTION_REQ          = 18
LMP_SWITCH_REQ                   = 19
LMP_HOLD                         = 20
LMP_HOLD_REQ                     = 21
LMP_SNIFF                        = 22
LMP_SNIFF_REQ                    = 23
LMP_UNSNIFF_REQ                  = 24
LMP_PARK_REQ                     = 25
LMP_SET_BROADCAST_SCAN_WINDOW    = 27
LMP_MODIFY_BEACON                = 28
LMP_UNPARK_BD_ADDR_REQ           = 29
LMP_UNPARK_PM_ADDR_REQ           = 30
LMP_POWER_CONTROL_REQ            = 31
LMP_POWER_CONTROL_RES            = 32
LMP_MAX_POWER                    = 33
LMP_MIN_POWER                    = 34
LMP_AUTO_RATE                    = 35
LMP_PREFERRED_RATE               = 36
LMP_VERSION_REQ                  = 37
LMP_VERSION_RES                  = 38
LMP_FEATURES_REQ                 = 39
LMP_FEATURES_RES                 = 40
LMP_QUALITY_OF_SERVICE           = 41
LMP_QUALITY_OF_SERVICE_REQ       = 42
LMP_SCO_LINK_REQ                 = 43
LMP_REMOVE_SCO_LINK_REQ          = 44
LMP_MAX_SLOT                     = 45
LMP_MAX_SLOT_REQ                 = 46
LMP_TIMING_ACCURACY_REQ          = 47
LMP_TIMING_ACCURACY_RES          = 48
LMP_SETUP_COMPLETE               = 49
LMP_USE_SEMI_PERMANENT_KEY       = 50
LMP_HOST_CONNECTION_REQ          = 51
LMP_SLOT_OFFSET                  = 52
LMP_PAGE_MODE_REQ                = 53
LMP_PAGE_SCAN_MODE_REQ           = 54
LMP_SUPERVISION_TIMEOUT          = 55
LMP_TEST_ACTIVATE                = 56
LMP_TEST_CONTROL                 = 57
LMP_ENCRYPTION_KEY_SIZE_MASK_REQ = 58
LMP_ENCRYPTION_KEY_SIZE_MASK_RES = 59
LMP_SET_AFH                      = 60
LMP_ENCAPSULATED_HEADER          = 61
LMP_ENCAPSULATED_PAYLOAD         = 62
LMP_SIMPLE_PAIRING_CONFIRM       = 63
LMP_SIMPLE_PAIRING_NUMBER        = 64
LMP_DHKEY_CHECK                  = 65
LMP_ESCAPE_1                     = 124
LMP_ESCAPE_2                     = 125
LMP_ESCAPE_3                     = 126
LMP_ESCAPE_4                     = 127

# LMP extended opcodes
LMP_ACCEPTED_EXT                = 1
LMP_NOT_ACCEPTED_EXT            = 2
LMP_FEATURES_REQ_EXT            = 3
LMP_FEATURES_RES_EXT            = 4
LMP_CLK_ADJ						= 5
LMP_PACKET_TYPE_TABLE_REQ       = 11
LMP_ESCO_LINK_REQ               = 12
LMP_REMOVE_ESCO_LINK_REQ        = 13
LMP_CHANNEL_CLASSIFICATION_REQ  = 16
LMP_CHANNEL_CLASSIFICATION      = 17
LMP_SNIFF_SUBRATING_REQ         = 21
LMP_SNIFF_SUBRATING_RES         = 22
LMP_PAUSE_ENCRYPTION_REQ        = 23
LMP_RESUME_ENCRYPTION_REQ       = 24
LMP_IO_CAPABILITY_REQ           = 25
LMP_IO_CAPABILITY_RES           = 26
LMP_NUMERIC_COMPARISON_FAILED   = 27
LMP_PASSKEY_FAILED              = 28
LMP_OOB_FAILED                  = 29
LMP_KEYPRESS_NOTIFICATION       = 30
LMP_POWER_CONTROL_INC           = 31
LMP_POWER_CONTROL_DEC           = 32

LMP_OP2STR = {
	LMP_NAME_REQ: "LMP_NAME_REQ",
	LMP_NAME_RES: "LMP_NAME_RES",
	LMP_ACCEPTED: "LMP_ACCEPTED",
	LMP_NOT_ACCEPTED: "LMP_NOT_ACCEPTED",
	LMP_CLKOFFSET_REQ: "LMP_CLKOFFSET_REQ",
	LMP_CLKOFFSET_RES: "LMP_CLKOFFSET_RES",
	LMP_DETACH: "LMP_DETACH",
	LMP_IN_RAND: "LMP_IN_RAND",
	LMP_COMB_KEY: "LMP_COMB_KEY",
	LMP_UNIT_KEY: "LMP_UNIT_KEY",
	LMP_AU_RAND: "LMP_AU_RAND",
	LMP_SRES: "LMP_SRES",
	LMP_TEMP_RAND: "LMP_TEMP_RAND",
	LMP_TEMP_KEY: "LMP_TEMP_KEY",
	LMP_ENCRYPTION_MODE_REQ: "LMP_ENCRYPTION_MODE_REQ",
	LMP_ENCRYPTION_KEY_SIZE_REQ: "LMP_ENCRYPTION_KEY_SIZE_REQ",
	LMP_START_ENCRYPTION_REQ: "LMP_START_ENCRYPTION_REQ",
	LMP_STOP_ENCRYPTION_REQ: "LMP_STOP_ENCRYPTION_REQ",
	LMP_SWITCH_REQ: "LMP_SWITCH_REQ",
	LMP_HOLD: "LMP_HOLD",
	LMP_HOLD_REQ: "LMP_HOLD_REQ",
	LMP_SNIFF: "LMP_SNIFF",
	LMP_SNIFF_REQ: "LMP_SNIFF_REQ",
	LMP_UNSNIFF_REQ: "LMP_UNSNIFF_REQ",
	LMP_PARK_REQ: "LMP_PARK_REQ",
	LMP_SET_BROADCAST_SCAN_WINDOW: "LMP_SET_BROADCAST_SCAN_WINDOW",
	LMP_MODIFY_BEACON: "LMP_MODIFY_BEACON",
	LMP_UNPARK_BD_ADDR_REQ: "LMP_UNPARK_BD_ADDR_REQ",
	LMP_UNPARK_PM_ADDR_REQ: "LMP_UNPARK_PM_ADDR_REQ",
	LMP_POWER_CONTROL_REQ: "LMP_POWER_CONTROL_REQ",
	LMP_POWER_CONTROL_RES: "LMP_POWER_CONTROL_RES",
	LMP_MAX_POWER: "LMP_MAX_POWER",
	LMP_MIN_POWER: "LMP_MIN_POWER",
	LMP_AUTO_RATE: "LMP_AUTO_RATE",
	LMP_PREFERRED_RATE: "LMP_PREFERRED_RATE",
	LMP_VERSION_REQ: "LMP_VERSION_REQ",
	LMP_VERSION_RES: "LMP_VERSION_RES",
	LMP_FEATURES_REQ: "LMP_FEATURES_REQ",
	LMP_FEATURES_RES: "LMP_FEATURES_RES",
	LMP_QUALITY_OF_SERVICE: "LMP_QUALITY_OF_SERVICE",
	LMP_QUALITY_OF_SERVICE_REQ: "LMP_QUALITY_OF_SERVICE_REQ",
	LMP_SCO_LINK_REQ: "LMP_SCO_LINK_REQ",
	LMP_REMOVE_SCO_LINK_REQ: "LMP_REMOVE_SCO_LINK_REQ",
	LMP_MAX_SLOT: "LMP_MAX_SLOT",
	LMP_MAX_SLOT_REQ: "LMP_MAX_SLOT_REQ",
	LMP_TIMING_ACCURACY_REQ: "LMP_TIMING_ACCURACY_REQ",
	LMP_TIMING_ACCURACY_RES: "LMP_TIMING_ACCURACY_RES",
	LMP_SETUP_COMPLETE: "LMP_SETUP_COMPLETE",
	LMP_USE_SEMI_PERMANENT_KEY: "LMP_USE_SEMI_PERMANENT_KEY",
	LMP_HOST_CONNECTION_REQ: "LMP_HOST_CONNECTION_REQ",
	LMP_SLOT_OFFSET: "LMP_SLOT_OFFSET",
	LMP_PAGE_MODE_REQ: "LMP_PAGE_MODE_REQ",
	LMP_PAGE_SCAN_MODE_REQ: "LMP_PAGE_SCAN_MODE_REQ",
	LMP_SUPERVISION_TIMEOUT: "LMP_SUPERVISION_TIMEOUT",
	LMP_TEST_ACTIVATE: "LMP_TEST_ACTIVATE",
	LMP_TEST_CONTROL: "LMP_TEST_CONTROL",
	LMP_ENCRYPTION_KEY_SIZE_MASK_REQ: "LMP_ENCRYPTION_KEY_SIZE_MASK_REQ",
	LMP_ENCRYPTION_KEY_SIZE_MASK_RES: "LMP_ENCRYPTION_KEY_SIZE_MASK_RES",
	LMP_SET_AFH: "LMP_SET_AFH",
	LMP_ENCAPSULATED_HEADER: "LMP_ENCAPSULATED_HEADER",
	LMP_ENCAPSULATED_PAYLOAD: "LMP_ENCAPSULATED_PAYLOAD",
	LMP_SIMPLE_PAIRING_CONFIRM: "LMP_SIMPLE_PAIRING_CONFIRM",
	LMP_SIMPLE_PAIRING_NUMBER: "LMP_SIMPLE_PAIRING_NUMBER",
	LMP_DHKEY_CHECK: "LMP_DHKEY_CHECK",
	LMP_ESCAPE_1: "LMP_ESCAPE_1",
	LMP_ESCAPE_2: "LMP_ESCAPE_2",
	LMP_ESCAPE_3: "LMP_ESCAPE_3",
	LMP_ESCAPE_4: "LMP_ESCAPE_4",
}

LMP_OPEXT2STR = {
	LMP_ACCEPTED_EXT: "LMP_ACCEPTED_EXT",
	LMP_NOT_ACCEPTED_EXT: "LMP_NOT_ACCEPTED_EXT",
	LMP_FEATURES_REQ_EXT: "LMP_FEATURES_REQ_EXT",
	LMP_FEATURES_RES_EXT: "LMP_FEATURES_RES_EXT",
	LMP_PACKET_TYPE_TABLE_REQ: "LMP_PACKET_TYPE_TABLE_REQ",
	LMP_ESCO_LINK_REQ: "LMP_ESCO_LINK_REQ",
	LMP_REMOVE_ESCO_LINK_REQ: "LMP_REMOVE_ESCO_LINK_REQ",
	LMP_CHANNEL_CLASSIFICATION_REQ: "LMP_CHANNEL_CLASSIFICATION_REQ",
	LMP_CHANNEL_CLASSIFICATION: "LMP_CHANNEL_CLASSIFICATION",
	LMP_SNIFF_SUBRATING_REQ: "LMP_SNIFF_SUBRATING_REQ",
	LMP_SNIFF_SUBRATING_RES: "LMP_SNIFF_SUBRATING_RES",
	LMP_PAUSE_ENCRYPTION_REQ: "LMP_PAUSE_ENCRYPTION_REQ",
	LMP_RESUME_ENCRYPTION_REQ: "LMP_RESUME_ENCRYPTION_REQ",
	LMP_IO_CAPABILITY_REQ: "LMP_IO_CAPABILITY_REQ",
	LMP_IO_CAPABILITY_RES: "LMP_IO_CAPABILITY_RES",
	LMP_NUMERIC_COMPARISON_FAILED: "LMP_NUMERIC_COMPARISON_FAILED",
	LMP_PASSKEY_FAILED: "LMP_PASSKEY_FAILED",
	LMP_OOB_FAILED: "LMP_OOB_FAILED",
	LMP_KEYPRESS_NOTIFICATION: "LMP_KEYPRESS_NOTIFICATION",
	LMP_POWER_CONTROL_INC: "LMP_POWER_CONTROL_INC",
	LMP_POWER_CONTROL_DEC: "LMP_POWER_CONTROL_DEC",
}

# TYLER added array to hold feature labels
FEATURE_ARRAY = [
	'3 Slot Packets', '5 Slot Packets', 'Encryption', 'Slot Offset',
	'Timing Accuracy', 'Role Switch', 'Hold Mode', 'Sniff Mode',
	'Park State', 'Power Control Requests', 'Channel Quality Driven Data Rate', 'SCO Link',
	'HV2 Packets', 'HV3 Packets', 'u-Law Log Synchronous Data', 'A-Law Log Synchronous Data',
	'CVSD Synchronous Data', 'Paging Parameter Negotiation', 'Power Control', 'Transparent Synchonous Data',
	'Flow Control Lag', 'Broadcast Encryption', 'Reserved (1)', 'EDR ACL 2Mbps Mode',
	'EDR ACL 3Mbps Mode', 'Enhanced Inquiry Scan', 'Interlaced Inquiry Scan', 'Interlaced Page Scan',
	'RSSI with Inquiry Results', 'Extended SCO Link', 'EV4 Packets', 'EV5 Packets',
	'Reserved (2)', 'AFH Capable Slave', 'AFH Classification Slave', 'BR/EDR Not Supported',
	'LE Supported (Controller)', '3-Slot EDR ACL Packets', '3-Slot EDR ACL Packets', 'Sniff Subrating',
	'Pause Encryption', 'AFH Capable Master', 'AFH Classification Master', 'EDR eSCO 2 Mbps Mode',
	'EDR eSCO 3 Mbps Mode', '3-Slot EDR eSCO Packets', 'Extended Inquiry Response', 'Simultaneous LE and BR/EDR',
	'Reserved (3)', 'Secure Simple Pairing', 'Encapsulated PDU', 'Erroneous Data Pairing',
	'Non-Flushable Packet Boundary Flag', 'Reserved (4)', 'Link Supervision Timeout Changed Event', 'Inquiry Tx Power Level',
	'Enhanced Power Control', 'Secure Connections', 'Reserved (5)', 'Extended Features'
]

# Dictionary to keep track of current features for a device
current_features = {}

# Map bitcodes to Bluetooth versions
VERSIONS = {
	'0':	'Bluetooth Core Specification 1.0b',
	'1':	'Bluetooth Core Specification 1.1',
	'2':	'Bluetooth Core Specification 1.2',
	'3':	'Bluetooth Core Specification 2.0 + EDR',
	'4':	'Bluetooth Core Specification 2.1 + EDR',
	'5':	'Bluetooth Core Specification 3.0 + HS',
	'6':	'Bluetooth Core Specification 4.0',
	'7':	'Bluetooth Core Specification 4.1',
	'8':	'Bluetooth Core Specification 4.2',
	'9':	'Bluetooth Core Specification 5.0',
	'10':	'Bluetooth Core Specification 5.1',
	'11':	'Bluetooth Core Specification 5.2'
}

# Map bitcodes to Bluetooth manufacturers from CSV file
MANUFACTURERS = pd.read_csv('manufacturers.csv', usecols=['Decimal', 'Company'])
# MANUFACTURERS = {'29':'Qualcomm',
# 	'15':'Broadcomm'}

def u8(d):	return d
def u16(d):
	assert (len(d)==2)
	return d[0]+(d[1]<<8)
def u32(d):
	assert (len(d)==4)
	return d[0]+(d[1]<<8)+(d[2]<<16)+(d[3]<<24)
def p16(n):	return bytes((n&0xff,(n>>8)&0xff))
def p32(n):	return bytes((n&0xff,(n>>8)&0xff,(n>>16)&0xff,(n>>24)&0xff))
def p8(n):	return bytes((n,))

def pdu2str(pdu):
	opcode = u8(pdu[0])
	tid = opcode & 1
	opcode >>= 1

	if opcode == LMP_ESCAPE_4:
		op = u8(pdu[1])
		opstr = LMP_OPEXT2STR.get(op)
	else:
		opstr = LMP_OP2STR.get(opcode)
	opstr = "\x1b[33;1m%s\x1b[0m"%opstr
	return ("(tid %d) %-40s | %s"%(tid, opstr, hexlify(pdu)))

class LMP:
	# Features supported (Core v5.2 | Vol 2, Part C, table 3.2 p585)
	#FEATURES = b"\x03\x00\x00\x00\x08\x08\x19\x80" # With AFH
	# FEATURES = b"\x03\x00\x00\x00\x00\x00\x19\x80" # No AFH
	# TYLER changed features list to support role switch
	# FEATURES = b"\xFF\x00\x00\x00\x00\x00\x19\x80"
	FEATURES = b"\xFF\xFF\xFF\xFF\xFF\xFF\x19\x80"
	# FEATURES_EXT = b"\x01\x01\x07"
	FEATURES_EXT = b"\x01\x01\x09"

	def __init__(self, con, debug=True):
		debug = False
		self._debug = debug
		self._con = con
		self._start_time = time()
		self._clkn = 0

	def time(self):
		return time()-self._start_time

	# FSM per LMP_state
	def receive(self, clkn, pdu):
		self._clkn = clkn
		# Parse lmp message
		opcode = u8(pdu[0])
		tid = opcode & 1
		opcode >>= 1

		if opcode == LMP_ESCAPE_4:
			op = u8(pdu[1]) | EXT_OPCODE
			data = pdu[2:]
		else:
			op = opcode
			data = pdu[1:]

		if self._debug:
			log.info("%d|%.2f sec | <<< lmp_rx (state=%d): %s"%(clkn,self.time(),self._state, pdu2str(pdu)))

		print('Received state %d' % self._state)
		fsm = self._FSM[self._state]
		reg = fsm.get(op)
		print(op)
		if reg is None:
			# log.warn("Unhandled opcode 0x%x"%op)
			return False
		else:
			handler = reg[0]
			if len(reg) > 1:
				next_state = reg[1]
			else:
				next_state = self._state
			retval = handler(op, data) or 0
			if retval is not None:
				if retval < 0:
					return retval
				elif retval > 0:
					next_state = retval
			self.set_state(next_state)

	def set_state(self, state):
		if (state != self._state):
			log.info("%.2f sec | Switch state %d -> %d"%(self.time(), self._state, state))
			self._state = state

	def lmp_down(self, pdu):
		self._con.send_acl(LLID_LMP, pdu)

	def pack_lmp(self, opcode, data, tid=0):
		pdu = p8((opcode<<1)|(tid&1)) + data
		pdu = pdu.ljust(17, b"\x00")
		return pdu

	def lmp_send(self, opcode, data, tid=0):
		pdu = self.pack_lmp(opcode, data, tid=tid)
		if self._debug:
			log.info("%.2f sec | >>> lmp_tx (state=%d): %s"%(self.time(),self._state, pdu2str(pdu)))
		return self.lmp_down(pdu)

	def handle_name_req(self, op, data):
		offset = u8(data[0])
		name = b"Ubertooth"
		sleep(0.1)
		return self.lmp_send_name_res(offset, len(name), name)

	def handle_feat_req(self, op, data):
		log.info("handle_feat_req")
		self.lmp_send_feat(False)

	def handle_feat_req_ext(self, op, data):
		log.info("handle_feat_req_ext")
		self.lmp_send_feat_ext(False)

	def handle_vers_req(self, op, data):
		log.info("handle_vers_req")
		self.lmp_send_version(False)

	def handle_io_cap_req(self, op, data):
		log.info("handle_io_cap_req")
		self.lmp_send_io_cap(False)

	# TYLER added handler for packet type
	def handle_packet_type(self, op):
		log.info("handle_packet_type")
		self.lmp_send_accepted_ext(LMP_PACKET_TYPE_TABLE_REQ)

	# TYLER added 2/3 handler
	# def handle_23_request(self, op):
	# 	log.info("handle_23_request")
	# 	self.lmp_send_

	def lmp_send_conn_req(self, **kwargs):
		return self.lmp_send(LMP_HOST_CONNECTION_REQ, b'', **kwargs)

	def lmp_send_name_req(self, offset, **kwargs):
		return self.lmp_send(LMP_NAME_REQ, p8(offset), **kwargs)

	def lmp_send_name_res(self, poffset, psize, payload, **kwargs):
		assert(len(payload)<=14)
		data = p8(poffset) + p8(psize) + payload
		return self.lmp_send(LMP_NAME_RES, data, **kwargs)

	def lmp_send_accepted(self, opcode, **kwargs):
		return self.lmp_send(LMP_ACCEPTED, p8(opcode), **kwargs)

	def lmp_send_accepted_ext(self, opcode, **kwargs):
		return self.lmp_send(LMP_ACCEPTED_EXT, p8(opcode), **kwargs)

	def lmp_send_not_accepted(self, opcode, data=b'', **kwargs):
		return self.lmp_send(LMP_NOT_ACCEPTED, p8(opcode)+data, **kwargs)

	def lmp_send_io_cap(self, is_req, **kwargs):
		# ext opcode
		if is_req:
			data = p8(LMP_IO_CAPABILITY_REQ)
		else:
			data = p8(LMP_IO_CAPABILITY_RES)
		data += b"\x01\x00\x03"
		return self.lmp_send(LMP_ESCAPE_4, data, **kwargs)

	def lmp_send_encap_header(self, size, minor=1,major=1,**kwargs):
		payload = p8(minor)+p8(major) # version
		payload += p8(size)
		return self.lmp_send(LMP_ENCAPSULATED_HEADER, payload, **kwargs)

	def lmp_send_encap_payload(self, data, **kwargs):
		assert(len(data) == 16)
		return self.lmp_send(LMP_ENCAPSULATED_PAYLOAD, data, **kwargs)

	def lmp_send_version(self, is_req, **kwargs):
		# Opcode
		if is_req:	op = LMP_VERSION_REQ
		else:		op = LMP_VERSION_RES
		data = p8(6)		# version num
		data += p16(29)		# Qualcomm
		data += p16(2003)	# sub version num
		return self.lmp_send(op, data, **kwargs)

	def lmp_send_feat(self, is_req, **kwargs):
		if is_req:	op = LMP_FEATURES_REQ
		else:		op = LMP_FEATURES_RES
		return self.lmp_send(op, self.FEATURES, **kwargs)

	def lmp_send_feat_ext(self, is_req, **kwargs):
		# Ext opcode
		if is_req:	data = p8(LMP_FEATURES_REQ_EXT)
		else:		data = p8(LMP_FEATURES_RES_EXT)
		data += self.FEATURES_EXT
		data = data.ljust(11, b"\x00")
		return self.lmp_send(LMP_ESCAPE_4, data, **kwargs)

	def lmp_send_setup_complete(self, **kwargs):
		return self.lmp_send(LMP_SETUP_COMPLETE, b'', **kwargs)

	# TYLER added host connection request
	def lmp_send_host_connection_request(self, **kwargs):
		return self.lmp_send(LMP_HOST_CONNECTION_REQ, b'', **kwargs)

	# TYLER added role switch function
	def lmp_send_switch(self, **kwargs):
		return self.lmp_send(LMP_SWITCH_REQ, b'', **kwargs)

	# TYLER added clock offset request function
	def lmp_send_clk_offset(self, **kwargs):
		return self.lmp_send(LMP_CLKOFFSET_REQ, b'', **kwargs)

	# TYLER added slot offset request function
	def lmp_send_slot_offset(self, **kwargs):
		return self.lmp_send(LMP_SLOT_OFFSET, b'\x00\x00\x66\x55\x44\x33\x22\x11', **kwargs)

	# TYLER added slot offset request function
	def lmp_send_max_slot(self, **kwargs):
		return self.lmp_send(LMP_MAX_SLOT_REQ, b'', **kwargs)

	def lmp_send_detach(self, **kwargs):
		return self.lmp_send(LMP_DETACH, b'', **kwargs)

class LMPMaster(LMP):
	def __init__(self, con, addr = None):
		self._FSM = {
			# First state: fetch device infos
			1: {
				LMP_VERSION_REQ: 	(self.handle_vers_req,),
				LMP_FEATURES_REQ:	(self.handle_feat_req,),
				EXT_OPCODE|LMP_FEATURES_REQ_EXT:	(self.handle_feat_req_ext,),
				LMP_IO_CAPABILITY_REQ: 	(self.handle_io_cap_req,),
				LMP_NAME_REQ: 		(self.handle_name_req,),
				LMP_FEATURES_RES:	(self.handle_info_res,),
				EXT_OPCODE|LMP_FEATURES_RES_EXT: (self.handle_info_res,),
				LMP_VERSION_RES: 	(self.handle_info_res,),
				LMP_IO_CAPABILITY_RES: 	(self.handle_info_res,),
				LMP_NAME_RES: 		(self.handle_info_res,),
				LMP_SLOT_OFFSET:	(self.handle_slot_offset,),
				LMP_SWITCH_REQ:		(self.handle_switch_req,),
				LMP_ACCEPTED:		(self.handle_accepted,),
				LMP_SETUP_COMPLETE:	(self.handle_setup_complete,),
				LMP_PACKET_TYPE_TABLE_REQ:	(self.handle_packet_type,),
			},
		}
		self._state = 1
		self.rmt_features = None
		self.rmt_features_ext = None
		self.rmt_iocap = None
		self.rmt_version = None
		self.rmt_name = None
		self.success = False
		self.addr = addr
		self.entry = {'addr':hex(self.addr), 'name':None, 'manu':None, 'ver':None, 'subver':None}
		print(self.entry)
		super().__init__(con)

	def start(self):
		self.send_info_req()

	def handle_accepted(self, op, data):
		o = data[0]
		if o == LMP_HOST_CONNECTION_REQ:
			pass

	def handle_slot_offset(self, op, data):
		offset = u16(data[:2])
		bdaddr = data[2:][::-1]
		self.addr = bdaddr
		self.entry['addr'] = hexlify(bdaddr)
		log.info("slot_offset from %s: %dusec\n"%(
			hexlify(bdaddr).decode(),offset))

	def handle_switch_req(self, op, data):
		instant = u32(data)
		log.info("switch req: instant: %d (in %d ticks)"%(
			instant, (instant<<1)-self._clkn))

	# TYLER added print function to read bytearrays
	def print_bytearray(self, arr):
		for byte in arr:
			print(bin(byte), end = ' ')
		print()

	# TYLER added decode functions for LMP messages
	def decode_name(self, n):
		offset = int(n[0])
		length = int(n[1])
		name = n[2+offset:2+length].decode(encoding='utf-8')
		print(name) #.strip().replace('\n',''))
		self.entry['name'] = name

	def decode_features(self, n):
		i = 0
		j = 7
		for byte in n:
			# print('{:08b}'.format(byte)[::-1], end=' ')
			reversed = int('{:08b}'.format(byte)[::-1])
			while j >= 0:
				# print(FEATURE_ARRAY[i])
				# Handle special cases of numerical fields
				if (FEATURE_ARRAY[i] == 'Flow Control Lag' or FEATURE_ARRAY[i] == 'Reserved (5)'):
					j -= 2
					# TODO Fix logic for flow control: 1111[001]1 -> [100]
					if (FEATURE_ARRAY[i] == 'Flow Control Lag'):
						# print('Flow controlllll: j = ', j)
						# print('{:08b}'.format((reversed & 7 << 1) >> 1)[::-1])
						current_features[FEATURE_ARRAY[i]] = (reversed & 7 << j) >> j
					i += 1
					j -= 1
				elif (FEATURE_ARRAY[i].startswith('Reserved')):
					j -= 1
					i += 1
				elif (reversed & 1 << j):
					current_features[FEATURE_ARRAY[i]] = True
					j -= 1
					i += 1
				else:
					j -= 1
					i += 1
			j = 7
		# print('{:08b}'.format(byte)[::-1], end=' ')
		print(list(current_features.keys())[0:10])

	def decode_ext(self, n):
		print('Features Page: ', n[0])
		print('Max Supported Page: ', n[1])
		if (n[2] & 0x0F):
			print('LMP Page 1 Extended Features:')
			if (n[2] & 0x08):
				print('-Secure Simple Pairing')
			if (n[2] & 0x04):
				print('-LE Supported (Host)')
			if (n[2] & 0x02):
				print('-Simultaneous LE and BR/EDR')
			if (n[2] & 0x01):
				print('-Secure Connections (Host Support)')

	def decode_version(self, n):
		version = str(int(n[0]))
		if (version in VERSIONS):
			version = VERSIONS[version]
		manufacturer = str(int((n[2] << 8) | n[1]))
		manufacturer = MANUFACTURERS.loc[MANUFACTURERS['Decimal'] == int(manufacturer)]['Company'].item()
		# if (manufacturer in MANUFACTURERS):
		# 	manufacturer = MANUFACTURERS[manufacturer]
		self.entry['manu'] = manufacturer
		self.entry['ver'] = version
		self.entry['subver'] = int((n[4] << 8) | n[3])
		print('Version: ', version)
		print('Company ID: ', manufacturer)
		print('Subversion Number: ', int((n[4] << 8) | n[3]))

	def send_info_req(self):
		if self.rmt_features is None:
			self.lmp_send_feat(True)
			return
		if self.rmt_features_ext is None:
			self.lmp_send_feat_ext(True)
			return
		if self.rmt_version is None:
			self.lmp_send_version(True)
			return
		if self.rmt_name is None:
			self.lmp_send_name_req(0)
			return
		self.lmp_send_conn_req()
		self.lmp_send_detach()
		# log.info("got all infos")
		# self.lmp_send_slot_offset()
		print('\nName')
		self.decode_name(self.rmt_name)
		print('\nFeatures')
		self.decode_features(self.rmt_features)
		print('\nFeatures Ext')
		self.decode_ext(self.rmt_features_ext)
		print('\nVersion')
		self.decode_version(self.rmt_version)
		self.success = True

		con = sqlite3.connect('blues.sqlite')
		cur = con.cursor()
		cur.execute('INSERT OR IGNORE INTO devices VALUES (?,?,?,?,?)',(self.entry['addr'],self.entry['name'],self.entry['manu'],self.entry['ver'],self.entry['subver']))
		con.commit()
		con.close()
		# self.lmp_send_accepted(LMP_HOST_CONNECTION_REQ)
		# self.lmp_send_switch()
		# self.lmp_send(LMP_HOST_CONNECTION_REQ,b'')

	def handle_info_res(self, op, data):
		if op == LMP_FEATURES_RES:
			self.rmt_features = data
		elif op == LMP_VERSION_RES:
			self.rmt_version = data
		elif op == EXT_OPCODE|LMP_FEATURES_RES_EXT:
			self.rmt_features_ext = data
		elif op == LMP_NAME_RES:
			self.rmt_name = data
		self.send_info_req()

	def handle_setup_complete(self, op, data):
		self.lmp_send(LMP_SETUP_COMPLETE, b"\x00"*16)
		self._con.handle_setup_complete()

class LMPSlave(LMP):
	def __init__(self, con):
		self._FSM = {
			# First state: wait for establishment message
			1: {
				LMP_DETACH: 		(self.handle_detach,),
				LMP_VERSION_REQ: 	(self.handle_vers_req,),
				LMP_FEATURES_REQ:	(self.handle_feat_req,),
				EXT_OPCODE|LMP_FEATURES_REQ_EXT:	(self.handle_feat_req_ext,),
				LMP_NAME_REQ: 		(self.handle_name_req,),
				LMP_HOST_CONNECTION_REQ: (self.handle_host_connection_req,),
				LMP_SETUP_COMPLETE: 	(self.handle_setup_complete,),
				LMP_SET_AFH:		(self.handle_set_afh,),
			},
		}
		self._state = 1
		super().__init__(con)

	def handle_host_connection_req(self, op, data):
		self.lmp_send_accepted(op)

	def handle_detach(self, op, data):
		self._con.stop()
		pass

	def handle_setup_complete(self, op, data):
		self.lmp_send_setup_complete()
		self._con.handle_setup_complete()

	def handle_set_afh(self, op, data):
		instant = u32(data[:4])
		mode = data[4]
		chan_map = data[5:]
		log.info("AFH req: instant=%d, (cur %d), mode=%d"%(
			instant<<1, self._clkn, mode))
		self.lmp_send_accepted(op)
		self._con._bt.send_set_afh_cmd(instant<<1, mode, chan_map)

	def start(self):
		pass
