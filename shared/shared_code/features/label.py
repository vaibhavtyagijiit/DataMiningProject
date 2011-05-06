import os
import sys
from featcomp import *

# 
# labelStrategy:
#  - 0 : average gain (closing)
#  - 1 : max gain (closing)
#  - 2 : period end gain (closing)
# Returns labels representing the numeric value of the label strategy if stock was bought on a given day

def computeCoeff(data, earlyInd, lateInd):
	volumes = []
	
	for i in range(lateInd, earlyInd + 1):
    	    volumes.append(data[i][volume])
    	volumes.sort()
        k = volumes[-1] #or maybe take the median
        return k
        
def average(liste):
	summe =0
	for i in liste:
		summe +=i
	return float(summe)/len(liste)
	

	
def labelPeriodsStandard(data, earlyInd, lateInd, timeFrame, threshold):
	labels = []
	i = lateInd
	
	while (i + timeFrame < earlyInd):
		k = (data[i][close] - data[i+timeFrame][openp])/data[i][close]
		if math.fabs(k) < threshold:
			labels.insert(0, 'H')
		elif k >= threshold:
			labels.insert(0, 'R')
		elif k <= -threshold:
			labels.insert(0, 'F')
	
		i += timeFrame
	return labels
        
def labelNumericTimeFrames(data, earlyInd, lateInd, labelPeriod, labelStrategy, timeFrame):
    results = []
    i = lateInd + labelPeriod - 1
    while (i < earlyInd + 1):
    	t=0
    	labels = []
    	while t<timeFrame:
    		s = i+t
		if labelStrategy < 2:
		    avg = 0.0
		    maxGain = -99999999
		    for d in reversed(data[s - labelPeriod:s]):
			maxGain = max(maxGain, d[close] - data[s][close])
			#print "close price", d[close] -  data[s][close]
			avg += d[close] - data[s][close]
		    avg /= labelPeriod
		    if labelStrategy == 0:
	        	labels.append(avg)
                    else:
                	labels.append(maxGain)
                elif labelStrategy == 2:
               	       	labels.append(data[s - labelPeriod][close] - data[s][close])
               	t +=1
        i += timeFrame
        results.append(average(labels)) 	
    return results


def labelNumericWeighted(data, earlyInd, lateInd, labelPeriod, labelStrategy):
    volumes = []
    #print earlyInd + 1, lateInd
    for i in range(lateInd, earlyInd + 1):
    	    volumes.append(data[i][volume])
    volumes.sort()
    k = volumes[-1] #or maybe take the median
    
    #print "sorted volumes", k, volumes
    labels = []
    for i in reversed(range(lateInd + labelPeriod - 1, earlyInd + 1)):
    	coeff = float(data[i - labelPeriod][volume])/k
    	coeff = 1 + 0.2*coeff
        #print coeff
        if labelStrategy < 2:
            avg = 0.0
            maxGain = -99999999
            for d in reversed(data[i - labelPeriod:i]):
                maxGain = max(maxGain, coeff*(d[close] - data[i][close]))
                avg += coeff*(d[close] - data[i][close])
            avg /= labelPeriod
            if labelStrategy == 0:
                labels.append(avg)
            else:
                labels.append(maxGain)
        elif labelStrategy == 2:
            labels.append(coeff*(data[i - labelPeriod][close] - data[i][close]))
    return labels
    
    
def labelNumeric(data, earlyInd, lateInd, labelPeriod, labelStrategy):
    labels = []
    #for i in reversed(range(lateInd + labelPeriod - 1, earlyInd + 1)):
    for i in reversed(range(lateInd, earlyInd)):
        if labelStrategy < 2:
            avg = 0.0
            maxGain = -99999999
            for d in reversed(data[i - labelPeriod:i]):
                maxGain = max(maxGain, d[close] - data[i][close])
                #print "close price", d[close] -  data[i][close]
                avg += d[close] - data[i][close]
            avg /= labelPeriod
            if labelStrategy == 0:
                labels.append(avg)
            else:
                labels.append(maxGain)
        elif labelStrategy == 2:
            labels.append(data[i - labelPeriod][close] - data[i][close])
    return labels

# Turns numeric labels indicating gain into 5 categories: strong/weak buy/sell and hold
# The last 5 parameters indicate the amount of the labels that should be of that kind. These number must sum to 1.0
def label5Class(data, labels, sbAmt, bAmt, hAmt, sAmt, ssAmt):
    sum = sbAmt + bAmt + hAmt + sAmt + ssAmt
    if not (sum - 1e-4 <= 1.0 and sum + 1e-4 >= 1.0):
        print "Invalid label amounts: %f %f %f %f %f does not sum to 1.0 (sums to %f)" % (sbAmt, bAmt, hAmt, sAmt, ssAmt, sum)
        sys.exit(1)
    # Load the labels and their indices into a sortable tuple
    lblInd = []
    for i, lbl in enumerate(labels):
        lblInd.append((lbl, i))
    lblInd.sort()
    totalLabels = len(lblInd)
    lblCounts = [ssAmt, sAmt, hAmt, bAmt, sbAmt]
    lblCounts = map(lambda x: round(x * totalLabels), lblCounts)
    
    retLabels = ['unlabeled'] * totalLabels
    for lbl, ind in lblInd:
        if lblCounts[0] > 0:
            lblCounts[0] -= 1
            retLabels[ind] = 'strong_sell'
        elif lblCounts[1] > 0:
            lblCounts[1] -= 1
            retLabels[ind] = 'sell'
        elif lblCounts[2] > 0:
            lblCounts[2] -= 1
            retLabels[ind] = 'hold'
        elif lblCounts[3] > 0:
            lblCounts[3] -= 1
            retLabels[ind] = 'buy'
        else:
            retLabels[ind] = 'strong_buy'
    #print lblInd
    return retLabels

#returns the next working day, well, unless Christmas
#todo, end of month

def dateTupleToIndex(data, dmy):
    return dateToIndex(data, dmy[0], dmy[1], dmy[2])


def dateToIndex(data, day, month, year):
    day = int(day)
    month = int(month)
    year = int(year)
    for i,d in enumerate(data):
        (sy, sm, sd) = map(int, d[date].split("-"))
        if (day == sd and sm == month and sy == year) or (day+1 == sd and sm == month and sy == year) or (day+2 == sd and sm == month and sy == year):
            return i
    print "Unable to find given date (%i-%i-%i) in the stock data." % (day, month, year)
    sys.exit(1)
    
    
def label_function(file_name, labels):
	f = open('../%s.txt'%file_name, 'w')
	
	for label in labels:
		if label == 'strong_sell':
			f.write('1')
		elif label == 'sell':
			f.write('2')
		elif label == 'hold':
			f.write('3')
		elif label == 'buy':
			f.write('4')
		elif label == 'strong_buy':
			f.write('5')
	return
	
def label_standard(file_name, labels):
	f = open('../%s.txt'%file_name, 'w')
	
	for l in labels:
		f.write(l)

	return

def labelAll(sector, labelPeriod, labelStrategy, trainBegin, trainEnd, testBegin, testEnd):
    symDir = "../../data/%s" % sector
    syms = os.listdir(symDir)
    for symbolDirty in syms:
        symbol = symbolDirty[:-4].lower()
        data = loadData(sector, symbol)
        # Swap begin and end since as the index in data increases, the date goes backwards
        trainStartInd = dateTupleToIndex(data, trainEnd)
        trainEndInd = dateTupleToIndex(data, trainBegin)
        testStartInd = dateTupleToIndex(data, testEnd)
        testEndInd = dateTupleToIndex(data, testBegin)
        
        trainLabeled = labeledFeatures(data, trainStartInd, trainEndInd)
        testLabeled = labeledFeatures(data, testStartInd, testEndInd)
        
        fnames = ','.join(featureNames())
        fp = open("../../labeled/%s/%s_train.csv" % (sector, symbol), 'w')
        fp.write("%s,label\n" % fnames)
        for lfeat in trainLabeled:
            for i, lf in enumerate(lfeat):
                fp.write("%s" % lf)
                if i < len(lfeat) - 1:
                    fp.write(",")
            fp.write("\n")
        fp.close()
        
        fp = open("../../labeled/%s/%s_test.csv" % (sector, symbol), 'w')
        fp.write("%s,label\n" % fnames)
        for lfeat in testLabeled:
            for i, lf in enumerate(lfeat[:-1]): # do not output class label
                fp.write("%s" % lf)
                if i < len(lfeat) - 2:
                    fp.write(",")
            fp.write("\n")
        fp.close()

def labeledFeatures(data, startInd, endInd):
    if startInd == endInd:
        return []
    labelsn = labelNumeric(data, endInd, startInd, labelPeriod, labelStrategy)
    classLabels = label5Class(data, endInd, startInd, labelsn, 0.05, 0.2, 0.5, 0.2, 0.05)
    feats = features(data, startInd, endInd)
    normFeats = normalize(feats)
    lfeats = []
    for i, n in enumerate(normFeats):
        n.append(classLabels[i])
        lfeats.append(n)
    return lfeats

if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 9:
        sector = args[1]
        ticker = args[2].lower().strip()
        (sday, smonth, syear) = args[3].split("-")
        (eday, emonth, eyear) = args[4].split("-")
        data = loadData(sector, ticker)
        startInd = dateToIndex(data, sday, smonth, syear)
        endInd = dateToIndex(data, eday, emonth, eyear)
        labelPeriod = int(args[5])
        labelStrategy = int(args[6])
        labelsn = labelNumeric(data, startInd, endInd, labelPeriod, labelStrategy)
        labelsnW = labelNumericWeighted(data, startInd, endInd, labelPeriod, labelStrategy)
        timeFrame = int(args[7])
        labelsTimeFrames = labelNumericTimeFrames(data, startInd, endInd, labelPeriod, labelStrategy, timeFrame)
        classLabels = label5Class(data, labelsTimeFrames, 0.0, 0.25, 0.5, 0.25, 0.0)
        labelsStandard = labelPeriodsStandard(data, startInd, endInd, timeFrame, 0.02)
        #print labelsStandard
        #print len(labelsTimeFrames)
        #print len(classLabels)
        #print len(labelsnW)
	#print "time frame", average(labelsTimeFrames) 
	#print "\n standard", average(labelsn)
	#print "\n \n weighted", average(labelsnW)
	
	label_standard(args[8], labelsStandard)		
	
    #else:
     #   print "Usage: python label.py sector ticker start-label[dd-mm-yyyy] end-label[dd-mm-yyyy] label_period label_strategy time_frame output_file"
      #  print "label_period: Number of stock pricing periods to perform the label analysis over"
       # print "label_strategy: 0 = average gain over period, 1 = max gain over period, 2 = end gain over period. All labeling strategies use the period closing price."
       # print "time_frame: the length of the period to be labeled"

        if ticker == "*all*":
            trainBegin = (sday, smonth, syear)
            trainEnd = (eday, emonth, eyear)
            testBegin = (eday, emonth, eyear)
            testEnd = (eday, emonth, eyear)
            if len(args) >= 9:
                testBegin = args[7].split("-")
                testEnd = args[8].split("-")
            labelAll(sector, labelPeriod, labelStrategy, trainBegin, trainEnd, testBegin, testEnd)
        else:
            data = loadData(sector, ticker)
            startInd = dateToIndex(data, sday, smonth, syear)
            endInd = dateToIndex(data, eday, emonth, eyear)
            labelsn = labelNumeric(data, startInd, endInd, labelPeriod, labelStrategy)
            classLabels = label5Class(data, startInd, endInd, labelsn, 0.05, 0.2, 0.5, 0.2, 0.05)
            print classLabels
    else:
        print "Usage: python label.py sector ticker train-start-label[dd-mm-yyyy] train-end-label[dd-mm-yyyy] label_period label_strategy [test_begin[dd-mm-yyyy] test_end[dd-mm-yyyy]]"
        print "ticker: use *ALL* to label all stocks in the sector and output their features + labels to a file (shared/labeled/ticker_name.{train/test}"
        print "label_period: Number of stock pricing periods to perform the label analysis over"
        print "label_strategy: 0 = average gain over period, 1 = max gain over period, 2 = end gain over period. All labeling strategies use the period closing price."
        print "test_begin: Begin of testing data (labels will not be printed), optional and only for *all*."

        sys.exit(1)


