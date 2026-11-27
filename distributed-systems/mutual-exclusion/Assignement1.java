package Mini_Projet1;

import java.util.ArrayList;
import java.util.concurrent.Semaphore;

/*********************   SCENARIO 1  TRAIN CLASS  **************************/

class Train1 extends Thread{
	
	//binary semaphore to ensure that only one train is allowed on track T at any given time
	static Semaphore mutex = new Semaphore(1);
	
	//constructor
	public Train1(String name) { 
		this.setName(name);
	}
	
	
	public void enteringSectionT() throws InterruptedException {
		mutex.acquire(); // train checks if track T is empty
		
		// start of critical section
		System.out.println(this.getName()+" entered the T section.");
	}
	
	public void leavingSectionT() {
		System.out.println(this.getName()+" left the T section.\n");
		mutex.release(); // end of critical section: train left track T => track T is empty again 
	}
	
	@Override
	public void run() {
		try {
			enteringSectionT();
			Thread.sleep(100);  // train is travelling on track T
			leavingSectionT();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		
		
	}
	
}


/*********************   SCENARIO 2  TRAIN CLASS  **************************/

class Train2 extends Thread{
	
	// binary semaphore to ensure that only one train changes the direction of track T
	static Semaphore mutex = new Semaphore(1); 

	// counting semaphore to manipulate (control) trains that aren't allowed to enter Track T yet 
	// (trains waiting to enter track T)
	static Semaphore waiting = new Semaphore(0); 

	// keep track of the state of track T (initial state = empty)
	static String currentDirection=null; 
	
	// counter for the number of trains that are on Track T
	static int ontrack = 0; 
	
	//counter for the number of trains that are waiting to enter track T 
	static int waitingfortrack = 0;  

	//counter for the number of trains that are going right and are on Track T
	static int rightOnTrack = 0;
	
	//counter for the number of trains that are going left and are on Track T
	static int leftOnTrack = 0; 
	
	//attribute that specifies the direction of the train
	String trainDirection;   
	
	//constructor
	public Train2(String name, String direction) { 
		this.setName(name);
		trainDirection = direction;
	}
	
	
	public void enteringSectionT() throws InterruptedException {
		//Before entering track T, the train checks if the track is empty 
		//or the current direction on the track is the same as it's own 
		
		while(currentDirection != null && !currentDirection.equalsIgnoreCase(trainDirection)) {
			// track T not empty and current direction on it is different than the train's
			
			System.out.println(this.getName()+" is waiting to access the T section to travel \""+trainDirection+"\"\n");
			waitingfortrack++;           // increment number of waiting trains
			waiting.acquire();          // the train must wait
			
		}
		
		// track T is empty or its current direction is the same as the train's
		// the train enters track T and must change the track's current direction to its own
		
		mutex.acquire();      // to ensure it's the only train that's changing the direction on track T
		

		System.out.println(this.getName()+" entered the T section.\n");
		currentDirection = trainDirection;     //changing track T's direction
		ontrack++;       //increment the number of trains on track T (total number of trains at that moment)
		
		// depending on the way the train is going, increment the number of the trains on track T
		// this is to ensure, while executing, that only trains of the same direction are on track T 
		
		if(trainDirection.equalsIgnoreCase("right")) {
			rightOnTrack++;     // total number of trains  going right on track T
		}else {
			leftOnTrack++;     // total number of trains going left on track T
		}
		System.out.println("Count of right on track: "+rightOnTrack);
		System.out.println("Count of left on track: "+leftOnTrack+"\n");
		
		mutex.release();    // current direction is changed and train is on track

	}
	
	public void leavingSectionT() throws InterruptedException {
		// to ensure that only one train is manipulating the current direction 
		//(when the train is leaving a track and if a change in current direction is necessary) 
		mutex.acquire(); 
		
		System.out.println(this.getName()+" exited the T section.\n");
		ontrack--;   // decrement number of trains on track (total trains on track after this one leaves)
		
		// depending on the train's direction 
		//decrement number of total trains going in its direction on track T 
		if(trainDirection.equalsIgnoreCase("right")) {
			rightOnTrack--;
		}else {
			leftOnTrack--;
		}
		
		// check if there are no trains on track T when this one leaves
		if (ontrack==0){
			// no trains on track T after this one leaves
			
			currentDirection=null;    // reset track T's state (empty)
			
			//check if there are waiting trains
			while (waitingfortrack > 0) {
				// there are waiting trains
				waiting.release();   // give permits to all of them so that they can try to enter track T again
				waitingfortrack--;  // decrement number of waiting trains
			}
			}
		
		// if there already are trains on the track => current direction isn't changing
		// or there are no more and all waiting trains are released => track T is empty again
		
		mutex.release();   // train leaves
	}
	
	
	@Override
	public void run() {

			try {
				this.enteringSectionT();
				Thread.sleep(1000);    // train is travelling on track T
				this.leavingSectionT();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
			
}


/*********************   MAIN CLASS  **************************/
public class Assignement1 {

	public static void main(String[] args) throws InterruptedException {
		String n = "Train-";
		String name;
		
		//SCENARIO 1
		
		System.out.println("********** SCENARIO 01 EXECUTION : Ensure that only one train is allowed on track T at any given time **********\n");
		
		// ArrayList to store all trains (threads)
		ArrayList<Train1> trainListS1 = new ArrayList<Train1>();
		Train1 train;
		
		
		for(int i=0;i<7;i++) {
			name = n + i;
			
			// creating a new train (thread)
			train = new Train1(name);
			trainListS1.add(train);
			train.start();
		}
		
		for(Train1 t: trainListS1) {
			t.join();
		}

		System.out.println("\n******* SCENARIO 01 SUCCESSFUL *******");
		
		System.out.println("-------------------------------------------------------------------------------------------");
		
		//SCENARIO 2
		
		System.out.println("********** SCENARIO 02 EXECUTION :  Allow an unlimited number of trains to travel in the same direction on the single track **********\n");
		
		// ArrayList to store all trains (threads)
				ArrayList<Train2> trainListS2 = new ArrayList<Train2>();
				Train2 trainS2;
				
				// creating only trains that are going left
				for(int i=0;i<3;i++) {
					name = n + i;
					trainS2 = new Train2(name, "left");
					trainListS2.add(trainS2);
					trainS2.start();
				}
				
				// creating trains that are going left and others going right 
				for(int i=3;i<10;i++) {
					name = n + i;
					if(i%2==0) {
						trainS2 = new Train2(name, "right");
					}else {
						trainS2 = new Train2(name, "left");
					}
					trainListS2.add(trainS2);
					trainS2.start();
				}

				// creating only trains that are going right
				for(int i=10;i<13;i++) {
					name = n + i;
					trainS2 = new Train2(name, "right");
					trainListS2.add(trainS2);
					trainS2.start();
				}

				for(Train2 t: trainListS2) {
					t.join();
				}

				System.out.println("\n******* SCENARIO 02 SUCCESSFUL *******");
		

	}

}
