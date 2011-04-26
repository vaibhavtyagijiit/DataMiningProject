import sys
from featcomp import *

# 
# labelStrategy:
#  - 0 : average gain (closing)
#  - 1 : max gain (closing)
#  - 2 : period end gain (closing)
# Returns labels representing the numeric value of the label strategy if stock was bought on a given day
def labelNumeric(data, earlyInd, lateInd, labelPeriod, labelStrategy):
    labels = []
    for i in reversed(range(lateInd + labelPeriod - 1, earlyInd + 1)):
        if labelStrategy < 2:
            avg = 0.0
            maxGain = -99999999
            for d in reversed(data[i - labelPeriod:i]):
                maxGain = max(maxGain, d[close] - data[i][close])
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
def label5Class(data, earlyInd, lateInd, labels, sbAmt, bAmt, hAmt, sAmt, ssAmt):
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
    print lblInd
    return retLabels

def dateToIndex(data, day, month, year):
    day = int(day)
    month = int(month)
    year = int(year)
    for i,d in enumerate(data):
        (sy, sm, sd) = map(int, d[date].split("-"))
        if day == sd and sm == month and sy == year:
            return i
    print "Unable to find given date (%i-%i-%i) in the stock data." % (day, month, year)
    sys.exit(1)

if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 7:
        sector = args[1]
        ticker = args[2].lower()
        (sday, smonth, syear) = args[3].split("-")
        (eday, emonth, eyear) = args[4].split("-")
        data = loadData(sector, ticker)
        startInd = dateToIndex(data, sday, smonth, syear)
        endInd = dateToIndex(data, eday, emonth, eyear)
        labelPeriod = int(args[5])
        labelStrategy = int(args[6])
        labelsn = labelNumeric(data, startInd, endInd, labelPeriod, labelStrategy)
        classLabels = label5Class(data, startInd, endInd, labelsn, 0.05, 0.2, 0.5, 0.2, 0.05)
        print classLabels
    else:
        print "Usage: python label.py sector ticker start-label[dd-mm-yyyy] end-label[dd-mm-yyyy] label_period label_strategy"
        print "label_period: Number of stock pricing periods to perform the label analysis over"
        print "label_strategy: 0 = average gain over period, 1 = max gain over period, 2 = end gain over period. All labeling strategies use the period closing price."
        sys.exit(1)


