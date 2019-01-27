import paho.mqtt.client as mqttClient
import paho.mqtt.publish as publish
import time
import serial
import json
import threading
import io
import argparse
import logging
import logging.handlers as handlers

lock = threading.Lock()
status_command = '* 0 Lamp ?' 
logger = logging.getLogger("Acer-MQTT-Log")
previous_status = 'OFF'

def setup_logger():
    logger.setLevel(logging.INFO)
    logHandler = handlers.TimedRotatingFileHandler('acer-mqtt.log', when='D', interval=1, backupCount=1)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

def get_projector():
    return serial.Serial(
        port=globals()['serial_port'],
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=2,
        writeTimeout=0
    )

def get_io_wrapper(projector):
    return io.TextIOWrapper(
        io.BufferedRWPair(projector, projector, 1),
        newline='\r',
        line_buffering=True
    )

def send_command(acer_command):

    try:

        lock.acquire()
        
        projector = get_projector()
        
        ser_io = get_io_wrapper(projector)
        
        if projector.isOpen():

            projector.flushInput()
            projector.flushOutput()
        
            ser_io.write(unicode(acer_command + '\r'))
            ser_io.flush()
            
            while projector.inWaiting() == 0:
                time.sleep(1)
            
            while projector.inWaiting() > 0:
                line = ser_io.readline();
                logger.info(line)
                 
        else:
            logger.error('Projector connection closed')  
                 
    finally:
        logger.info('closing projector') 
        projector.close()
        logger.info('releasing the lock') 
        lock.release()  




    
def get_status():

    try:

        lock.acquire()
        
        projector = get_projector()
        
        ser_io = get_io_wrapper(projector)
        
        if projector.isOpen():

            projector.flushInput()
            projector.flushOutput()
        
            ser_io.write(unicode(status_command + '\r'))
            
            while projector.inWaiting() == 0:
                time.sleep(1)
            
            while projector.inWaiting() > 0:
                line = ser_io.readline();
            
                if not line.startswith('*'):
                    status = str(line.strip())
                    if status.endswith('0'):
                        return 'OFF'
                    else:
                        return 'ON'  
        else:
            logger.error('Projector connection closed')  
                 
    finally:
        #print('closing projector') 
        projector.close()
        #print('releasing the lock') 
        lock.release()    

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        logger.info("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        logger.error("Connection failed")
 
def on_message(client, userdata, msg):
    logger.info ("Message received: "  + msg.payload)
    payload = json.loads(msg.payload)
    logger.info('Command {}'.format(payload['command']))
    logger.info('Expected state {}'.format(payload['expected_status']))

    acer_command = payload['command']
    expected_status = payload['expected_status']

    power_status = get_status()

    while expected_status != power_status:
        logger.info('Toggle projector power from {} to {}'.format(power_status, expected_status))
        send_command(acer_command)
        time.sleep(10)
        power_status = get_status()

    logger.info('Projector power toggled to {}'.format(power_status))

parser = argparse.ArgumentParser()

parser.add_argument('-b', '--broker', help='IP Address for MQTT Broker (Required)', required=True)
parser.add_argument('-p', '--port', help='Port for MQTT Broker (Required)', required=True)
parser.add_argument('-u', '--user', help='User for MQTT Broker (Required)', required=True)
parser.add_argument('-pw', '--password', help='Password for MQTT Broker (Required)', required=True)
parser.add_argument('-sp', '--serialport', help='Serial port for acer projector (Required)', required=True)
parser.add_argument('-st', '--statetopic', help='Optional topic for state')
parser.add_argument('-pt', '--powertopic', help='Optional topic for power')

args = vars(parser.parse_args())

setup_logger()

globals()['serial_port'] = args['serialport']
 
Connected = False #global variable for the state of the connection
 
broker_address= args['broker']
port = args['port']
user = args['user']
password = args['password'] 

client = mqttClient.Client("Projector")               #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message 


client.connect(broker_address, port=port)  #connect to broker
client.loop_start()                        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)

powertopic = "acer/power" if args['powertopic'] is None else args['powertopic']
statetopic = "acer/state" if args['statetopic'] is None else args['statetopic']

client.subscribe(powertopic)




try:
    while True:
        status = get_status()
        if status != previous_status:
            logger.info("Current status %s" % status)
            previous_status = status

        #print(status)
        #print(statetopic)
        client.publish(statetopic,status)
        time.sleep(5)# sleep for 5 seconds before next call
 
except KeyboardInterrupt:
    print ("exiting")
    client.disconnect()
    client.loop_stop()