# author: Eugenio CORTESI

import os
import json
import simplejson
import collections
import time
from datetime import datetime
import statistics
import networkx as nx
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import numpy as np
import pandas as pd
import gc

plt.rcParams['font.size'] = 22

def epochsBoxplot():
    print('epochs boxplots')

    print('before and after')
    blist = []
    l1 = []
    for el in epochsLength:
        l1.append(el/3600)
    blist.append(l1)
    #plt.figure(figsize=(100, 100))
    #plt.ylabel("Distribution epochs length in hours")
    #plt.boxplot(list, vert = True, labels=['epochs'])
    #plt.show()
    print('after the adjustment')
    l2 = []
    for hopper in epochSchedule:
        for epoch in epochSchedule[hopper]:
            start = time.mktime(time.strptime(epoch['epoch start'],"%Y-%m-%d %H:%M:%S"))
            end = time.mktime(time.strptime(epoch['end'],"%Y-%m-%d %H:%M:%S"))
            length = (end - start)/3600
            l2.append(length)
    blist.append(l2)
    labels = ['Before', 'After']
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Epochs length (h)')
    #yint = range(min, max+1)
    #plt.yticks(yint)
    plt.boxplot(blist, vert = True, labels=labels)
    plt.yscale('log')
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.autoscale(True)
    fig.savefig('epochs.png')

    print('epochs length per pool')

    finallist = []

    epochsPoolin = []
    epochsF2 = []
    epochsHuobi = []
    epochsAnt = []
    epochsBTC = []
    for hopper in epochSchedule:
        for epoch in epochSchedule[hopper]:
            start = time.mktime(time.strptime(epoch['epoch start'],"%Y-%m-%d %H:%M:%S"))
            end = time.mktime(time.strptime(epoch['end'],"%Y-%m-%d %H:%M:%S"))
            length = (end - start)/3600
            if epoch['pool'] == 'PoolinPool':
                epochsPoolin.append(length)
            elif epoch['pool'] == 'F2Pool':
                epochsF2.append(length)
            elif epoch['pool'] == 'HuobiPool':
                epochsHuobi.append(length)
            elif epoch['pool'] == 'AntPool':
                epochsAnt.append(length)
            elif epoch['pool'] == 'BTCPool':
                epochsBTC.append(length)
    finallist.append(epochsAnt)
    finallist.append(epochsBTC)
    finallist.append(epochsF2)
    finallist.append(epochsHuobi)
    finallist.append(epochsPoolin)
    labels = ['Ant', 'BTC', 'F2', 'Huobi', 'Poolin']
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Epochs length (h)')
    plt.boxplot(finallist, vert = True, labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('epochSchedule.png')

def getJumpsPerPool():
    antbtc = 0
    antf2 = 0
    anthuobi = 0
    antpoolin = 0
    btcf2 = 0
    btchuobi = 0
    btcpoolin = 0
    f2huobi = 0
    f2poolin = 0
    huobipoolin = 0

    btcant  = 0
    f2ant = 0
    huobiant = 0
    poolinant = 0
    f2btc = 0
    huobibtc = 0
    poolinbtc = 0
    huobif2 = 0
    poolinf2 = 0
    poolinhuobi = 0

    for hopper in rwtPerHoppers:
        for rwt in rwtPerHoppers[hopper]:
            idx = rwtPerHoppers[hopper].index(rwt)
            if idx < len(rwtPerHoppers[hopper]) - 1:
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'AntPool' and  rwt['pool'] == 'BTCPool':
                    antbtc += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'AntPool' and  rwt['pool'] == 'F2Pool':
                    antf2 += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'AntPool' and  rwt['pool'] == 'HuobiPool':
                    anthuobi += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'AntPool' and  rwt['pool'] == 'PoolinPool':
                    antpoolin += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'BTCPool' and  rwt['pool'] == 'F2Pool':
                    btcf2 += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'BTCPool' and  rwt['pool'] == 'HuobiPool':
                    btchuobi += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'BTCPool' and  rwt['pool'] == 'PoolinPool':
                    btcpoolin += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'F2Pool' and  rwt['pool'] == 'HuobiPool':
                    f2huobi += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'F2Pool' and  rwt['pool'] == 'PoolinPool':
                    f2poolin += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'HuobiPool' and  rwt['pool'] == 'PoolinPool':
                    huobipoolin += 1

                if rwtPerHoppers[hopper][idx+1]['pool'] == 'BTCPool' and  rwt['pool'] == 'AntPool':
                    btcant += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'F2Pool' and  rwt['pool'] == 'AntPool':
                    f2ant += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'HuobiPool' and  rwt['pool'] == 'AntPool':
                    huobiant += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'PoolinPool' and  rwt['pool'] == 'AntPool':
                    poolinant += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'F2Pool' and  rwt['pool'] == 'BTCPool':
                    f2btc += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'HuobiPool' and  rwt['pool'] == 'BTCPool':
                    huobibtc += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'PoolinPool' and  rwt['pool'] == 'BTCPool':
                    poolinbtc += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'HuobiPool' and  rwt['pool'] == 'F2Pool':
                    huobif2 += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'PoolinPool' and  rwt['pool'] == 'F2Pool':
                    poolinf2 += 1
                if rwtPerHoppers[hopper][idx+1]['pool'] == 'PoolinPool' and  rwt['pool'] == 'HuobiPool':
                    poolinhuobi += 1
    l1 = []
    l1.append(antbtc)
    l1.append(antf2)
    l1.append(anthuobi)
    l1.append(antpoolin)
    l1.append(btcf2)
    l1.append(btchuobi)
    l1.append(btcpoolin)
    l1.append(f2huobi)
    l1.append(f2poolin)
    l1.append(huobipoolin)

    l2 = []
    l2.append(btcant)
    l2.append(f2ant)
    l2.append(huobiant)
    l2.append(poolinant)
    l2.append(f2btc)
    l2.append(huobibtc)
    l2.append(poolinbtc)
    l2.append(huobif2)
    l2.append(poolinf2)
    l2.append(poolinhuobi)

    #ind = ['antbtc', 'antf2', 'anthuobi', 'antpoolin', 'btcf2', 'btchuobi', 'btcpoolin', 'f2huobi', 'f2poolin', 'huobipoolin', 'btcant', 'f2ant', 'huobiant', 'poolinant', 'f2btc','huobibtc', 'poolinbtc', 'huobif2', 'poolinf2', 'poolinhuobi']
    ind = ['Ant-BTC\nBTC-Ant ', 'An-tF2\nF2-Anr', 'Ant-Huobi\nHuobi-Ant', 'Ant-Poolin\nPoolin-Ant', 'BTC-F2\nF2-BTC', 'BTC-Huobi\nHuobi-BTC', 'BTC-Poolin\nPoolin-BTC', 'F2-Huobi\nHuobi-F2', 'F2-Poolin\nPoolin-F2', 'Huobi-Poolin\nPoolin-Huobi']

    x = np.arange(10)  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.grid(axis='y')
    rects1 = ax.bar(x - width/2, l1, width, color='lightblue')
    rects2 = ax.bar(x + width/2, l2, width, color='#fc8d62')

    ax.set_ylabel('Migrations of overall population')
    ax.set_xlabel('Cross-pooling')
    ax.set_xticks(x)
    ax.set_xticklabels(ind, fontsize=12)

    fig.savefig('Cross-pooling.png')

    li = []
    jumpsBTC = 0
    jumpsHuobi = 0
    jumpsAnt = 0
    jumpsF2 = 0
    jumpsPoolin = 0
    for hopper in hoppers:
        for el in hoppers[hopper]:
            if el['pool'] == 'PoolinPool':
                jumpsPoolin += el['jumps from this pool']
            elif el['pool'] == 'F2Pool':
                jumpsF2 += el['jumps from this pool']
            elif el['pool'] == 'HuobiPool':
                jumpsHuobi += el['jumps from this pool']
            elif el['pool'] == 'AntPool':
                jumpsAnt += el['jumps from this pool']
            elif el['pool'] == 'BTCPool':
                jumpsBTC += el['jumps from this pool']

    li.append(jumpsAnt/2130)
    li.append(jumpsBTC/10704)
    li.append(jumpsF2/19616)
    li.append(jumpsHuobi/7566)
    li.append(jumpsPoolin/3192)
    labels = ['Ant', 'BTC', 'F2', 'Huobi', 'Poolin']
    plt.figure(figsize=(15, 10))
    plt.bar(labels, li, width=0.35, color='lightblue')
    plt.ylabel("Desertation rate on total population")
    fig.savefig('DesertationRate.png')

def getUsersNetwork():

    print('start network')

    minersList = []
    hoppersList = []
    labels = {}
    plt.figure(figsize=(10, 10))
    G = nx.Graph()
    G.add_node('BTCPool')
    G.add_node('F2Pool')
    G.add_node('PoolinPool')
    G.add_node('AntPool')
    G.add_node('HuobiPool')

    for node in G:
        labels[node]=node

    for miner in allMiners:

        if len(allMiners[miner]) > 5 and len(allMiners[miner]) < 20:

            poolList = []
            m = 'Miner'+ str(miner+1)
            G.add_node(m)
            minersList.append(m)

            for h in allHash[miner]:
                rwt = orderedRWT[h]
                if rwt['nameMP'] not in poolList:
                    poolList.append(rwt['nameMP'])

            if len(poolList) > 1:
                hoppersList.append(m)

            for pool in poolList:
                G.add_edge(m, pool)

    print('start drawing')

    layout = nx.spring_layout(G,k=10.5/np.sqrt(len(G.nodes())))
    print('layout done')
    nx.draw_networkx_nodes(G, layout, nodelist=minersList, node_size=100, node_color='#AAAAAA')
    nx.draw_networkx_nodes(G, layout, nodelist=hoppersList, node_size=100, node_color='#fc8d62')
    nx.draw_networkx_nodes(G, layout, nodelist=['BTCPool', 'F2Pool', 'PoolinPool', 'AntPool', 'HuobiPool'], node_size=2000, node_color='lightblue')
    nx.draw_networkx_edges(G, layout, width=0.3, edge_color="#cccccc")
    nx.draw_networkx_labels(G, layout, labels, font_size=10, font_color='k')
    plt.axis('off')
    plt.savefig('UsersNetwork.png')

def contaRWT():

    countAnt = 0
    countBTC = 0
    countF2 = 0
    countHuobi = 0
    countPoolin = 0

    for rwt in RWTs:
        if rwt['nameMP'] == 'AntPool':
            countAnt += 1
        if rwt['nameMP'] == 'BTCPool':
            countBTC += 1
        if rwt['nameMP'] == 'F2Pool':
            countF2 += 1
        if rwt['nameMP'] == 'HuobiPool':
            countHuobi += 1
        if rwt['nameMP'] == 'PoolinPool':
            countPoolin +=1

    print('AntPool RWTs %s' %countAnt)
    print('BTCPool RWTs %s' %countBTC)
    print('F2Pool RWTs %s' %countF2)
    print('HuobiPool RWTs %s' %countHuobi)
    print('PoolinPool RWTs %s' %countPoolin)

def contaIndirizzi():

    addresses = {}

    for rwt in RWTs:
        adds = rwt['receiver'].split('_')
        del adds[0]

        for el in adds:
            if el not in addresses:
                addresses[el] = None

    print(len(addresses))

def contaHoppers():

    anthoppers = 0
    btchoppers = 0
    f2hoppers = 0
    huobihoppers = 0
    poolinhoppers = 0

    for hopper in hoppers:
        pools = []
        for el in hoppers[hopper]:
            if el['pool'] not in pools:
                pools.append(el['pool'])
        for p in pools:
            if p == 'AntPool':
                anthoppers +=1
            if p == 'BTCPool':
                btchoppers +=1
            if p == 'F2Pool':
                f2hoppers+=1
            if p == 'HuobiPool':
                huobihoppers+=1
            if p == 'PoolinPool':
                poolinhoppers +=1

    print('in ant %s general hoppers' %anthoppers)
    print('in btc %s general hoppers' %btchoppers)
    print('in f2 %s general hoppers' %f2hoppers)
    print('in huobi %s general hoppers' %huobihoppers)
    print('in poolin %s general hoppers' %poolinhoppers)

    antacthoppers = 0
    btcacthoppers = 0
    f2acthoppers = 0
    huobiacthoppers = 0
    poolinacthoppers = 0

    for hopper in realisticHoppers:
        pools = []
        for pool in realisticHoppers[hopper]:
            if pool not in pools:
                pools.append(pool)
        for p in pools:
            if p == 'AntPool':
                antacthoppers +=1
            if p == 'BTCPool':
                btcacthoppers +=1
            if p == 'F2Pool':
                f2acthoppers+=1
            if p == 'HuobiPool':
                huobiacthoppers+=1
            if p == 'PoolinPool':
                poolinacthoppers +=1

    print('in ant %s active hoppers' %antacthoppers)
    print('in btc %s active hoppers' %btcacthoppers)
    print('in f2 %s active hoppers' %f2acthoppers)
    print('in huobi %s active hoppers' %huobiacthoppers)
    print('in poolin %s active hoppers' %poolinacthoppers)

    antinacthoppers = anthoppers - antacthoppers
    btcinacthoppers = btchoppers - btcacthoppers
    f2inacthoppers = f2hoppers - f2acthoppers
    huobiinacthoppers = huobihoppers - huobiacthoppers
    poolininacthoppers = poolinhoppers - poolinacthoppers

    print('in ant %s inactive hoppers' %antinacthoppers)
    print('in btc %s inactive hoppers' %btcinacthoppers)
    print('in f2 %s inactive hoppers' %f2inacthoppers)
    print('in huobi %s inactive hoppers' %huobiinacthoppers)
    print('in poolin %s inactive hoppers' %poolininacthoppers)

def baractive():

    countAnt = 0
    countBTC = 0
    countF2 = 0
    countHuobi = 0
    countPoolin = 0

    for h in epochSchedule:
        for epoch in epochSchedule[h]:

            if epoch['pool'] == 'AntPool':
                countAnt += 1
            if epoch['pool'] == 'BTCPool':
                countBTC += 1
            if epoch['pool'] == 'F2Pool':
                countF2 += 1
            if epoch['pool'] == 'HuobiPool':
                countHuobi += 1
            if epoch['pool'] == 'PoolinPool':
                countPoolin +=1

    antlist = 0
    btclist = 0
    f2list = 0
    huobilist = 0
    poolinlist = 0
    for hopper in realisticHoppers:
        for pool in realisticHoppers[hopper]:
            current = ''
            for epoch in realisticHoppers[hopper][pool]:
                if epoch['end'] != current:
                    current = epoch['end']
                    if pool == 'AntPool':
                        antlist += 1
                    if pool == 'BTCPool':
                        btclist += 1
                    if pool == 'F2Pool':
                        f2list += 1
                    if pool == 'HuobiPool':
                        huobilist += 1
                    if pool == 'PoolinPool':
                        poolinlist +=1

    percant = (100 * antlist) / countAnt
    percbtc = (100 * btclist) / countBTC
    percf2 = (100 * f2list) / countF2
    perchuobi = (100 * huobilist) / countHuobi
    percpoolin = (100 * poolinlist) / countPoolin


    finlist = []
    finlist.append(percant)
    finlist.append(percbtc)
    finlist.append(percf2)
    finlist.append(perchuobi)
    finlist.append(percpoolin)


    """finlist.append(antlist)
    finlist.append(btclist)
    finlist.append(f2list)
    finlist.append(huobilist)
    finlist.append(poolinlist)"""

    labels = ['Ant', 'BTC', 'F2', 'Huobi', 'Poolin']
    plt.figure(figsize=(10, 10))
    plt.bar(labels, finlist, width=0.35, color='lightblue')
    plt.ylabel('Percentage of overlapped epoch')
    #plt.xticks(fontsize=20)
    plt.savefig('overlappedEpoch.png')

# ---------------------FUNZIONE 7
def boxplotwindow():

    antw = []
    btcw = []
    f2w = []
    huobiw = []
    poolinw = []

    for h in roundsPerWindow:
    	for pool in roundsPerWindow[h]:
            for window in roundsPerWindow[h][pool]:

                index = window.find('-perc: ')
                perc = float(window[(index+7):])
                if pool == 'AntPool':
                    antw.append(perc)
                if pool == 'BTCPool':
                    btcw.append(perc)
                if pool == 'F2Pool':
                    f2w.append(perc)
                if pool == 'HuobiPool':
                    huobiw.append(perc)
                if pool == 'PoolinPool':
                    poolinw.append(perc)

    finlist = []
    finlist.append(antw)
    finlist.append(btcw)
    finlist.append(f2w)
    finlist.append(huobiw)
    finlist.append(poolinw)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Median percentage of window coverage')
    labels = ['Ant', 'BTC', 'F2', 'Huobi','Poolin']
    plt.boxplot(finlist, vert = True, whis=[5,95], labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('windowCoverage.png')

    antw = []
    btcw = []
    f2w = []
    huobiw = []
    poolinw = []

    for h in roundsPerWindow:
    	for pool in roundsPerWindow[h]:
            for window in roundsPerWindow[h][pool]:

                index = window.find('-ep.len: ')
                to = window.find('-perc: ')
                if len(roundsPerWindow[h][pool][window]) > 0:
                    perc = float(window[(index+9):(to-2)]) / len(roundsPerWindow[h][pool][window])

                    if pool == 'AntPool':
                        antw.append(perc)
                    if pool == 'BTCPool':
                        btcw.append(perc)
                    if pool == 'F2Pool':
                        f2w.append(perc)
                    if pool == 'HuobiPool':
                        huobiw.append(perc)
                    if pool == 'PoolinPool':
                        poolinw.append(perc)

    finlist = []
    finlist.append(antw)
    finlist.append(btcw)
    finlist.append(f2w)
    finlist.append(huobiw)
    finlist.append(poolinw)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Median percentage of rounds lengths in a windows')
    labels = ['Ant', 'BTC', 'F2', 'Huobi','Poolin']
    plt.boxplot(finlist, vert = True, whis=[5,95], labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('roundsLengths.png')


def rewards():

    mto = {}
    nmto = {}
    for m in rwtPerHoppers:
        el = 'h' + m[11:]
        print(el)
        mto[el] = None
        for ac in realisticHoppers:
            if ac ==  el:
                mto[el] = 'active'
        if mto[el] == None:
            for h in hoppers:
                if h == el:
                    mto[el] = 'inactive'
        if mto[el] == None:
            mto[el] = 'normal'

    normalmf = []
    activehf = []
    inactivehf = []

    normalme = []
    activehe = []
    inactivehe = []

    normalmemed = []
    activehemed = []
    inactivehemed = []

    for m in rwtPerHoppers:
        miner = 'h' + m[11:]
        if miner in mto:
            print('%s has more than one addrs' %miner)
            avgfreq = 0
            avgearn = 0
            avgearnmed = 0

            #calcola media frequenza e media guadagno
            sumf = []
            summed = []
            sume = 0
            count = 0
            prevtime = ''
            for rwt in rwtPerHoppers[m]:
                count += 1
                sume = sume + rwt['amount']
                summed.append(rwt['amount'])
                if prevtime != '':
                    prev = time.mktime(time.strptime(prevtime,"%Y-%m-%d %H:%M:%S"))
                    curr = time.mktime(time.strptime(rwt['time'],"%Y-%m-%d %H:%M:%S"))
                    interval = (curr - prev )/3600
                    #sumf = sumf + interval
                    sumf.append(interval)
                prevtime = rwt['time']

            #avgfreq = sumf / count
            #avgearn = sume / count
            #if len(sume)>0 and len(sumf)>0:
            if sume>0 and len(sumf)>0 and len(summed)>0:

                avgfreq = statistics.median(sumf)
                avgearnmed = statistics.median(summed)
                avgearn = sume

                if mto[miner] == 'active':
                    activehf.append(avgfreq)
                    activehe.append(avgearn)
                    activehemed.append(avgearnmed)

                if mto[miner] == 'inactive':
                    inactivehf.append(avgfreq)
                    inactivehe.append(avgearn)
                    inactivehemed.append(avgearnmed)

                if mto[miner] == 'normal':
                    normalmf.append(avgfreq)
                    normalme.append(avgearn)
                    normalmemed.append(avgearnmed)

        #else:

    print(normalmf)
    print(normalme)
    print(normalmemed)

    print(activehf)
    print(activehe)
    print(activehemed)

    print(inactivehf)
    print(inactivehe)
    print(inactivehemed)

    totlistf = []
    totliste = []
    totlistemed = []

    totlistf.append(normalmf)
    totliste.append(normalme)
    totlistemed.append(normalmemed)

    totlistf.append(activehf)
    totliste.append(activehe)
    totlistemed.append(activehemed)

    totlistf.append(inactivehf)
    totliste.append(inactivehe)
    totlistemed.append(inactivehemed)

    labels = ['Miners', 'Cross-epoch h.', 'Intra-epoch h.']

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Average of time between earnings (s)')
    plt.boxplot(totlistf, vert = True, whis=[5,95], labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('earningsPerUser.png')

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Average of total earnings per miner (BTC)')
    plt.boxplot(totliste, vert = True, whis=[5,95], labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('TotalEarningPerUser.png')

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Average earnings per miner (BTC)')
    plt.boxplot(totlistemed, vert = True, whis=[5,95], labels=labels)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.yscale('log')
    plt.autoscale(True)
    fig.savefig('MedianEarningsPerUser.png')

def rewardmedi():

    a = []
    b = []
    f = []
    h = []
    p = []

    aa = []
    bb = []
    ff = []
    hh = []
    pp = []



    for rwt in RWTs:

        sum = 0
        count = 0
        avg = 0

        for amm in rwt['ammount']:
            if amm < 0.06:
                sum = sum + amm
                count = count + 1

        avg = sum / count

        if rwt['nameMP'] == 'AntPool':
            aa.append(count)
            a.append(avg)
        if rwt['nameMP'] == 'BTCPool':
            bb.append(count)
            b.append(avg)
        if rwt['nameMP'] == 'F2Pool':
            ff.append(count)
            f.append(avg)
        if rwt['nameMP'] == 'HuobiPool':
            hh.append(count)
            h.append(avg)
        if rwt['nameMP'] == 'PoolinPool':
            pp.append(count)
            p.append(avg)


    dimensions = []
    dimensions.append(a)
    dimensions.append(b)
    dimensions.append(f)
    dimensions.append(h)
    dimensions.append(p)

    lens = []
    lens.append(aa)
    lens.append(bb)
    lens.append(ff)
    lens.append(hh)
    lens.append(pp)

    labels = ['Ant', 'BTC', 'F2', 'Huobi','Poolin']

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Average amount of BTC sent')
    plt.boxplot(dimensions, vert = True, labels=labels)
    plt.yscale('log')
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.autoscale(True)
    fig.savefig('BTCSent.png')

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.grid(axis='y')
    plt.ylabel('Number of outgoing transfers')
    plt.boxplot(lens, vert = True, labels=labels)
    plt.yscale('log')
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=16)
    plt.autoscale(True)
    fig.savefig('outgoingTransfers.png')

def salti():
    li = []
    jumpsBTC = 0
    jumpsHuobi = 0
    jumpsAnt = 0
    jumpsF2 = 0
    jumpsPoolin = 0
    for hopper in hoppers:
        for el in hoppers[hopper]:
            if el['pool'] == 'PoolinPool':
                jumpsPoolin += el['jumps from this pool']
            elif el['pool'] == 'F2Pool':
                jumpsF2 += el['jumps from this pool']
            elif el['pool'] == 'HuobiPool':
                jumpsHuobi += el['jumps from this pool']
            elif el['pool'] == 'AntPool':
                jumpsAnt += el['jumps from this pool']
            elif el['pool'] == 'BTCPool':
                jumpsBTC += el['jumps from this pool']

    li.append(jumpsAnt/723)
    li.append(jumpsBTC/7417)
    li.append(jumpsF2/7458)
    li.append(jumpsHuobi/6862)
    li.append(jumpsPoolin/737)
    labels = ['Ant', 'BTC', 'F2', 'Huobi', 'Poolin']
    plt.figure(figsize=(10, 10))
    plt.bar(labels, li, width=0.35, color='lightblue')
    plt.ylabel("Desertation rate on total population")
    #plt.xticks(fontsize=20)
    plt.savefig('DesertationRate2.png')

def getPoolMiners():

    countBTC = 0
    countF2 = 0
    countAnt = 0
    countPoolin = 0
    countHuobi  = 0
    for miner in allMiners:
        if len(allMiners[miner]) >= 1 :

            btc = False
            f2 = False
            ant = False
            poolin = False
            huobi = False

            for h in allHash[miner]:
                rwt = orderedRWT[h]

                if rwt['nameMP'] == 'PoolinPool':
                    poolin = True
                if rwt['nameMP'] == 'F2Pool':
                    f2 = True
                if rwt['nameMP'] == 'HuobiPool':
                    huobi = True
                if rwt['nameMP'] == 'AntPool':
                    ant = True
                if rwt['nameMP'] == 'BTCPool':
                    btc = True
            
            if poolin == True:
                countPoolin = countPoolin +1
            if f2 == True:
                countF2 = countF2 +1
            if huobi == True:
                countHuobi = countHuobi +1
            if ant == True:
                countAnt = countAnt+1
            if btc == True:
                countBTC = countBTC +1

    print('countPoolin %s'%countPoolin)
    print('countF2 %s'%countF2)
    print('countHuobi %s'%countHuobi)
    print('countAnt %s'%countAnt)
    print('countBTC %s'%countBTC)


# -----------------------------------------------------------------------

file1 = os.getcwd() + '/epochsLength.txt'
file2 = os.getcwd() + '/minersCompleted.txt'
file3 = os.getcwd() + '/poolJumpsPerHoppers.txt'
file4 = os.getcwd() + '/realisticHoppers.txt'
file5 = os.getcwd() + '/rwtPerHoppers.txt'
file7 = os.getcwd() + '/roundsPerWindow.txt'
file9 = os.getcwd() + '/principalAddresses.txt'
file10 = os.getcwd() + '/hoppersEarnings.txt'
file11 = os.getcwd() + '/rewardingTransactions.txt'
file12 = os.getcwd() +  '/epochsScheduleOrdered.txt'

with open(file1) as json_file1:
	epochsLength = json.load(json_file1)
json_file1.close()

with open(file2) as json_file2:
	allM = json.load(json_file2)
json_file2.close()

with open(file3) as json_file3:
    hoppers = simplejson.load(json_file3, object_pairs_hook = collections.OrderedDict)
json_file3.close()

with open(file4) as json_file4:
    realisticHoppers = simplejson.load(json_file4, object_pairs_hook = collections.OrderedDict)
json_file4.close()

with open(file5) as json_file5:
    rwtPerHoppers = simplejson.load(json_file5, object_pairs_hook = collections.OrderedDict)
json_file5.close()

with open(file7) as json_file7:
	roundsPerWindow = simplejson.load(json_file7, object_pairs_hook = collections.OrderedDict)
json_file7.close()

with open(file10) as json_file10:
	hoppersEarnings = simplejson.load(json_file10, object_pairs_hook = collections.OrderedDict)
json_file10.close()

with open(file11) as json_file11:
    RWTs = json.load(json_file11)
json_file11.close()

with open(file12) as json_file12:
    epochSchedule = json.load(json_file12, object_pairs_hook = collections.OrderedDict)
json_file12.close()

orderedRWT = {}
receiversAddresses = {}
listOfAmounts=[]
allMiners = {}
allHash = {}

for rwt in RWTs:

    orderedRWT[rwt['txHash']] = rwt

    receivers = rwt['receiver'].split("_")
    del receivers[0]

    for receiver in receivers:

        if receiver not in receiversAddresses:
            receiversAddresses[receiver] = []

        if rwt['txHash'] not in receiversAddresses[receiver]:
            receiversAddresses[receiver].append(rwt['txHash'])

#del RWTs

c = 0
for m in allM:
    allMiners[c] = {}
    allHash[c] = {}
    hashList = []

    for a in m:
        allMiners[c][a] = None

        if a in receiversAddresses:
            for h in receiversAddresses[a]:
                if h not in hashList:
                    hashList.append(h)

    allHash[c] = hashList
    del hashList

    c = c + 1

gc.collect()

# print('epochsBoxplot')
# epochsBoxplot()
# print('getJumpsPerPool')
# getJumpsPerPool()
# print('getUsersNetwork')
# getUsersNetwork()
# print('contaRWT')
# contaRWT()
# print('contaIndirizzi')
# contaIndirizzi()
# print('rewardmedi')
# rewardmedi()
# print('contaHoppers')
del RWTs
# contaHoppers()
# print('baractive')
# baractive()
# print('boxplotwindow')
# boxplotwindow()
# print('rewards')
# rewards()
# print('salti')
# salti()
# print('getPoolMiners')
# getPoolMiners()
# print('getPoolMiners')
# getPoolMiners()

