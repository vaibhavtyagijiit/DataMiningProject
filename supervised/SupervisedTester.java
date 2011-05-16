import java.io.*;
import java.util.*;

import weka.core.*;
import weka.classifiers.Classifier;


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
            SupervisedTester st = new SupervisedTester(trainf, testf);
            double res = st.learnAndTest(classifier);
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

    public double learnAndTest(String classifier) {
        File ftrain = new File(trainFeatures);
        File ftest = new File(testFeatures);
        if(!ftrain.exists()) {
            System.err.println("File: " + trainFeatures + " not found.");
            System.exit(1);
        }
        if(!ftest.exists()) {
            System.err.println("File: " + testFeatures + " not found.");
            System.exit(1);
        }
        Classifier cls = loadClassifier(classifier);
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
            System.exit(1);
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
