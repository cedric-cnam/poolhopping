# author: Eugenio CORTESI

import json
import sys
import os
import gc
import time
import collections
import statistics
import numpy as np


def getMedian(list):
    return statistics.median(list)

def getBound(list):
    sorted(list)
    q1, q3= np.percentile(list,[25,75])
    iqr = q3 - q1
    return q3 +(1.5 * iqr)

def isRewarding(trans):
    rewarding = False
    count = 0
    if len(trans['ammount'])> minAmounts:
        for i in range(0, len(trans['ammount'])):
            if trans['ammount'][i] <= maxPayout:
                count = count +1
        if count > minAmounts:
            rewarding = True
    return rewarding

def getAddressesToFollow(trans, adds):
    toF = []
    countAmm = 0
    """for amm in trans['ammount']:
        if amm == 0.0:
            countAmm = countAmm +1
    for l in range(0, countAmm):
        trans['ammount'].remove(0.0)"""
    for i in range(0, len(trans['ammount'])):
        if trans['ammount'][i] > maxPayout:
            toF.append(0)
        else:
            toF.append(1)
    return toF

def deleteZeroAmount(trans):
    #print ('deleting zero amounts')
    countAmm = 0
    for amm in trans['ammount']:
        if amm == 0.0:
            countAmm = countAmm +1
    for l in range(0, countAmm):
        trans['ammount'].remove(0.0)
    return trans

def follow(cH, followList, p, lev, coinbaseH):
    #print('ID: %s' %cH)
    #print('follow list %s' %str(followList))

    itemList = []
    if cH in transactionSet:

        for tr in transactionSet[cH]:
            #print('TX: %s' %tr)

            if followList[tr['prevPos']] == 0:

                if 'grade' not in tr.keys() or tr['grade'] >= lev:
                    tr['grade'] = lev

                    if tr['rwt'] is True:
                        if tr['txHash'] not in rwtFound or rwtFound[tr['txHash']]['grade'] > lev:
                            rwtFound[tr['txHash']]= tr

                        found = False
                        for u in rwtToFind[tr['txHash']]:
                            if u[0] == coinbaseH:
                                found = True
                                if u[2] > lev:
                                    u[2] = lev
                        if found is False:
                            usage = (coinbaseH, p, lev)
                            rwtToFind[tr['txHash']].append(usage)

                    item = (tr['txHash'], tr['toFollow'])
                    itemList.append(item)

            #else:
                #print('not following %s' %tr['txHash'])

    return itemList

def analyseTransactions(minAmounts, maxPayout, numberOfAmounts, payouts):

    for directory in listofDirectories:

        #print('READING DIRECTORY %s' %directory)

        abs_file_path1 = os.getcwd() + '/' + directory  + '/allTransa.txt'

        with open(abs_file_path1) as json_file1:
            allTransactions = json.load(json_file1)
        json_file1.close()

        for transaction in allTransactions['transactions']:
            isRWT = isRewarding(transaction)
            if isRWT == True:
                numberOfAmounts.append(len(transaction['ammount']))
                for amm in transaction['ammount']:
                    if amm != 0.0:
                        payouts.append(amm)
        del allTransactions

    minAmounts = getMedian(numberOfAmounts)
    print('median amounts %s' %minAmounts)

    maxPayout = getBound(payouts)
    print('upperbound payout %s' %maxPayout)

    del numberOfAmounts
    del payouts

    return minAmounts, maxPayout

firstBlock = input('first')
lastBlock = input('last')
listofDirectories = []
a = os.listdir('./')
interval = []

transactionSet = {}

minAmounts = 50
maxPayout = 0.1
numberOfAmounts = []
payouts = []

rwtToFind = {}
rwtFound = {}

orderedRWTs = []

visitedDirectories = []
dirToDel = ''

totass = 0
totint = 0
totdif = 0

for i in range(firstBlock, lastBlock+1):
    dir = 'res_blk0%s.dat' %i
    interval.append(dir)

for i in a:
    for j in range(len(interval)):
        if interval[j] == i:
            listofDirectories.append(i)
        listofDirectories.sort()

minAmounts, maxPayout = analyseTransactions(minAmounts, maxPayout, numberOfAmounts, payouts)
gc.collect()

for directory in listofDirectories:

    print('READING DIRECTORY %s' %directory)

    antAdds =  []
    btcAdds = []
    f2Adds = []
    huobiAdds = []
    poolinAdds = []

    coinbaseSet = collections.OrderedDict()

    abs_file_path2 = os.getcwd() + '/' + directory  + '/allCoinbaseTransa.txt'

    with open(abs_file_path2) as json_file2:
        allCoinbaseTransactions = json.load(json_file2)
    json_file2.close()

    abs_file_path3 = os.getcwd() + '/' + directory  + '/allPoolsCoinbase.txt'

    with open(abs_file_path3) as json_file3:
        otherCoinbase = json.load(json_file3)
    json_file3.close()

    for otherPoolsC in otherCoinbase ['CoinbaseTransactions']:
        coinbaseSet[otherPoolsC['txHash']] = otherPoolsC

    for coinbase in allCoinbaseTransactions['CoinbaseTransactions']:
        coinbaseSet[coinbase['txHash']] = coinbase

    if dirToDel != '':
        abs_file_path4 = os.getcwd() + '/' + dirToDel  + '/dataStructure.txt'

        with open(abs_file_path4) as json_file4:
            structureToDel = json.load(json_file4)
        json_file4.close()

        #print('deleting %s' %dirToDel)
        for idToDel in structureToDel :

            l = 0
            while (l<len(transactionSet[idToDel])):
                t = transactionSet[idToDel][l]

                if t['txHash'] in structureToDel[idToDel]:

                    transactionSet[idToDel].remove(t)

                    if t['txHash'] in rwtToFind:
                        del rwtToFind[t['txHash']]
                    if t['txHash'] in rwtFound:
                        del rwtFound[t['txHash']]

                else:
                    l = l + 1

            if len(transactionSet[idToDel]) == 0:
                    del transactionSet[idToDel]

        del structureToDel
        gc.collect()

    dirToDel = directory

    indexDir = listofDirectories.index(directory)
    for d in range(indexDir, (indexDir+8)):
        if d < len(listofDirectories) and listofDirectories[d] not in visitedDirectories:

            #print('opening block %s' %listofDirectories[d])
            visitedDirectories.append(listofDirectories[d])

            toDelete = {}
            rewardingTransactions = []

            abs_file_path5 = os.getcwd() + '/' + listofDirectories[d]  + '/allTransa.txt'

            with open(abs_file_path5) as json_file5:
                allTransactions = json.load(json_file5)
            json_file5.close()

            for transaction in allTransactions['transactions']:

                addresses = transaction['receiver'].split("_")
                del addresses[0]
                toFollow = getAddressesToFollow(transaction, addresses)
                isRWT = isRewarding(transaction)
                if isRWT is True:
                    rwtToFind[transaction['txHash']] = []
                    rewardingTransactions.append(transaction)

                for idx in transaction['txID']:

                    pos = transaction['txID'].index(idx)
                    prevPos = transaction['positions'][pos]
                    relevantData = {'txHash': transaction['txHash'],'prevPos': prevPos, 'toFollow': tuple(toFollow), 'rwt': isRWT}

                    if idx not in transactionSet:
                        transactionSet[idx] = []
                    if relevantData not in transactionSet[idx]:
                        transactionSet[idx].append(relevantData)

                    if idx not in toDelete:
                        toDelete[idx] = []
                    if transaction['txHash'] not in toDelete[idx]:
                        toDelete[idx].append(transaction['txHash'])

            abs_file_pathS = os.getcwd() + '/' + listofDirectories[d]  + '/dataStructure.txt'

            with open(abs_file_pathS, 'w') as outfile:
                json.dump(toDelete, outfile)

            abs_file_pathRT = os.getcwd() + '/' + listofDirectories[d]  + '/rewardingTransa.txt'

            with open(abs_file_pathRT, 'w') as outfile:
                json.dump(rewardingTransactions, outfile)

            del rewardingTransactions
            del allTransactions
            gc.collect()

    #print('%s COINBASE TO FOLLOW' %len(coinbaseSet))
    for n, coinbaseHash in enumerate(coinbaseSet):

        pool = coinbaseSet[coinbaseHash]['nameOfMP']
        transactions = []
        tToFollow = []
        level = 0
        subList = []
        #print('N: %s FROM POOL %s' %(n,pool))

        tToFollow.append(0)
        transactions.append((coinbaseHash, tToFollow))

        while(len(transactions)>0):
            sub = follow(transactions[0][0], transactions[0][1], pool, level, coinbaseHash)

            if len(sub) > 0:
                for s in sub:
                    subList.append(s)
            del transactions[0]

            if len(transactions) == 0 and len(subList) > 0:
                #print('next level: %s transactions'%len(subList))
                level = level + 1
                j = 0
                while(len(subList) > 0):
                    transactions.append(subList.pop(j))

    gc.collect()

    abs_file_path6 = os.getcwd() + '/' + directory  + '/rewardingTransa.txt'

    with open(abs_file_path6) as json_file6:
        RWTs = json.load(json_file6)
    json_file6.close()

    associated = 0
    assToPoolOfInterest = 0

    for rwt in RWTs:

        rwtH = rwt['txHash']
        if rwtH in rwtToFind:

            if len(rwtToFind[rwtH]) > 0:
                #print('%s: %s' %(rwtH, rwtToFind[rwtH]))

                associated = associated + 1
                lowerLevel = rwtToFind[rwtH][0][2]
                countA = 0
                countB = 0
                countF = 0
                countH = 0
                countP = 0

                for r in rwtToFind[rwtH]:
                    if r[2] < lowerLevel:
                        lowerLevel = r[2]
                    if r[1] == 'AntPool':
                        countA = countA + 1
                    elif r[1] == 'BTCPool':
                        countB = countB + 1
                    elif r[1] == 'F2Pool':
                        countF = countF + 1
                    elif r[1] == 'HoubiPool':
                        countH = countH + 1
                    elif r[1] == 'PoolinPool':
                        countP = countP + 1

                mostFrequentPools = []
                minCount = max(countA, countB, countF, countH, countP)

                if countA == minCount:
                    mostFrequentPools.append('AntPool')
                if countB == minCount:
                    mostFrequentPools.append('BTCPool')
                if countF == minCount:
                    mostFrequentPools.append('F2Pool')
                if countH == minCount:
                    mostFrequentPools.append('HuobiPool')
                if countP == minCount:
                    mostFrequentPools.append('PoolinPool')

                lowerLevelPools = []

                for r in rwtToFind[rwtH]:
                    if r[2] == lowerLevel and r[1] not in lowerLevelPools:
                        lowerLevelPools.append(r[1])

                rwtPool = 'Unknown'
                #print(mostFrequentPools)
                #print(lowerLevelPools)
                if  len(lowerLevelPools) == 1:
                    #vince lowerLevelPools anche se diversi
                    rwtPool =  lowerLevelPools[0]
                elif len(lowerLevelPools) > 1:
                    # quale dei lowerLevelPools vince? quello che e anche in mostFrequentPools, se c e altrimenti non si puo dire
                    pList = []
                    for p in lowerLevelPools:
                        if p in mostFrequentPools:
                            pList.append(p)
                    if len(pList) == 1:
                        rwtPool = pList[0]

                if rwtPool != 'Other' and rwtPool != 'Unknown':

                    rwt['nameMP'] = rwtPool
                    rwt['leaf'] = lowerLevel
                    orderedRWTs.append(rwt)

                    assToPoolOfInterest = assToPoolOfInterest + 1

                    ads = rwt['receiver'].split("_")
                    del ads[0]

                    if len(ads) != len(rwt['ammount']):
                        rwt = deleteZeroAmount(rwt)

                    for n in range(0, len(ads)):
                        if rwt['ammount'][n] < maxPayout:

                            if rwtPool == 'AntPool':
                                antAdds.append(ads[n])
                            if rwtPool == 'BTCPool':
                                btcAdds.append(ads[n])
                            if rwtPool == 'F2Pool':
                                f2Adds.append(ads[n])
                            if rwtPool == 'HuobiPool':
                                huobiAdds.append(ads[n])
                            if rwtPool == 'PoolinPool':
                                poolinAdds.append(ads[n])

    #print('%s rwts associated to a pool, %s associated to a pool of interest' %(associated,assToPoolOfInterest))
    diff = len(RWTs) - associated
    #print('%s rwts not associated' %diff)
    totass = totass + associated
    totint = totint + assToPoolOfInterest
    totdif = totdif + diff

    del RWTs

    abs_file_path4 = os.getcwd()  + '/' + directory  + '/AntAdds.txt'
    abs_file_path5 = os.getcwd()  + '/' + directory  + '/BTCAdds.txt'
    abs_file_path6 = os.getcwd()  + '/' + directory  + '/F2Adds.txt'
    abs_file_path7 = os.getcwd()  + '/' + directory  + '/HuobiAdds.txt'
    abs_file_path8 = os.getcwd()  + '/' + directory  + '/PoolinAdds.txt'

    with open(abs_file_path4, 'w') as outfile:
        json.dump(antAdds, outfile)

    with open(abs_file_path5, 'w') as outfile:
        json.dump(btcAdds, outfile)

    with open(abs_file_path6, 'w') as outfile:
        json.dump(f2Adds, outfile)

    with open(abs_file_path7, 'w') as outfile:
        json.dump(huobiAdds, outfile)

    with open(abs_file_path8, 'w') as outfile:
        json.dump(poolinAdds, outfile)

    del antAdds
    del btcAdds
    del f2Adds
    del huobiAdds
    del poolinAdds

    gc.collect()

abs_file_path9 = os.getcwd()  + '/rewardingTransactions.txt'

with open(abs_file_path9, 'w') as outfile:
    json.dump(orderedRWTs, outfile)

print('totass %s'%totass)
print('totint %s'%totint)
print('totdif %s'%totdif)
