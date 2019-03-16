#!/usr/bin/python -u
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






    
def get_status():

    try:

        lock.acquire()
        
        projector = get_projector()
        
        ser_io = get_io_wrapper(projector)
        
        if projector.isOpen():

            projector.flushInput()
            projector.flushOutput()
        
            ser_io.write(unicode(status_command + '\r'))

            for x in range(0, 5):
                time.sleep(1)
                if projector.inWaiting() > 0:
                    break
            
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



parser = argparse.ArgumentParser()

parser.add_argument('-st', '--statetopic', help='Optional topic for state')

args = vars(parser.parse_args())

setup_logger()

globals()['serial_port'] = args['serialport']
 
status = get_status()

logger.info("Current status %s" % status)
previous_status = status
