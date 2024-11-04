import sys,time
import serial
import serial.tools.list_ports



'''
Usage: python script_name.py <relay_no.> <state> <relay_no.> <state> //example: python script_name.py 1 on 2 off 3 on

on = close
off = open

relay_no. and state are interchangable

You can pass as many commands as you want in a single run.

pin 2 on the arduino is pin 0 in the script

ARDUINO-PIN 2 = 0
ARDUINO-PIN 3 = 1   
ARDUINO-PIN 4 = 2
ARDUINO-PIN 5 = 3
ARDUINO-PIN 6 = 4
ARDUINO-PIN 7 = 5
ARDUINO-PIN 8 = 6
ARDUINO-PIN 9 = 7
ARDUINO-PIN 10 = 8
ARDUINO-PIN 11 = 9
ARDUINO-PIN 12 = 10

The scripts runs the commands in a sequential manner

'''

serialobj = None
arduino_port = None

# Returns the first arduino port available
def Auto_detect_port():
    
    global arduino_port

    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

    ports_dict = {
        p[0]: {'name': p[1] ,'description':p[2]}
        for p in myports
    }
    
    arduino_port = ""

    for k,v in ports_dict.items():
        if "VID:PID=2341:0043" in v['description']:
            arduino_port = str(k)

    return arduino_port

def connect():
    
    global arduino_port
    global serialobj
    counter = 1

    if serialobj is None:
        if arduino_port:
            while True:
                try:
                    print(f"Connecting to {arduino_port}...")
                    time.sleep(3)
                    serialobj = serial.Serial(arduino_port, 9600, timeout=5)
                    if serialobj.isOpen():
                        print("Connected successfully")
                        break
                    else:
                        serialobj.close()
                        serialobj.open()
                
                except Exception as e:
                    print (f"Arduino not detected {e}")
                    print(f"Retrying in 3 second...retry number {counter}")
                    counter += 1

                    if counter < 10 and serialobj:
                        print("Resetting port")
                        serialobj.close()
                        serialobj.open()

                    elif counter == 10 and serialobj is None:
                        print (f"timed out")
                        sys.exit(1)

                    time.sleep(5)
        else:
            print("Searching for valid ports.....")
            while True:
                arduino_port = Auto_detect_port()
                if arduino_port:
                    print(f"Arduino port Found {arduino_port}")
                    break
                else:
                    while counter < 10:
                        print (f"Retrying in 5 seconds... retry number:{counter}")
                        arduino_port = Auto_detect_port()
                        if arduino_port:
                            try:
                                serialobj = serial.Serial(arduino_port, 9600, timeout=5,bufferSize=8192)
                                print("Connected successfully")
                            except Exception as e:
                                print (f"Arduino not detected {e}")
                            return
                        counter += 1
                        time.sleep(5)
                    print("Timeout No port Found")
                    break

def readData():
    line=""
    while True:
        line = serialobj.readline().decode().strip()
        if len(line) > 0:
            return line
                            
def relay_control(command):
    time.sleep(2) #Don't remove this
    serialobj.write(command.encode())
    print(readData())
    
def commandparser(argList):

    listOfCommands = []

    for i in range(0,len(argList),2):
        state,relay_no = argList[i], argList[i+1]
        
        if state.isdigit():
            state,relay_no = relay_no, state.lower()

        if state.lower() == 'on': # you can change it for any word you want
            listOfCommands.append(f"close Relay0{relay_no}")

        elif state.lower() == 'off': # you can change it for any word you want
            listOfCommands.append(f"open Relay0{relay_no}")

    return listOfCommands

def command_exec(listOfCommands):

    connect()
    #executing commands
    for i in listOfCommands:
        try:
            relay_control(i)
        except Exception as e:
            print (e)

if __name__ == "__main__":
    
    print("===========Starting Arduino Control CLI==============")
    
    arduino_port = Auto_detect_port()
    
    sys.argv =sys.argv[1:]
    command_exec(commandparser(sys.argv))


    