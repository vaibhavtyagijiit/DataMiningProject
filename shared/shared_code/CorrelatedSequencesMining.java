import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.Hashtable;
import java.util.LinkedList;


public class CorrelatedSequencesMining {
	
	
	public static String readFile(String path) throws Exception {
		File file = new File(path);
		BufferedReader bufRdr = new BufferedReader(new FileReader(file));
		
		return bufRdr.readLine();
	}
	
	public static String combineStocks(String s1, String s2, int period){
		
		if (s1.length() != s2.length()){
			System.out.println("Inputs must be over same period: " + s1.length() + " " + s2.length());
			System.exit(0);
		}
			
		StringBuilder sb = new StringBuilder();
	
		int ind =0;
		
		for (int i =0; i < s2.length()-period-1; i++){
			ind = 0;
			while (ind<period)
				sb.append(s1.charAt(i+ind++));
				
			sb.append(s2.charAt(i+ind));
		}
		
		return sb.toString();
	}
	
	public static double support(String input, String countString, int frame){
		double denom = input.length()/(double)frame;
		 return 
		  (double)(input.split("\\Q"+countString+"\\E", -1).length - 1)/denom;
		}
	
	public static LinkedList<String> frequent(String input, int frame, double support){
		LinkedList<String> results = new LinkedList<String>();
		Hashtable<String, Integer> ht = new Hashtable<String, Integer>();
		
		for (int i =0; i< input.length()-frame; i+= frame){
			String substr = input.substring(i, i+frame);
			if (ht.containsKey(substr))
				ht.put(substr, ht.get(substr) + 1);
			else ht.put(substr, 1);
		}
		
		double denom = input.length()/(double)frame;
		
		for (String s : ht.keySet())
			if (ht.get(s)/denom >= support)
				results.add(s);
		
		return results; 
	}
	
	public static LinkedList<String> generate_rules(String input, LinkedList<String> frequent, double confidence, int frame){
		
		LinkedList<String>  results = new LinkedList<String>();
		
		for (String s : frequent)
			if (support(input, s, frame)/support(input, s.substring(0, s.length()-1), frame) > confidence)
				results.add(s);
		
		return results;
	}
	
	public static void print_rules(LinkedList<String> rules){
		System.out.println("+++++++++++++RULES+++++++++++++++++++");
		
		for (String s : rules){
			System.out.println("Rule = " + s);
			System.out.println(s.substring(0, s.length()-1) + " --> " + s.substring(s.length() -1, s.length()));
		}
	}
	
	public static void main(String[] args){
		
		if (args.length <5){
			System.out.println("Please specify as parameters [stock1] [stock2] [period] [support] [confidence]");
			System.exit(0);
			//s = "nababanbalbababtifarchilotobesbebakbasbebabab";
			//threshold = 0.04;
			//confidence = 0.2
		}
		try{
		String s1 = readFile(args[0]);
		String s2 = readFile(args[1]);
		
		int period = Integer.parseInt(args[2]);
		double support = Double.parseDouble(args[3]);
		double confidence = Double.parseDouble(args[4]);
		
		int frame = period + 1;
		
		String comb= combineStocks(s1, s2, period);
		
		LinkedList<String> results = frequent(comb, frame, support);
		
		for (String s:results)
			System.out.println(s);
		
		LinkedList<String> rules = generate_rules(comb, results, confidence, frame);
		
		print_rules(rules);
		} catch(Exception ex){ex.printStackTrace();}
	}

}
