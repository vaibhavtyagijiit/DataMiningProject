import java.util.*;

/*
 * Run as java FrequentSequenceMining [support] [confidence] [maximum sequence length] [string]
 * with 0< support < 1, 0< confidence < 1, maximum sequence length is the maximum length of mined sequences
 * and string is the input to be mined
 */

public class FrequentSequenceMining {
	
	public static LinkedList<String> frequent_sequences(String input, int k, double threshold){
		LinkedList<String> two_list = generateFrequentTwoItemsets(input, threshold);
		
		LinkedList<String> results = new LinkedList<String>();
		
		results.addAll(two_list);
		
		LinkedList<String> new_list = generateFrequentItemsets(two_list, input, threshold);
		
		int cnt = 1;
		
		while (!new_list.isEmpty() && ++cnt < k){
			results.addAll(new_list);
			new_list = generateFrequentItemsets(new_list, input, threshold);
		}
		
		return results;
	}
	
	
	public static LinkedList<Character> frequent_items(String str, double threshold){
		Hashtable<Character, Integer> ht = new Hashtable<Character, Integer>();
		
		for (int i=0; i<str.length(); i++){
			char c = str.charAt(i);
			if (ht.containsKey(c))
				ht.put(c, ht.get(c) + 1);
			
			else ht.put(c, 1);	
		}
		
		LinkedList<Character> result = new LinkedList<Character>();
		for (char c : ht.keySet())
			if ((double)ht.get(c)/str.length() >= threshold)
				result.add(c);//put(c, ht.get(c));
		
		return result;
	}
	
	public static LinkedList<String> generateFrequentTwoItemsets(String input, double threshold){
		LinkedList<String> list = new LinkedList<String>();
		
		LinkedList<Character> char_list = frequent_items(input, threshold);
		
		for (char a: char_list){
			for (char b: char_list){
				String cand = ""+a+b;
				if (support(input, cand) > threshold)
					list.add(""+a+b);
			}
		}
		
		return list;
	}
	
	public static LinkedList<String> generateFrequentItemsets(LinkedList<String> candidates, String input, double threshold){
		LinkedList<String> list = new LinkedList<String>();
		
		for (String s1: candidates)
			for (String s2: candidates)
				if (compatible(s1, s2)){
					String cand = join(s1, s2);
					if (support(input, cand) > threshold)
					list.add(cand);
				}
		return list;
	}
	
	public static boolean compatible(String s1, String s2){
		return (s1.length() == s2.length()) && (s1.substring(1, s1.length())).equals(s2.substring(0, s2.length()-1));
	}
	
	public static String join(String s1, String s2){
		return s1+s2.charAt(s2.length()-1);
	}
	
	public static double support(String input, String countString){
		 return 
		  (double)(input.split("\\Q"+countString+"\\E", -1).length - 1)/(input.length() - countString.length() +1);
		}
	
	public static LinkedList<String> generate_rules(String input, LinkedList<String> frequent, double confidence){
		
		LinkedList<String>  results = new LinkedList<String>();
		
		for (String s : frequent)
			if (support(input, s)/support(input, s.substring(0, s.length()-2)) > confidence)
				results.add(s);
		
		return results;
	}
	
	public static void print_rules(LinkedList<String> rules){
		System.out.println("+++++++++++++RULES+++++++++++++++++++");
		
		for (String s : rules)
			System.out.println(s.substring(0, s.length()-2) + " --> " + s.substring(s.length() -2, s.length()-1));
	}
	
	public static void main(String[] args){
		
		String s;
		double support;
		double confidence;
		int max_sequence_length;
		
		if (args.length <4){
			System.out.println("Please specify as parameters [support] [confidence] [maximum sequence length] [string]");
			System.exit(0);
			//s = "nababanbalbababtifarchilotobesbebakbasbebabab";
			//threshold = 0.04;
			//confidence = 0.25;
		}
		
		
		support = Double.parseDouble(args[0]);
		confidence = Double.parseDouble(args[1]);
		max_sequence_length = Integer.parseInt(args[2]);
		s = args[3];
		
		System.out.println("Input length = " + s.length());
			
		LinkedList<String> new_list = frequent_sequences(s, max_sequence_length, support);
		
		for (String str : new_list)
			System.out.println(str);	
		
		LinkedList<String> rules = generate_rules(s, new_list, confidence);
		
		print_rules(rules);
	}

}
