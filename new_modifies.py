from socket import *
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
import threading 

GPIO.setmode(GPIO.BOARD)
mot = 33                                                                                    #the "redLED" variable refers to the GPIO pin 12 which the red LED is connected on.
mot1 = 35                                                                                   #the "blueLED" variable refers to the GPIO pin 19 which the blue LED is connected on.
moten = 37

Motor1 = 16    # Input Pin
Motor2 = 18    # Input Pin
Motor3 = 22    # Enable Pin
GPIO.setup(40, GPIO.IN)   # for LPG
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)
channel = 38
GPIO.setup(channel, GPIO.IN)  #  for flme

GPIO.setup(mot,GPIO.OUT)
GPIO.setup(mot1,GPIO.OUT)
GPIO.setup(moten,GPIO.OUT)

GPIO.setwarnings(False)

HOST = ''
PORT = 21567
BUFSIZE = 1024
ADDR = (HOST,PORT)
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

lpg_flag = 0
flame_flag = 2  #knob

            


def Sytem_CloseKnob():
    GPIO.output(Motor1,GPIO.LOW)
    GPIO.output(Motor2,GPIO.HIGH)
    GPIO.output(Motor3,GPIO.HIGH)
    sleep(3)
    GPIO.output(Motor3,GPIO.LOW)
    print('Knob closed by system.')
    
    
    
def Sytem_CloseKnob_Flameoff():
    #if flame_flag == 0:
    GPIO.output(Motor1,GPIO.LOW)
    GPIO.output(Motor2,GPIO.HIGH)
    GPIO.output(Motor3,GPIO.HIGH)
    sleep(3)
    GPIO.output(Motor3,GPIO.LOW)
    print('Knob closed by system.')
        
    
    
    
def FLAME():
    while True:
        i=GPIO.input(38)
        if i==1 and flame_flag==1:
            print('Closing knob in 15 seconds...')
            sleep(15)
            Sytem_CloseKnob()
            break
        


    
    
###############For LPG Sensor#########################
def LPG():
    
    while True :
        #FLAME()
        i=GPIO.input(40)
        if i==1:                        #When output from LPG sensor is LOW        
            #print("No Gas Leakage Detected",i)
            pass
            
        if i==0:                        #When output from LPG sensor is HIGH
            
            if  lpg_flag == 0 :             #if knob is open
                print("Gas Leakage Detected.")
                GPIO.output(mot,GPIO.HIGH)
                GPIO.output(mot1,GPIO.LOW)
                GPIO.output(moten,GPIO.HIGH)
                Sytem_CloseKnob()                
                sleep(15)
                print('Done')
                
            elif lpg_flag == 1 :           #if knob is close
                print("Gas Leakage Detected. Knob already closed.")
                sleep(15)
                print('Done')
                GPIO.output(moten,GPIO.LOW)
        

t1 = threading.Thread(target=LPG)
t1.start()
#t1.join()
###############END#######################

################For Flame Sensor###########






################END######################     

##############Motor Rotation##############
while True:
        
        print('Waiting for connection')
        tcpCliSock,addr = tcpSerSock.accept()
        print('Connected from :', addr)
        
        try:
               while True:                 
                        data = tcpCliSock.recv(BUFSIZE)                        
                        #print('data : ',data)
                        data=str(data)
                        #print(type(data))
                        if not data:
                                break
                        if data[2] == '1':
                                print("User Open Knob.")
                                print("Openinig...",end='')
                                GPIO.output(Motor1,GPIO.HIGH)
                                GPIO.output(Motor2,GPIO.LOW)
                                GPIO.output(Motor3,GPIO.HIGH)                                
                                sleep(2.5)
                                GPIO.output(Motor3,GPIO.LOW)
                                print('Done')
                                lpg_flag = 0
                                flame_flag = 1
                                close = 0
                                t2 = threading.Thread(target=FLAME)
                                sleep(10)
                                t2.start()
                        if data[2] == '0':
                                print("User Close Knob.")
                                print("Closing...",end='')
                                GPIO.output(Motor1,GPIO.LOW)
                                GPIO.output(Motor2,GPIO.HIGH)
                                GPIO.output(Motor3,GPIO.HIGH)
                                sleep(2.5)
                                GPIO.output(Motor3,GPIO.LOW)
                                print('Done')
                                lpg_flag = 1
                                flame_flag = 0
                                close = 1
                        else:                            
                            break
               #t3 = threading.Thread(target=LPG)
               #t3.start()                  
                                  
        except KeyboardInterrupt:
                print('Error')
                print("STOP")
                GPIO.output(Motor3,GPIO.LOW)
                GPIO.cleanup()
###################END##############################
tcpSerSock.close();



