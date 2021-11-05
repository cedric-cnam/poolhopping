# author: Eugenio CORTESI, Sofiane KIRATI

from __future__ import absolute_import, division, print_function, unicode_literals
from urllib2 import Request, urlopen, URLError
from httplib import IncompleteRead
from ssl import SSLError
import hashlib
import bitcoin
from bitcoin.core import *
from bitcoin.messages import *
from bitcoin.wallet import *
from bitcoin.rpc import *
from bitcoin.signature import *
from bitcoin.core.key import *
from bitcoin.core.script import *
from bitcoin.core.scripteval import *
from bitcoin.core.serialize import *
import binascii
import struct
import sys, urllib2, re
import os
import time
import json
import datetime
import bitcoin.core.script as script

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
	"""Internal function that computes the Bech32 checksum."""
	generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
	chk = 1
	for value in values:
		top = chk >> 25
		chk = (chk & 0x1ffffff) << 5 ^ value
		for i in range(5):
			chk ^= generator[i] if ((top >> i) & 1) else 0
	return chk

def bech32_hrp_expand(hrp):
	"""Expand the HRP into values for checksum computation."""
	return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify_checksum(hrp, data):
	"""Verify a checksum given HRP and converted data characters."""
	return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

def bech32_create_checksum(hrp, data):
	"""Compute the checksum values given HRP and data."""
	values = bech32_hrp_expand(hrp) + data
	polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
	return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
	"""Compute a Bech32 string given HRP and data values."""
	combined = data + bech32_create_checksum(hrp, data)
	return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def bech32_decode(bech):
	"""Validate a Bech32 string, and determine HRP and data."""
	if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
			(bech.lower() != bech and bech.upper() != bech)):
		return (None, None)
	bech = bech.lower()
	pos = bech.rfind('1')
	if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
		return (None, None)
	if not all(x in CHARSET for x in bech[pos+1:]):
		return (None, None)
	hrp = bech[:pos]
	data = [CHARSET.find(x) for x in bech[pos+1:]]
	if not bech32_verify_checksum(hrp, data):
		return (None, None)
	return (hrp, data[:-6])

def convertbits(data, frombits, tobits, pad=True):
	"""General power-of-2 base conversion."""
	acc = 0
	bits = 0
	ret = []
	maxv = (1 << tobits) - 1
	max_acc = (1 << (frombits + tobits - 1)) - 1
	for value in data:
		if value < 0 or (value >> frombits):
			return None
		acc = ((acc << frombits) | value) & max_acc
		bits += frombits
		while bits >= tobits:
			bits -= tobits
			ret.append((acc >> bits) & maxv)
	if pad:
		if bits:
			ret.append((acc << (tobits - bits)) & maxv)
	elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
		return None
	return ret

def decode(hrp, addr):
	"""Decode a segwit address."""
	hrpgot, data = bech32_decode(addr)
	if hrpgot != hrp:
		return (None, None)
	decoded = convertbits(data[1:], 5, 8, False)
	if decoded is None or len(decoded) < 2 or len(decoded) > 40:
		return (None, None)
	if data[0] > 16:
		return (None, None)
	if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
		return (None, None)
	return (data[0], decoded)

def encode(hrp, witver, witprog):
	"""Encode a segwit address."""
	ret = bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))
	if decode(hrp, ret) == (None, None):
		return None
	return ret

#convert a hexa time to string time
def convert_time(hexstamp):
	return datetime.datetime.fromtimestamp(int(hexstamp)).strftime('%Y-%m-%d %H:%M:%S')

# iterate according to the number of outputs
def boucle_outputs(transaction, longueurOutPuts, senderAdress, boolSegWit, timeStamp, t, positions, hsh):
	receiverAdressJoin = ' '
	allValues = []
	for k in range(longueurOutPuts):
		value = (transaction.vout[k].nValue) * 0.00000001
		allValues.append(value)
		if value != 0:
			try:
				scrPubKey = b2x(transaction.vout[k].scriptPubKey)
				bcBool = int(scrPubKey[0:1],16)
				if bcBool == 0:
					n = 2
					liste = [int(scrPubKey[i:i+n],16) for i in range(0, len(scrPubKey), n)]
					liste[0:2]=[]
					receiverAdress =  encode('bc', bcBool, liste)
				else:
					ScriptPubKey = script.CScript(x(scrPubKey))
					receiverAdress = CBitcoinAddress.from_scriptPubKey(ScriptPubKey)

			except CBitcoinAddressError:
				receiverAdress = "no address found"

			receiverAdressJoin = receiverAdressJoin + "_" + str(receiverAdress)

	allTransactions['transactions'].append({'Sender': senderAdress, 'receiver': receiverAdressJoin, 'ammount': allValues, 'time': timeStamp, 'txID': t, 'positions': positions, 'txHash': hsh})
	return (allTransactions, value)

# if an address is used more than 1 time in an input transaction we store it once by deleting the redundant onces
def del_redundancy(address):
	addrDecouper = address.split("_")
	newAddress = ""
	for m in range(1, len(addrDecouper)):
		estEgal = False
		for n in range(1+m, len(addrDecouper)):

			if addrDecouper[m] == addrDecouper[n]:
				estEgal = True
		if estEgal == False:
			newAddress = newAddress + "_"+ addrDecouper[m]

		else:
			estEgal = False

	address = newAddress
	return address

# get sender by connecting to blockchain.info
def get_sender(regexR, source_code,n):
	matches = re.findall(regexR, source_code)
	if len(matches) == 0:
		sAdress = 'Impossible de decoder l adresse de saisie'
	#elif len(matches) <= 2 and len(matches) != 0:
		#sAdress = matches[-1]
		#print('regex ok')
	else:
		sAdress = matches[n]
		#print('regex ok')
	return sAdress

# get the source code of the blockchain.info according to the txHash
def get_code_source(txHash):
	failed = True
	while failed is True:
		try:
			req = Request("https://blockchain.info/fr/tx/"+txHash)
			fd = urlopen(req, timeout = 30)
			source_code = fd.read()
			failed = False
		except IncompleteRead:
			print ('We failed to reach a server.')
		except URLError:
			print ('URL error.')
		except SSLError:
			print ('SSL error.')
	return source_code

blocksDirectory = sys.argv[1]
firstBlock = input('first')
lastBlock = input('last')
block_list = []
block_interval = []

for i in range(firstBlock, lastBlock+1):
	blk = 'blk%05d.dat' %i
	block_interval.append(blk)

for file in os.listdir(blocksDirectory): #/home/lip6/.bitcoin/blocks
	for j in range(len(block_interval)):
		if block_interval[j] == file:
			block_list.append(file)
	block_list.sort()

for block in block_list:

	fichier = block
	path= blocksDirectory + '/' + fichier
	print(path)

	allTransactions = {}
	allTransactions['transactions'] = []
	transactions = []
	theHashList = []
	address = ' '

	#get the zise of the file
	sizeFile = os.path.getsize(path)
	#print("the size of the file is %s " % sizeFile)

	#open the file to read with "r" option
	myFile = open(path,"r")

	#we can do it by idx=0
	idx = myFile.tell()

	while idx < sizeFile:

		percentage = (idx * 100)/sizeFile
		print(percentage)

		#read 8 bytes which contain magicBytes an the size of the upComing Block
		r1 = (ser_read(myFile,8))
		idx = myFile.tell()

		#read the header of the block
		header = CBlockHeader().stream_deserialize(myFile)
		idx = myFile.tell()

		#get timestamp
		hexstamp = header.nTime
		timeStamp = convert_time(hexstamp)

		# read the transaction count
		txCount = VarIntSerializer.stream_deserialize(myFile)
		#print(txCount)

		for i in range(txCount):
			t = []
			positions = []
			idx = myFile.tell()

			# read the transaction
			transaction = CTransaction.stream_deserialize(myFile)

			idx = myFile.tell()

			#test if it's a new generation of coins
			isBase = transaction.is_coinbase()

			# coinbase it means : new generation of coins
			if isBase:
				pass
			else: # if it is a normal transaction

				s = Serializable.serialize(transaction)

				hsh = b2lx(transaction.GetTxid()) # get the transaction has. it is a double sha256
				hasWitness = transaction.has_witness() # test if it is a segregated witness transaction
				if hasWitness: # if it is segregated witness
					senderAdressWitnessJoin = ' '
					longtwin = len(transaction.wit.vtxinwit)
					for z in range(longtwin):
						try:
							t.append(b2lx(transaction.vin[z].prevout.hash))
							positions.append(transaction.vin[z].prevout.n)
							if len(b2x(transaction.vin[z].scriptSig)):
								if not (transaction.wit.vtxinwit[z].scriptWitness):
									scr = ''
									fAccur = transaction.vin[z].scriptSig.raw_iter()
									for (opcode, data, sop_idx) in fAccur:
										scr = data
									p2shpubkey = CScript(scr)
									SenderaddressWit = P2PKHBitcoinAddress.from_pubkey(p2shpubkey)
								else:
									lenScriptSignature = int(b2x(transaction.vin[z].scriptSig[0:1]),16)
									scrSignature = b2x(transaction.vin[z].scriptSig[1:lenScriptSignature+1])
									p2shpubkey = CScript(x(scrSignature)).to_p2sh_scriptPubKey()
									SenderaddressWit = CBitcoinAddress.from_scriptPubKey(p2shpubkey)

							else: # no scriptSig
								vtx = transaction.wit.vtxinwit[z].scriptWitness.stack[1:2]
								bb = [list(b2x(xx)) for xx in vtx]
								pubKeyW = ''.join(map(str, bb[0]))
								pubKeyW = b2x(Hash160(x(pubKeyW)))
								n = 2
								liste = [int(pubKeyW[i:i+n],16) for i in range(0, len(pubKeyW), n)]
								SenderaddressWit = encode('bc', 0, liste)
						except CBitcoinAddressError:
							try:
								last = b2x(scr[-1])
								if last == "ae":
									p2shpubkey = CScript(scr).to_p2sh_scriptPubKey()
									SenderaddressWit = CBitcoinAddress.from_scriptPubKey(p2shpubkey)
								else:
									#regexR = r"address/[a-zA-Z0-9]*.>([a-zA-Z0-9]*)</a>\s<span"
									regexR = r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{11,71})","spender\b'
									txHash = b2lx(transaction.vin[z].prevout.hash)
									n = transaction.vin[z].prevout.n
									source_code = get_code_source(txHash)
									SenderaddressWit = get_sender(regexR, source_code, n)
									#print('CASE 1: %s - %s - %s ' %(txHash, n, senderAdress))
							except IndexError:
									SenderaddressWit = 'Impossible de decoder l adresse de saisie'

						senderAdressWitnessJoin = senderAdressWitnessJoin + "_" + str(SenderaddressWit)

					#senderAdressWitnessJoin = del_redundancy(senderAdressWitnessJoin)

					longueurOutPuts = len(transaction.vout)
					allTransactions, value = boucle_outputs(transaction, longueurOutPuts, senderAdressWitnessJoin, 'segWit True', timeStamp, t, positions, hsh)

				else: # if it is not a segregated witness
					longueurInPuts = len(transaction.vin) # count the number of the inputs used in this transaction
					senderAdressJoin = ' '
					for j in range(longueurInPuts): # iterate according to the number of inputs
						try:
							t.append(b2lx(transaction.vin[j].prevout.hash))
							positions.append(transaction.vin[j].prevout.n)
							isMulti = False
							scr = ''
							senderAdress = ''
							fAccur = transaction.vin[j].scriptSig.raw_iter() # Yields tuples of (opcode, data, sop_idx)
							for (opcode, data, sop_idx) in fAccur:
								if sop_idx >= 140:
									isMulti = True
									scr = data
								else:
									isMulti = False
									scr = data
							if isMulti: # if is a multisignature address which start with 3
								p2shpubkey = CScript(scr).to_p2sh_scriptPubKey()
								senderAdress = CBitcoinAddress.from_scriptPubKey(p2shpubkey) # # get the address for the script publicKey
							else: # if it is a normal address which start with 1
								p2shpubkey = CScript(scr)
								senderAdress = P2PKHBitcoinAddress.from_pubkey(p2shpubkey) # get the address for the publicKey
						except CBitcoinAddressError: # if there an error to decode the address
							try:
								last = b2x(scr[-1])
								if last == "ae": # verify if the last byte of the script == 'ae'
									p2shpubkey = CScript(scr).to_p2sh_scriptPubKey()
									senderAdress = CBitcoinAddress.from_scriptPubKey(p2shpubkey)
								else: # this case is when we don't found a pubkey on the scriptSig
									#regexR = r"address/[a-zA-Z0-9]*.>([a-zA-Z0-9]*)</a>\s<span"
									regexR = r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{11,71})","spender\b'
									txHash = b2lx(transaction.vin[j].prevout.hash)
									n = transaction.vin[j].prevout.n
									source_code = get_code_source(txHash)
									senderAdress = get_sender(regexR, source_code, n)
									#print('CASE 2: %s - %s - %s ' %(txHash, n, senderAdress))
							except IndexError:
									senderAdress = 'Impossible de decoder l adresse de saisie'
						senderAdressJoin = senderAdressJoin + "_" +str(senderAdress)

					#senderAdressJoin = del_redundancy(senderAdressJoin)

					longueurOutPuts = len(transaction.vout)
					allTransactions, value = boucle_outputs(transaction, longueurOutPuts, senderAdressJoin, ' ', timeStamp, t, positions, hsh)

	name_new_rep = 'res'+ '_' + fichier

	a = os.listdir('./')
	if name_new_rep not in a:
		os.makedirs(name_new_rep)

	abs_file_path = os.getcwd() + '/' + name_new_rep  + '/allTransa.txt' # the name of the file

	with open(abs_file_path, 'w') as outfile:
		json.dump(allTransactions, outfile) # save the file on a json format

	myFile.close()

	print("NEXT BLOCK")
