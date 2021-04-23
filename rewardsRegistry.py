# author: Eugenio CORTESI

import json
import sys
import os
import time
import collections

def reorderList(rwtList):
    for i in range(0, len(rwtList)):
        for j in range(i+1, len(rwtList)):
            t1 = rwtList[i]['time']
            t2 = rwtList[j]['time']
            delta = time.mktime(time.strptime(t2,"%Y-%m-%d %H:%M:%S"))-\
                   time.mktime(time.strptime(t1, "%Y-%m-%d %H:%M:%S"))
            if delta < 0:
                rwtList[i], rwtList[j] = rwtList[j], rwtList[i]
    return rwtList

#this function grouops rwt by the potential hopper who riceived them, this structure will then be used to find hoppers
def groupRWTPerHopper(rwtPerHoppers):

    for hopper in hoppers:                                         #a potential hopper is identified by a group of addresses
        print(hopper)
        rwtPerHoppers[hopper] = collections.OrderedDict()
        rwtList =[]
        hashList = []

        for address in hoppers[hopper]:                                              #for each of a miner address i want to get all rwt sended to one of these addresses
            if address in receiversAddresses:
                for h in receiversAddresses[address]:
                    if h not in hashList:
                        hashList.append(h)

        print('%s rwts' %len(hashList))


        for h in hashList:                                                  #scan all rwt saving the ones with the current address
            rwt = rewardingTransactions[h]

            receivers = rwt['receiver'].split("_")
            del receivers[0]

            sumRepetitions = 0
            sumAmounts = 0

            for receiver in receivers:
                if receiver in hoppers[hopper]:

                    i = receivers.index(receiver)

                    sumAmounts = sumAmounts + rwt['ammount'][i]
                    sumRepetitions = sumRepetitions +1

            rwtList.append(collections.OrderedDict([('time', rwt['time'] ), ('pool', rwt['nameMP']),  ('txHash', rwt['txHash'] ), ('repetitions', sumRepetitions), ('amount', sumAmounts)]))

        rwtList = reorderList(rwtList)
        rwtPerHoppers[hopper] = rwtList

    return rwtPerHoppers

rwtPerHoppers = collections.OrderedDict()
rewardingTransactions = {}
receiversAddresses = {}
hoppers = collections.OrderedDict()

file2 = os.getcwd() + '/rewardingTransactions.txt'

with open(file2) as json_file:
    RWTs = json.load(json_file)
json_file.close()

for rwt in RWTs:
    rewardingTransactions[rwt['txHash']] = rwt
    receivers = rwt['receiver'].split("_")
    del receivers[0]
    for receiver in receivers:
        if receiver not in receiversAddresses:
            receiversAddresses[receiver] = []
        if rwt['txHash'] not in receiversAddresses[receiver]:
            receiversAddresses[receiver].append(rwt['txHash'])

del RWTs

file1 = os.getcwd() + '/minersCompleted.txt'

with open(file1) as json_file1:
	pHs = json.load(json_file1)
json_file1.close()

count = 0
for pH in pHs:
    thisHopper = 'Potential Hopper ' + str(count)
    hoppers[thisHopper] = {}
    for add in pH:
        hoppers[thisHopper][add] = None
    count = count + 1

rwtPerHoppers = groupRWTPerHopper(rwtPerHoppers)

with open('rwtPerHoppers.txt', 'w') as outfile:
    outfile.write("{")
    for line in rwtPerHoppers:
        outfile.write('"' + line + '":')
        outfile.write("\n[")
        for el in rwtPerHoppers[line]:
            outfile.write(json.dumps(el))
            if rwtPerHoppers[line].index(el) != len(rwtPerHoppers[line])-1:
                outfile.write(",\n")
            elif rwtPerHoppers[line].index(el) == len(rwtPerHoppers[line])-1 and not rwtPerHoppers.keys().index(line) == len(rwtPerHoppers)-1:
                outfile.write("],\n")
            elif rwtPerHoppers.keys().index(line) == len(rwtPerHoppers)-1:
                outfile.write("]\n")
    outfile.write("}")
