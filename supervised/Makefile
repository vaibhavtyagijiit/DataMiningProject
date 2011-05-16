JFLAGS = -classpath .:/Applications/weka-3-6-4.app/Contents/Resources/Java/weka.jar
JC = javac
.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) $*.java

CLASSES = \
        SupervisedTester.java 

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) *.class

rebuild: clean classes

