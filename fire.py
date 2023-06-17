from pushbullet import Pushbullet
import RPi.GPIO as GPIO
import smtplib
import time

channel=14
buzzer=4
ledred=21
ledgreen=20
SPICLK=11
SPIMISO=9
SPIMOSI=10
SPICS=8
mq2_dpin = 26
mq2_apin = 0
GMAIL_USER_TO=["cjkteam25@gmail.com","kyrillosadel503@gmail.com","keroadelbeast@gmail.com"]
GMAIL_USER_FROM="carlosadel503@gmail.com"
PASS="ostpotbregtkxmlp"
SUBJECT='ALERT!'
TEXT= ['Fire in The company','Fire is increasing please evacuate']
TEXT2='Gas Leak, Please evacuate'
num=0
#pb= Pushbullet("o.yI2MhPKc2rrfwfJUakaFZbnsp7toy5DG")
#print (pb.devices)

#dev =pb.get_device ('Oppo F7')

def send_mail(channel,num):
	server=smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(GMAIL_USER_FROM,PASS)
	header='From: ' + GMAIL_USER_FROM
	header= header + '\n' + 'Subject: ' +SUBJECT + '\n'
	print (header)
	msg = header + '\n' + TEXT + '\n\n'
	server.sendmail(GMAIL_USER_FROM,GMAIL_USER_TO,msg)
	server.quit()
	print("text sent")
	time.sleep(6)
    
def send_mail2(mq2_apin):
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(GMAIL_USER_FROM,PASS)
	header= 'To: ' + GMAIL_USER_TO +'\n' + 'From: ' + GMAIL_USER_FROM
	header= header + '\n' + 'Subject: ' +SUBJECT + '\n'
	print (header)
	msg= header + '\n' + TEXT2 + '\n\n'
	server.sendmail(GMAIL_USER_FROM,GMAIL_USER_TO,msg)
	server.quit()
	print("text sent")
	time.sleep(6)
def init():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(mq2_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(mq2_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(channel,GPIO.IN)
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setup(ledred,GPIO.OUT)
    GPIO.setup(ledgreen,GPIO.OUT)

    #GPIO.add_event_callback(channel,callback)
    def callback(channel):
        print("flame detected")
    GPIO.add_event_detect(channel,GPIO.BOTH, bouncetime=300) 
    GPIO.add_event_callback(channel,callback)  
    GPIO.output(buzzer,GPIO.LOW) 
    GPIO.output(ledgreen,GPIO.HIGH)
    GPIO.output(ledred,GPIO.LOW)
     
#def callback(channel):
 #   print("flame detected")
 
# let us know when the pin goes HIgH or LOW
#assign function GPio BIN,
#Run function on change
#infinite loop
#read SPI data from MCP3008 chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    #print("ADC Num!!",adcnum)
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)	

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
                GPIO.output(mosipin, True)
        else:
                GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)
    
    adcout >>= 1       # first bit is 'null' so drop it
    return adcout
    
def main():
    init()
    
    time.sleep(4)
    while True:
            COlevel=readadc(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
            send_count=0
            SmokeTrigger = ((COlevel/1024.)*3.3)
            
            if (GPIO.input(14) == True)and(time.sleep(2)):
                print ("fire in the company")
                GPIO.output(ledgreen,GPIO.LOW)
                GPIO.output(buzzer, 1)
                GPIO.output(ledred, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred, GPIO.LOW)
                time.sleep(1)
            
                try :
                    send_mail(channel,0)
                    send_count +=1
                except:
                    continue
 #               push =dev.push_note ("fire", "pleaaaaase evacuate")
                if (send_count>=2):
                    try:
                        send_mail(channel,1)
                        send_count +=1
                    except:
                        continue
            elif GPIO.input(mq2_dpin):
                print("Gas not leak")
                time.sleep(0.5)
            elif (SmokeTrigger>1.60):
                print("Gas leakage")
                print("Current Gas AD vaule = " +str("%.2f"%((COlevel/1024.)*3.3))+" V")
                
                GPIO.output(ledgreen,GPIO.LOW)
                GPIO.output(buzzer, 1)
                GPIO.output(ledred, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred, GPIO.LOW)
                time.sleep(1)
                #push =dev.push_note ("Gas leakage", "pleake evacuate")
                #print ("Sent") 
                try: 
                    send_mail2(mq2_apin)
                except:
                    continue 
            #elif (SmokeTrigger>=1.55) and (GPIO.input(14) == True):
             #   print("please call 911 and authorities") 
              #  GPIO.output(ledgreen,GPIO.LOW)
               # GPIO.output(buzzer, 1)
                #time.sleep(2)
                #GPIO.output(ledred, GPIO.HIGH)
                #time.sleep(5)
                #GPIO.output(buzzer, 0)
                #GPIO.output(ledred, GPIO.LOW)
                #time.sleep(5)
                #send_mail(channel,SmokeTrigger)
                #push =dev.push_note ("تحذير","الرجاء اخلاء المبني")
                #print ("Sent") 
            else:
                print ("you are safe")
                #print ("Gas not leak")
                time.sleep(1)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred,GPIO.LOW)
                GPIO.output(ledgreen,GPIO.HIGH)
if __name__=='__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass    


