
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;

public class BTConReader extends DataInputStream{
	
	private String string;
	private int maxLen = 128;
	private byte[] bytes;
	private char[] chars;
	private int actualLen;
	
	public BTConReader(InputStream in) {
		super(in);
		bytes = new byte[maxLen];
	}
	
	public String readThatLine() throws IOException{
		actualLen = in.read(bytes, 0, maxLen);
		chars = new char[actualLen];
		int i = 0;
		while(bytes[i] != '\n' && i < actualLen){
			chars[i] = (char) bytes[i];
			i++;
		}
		chars = Arrays.copyOf(chars, i);
		string = new String(chars);
		chars = new char[maxLen];
		return string;
	}
}