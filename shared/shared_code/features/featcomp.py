# Calculate features for the data and output them

import csv
import os.path
import sys

dataDir = '../../data'

date = 0
openp = 1
high = 2
low = 3
close = 4
volume = 5

def loadData(sector, ticker):
    path = "%s/%s/%s.csv" % (dataDir, sector, ticker)
    if not os.path.exists(path):
        path = "%s/%s/%s.csv" % (dataDir, sector, ticker.upper())
        if not os.path.exists(path):
            print "Unable to find ticker %s in sector %s (searched in: %s)" % (ticker, sector, path)
            sys.exit(1)
    fp = open(path,'r')
    fpcsv = csv.reader(fp)
    data = list(fpcsv)[1:] # remove labels at the top
    cleaned = []
    for row in data:
        cl = []
        cl.append(row[date])
        cl.append(float(row[openp]))
        cl.append(float(row[high]))
        cl.append(float(row[low]))
        cl.append(float(row[close]))
        cl.append(int(row[volume]))
        cleaned.append(cl)
    return cleaned

# Returns a feature vector of the following values:
# SMA-200
# SMA-200(today) - SMA-200(20 days ago)
# EMA-50
# EMA-50(today) - EMA-50(20 days ago)
# MACD (difference from signal line today)
# KDJ(5,3)
#
def features(data):
    feats = []
    smas = sma(data, 0, 20, 200)
    feats.append(smas[0])
    feats.append(smas[-1] - smas[0]) # Direction of SMA over last 20 days
    emas = ema(data, 0, 20, 50)
    feats.append(emas[0])
    feats.append(emas[-1] - emas[0]) # Direction of EMA over last 20 days
    feats.append(macd(data))
    #feats.append(kdjIndicator(data, 0))
    return feats

# Simple Moving Average -- Calculates an SMA for each day in startIndex to
# endIndex over the given period
def sma(data, startIndex, endIndex, period):
    smas = []
    curSma = 0.0
    for i in range(startIndex, endIndex + period):
        if i - period >= startIndex:
            smas.append(curSma)
            curSma = curSma - (data[i - period][close] / period) + (data[i][close] / period)
        else:
            curSma += (data[i][close] / period)
    return smas

# Exponential Moving Average -- Calculates an EMA for each day in startIndex to
# endIndex over the given period. Alpha is the constant smoothing factor.
def ema(data, startIndex, endIndex, period):
    emas = []
    lastEma = emarecur(data, startIndex, period)
    emas.append(lastEma)
    for i in range(startIndex + 1, endIndex):
        lastEma = lastEma + (2.0 / (period + 1)) * (data[i][close] - lastEma)
        emas.append(lastEma)
    return emas

def emarecur(data, startIndex, period):
    if period <= 2:
        return data[startIndex][close]
    else:
        alpha =  2.0 / (period + 1)
        return alpha * data[startIndex][close] + (1 - alpha) * emarecur(data, startIndex + 1, period - 1)

# Calculates the Moving Average Convergence/Divergence indicator (MACD)
def macd(data):
    global close
    signal = emarecur(data, 0, 9)
    # reset close to use on macdData
    macdData = []
    for i in range(26):
        macd = emarecur(data, i, 12) - emarecur(data, i, 26)
        macdData.append([macd])
    saveClose = close
    close = 0
    signal = emarecur(macdData, 0, 9)
    close = saveClose
    return macd - signal

# Calculates the KDJ indicator. 
def kdjIndicator(data, startIndex, periodLong = 10, periodShort = 7):
    highestHigh = 0
    lowestLow = 9999999999
    for i in range(startIndex, startIndex + periodLong):
        highestHigh = max(data[i][high], highestHigh)
        lowestLow = min(data[i][low], lowestLow)
    k = (data[startIndex][close] - lowestLow) / (highestHigh - lowestLow)
    # TODO
    #d = (highestHighK, lowestLowK) # needs to be over period short!
    return d - k

if __name__ == '__main__':
    data = loadData('basic_materials', 'avp')
    #print features(data)
    print ema(data, 100, 150, 100)

