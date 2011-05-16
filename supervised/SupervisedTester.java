import java.io.*;
import java.util.*;

import weka.core.*;
import weka.classifiers.Classifier;
import weka.core.converters.CSVLoader;

class SupervisedTester {

    public static void main(String[] args) {
        if(args.length != 3) {
            System.err.println("Usage: java SupervisedTester sector ticker classifier");
            System.err.println("\tclassifier: {NaiveBayes}");
            System.exit(1);
        } else {
            String sector = args[0];
            String ticker = args[1];
            String classifier = args[2];
            System.out.println("Sector: " + sector);
            System.out.println("Ticker: " + ticker);
            String dataDir = "../shared/labeled/" + sector + "/" + ticker;
            String trainf =  dataDir + "_train.csv";
            String testf =  dataDir + "_test.csv";
            //String testf =  dataDir + "_train.csv";
            SupervisedTester st = new SupervisedTester(trainf, testf);
            List<String> labels = st.learnAndTest(classifier);
            double res = st.evaluate(labels);
            if(res > 0) {
                System.out.println("Earned: $" + res);
            } else {
                System.out.println("Lost: $" + res);
            }
        }
    }

    SupervisedTester(String trainFeatures, String testFeatures) {
        this.trainFeatures = trainFeatures;
        this.testFeatures = testFeatures;
    }

    public List<String> learnAndTest(String classifier) {
        File ftrain = new File(trainFeatures);
        File ftest = new File(testFeatures);
        if(!ftrain.exists()) {
            System.err.println("File: " + trainFeatures + " not found.");
            System.exit(2);
        }
        if(!ftest.exists()) {
            System.err.println("File: " + testFeatures + " not found.");
            System.exit(3);
        }
        Classifier cls = loadClassifier(classifier);
        Instances trainInstances = null;
        Instances testInstances = null;
        try {
            CSVLoader loader = new CSVLoader();
            loader.setFile(ftrain);
            trainInstances = loader.getDataSet();
            trainInstances.setClassIndex(trainInstances.numAttributes() - 1);
            System.out.println(trainInstances.numAttributes() - 1);
            System.out.println("Finished reading training data.");
            loader.setFile(ftest);
            testInstances = loader.getDataSet();
            testInstances.setClassIndex(testInstances.numAttributes() - 1);
            System.out.println("Finished reading testing data.");
        } catch(IOException ioe) {
            System.err.println(ioe.getMessage());
            System.exit(4);
        }
        try {
            System.out.println("Training classifier...");
            cls.buildClassifier(trainInstances);
            System.out.println("Classifying test data...");
        } catch(Exception e) {
            System.err.println("Exception while building classifier.");
            System.err.println(e.getMessage());
            System.exit(7);
        }
        List<String> labels = new LinkedList<String>();
        try {
            for(int i = 0; i < testInstances.numInstances(); i++) {
                Instance testInst = testInstances.instance(i);
                double[] dist = cls.distributionForInstance(testInst);
                int maxInd = -1;
                double maxVal = -1.0;
                for(int j = 0; j < dist.length; j++) {
                    if(dist[j] > maxVal) {
                        maxVal = dist[j];
                        maxInd = j;
                    }
                }
                labels.add(trainInstances.classAttribute().value(maxInd));
                /*System.out.print("dist: [");
                for(int j = 0; j < dist.length; j++) {
                    System.out.print(dist[j] + ", ");
                    if(dist[j] > maxVal) {
                        maxVal = dist[j];
                        maxInd = j;
                    }
                }
                System.out.print("]");
                System.out.println("; Label: " + trainInstances.classAttribute().value(maxInd));
                */

            }
        } catch(Exception e) {
            System.err.println("Exception while classifying.");
            System.err.println(e.getMessage());
            System.exit(8);
        }
        return labels;
    }

    double evaluate(List<String> labels, String testFile) {
        /*
         * Evaluates the labels with the following rules:
         * buy/sell: buys/sells a share (if possible)
         * strong buy/strong sell: buys/sells 2 shares (if possible)
         * hold: does nothing
         */
        int numShares = 0;
        
        return 0.0;
    }

    Classifier loadClassifier(String classifier) {
        Classifier ret = null;
        try {
            boolean valid = false;
            int c = 0;
            int validIndex = -1;
            for(String vc : validClassifiers) {
                if(vc.equalsIgnoreCase(classifier)) {
                    valid = true;
                    validIndex = c;
                }
                c++;
            }
            if(valid) {
                ret = Classifier.forName(classFullyQual[validIndex], classifierOptions[validIndex]);
            } else {
                System.err.println("Classifier not valid.");
            }
        } catch(Exception e) {
            System.err.println(e.getMessage());
            System.exit(5);
        }
        return ret;
    }

    private String trainFeatures;
    private String testFeatures;
    private String classifier;
    private String[] validClassifiers = {"NaiveBayes"};
    private String[] classFullyQual = {"weka.classifiers.bayes.NaiveBayes"};
    private String[][] classifierOptions = { {""} };

}
