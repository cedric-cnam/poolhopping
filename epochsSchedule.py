# author: Eugenio CORTESI

import json
import sys
import os
import time
import collections
import statistics
import numpy as np

def getEpochIntervals():   #it is better to calculate delta between epochs in separated pools?
    list = []
    for hopper in rwtPerHoppers:
        for rwt in rwtPerHoppers[hopper]:
            idx = rwtPerHoppers[hopper].index(rwt)
            if idx > 0:
                delta = time.mktime(time.strptime(rwt['time'],"%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(previous['time'],"%Y-%m-%d %H:%M:%S"))
                delta = delta
                list.append(delta)
                previous = rwt
            else:
                previous = rwt
    return list

def getEpochMedian(list):
    return statistics.median(list)

def getUpperBund(list):
    sorted(list)
    q1, q3= np.percentile(list,[25,75])
    iqr = q3 - q1
    #upper_bound = q3 +(1.5 * iqr)
    return q3

def getEpochBeginning(rwt, idx, list):
    if idx == -1 :                        #if its the first epoch it gets the starting date of the analysis
        secs = time.mktime(time.strptime(rwt['time'],"%Y-%m-%d %H:%M:%S")) - upperBound
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs))
    else:
        start = list[idx]['time']              #if it is not the first epoch it gets the last epoch end as starting time for this epoch
        if (time.mktime(time.strptime(rwt['time'],"%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(start,"%Y-%m-%d %H:%M:%S"))) > upperBound:
            secs = time.mktime(time.strptime(rwt['time'],"%Y-%m-%d %H:%M:%S")) - upperBound
            start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs))
    return start

def remove100Validation(start, end): # 100 validations, each 10 minutes -> 60 x 10 x 100 = 6k seconds
    start = time.mktime(time.strptime(start,"%Y-%m-%d %H:%M:%S"))
    start = start - 60000
    start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
    end = time.mktime(time.strptime(end,"%Y-%m-%d %H:%M:%S"))
    end = end - 60000
    end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end))
    return start, end


#this function creates the schedule of epoch of each hopper in each pool.
def createEpochsSchedule(epochs):
    for hopper in rwtPerHoppers:
        print(hopper)
        id = rwtPerHoppers.keys().index(hopper) +1
        epochs[hopper]= collections.OrderedDict()
        epochList = []
        for rwt in rwtPerHoppers[hopper]:                 #for each hopper it creates a list of his epochs
            idx = rwtPerHoppers[hopper].index(rwt)
            i = 0
            lastIdx = - 1
            found = False
            while (i < idx and found is False):
                if rwtPerHoppers[hopper][i]['pool'] == rwt['pool']:
                    if rwtPerHoppers[hopper][i]['time'] < rwt['time']:
                        lastIdx = i
                    else:
                        found = True                # when if is false means that it founded the last rwt in that pool, and 'i' saved its index
                i = i + 1
            start = getEpochBeginning(rwt, lastIdx, rwtPerHoppers[hopper])
            start, end = remove100Validation(start, rwt['time'])
            imput = collections.OrderedDict([('epoch start', start), ('end', end), ('pool', rwt['pool']) ])
            if imput not in epochList:
                epochList.append(imput)
        epochs[hopper] = epochList
    return epochs

epochs = collections.OrderedDict()
epochIntervals = []
median = 0
upperBound = 0

file1 = os.getcwd() + '/rwtPerHoppers.txt'

with open(file1) as json_file1:
    rwtPerHoppers = json.load(json_file1, object_pairs_hook = collections.OrderedDict)
json_file1.close()

epochIntervals = getEpochIntervals()
median = getEpochMedian(epochIntervals)
print(median)
upperBound = getUpperBund(epochIntervals)
print(upperBound)
epochs = createEpochsSchedule(epochs)

with open('epochsScheduleOrdered.txt', 'w') as outfile:
    outfile.write("{")
    for line in epochs:
        outfile.write('"' + line + '":')
        outfile.write("\n[")
        for el in epochs[line]:
            outfile.write(json.dumps(el))
            if epochs[line].index(el) != len(epochs[line])-1:
                outfile.write(",\n")
        if epochs.keys().index(line) != len(epochs)-1:
            outfile.write("],\n")
        else:
            outfile.write("]\n")
    outfile.write("}")

with open('epochsLength.txt', 'w') as outfile:
	json.dump(epochIntervals, outfile)
