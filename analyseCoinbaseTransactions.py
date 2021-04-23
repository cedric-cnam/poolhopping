# author: Eugenio CORTESI, Sofiane KIRATI

from __future__ import absolute_import, division, print_function, unicode_literals
import ssl
import hashlib
import bitcoin
from bitcoin.core import *
from bitcoin.messages import *
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.core import *
from bitcoin.rpc import *
from bitcoin.signature import *
from bitcoin.core.key import *
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress, CBitcoinAddressError
import binascii
import struct
import sys
import os
import time
import json
import pickle
import datetime
import bitcoin.core.script as script
from bitcoin.core.script import CScript, CScriptWitness, CScriptOp, OP_RETURN, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, IsLowDERSignature
from bitcoin.core.scripteval import *
from bitcoin.core.serialize import *
from bitcoin import SelectParams

def convert_time(hexstamp):
	return datetime.datetime.fromtimestamp(int(hexstamp)).strftime('%Y-%m-%d %H:%M:%S')

def boucle_outputs(transaction, receiverAddress, timeStamp, nameMP, hsh):

	senderAddress = 'No Inputs, Newly Generated Coins'

	value = (transaction.vout[0].nValue) * 0.00000001
	if value != 0:

		if nameMP != 'Other':

			allCoinbaseTransactions['CoinbaseTransactions'].append({'Sender': senderAddress , 'receiver': receiverAddress, 'ammount': value, 'time': timeStamp, 'nameOfMP': nameMP, 'txHash': hsh})

			if receiverAddress in minPoolsAddrs[nameMP]:
				pass
			else:
				minPoolsAddrs[nameMP].append(receiverAddress)
		else:

			allOthers['CoinbaseTransactions'].append({'Sender': senderAddress , 'receiver': receiverAddress, 'ammount': value, 'time': timeStamp, 'nameOfMP': nameMP, 'txHash': hsh})

			if receiverAddress in otherPoolsAdds:
				pass
			else:
				otherPoolsAdds.append(receiverAddress)

def getMiningPool(transaction):
	p = 'Other'
	id = b2x(transaction.vin[0].scriptSig)
	if '4d696e656420627920416e74506f6f6c' in id:
		p = 'AntPool'
	elif '706f6f6c696e2e636f6d' in id:
		p = 'PoolinPool'
	elif '4254432e434f4d' in id:
		p = 'BTCPool'
	elif '48756f4269' in id or '48756f6269' in id:
		p = 'HuobiPool'
	elif '4632506f6f6c' in id:
		p = 'F2Pool'
	#else:
		#print(id)
		#ascii_string = id.decode("hex")
		#print(ascii_string)
	#print ('\n')
	return p

def get_receiver_Address(transaction):
	rec = ''
	try:
		scrPubKey = b2x(transaction.vout[0].scriptPubKey)
		ScriptPubKey = script.CScript(x(scrPubKey))
		rec = CBitcoinAddress.from_scriptPubKey(ScriptPubKey)
		rec1 = str(rec)
	except CBitcoinAddressError:
		rec1 = "no Address found"
	return(rec1)

blocksDirectory = sys.argv[1] #/home/lip6/.bitcoin/blocks
firstBlock = input('first')
lastBlock = input('last')
listofDirectories = []
a = os.listdir('./')
interval = []

for i in range(firstBlock, lastBlock+1):
	dir = 'res_blk0%s.dat' %i
	interval.append(dir)

for i in a:
	for j in range(len(interval)):
		if interval[j] == i:
			listofDirectories.append(i)
		listofDirectories.sort()

for directory in listofDirectories:

	print('NEW DIRECTORY %s' %directory)
	abs_dir_path = os.getcwd() + '/' + directory
	numBlock =  abs_dir_path[-9:]
	fichier='blk'+numBlock
	path = blocksDirectory + '/' + fichier

	allCoinbaseTransactions = {}
	allCoinbaseTransactions['CoinbaseTransactions'] = []
	allOthers = {}
	allOthers['CoinbaseTransactions'] = []
	minPoolsAddrs = {'BTCPool' : [], 'PoolinPool' : [], 'AntPool' : [], 'F2Pool' : [], 'HuobiPool': []}
	otherPoolsAdds = []

	#get the zise of the file
	sizeFile = os.path.getsize(path)
	print("the size of the file is %s " % sizeFile)

	#open the file to read with "r" option
	monFichier1 = open(path,"r")

	#we can do it by idx=0
	idx = monFichier1.tell()

	while idx < sizeFile:

		#read 8 bytes which contain magicBytes an the size of the upComing Block
		r1 = (ser_read(monFichier1,8))
		idx = monFichier1.tell()

		#read the header of the block
		header = CBlockHeader().stream_deserialize(monFichier1)
		#print("The header is ===> %s  " % header)
		idx = monFichier1.tell()

		#get timestamp
		hexstamp = header.nTime
		timeStamp = convert_time(hexstamp)

		# read the transaction count
		txCount = VarIntSerializer.stream_deserialize(monFichier1)

		for i in range(txCount):
			idx = monFichier1.tell()

			# read the transaction
			transaction = CTransaction.stream_deserialize(monFichier1)
			#print("The transaction is ===> %s " % transaction)

			idx = monFichier1.tell()

			#test if it's a new generation of coins
			isBase = transaction.is_coinbase()

			# coin base it means : new generation of coins
			if isBase:
				s = Serializable.serialize(transaction)
				hsh = b2lx(transaction.GetTxid())

				pool = getMiningPool(transaction)

				if pool != 'Other':
					receiverAddress = get_receiver_Address(transaction)
					boucle_outputs(transaction, receiverAddress, timeStamp, pool, hsh)
				else:
					receiverAddress = get_receiver_Address(transaction)
					boucle_outputs(transaction, receiverAddress, timeStamp, pool, hsh)

			else:
				pass

	abs_file_path1 = os.getcwd() + '/' + directory  + '/allCoinbaseTransa.txt'
	abs_file_path2 = os.getcwd() + '/' + directory  +'/minPoolAdd.txt'
	abs_file_path3 = os.getcwd() + '/' + directory  + '/allPoolsCoinbase.txt'
	abs_file_path4 = os.getcwd() + '/' + directory  + '/otherPoolsAdds.txt'

	with open(abs_file_path1, 'w') as outfile:
		json.dump(allCoinbaseTransactions, outfile)

	with open(abs_file_path2, 'w') as outfile:
		json.dump(minPoolsAddrs, outfile)

	with open(abs_file_path3, 'w') as outfile:
		json.dump(allOthers, outfile)

	with open(abs_file_path4, 'w') as outfile:
		json.dump(otherPoolsAdds, outfile)

	nbrCoinBase = len(allCoinbaseTransactions['CoinbaseTransactions'])
	print("the number of coinbase transaction %s " % nbrCoinBase)

	monFichier1.close()
