# author: Eugenio CORTESI

from __future__ import absolute_import, division
import json
import sys
import os
import gc

def openAdds():

	miners = []

	i = 0
	vistedReceivers = {}
	for a in receivers:
		if a not in vistedReceivers:
			vistedReceivers[a] = None

			#percentage = (i * 100)/len(receivers)
			#print(percentage)

			if a in allSenders:

				hashes = {}
				visited = {}

				for thisHash in allSenders[a]:
					hashes[thisHash] = None

				while (len(hashes) > 0):
					#print('collecting hashes - visited %s, to visit %s' %(len(visited), len(hashes)))
					hash = hashes.keys()[0]

					if hash not in visited:

						for s in transactions[hash]:
							if s not in vistedReceivers:
								if s in allSenders:

									vistedReceivers[s] = None

									for h in allSenders[s]:
										if h not in hashes and h not in visited:
											hashes[h] = None

						visited[hash] = None

					del hashes[hash]

				homonyms = []
				for transactionHash in visited:
					for thisAdss in transactions[transactionHash]:
						if thisAdss not in homonyms:
							homonyms.append(thisAdss)

				if (len(homonyms)>0):
					miners.append(homonyms)

				del homonyms

			#else:
				#homonyms = []
				#homonyms.append(a)
				#miners.append(homonyms)

	return miners


firstBlock = input('first')
lastBlock = input('last')
listofDirectories = []
a = os.listdir('./')
interval = []

receivers = {}

for i in range(firstBlock, lastBlock+1):
	dir = 'res_blk0%s.dat' %i
	interval.append(dir)

for i in a:
	for j in range(len(interval)):
		if interval[j] == i:
			listofDirectories.append(i)
		listofDirectories.sort()

file1 = os.getcwd() + '/rewardingTransactions.txt'

with open(file1) as json_file1:
	RWTs = json.load(json_file1)
json_file1.close()

for rwt in RWTs:
	adds = rwt['receiver'].split('_')
	del adds[0]

	for el in adds:
		if el not in receivers:
			receivers[el] = None

for directory in listofDirectories:

	print('NEW_DIRECTORY %s' %directory)

	allTransactions = []
	allSenders = {}
	transactions = {}

	abs_file_path1 = os.getcwd() + '/' + directory + '/allTransa.txt'

	with open(abs_file_path1) as json_file1:
		allTransactions = json.load(json_file1)
	json_file1.close()

	for tr in allTransactions['transactions']:
		senders = tr['Sender'].split("_")
		del senders[0]

		transactions[tr['txHash']] = []

		for add in senders:
			if add not in transactions[tr['txHash']]:
				transactions[tr['txHash']].append(add)
			if add not in allSenders:
				allSenders[add] = []
			if tr['txHash'] not in allSenders[add]:
				allSenders[add].append(tr['txHash'])

	del allTransactions

	m = openAdds()

	abs_file_path = os.getcwd() + '/' + directory + '/miners.txt'

	with open(abs_file_path, 'w') as outfile:
		json.dump(m, outfile)
	del m

	del allSenders
	del transactions
	gc.collect()
