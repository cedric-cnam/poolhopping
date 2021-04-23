# author: Eugenio CORTESI

import json
import os
import time
import collections
import statistics
import collections

def countRounds(pool, windowStart, windowEnds, roundsPerWindows, overlapsWith, percentage, length):
    if pool not in roundsPerWindows.keys():
        roundsPerWindows[pool] = collections.OrderedDict()
    list = []
    for round in roundsSchedule[pool]:
        if round >= windowStart and round <= windowEnds:
            list.append(round)
    w = windowStart + ' - ' + windowEnds + ' - ' + overlapsWith + ' -ep.len: ' + str(length) + ' -perc: ' + str(percentage)
    roundsPerWindows[pool][w] = collections.OrderedDict()
    if len(list) > 0:
        roundsPerWindows[pool][w] = list
    return roundsPerWindows

def createWindows(roundsPerWindowsPerHopper, windowsLength):
    maxWindow = 0
    for hopper in overlappedEpochs:
        roundsPerWindowsPerHopper[hopper] = collections.OrderedDict()
        roundsPerWindows = collections.OrderedDict()
        for pool in overlappedEpochs[hopper]:
            for epoch in overlappedEpochs[hopper][pool]:
                overlapsWith = epoch['overlaps with']
                index = epoch['index']
                e1start = overlappedEpochs[hopper][overlapsWith][index]['epoch start']
                e1end = overlappedEpochs[hopper][overlapsWith][index]['end']
                e2start = epoch ['epoch start']
                e2end = epoch ['end']
                start = 0
                end = 0
                window = 0
                if e1start < e2start:
                    if e1end < e2end:
                        start = time.mktime(time.strptime(e2start,"%Y-%m-%d %H:%M:%S"))
                        end = time.mktime(time.strptime(e1end,"%Y-%m-%d %H:%M:%S"))
                    else:
                        start = time.mktime(time.strptime(e2start,"%Y-%m-%d %H:%M:%S"))
                        end = time.mktime(time.strptime(e2end,"%Y-%m-%d %H:%M:%S"))
                else:
                    if e1end > e2end:
                        start = time.mktime(time.strptime(e1start,"%Y-%m-%d %H:%M:%S"))
                        end = time.mktime(time.strptime(e2end,"%Y-%m-%d %H:%M:%S"))
                    else:
                        start = time.mktime(time.strptime(e1start,"%Y-%m-%d %H:%M:%S"))
                        end = time.mktime(time.strptime(e1end,"%Y-%m-%d %H:%M:%S"))
                window = (end - start)/3600
                ws = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
                we = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end))
                #epoch length
                length = (time.mktime(time.strptime(e2end,"%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(e2start,"%Y-%m-%d %H:%M:%S")))/3600
                percentage = (100/length)*window
                #print(length)
                roundsPerWindows = countRounds(pool, ws, we, roundsPerWindows, overlapsWith, round(percentage,2), length)
                windowsLength.append(window)
                if window > maxWindow:
                    maxWindow = window
        roundsPerWindowsPerHopper[hopper] = roundsPerWindows
    return maxWindow, windowsLength

file1 = os.getcwd() + '/realisticHoppers.txt'
file2 = os.getcwd() + '/roundsSchedule.txt'

with open(file1) as json_file1:
	overlappedEpochs = json.load(json_file1, object_pairs_hook = collections.OrderedDict)
json_file1.close()

with open(file2) as json_file2:
	roundsSchedule = json.load(json_file2, object_pairs_hook = collections.OrderedDict)
json_file2.close()

maxWindow = 0
windowsLength = []
roundsPerWindows = collections.OrderedDict()

maxWindow, windowsLength = createWindows(roundsPerWindows, windowsLength)
print(maxWindow)

with open('roundsPerWindow.txt', 'w') as outfile:
    outfile.write("{")
    for line in roundsPerWindows:
        outfile.write('"' + line + '":')
        outfile.write("\n{")
        for ell in roundsPerWindows[line]:
            outfile.write('"' + ell + '":')
            outfile.write("\n{")
            for el in roundsPerWindows[line][ell]:
                outfile.write('"' + el + '":')
                outfile.write("\n[")
                for e in roundsPerWindows[line][ell][el]:
                    outfile.write(json.dumps(e))
                    if roundsPerWindows[line][ell][el].index(e) != len(roundsPerWindows[line][ell][el])-1 :
                        outfile.write(",\n")
                if roundsPerWindows[line][ell].keys().index(el) != len(roundsPerWindows[line][ell])-1:
                    outfile.write("],\n")
                else:
                    outfile.write("]\n")
            if roundsPerWindows[line].keys().index(ell) != len(roundsPerWindows[line])-1:
                outfile.write("},\n")
            else:
                outfile.write("}\n")
        if roundsPerWindows.keys().index(line) != len(roundsPerWindows)-1:
            outfile.write("},\n")
        else:
            outfile.write("}\n")
    outfile.write("}")

with open('windowsLength.txt', 'w') as outfile:
	json.dump(windowsLength, outfile)
