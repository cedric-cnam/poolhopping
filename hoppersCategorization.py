# author: Eugenio CORTESI

import json
import simplejson
import sys
import os
import time
import collections

#this function creates the list of real hopper with information about the pools they worked in and the number of jumps performed by each pool
def getPoolsAndJumps(hoppers, countHoppers):
    print('funzione1')
    for hopper in epochsScheduleOrdered:   #for each group of epochs of a hopper, it checks if the consequent is from a different pools
        id = epochsScheduleOrdered.keys().index(hopper) + 1
        hoppers['hopper ' + str(id)]= collections.OrderedDict()
        print('hopper %s' %id)
        poolList = []
        for epoch in epochsScheduleOrdered[hopper]:                 #for each hopper's epoch it creates a list of pools in which he worked
            present = False
            for el in poolList:
                if el['pool'] == epoch['pool']:                             #miner has aready worked in this pool
                    present = True
            if present is False:
                poolList.append(collections.OrderedDict([('pool',epoch['pool']), ('jumps from this pool', 0) ]))     #first time in this pool
            idx = epochsScheduleOrdered[hopper].index(epoch)
            if idx < len(epochsScheduleOrdered[hopper]) - 1:
                if epochsScheduleOrdered[hopper][idx+1]['pool'] != epoch['pool']:                      #he performed a jump
                    for pool in poolList:
                        if pool['pool'] == epoch['pool']:
                            pool['jumps from this pool'] = pool['jumps from this pool'] + 1      #count the number of times he jumper from this pool
        if len(poolList) > 1:
            hoppers['hopper ' + str(id)] = poolList
            countHoppers = countHoppers +1
        else:
            del hoppers['hopper ' + str(id)]
    return hoppers, countHoppers

def getRealisticHoppers(overlappingEpochs, countHoppersWithOverlappingEpochs):
    print('funzione2')
    for hopper in epochsScheduleOrdered:
        id = epochsScheduleOrdered.keys().index(hopper) + 1
        overlappingEpochs['hopper ' + str(id)]= collections.OrderedDict()
        print('hopper %s' %id)
        epochList = collections.OrderedDict()
        for epoch in epochsScheduleOrdered[hopper]:
            idx = epochsScheduleOrdered[hopper].index(epoch)
            if idx > 0:
                for i in range (0, idx):           #to scan all the epoch before the current
                    previousEpoch = epochsScheduleOrdered[hopper][i]
                    #for each previous epoch it checks if the beginning of the current epoch comes earlies of the ending of one of that previous epochs
                    if epoch['epoch start'] < previousEpoch['end']:#both epochs must be appended, but only if not already present
                        #for the current
                        if epoch['pool'] not in epochList:
                            epochList[epoch['pool']] = []
                        if previousEpoch['pool'] not in epochList:
                            epochList[previousEpoch['pool']] = []
                        previousEpochIdx =len(epochList[previousEpoch['pool']])
                        currentEpochIdx = len(epochList[epoch['pool']])
                        imput = collections.OrderedDict([('epoch start', epoch['epoch start']), ('end', epoch['end']), ('overlaps with', previousEpoch['pool']), ('index', previousEpochIdx)])
                        epochList[epoch['pool']].append(imput)
                        #for the previous
                        imput = collections.OrderedDict([('epoch start', previousEpoch['epoch start']), ('end', previousEpoch['end']), ('overlaps with', epoch['pool']), ('index', currentEpochIdx)])
                        epochList[previousEpoch['pool']].append(imput)
                        #note: if more than two epochs are overlapped, then the epochs in the middle are inserted for each overlapped epoch with its inforation respectiely
        overlappingEpochs['hopper ' + str(id)] = epochList
        if len(epochList) > 0:
            countHoppersWithOverlappingEpochs = countHoppersWithOverlappingEpochs + 1
        else:
            del overlappingEpochs['hopper ' + str(id)]
    return overlappingEpochs, countHoppersWithOverlappingEpochs

#this functions sums for each hopper, his earning in each pool
def getHoppersEarnings(hoppersEarnings):
    print('funzione3')
    for hopper in rwtPerHoppers:
        idx = rwtPerHoppers.keys().index(hopper)
        h = 'hopper ' + str(idx + 1)
        if h in hoppers:
            hoppersEarnings[h] = []
            earnings = {'AntPool': 0,'F2Pool': 0,'BTCPool': 0,'PoolinPool': 0,'HuobiPool': 0}
            for rwt in rwtPerHoppers[hopper]:
                earnings[rwt['pool']] = earnings[rwt['pool']] + rwt['amount']
            hoppersEarnings[h] = earnings
    return hoppersEarnings

hoppers = collections.OrderedDict()
overlappingEpochs = collections.OrderedDict()
hoppersEarnings = collections.OrderedDict()
countHoppers = 0
countHoppersWithOverlappingEpochs = 0

file1 = os.getcwd() + '/epochsScheduleOrdered.txt'
file2 = os.getcwd() + '/rwtPerHoppers.txt'

with open(file1) as json_file1:
    epochsScheduleOrdered = simplejson.load(json_file1, object_pairs_hook = collections.OrderedDict)
json_file1.close()

with open(file2) as json_file2:
    rwtPerHoppers = json.load(json_file2, object_pairs_hook = collections.OrderedDict)
json_file2.close()

hoppers, countHoppers = getPoolsAndJumps(hoppers, countHoppers)
overlappingEpochs, countHoppersWithOverlappingEpochs = getRealisticHoppers(overlappingEpochs, countHoppersWithOverlappingEpochs)
print('one time hoppers %s' %countHoppers)
print('active hoppers %s ' %countHoppersWithOverlappingEpochs)
#hoppersEarnings = getHoppersEarnings(hoppersEarnings)

with open('poolJumpsPerHoppers.txt', 'w') as outfile:
    outfile.write("{")
    for line in hoppers:
        outfile.write('"' + line + '":')
        outfile.write("\n[")
        for el in hoppers[line]:
            outfile.write(json.dumps(el))
            if hoppers[line].index(el) != len(hoppers[line])-1:
                outfile.write(",\n")
        if hoppers.keys().index(line) != len(hoppers)-1:
            outfile.write("],\n")
        else:
            outfile.write("]\n")
    outfile.write("}")

with open('realisticHoppers.txt', 'w') as outfile:
    outfile.write("{")
    for line in overlappingEpochs:
        outfile.write('"' + line + '":')
        outfile.write("\n{")
        for el in overlappingEpochs[line]:
            outfile.write('"' + el + '":')
            outfile.write("\n[")
            for e in overlappingEpochs[line][el]:
                outfile.write(json.dumps(e))
                if overlappingEpochs[line][el].index(e) != len(overlappingEpochs[line][el])-1 :
                    outfile.write(",\n")
                #else:
                    #outfile.write("\n")
            if overlappingEpochs[line].keys().index(el) != len(overlappingEpochs[line])-1:
                outfile.write("],\n")
            else:
                outfile.write("]\n")
        if overlappingEpochs.keys().index(line) != len(overlappingEpochs)-1:
            outfile.write("},\n")
        else:
            outfile.write("}\n")
    outfile.write("}")

with open('hoppersEarnings.txt', 'w') as outfile:
    outfile.write("{")
    for line in hoppersEarnings:
        outfile.write('"' + line + '":')
        outfile.write("\n")
        json.dump(hoppersEarnings[line], outfile)
        if hoppersEarnings.keys().index(line) != len(hoppersEarnings)-1:
            outfile.write(",\n")
        else:
            outfile.write("\n")
    outfile.write("}")
