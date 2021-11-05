# author: Eugenio CORTESI

import json
import glob
import os
import sys
import gc
import collections

def openMiners():

	minersList = {}
	addressList = {}
	count = 0

	firstBlock = input('first')
	lastBlock = input('last')
	listofDirectories = []
	a = os.listdir('./')
	interval = []

	for i in range(firstBlock, lastBlock+1):
		dir = 'res_blk%05d.dat' %i
		interval.append(dir)

	for i in a:
		for j in range(len(interval)):
			if interval[j] == i:
				listofDirectories.append(i)
			listofDirectories.sort()

	for directory in listofDirectories:

		print('NEW_DIRECTORY %s' %directory)

		abs_file_path = os.getcwd() + '/' + directory  + '/miners.txt'

		with open(abs_file_path) as json_file:
			temp = json.load(json_file)
			json_file.close()

			for group in temp:

				minersList[count] = {}

				for add in group:

					minersList[count][add] = None

					if add not in addressList:
						addressList[add] = {}

					if count not in addressList[add]:
						addressList[add][count] = None

				count = count + 1

			del temp

	users = groupHomonyms(minersList, addressList)

	print('MINERS %s' %len(users))

	abs_file_path = os.getcwd() + '/minersCompleted.txt'

	with open(abs_file_path, 'w') as outfile:
		json.dump(users, outfile)

	del users
	gc.collect()


def groupHomonyms(mList, aList):

	finalListUsers = []
	visitedGroups = {}
	matchedAddresses = {}

	print(len(mList))
	for address in aList:

		if address not in matchedAddresses:

			groups = {}
			homonyms = []

			for gr in aList[address]:
				groups[gr] = None

			while (len(groups)>0):
				g = groups.keys()[0]

				if g not in visitedGroups:

					for minerAddress in mList[g]:

						if minerAddress not in matchedAddresses:

							matchedAddresses[minerAddress] = None
							homonyms.append(minerAddress)

							for homonym in aList[minerAddress]:
								if homonym not in groups and homonym not in visitedGroups:
									groups[homonym] = None

					visitedGroups[g] = None

				del groups[g]

			finalListUsers.append(homonyms)

			remaining = len(mList) - len(visitedGroups)

	gc.collect()

	file1 = os.getcwd() + '/rewardingTransactions.txt'

	with open(file1) as json_file1:
		RWTs = json.load(json_file1)
	json_file1.close()

	receivers = {}

	for rwt in RWTs:
		adds = rwt['receiver'].split('_')
		del adds[0]

		for el in adds:
			if el not in receivers:
				receivers[el] = None

	countsingle = 0
	for el in receivers:
		if el not in matchedAddresses:
			#single = []
			#single.append(el)
			#finalListUsers.append(single)
			countsingle = countsingle + 1

	print('not assigned addresses %s on total %s' %(countsingle, len(receivers)))

	return finalListUsers

openMiners()
