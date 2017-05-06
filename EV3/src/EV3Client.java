import java.io.IOException;
import java.io.PrintWriter;
import java.util.Scanner;
import lejos.hardware.Bluetooth;
import lejos.remote.nxt.NXTCommConnector;
import lejos.remote.nxt.NXTConnection;

public class EV3Client {
	
	private static String oliverMAC = "68:17:29:94:a7:77";
	private static String emilMAC = "18:5e:0f:0a:bc:56";
	private static String rpiMAC = "00:0c:78:33:da:22";
	private static String serverName = "raspberrypi";

	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		NXTCommConnector connector = Bluetooth.getNXTCommConnector();

		System.out.println("Connecting to server ...");
		NXTConnection connection = connector.connect(rpiMAC, NXTConnection.RAW);
		
		
		if (connection == null) {
		    System.err.println("Failed to connect");
		    return;
		}
		
		
		System.out.println("Connected");
		

		BTConReader input = new BTConReader(connection.openInputStream());
		PrintWriter output = new PrintWriter(connection.openOutputStream());
		
		System.out.println("Streams Opened");
		System.out.println(connection.toString());
		while(true) {
		    String s;
		    
			s = input.readThatLine();
			if(s == "Quit"){
				break;
			}
			System.out.println("Read " + s);
		    output.println(s);
		    output.flush();

		    
		}
		input.close();

	}


}
