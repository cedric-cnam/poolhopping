# author: Eugenio CORTESI

import json
import sys
import os
import time
import collections

def reorderList(rwtList):
    for i in range(0, len(rwtList)):
        for j in range(i+1, len(rwtList)):
            t1 = rwtList[i]
            t2 = rwtList[j]
            delta = time.mktime(time.strptime(t2,"%Y-%m-%d %H:%M:%S"))-\
                   time.mktime(time.strptime(t1, "%Y-%m-%d %H:%M:%S"))
            if delta < 0:
                rwtList[i], rwtList[j] = rwtList[j], rwtList[i]
    return rwtList

poolsList = collections.OrderedDict()
blocksAnt = []
blocksF2 = []
blocksHuobi = []
blocksBTC = []
blocksPoolin = []

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
    print('NEW DIRECTORY %s' %directory)

    abs_file_path1 = os.getcwd() + '/' + directory  + '/allCoinbaseTransa.txt'

    with open(abs_file_path1) as json_file1:
        coinbaseTransactions = json.load(json_file1)
	json_file1.close()

    for transaction in coinbaseTransactions['CoinbaseTransactions']:
        if transaction['nameOfMP'] == 'AntPool':
            blocksAnt.append(transaction['time'])
        elif transaction['nameOfMP'] == 'F2Pool':
            blocksF2.append(transaction['time'])
        elif transaction['nameOfMP'] == 'HuobiPool':
            blocksHuobi.append(transaction['time'])
        elif transaction['nameOfMP'] == 'BTCPool':
            blocksBTC .append(transaction['time'])
        elif transaction['nameOfMP'] == 'PoolinPool':
            blocksPoolin.append(transaction['time'])

reorderList(blocksAnt)
reorderList(blocksF2)
reorderList(blocksHuobi)
reorderList(blocksBTC)
reorderList(blocksPoolin)

poolsList['AntPool'] = blocksAnt
poolsList['F2Pool'] = blocksF2
poolsList['HuobiPool'] = blocksHuobi
poolsList['BTCPool'] = blocksBTC
poolsList['PoolinPool'] = blocksPoolin

print('Blocks Ant %s' %len(blocksAnt))
print('Blocks F2 %s' %len(blocksF2))
print('Blocks Huobi %s' %len(blocksHuobi))
print('Blocks BTC %s' %len(blocksBTC))
print('Blocks Poolin %s' %len(blocksPoolin))

with open('roundsSchedule.txt', 'w') as outfile:
    outfile.write("{")
    for line in poolsList:
        outfile.write('"' + line + '":')
        outfile.write("\n[")
        for el in poolsList[line]:
            outfile.write(json.dumps(el))
            if poolsList[line].index(el) != len(poolsList[line])-1:
                outfile.write(",\n")
        if poolsList.keys().index(line) != len(poolsList)-1:
            outfile.write("],\n")
        else:
            outfile.write("]\n")
    outfile.write("}")
