# Calculate features for the data and output them

import csv
import math
import os.path
import sys

dataDir = '../../data'

date = 0
openp = 1
high = 2
low = 3
close = 4
volume = 5

def loadAllData(sector):
	path = "%s/%s/" % (dataDir, sector)
	if not os.path.exists(path):
            print "Unable to find path"
            sys.exit(1)
	listing = os.listdir(path)
	for infile in listing:
		print "current file is: " + infile
	return

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
# SMA-200(today) / SMA-200(20 days ago)
# EMA-50
# EMA-50(today) / EMA-50(20 days ago)
# MACD (difference from signal line today)
# KDJ(5,3)
# RSI(14)
# Williams%R(10)
# Williams%R(30)
# stochasticOscillator(0, 20)
# stochasticOscillator(20, 20) / stochasticOscillator(0, 20)
# Commodity channel index(20)
# VMA-200
# VMA-200(today) / VMA-200(20 days ago)
#
#make it to work for a particular day
def findDay(data, day):
	i = 0
	for d in data:
		i += 1
		if d[date] == day:
			print d
			break
	if i < len(data):
		return i
	else:
		print "No such date"
		sys.exit(1)
	
def featuresDay(data, day):
	feats = []
	i = findDay(data, day)
	smas = sma(data, i, i+20, 200)
	feats.append(smas[0])
	feats.append(smas[-1] / smas[0]) # Direction of SMA over last 20 days
	emas = ema(data, i, i+20, 50)
	feats.append(emas[0])
	feats.append(emas[-1] / emas[0]) # Direction of EMA over last 20 days
	#ToDo
	return feats
def features(data):
    feats = []
    smas = sma(data, 0, 20, 200)
    feats.append(smas[0])
    feats.append(smas[-1] / smas[0]) # Direction of SMA over last 20 days
    emas = ema(data, 0, 20, 50)
    feats.append(emas[0])
    feats.append(emas[-1] / emas[0]) # Direction of EMA over last 20 days
    feats.append(macd(data))
    #feats.append(kdjIndicator(data, 0))
    feats.append(rsi(data, 14))
    feats.append(williamsPctR(data, 0, 10))
    feats.append(williamsPctR(data, 0, 60))
    sosc20 = stochasticOscillator(data, 0, 20)
    feats.append(sosc20)
    feats.append(stochasticOscillator(data, 20, 20) / sosc20)
    vmas = vma(data, 0, 20, 200)
    feats.append(vmas[0])
    feats.append(vmas[-1] / vmas[0])
    return feats

# Simple Moving Average -- Calculates an SMA for each day in startIndex to
# endIndex over the given period
def sma(data, startIndex, endIndex, period):
    smas = []
    curSma = 0.0
    for i in range(startIndex, endIndex + period):
    	print "date", i, len(data)
        if i - period >= startIndex:
            smas.append(curSma)
            curSma = curSma - (data[i - period][close] / period) + (data[i][close] / period)
        else:
            curSma += (data[i][close] / period)
    #print smas
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
    (highestHigh,lowestLow) = highestHighLowestLow(data, startIndex, periodLong)
    k = (data[startIndex][close] - lowestLow) / (highestHigh - lowestLow)
    # TODO
    #d = (highestHighK, lowestLowK) # needs to be over SMA over k along period short!
    return d - k

# Relative Strenght Index. 14 is usually the period used. 
# Precondition: len(data) > startIndex + period + 1!
# TODO This can have a divide by 0 -- find out how the real RSI prevents that
def rsi(data, startIndex, period = 14):
    avgGain = 0.0
    numGain = 0
    avgLoss = 0.0
    numLoss = 0
    for i in range(startIndex, startIndex + period):
        delta = data[i][close] - data[i+1][close]
        if delta > 0.0:
            numGain += 1
            avgGain += delta
        else:
            numLoss += 1
            avgLoss += delta
        if numGain == 0:
            avgGain = 1e-4
        else:
            avgGain /= numGain
        if numLoss == 0:
            avgLoss = 1e-4
        else:
            avgLoss /= numLoss
        # real RSI has 100 - this value, but for us that does nothing
        return (100 / (1 + (avgGain / avgLoss)))

def williamsPctR(data, startIndex, period):
    (highestHigh,lowestLow) = highestHighLowestLow(data, startIndex, period)
    return (highestHigh - data[startIndex][close]) / (highestHigh - lowestLow)

def stochasticOscillator(data, startIndex, period):
    (hH, lL) = highestHighLowestLow(data, startIndex, period)
    return (data[startIndex][close] - lL) / (hH - lL)

# Commodity channel index
def cci(data, startIndex):
    period = 20.0
    tpSma = 0.0
    tps = []
    for i in range(period):
        tp = (data[i][high] + data[i][low] + data[i][close]) / 3.0
        tps.append(tp)
        tpSma += tp
    tpSma /= period
    meanDev = 0.0
    for i in range(period):
        meanDev += tp - tps[i]
    meanDev /= period
    return (tp[0] - tpSma) / (0.015 * meanDev)

def vma(data, startIndex, endIndex, period):
    global close
    global volume
    closeInd = close
    close = volume
    vma = sma(data, startIndex, endIndex, period)
    close = closeInd
    return vma

# Returns the distance of the upper/lower bands from the middle bollinger band.
def bollinger(data, startIndex, n, k):
    sma = sma(data, startIndex, startIndex, n)[0]
    var = 0.0
    for i in range(startIndex, startIndex + n):
        var += (sma - data[i][close]) ** 2
    stdev = math.sqrt(var / float(n))
    # TODO TODO TODO
    pass


# Gets the highest high and lowest low over a period starting from startIndex
def highestHighLowestLow(data, startIndex, period):
    highestHigh = 0
    lowestLow = 9999999999
    for i in range(startIndex, startIndex + period):
        highestHigh = max(data[i][high], highestHigh)
        lowestLow = min(data[i][low], lowestLow)
    return (highestHigh, lowestLow)

if __name__ == '__main__':
    data = loadData('basic_materials', 'avp')
    #print features(data)
    #loadAllData('basic_materials')
    #print ema(data, 100, 150, 100)
    day = '2010-04-30'
    #print("day ", findDay(data, day))
    print featuresDay(data, day)
    
    f = open('test.txt', 'w')
    #feat = [] 
    feat = featuresDay(data, day)
    for line in feat:
    	    f.write('%f'%(line))
