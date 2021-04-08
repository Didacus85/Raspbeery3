#!/usr/bin/env python
# coding=utf-8

import sys, getopt
import RPi.GPIO as GPIO
import time
import threading
import ctypes 
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import tempidbmod

#impostare servizio a True per il file che verrà letto dal servizio, False per il file che verrà lanciato da interfaccia web
servizio = True

vuoto1 = 17 # define attori
vuoto2 = 27
co2 = 22
birra = 10
spunding = 9
sfiato = 11
rele7 = 5
rele8 = 6
ssr = 13

comandorunning = 19
ricezionerunning = 26

button1 = 18
button2 = 23
button3 = 24
button4 = 25
button5 = 12
button6 = 16

timeVuoto = 0
timeCo2 = 0
timeCo2Sfiato = 0
timeBirraRiempimento = 0
timeBirraAttesa = 0
timeSfiato = 0

numCicliPrepara=0
numCicliPulizia=0

running = False
relayAttivoOnHigh=False

lcd=1

def setUscita(uscita, stato):
    #i relè Elegoo funzionano al contrario si chiudono se il GPIO è LOW, cambiando relayAttivoOnHigh si puo cambiare velocemente la logica
    if relayAttivoOnHigh:
        if stato:
            GPIO.output(uscita, GPIO.HIGH)
        if not stato:
            GPIO.output(uscita, GPIO.LOW)
            
    if not relayAttivoOnHigh:
        if stato:
            GPIO.output(uscita, GPIO.LOW)
        if not stato:
            GPIO.output(uscita, GPIO.HIGH)

def setUscitaSSR(uscita, stato):
    #i relè SSR funzionano solo in un modo
    if stato:
        GPIO.output(uscita, GPIO.HIGH)
    if not stato:
        GPIO.output(uscita, GPIO.LOW)


def setuprunning():
    GPIO.setmode(GPIO.BCM) # use BCM mode
    GPIO.setwarnings(False)
    GPIO.setup(comandorunning, GPIO.OUT)
    GPIO.setup(ricezionerunning, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def setup():
    GPIO.setmode(GPIO.BCM) # use BCM mode
    GPIO.setwarnings(False)
    
    GPIO.setup(vuoto1, GPIO.OUT) # set OUTPUT mode
    setUscita(vuoto1,False)
    GPIO.setup(vuoto2, GPIO.OUT)
    setUscita(vuoto2,False)
    GPIO.setup(co2, GPIO.OUT)
    setUscita(co2,False)
    GPIO.setup(birra, GPIO.OUT)
    setUscita(birra,False)
    GPIO.setup(spunding, GPIO.OUT)
    setUscita(spunding,False)
    GPIO.setup(sfiato, GPIO.OUT)
    setUscita(sfiato,False)
    GPIO.setup(rele7, GPIO.OUT)
    setUscita(rele7,False)
    GPIO.setup(rele8, GPIO.OUT)
    setUscita(rele8,False)
    GPIO.setup(ssr, GPIO.OUT)
    setUscitaSSR(ssr,False)
    

    GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    if servizio:
        #$$ Commentare tutti gli add_event in Raspbeery_1
        GPIO.add_event_detect(button1, GPIO.FALLING, callback=threadCo2, bouncetime=1000)
        GPIO.add_event_detect(button2, GPIO.FALLING, callback=threadRiempimento, bouncetime=1000)
        GPIO.add_event_detect(button3, GPIO.FALLING, callback=threadRiempimentoConTimer, bouncetime=1000)
        GPIO.add_event_detect(button4, GPIO.FALLING, callback=threadSfiata, bouncetime=1000)
        GPIO.add_event_detect(button5, GPIO.FALLING, callback=threadProcessoCompleto, bouncetime=1000)
        GPIO.add_event_detect(ricezionerunning, GPIO.BOTH, callback=readrunning, bouncetime=300)
        #GPIO.add_event_detect(button6, GPIO.FALLING, callback=threadReset, bouncetime=5000)

def debounceinput(button):
    time.sleep(0.005) # debounce for 5mSec
    if GPIO.input(button)!=GPIO.LOW:
        print('Debounceinput KO')
        return False

    time.sleep(0.005)
    if GPIO.input(button)!=GPIO.LOW:
        print('Debounceinput KO')
        return False

    print('Debounceinput OK')
    return True

def setuplcd():
    global lcd
    PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
    PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
    # Create PCF8574 GPIO adapter.
    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except:
        try:
            mcp = PCF8574_GPIO(PCF8574A_address)
        except:
            print ('I2C Address Error !')
            exit(1)
    # Create LCD, passing in MCP GPIO adapter.
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)


    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns
    lcd.setCursor(0,0)  # set cursor position
    print ('setup end')

def readrunning(channel):
    GPIO.setmode(GPIO.BCM) # use BCM mode
    GPIO.setwarnings(False)
    global running
    if GPIO.input(ricezionerunning):
        running=True
    else:
        running=False
    print('readrunning '+str(running))
    
def writerunning(r):
    GPIO.setmode(GPIO.BCM) # use BCM mode
    GPIO.setwarnings(False)
    global running
    running=r
    if running:
        GPIO.output(comandorunning, GPIO.HIGH)
    if not running:
        GPIO.output(comandorunning, GPIO.LOW)
    print('writerunning '+str(running))


def lcdmessage():
    lcd.message('    WELCOME    ')

def readtempi():
    global numCicliPrepara
    global timeVuoto
    global timeCo2
    global timeCo2Sfiato
    global timeBirraRiempimento
    global timeBirraAttesa
    global timeSfiato
    global numCicliPulizia
    
    numCicliPrepara=int(tempidbmod.getNumCicliPrepara())
    timeVuoto=float(tempidbmod.getTimeVuoto())
    timeCo2=float(tempidbmod.getTimeCo2())
    timeCo2Sfiato=float(tempidbmod.getTimeCo2Sfiato())
    timeBirraRiempimento=float(tempidbmod.getTimeBirraRiempimento())
    timeBirraAttesa=float(tempidbmod.getTimeBirraAttesa())
    timeSfiato=float(tempidbmod.getTimeSfiato())
    numCicliPulizia=int(tempidbmod.getNumCicliPulizia())

    #f = open("/var/www/html/Birra/Tempi.txt", "r")
    #xnumCicliPrepara=f.readline()
    #xtimeVuoto=f.readline()
    #xtimeCo2=f.readline()
    #xtimeCo2Sfiato=f.readline()
    #xtimeBirraRiempimento=f.readline()
    #xtimeBirraAttesa=f.readline()
    #xtimeSfiato=f.readline()
    
    #xnumCicliPrepara = xnumCicliPrepara.replace("numCicliPrepara=", "")
    #xtimeVuoto = xtimeVuoto.replace("timeVuoto=", "")
    #xtimeCo2 = xtimeCo2.replace("timeCo2=", "")
    #xtimeCo2Sfiato = xtimeCo2Sfiato.replace("timeCo2Sfiato=", "")
    #xtimeBirraRiempimento = xtimeBirraRiempimento.replace("timeBirraRiempimento=", "")
    #xtimeBirraAttesa = xtimeBirraAttesa.replace("timeBirraAttesa=", "")
    #xtimeSfiato = xtimeSfiato.replace("timeSfiato=", "")

    #print(xnumCicliPrepara+xtimeVuoto+xtimeCo2+xtimeCo2Sfiato+xtimeBirraRiempimento+xtimeBirraAttesa+xtimeSfiato)
    #f.close()

    #numCicliPrepara=int(xnumCicliPrepara)
    #timeVuoto=float(xtimeVuoto)
    #timeCo2=float(xtimeCo2)
    #timeCo2Sfiato=float(xtimeCo2Sfiato)
    #timeBirraRiempimento=float(xtimeBirraRiempimento)
    #timeBirraAttesa=float(xtimeBirraAttesa)
    #timeSfiato=float(xtimeSfiato)

def writetempi():
    #global numCicliPrepara
    #global timeVuoto
    #global timeCo2
    #global timeCo2Sfiato
    global timeBirraRiempimento
    #global timeBirraAttesa
    #global timeSfiato

    tempidbmod.changesavesetting("timeBirraRiempimento",timeBirraRiempimento);
    #f = open("/var/www/html/Birra/Tempi.txt", "w")
    #f.write('numCicliPrepara='+str(numCicliPrepara))
    #f.write('\ntimeVuoto='+str(timeVuoto).replace(".0", ""))
    #f.write('\ntimeCo2='+str(timeCo2).replace(".0", ""))
    #f.write('\ntimeCo2Sfiato='+str(timeCo2Sfiato).replace(".0", ""))
    #f.write('\ntimeBirraRiempimento='+str(timeBirraRiempimento).replace(".0", ""))
    #f.write('\ntimeBirraAttesa='+str(timeBirraAttesa).replace(".0", ""))
    #f.write('\ntimeSfiato='+str(timeSfiato).replace(".0", ""))
    #f.close() 
        
def chiudiTutto():
    setUscita(vuoto1,False)
    setUscita(vuoto2,False)
    setUscita(co2,False)
    setUscita(birra,False)
    setUscita(spunding,False)
    setUscita(sfiato,False)
    setUscita(rele7,False)
    setUscita(rele8,False)
    setUscitaSSR(ssr,False)

def preparaCo2():
    lcd.clear()
    if timeVuoto > 0:
        lcd.message('PREPARA  '+str(numCicliPrepara) + ' Cicli\n( '+str(timeVuoto)+'s - '+str(timeCo2)+'s )')
        setUscitaSSR(ssr,True)
        setUscita(vuoto1,True)
        setUscita(vuoto2,True)
        time.sleep(timeVuoto)
        setUscita(vuoto1,False)
        #setUscita(vuoto2,False)
        #setUscitaSSR(ssr,False)
        for x in range(1,numCicliPrepara):
            setUscita(co2,True)
            time.sleep(timeCo2)
            setUscita(co2,False)
            #etUscitaSSR(ssr,True)
            setUscita(vuoto1,True)
            #setUscita(vuoto2,True)
            time.sleep(timeVuoto)
            setUscita(vuoto1,False)
            #setUscita(vuoto2,False)
            #setUscitaSSR(ssr,False)
        setUscita(vuoto2,False)
        setUscitaSSR(ssr,False)
        
    if timeVuoto <= 0 or timeVuoto == '':
        lcd.message('PREPARA  '+str(numCicliPrepara) + ' Cicli\n( '+str(timeCo2)+'s - '+str(timeCo2Sfiato)+'s )')
        for x in range(0,numCicliPrepara):
            #lcd.clear()
            #lcd.message('PREPARAZIONE\nCO2 '+str(timeCo2)+'s')
            setUscita(co2,True)
            time.sleep(timeCo2)
            setUscita(co2,False)
            #lcd.clear()
            #lcd.message('PREPARAZIONE\nSFIATO '+str(timeCo2Sfiato)+'s')
            setUscita(sfiato,True)
            time.sleep(timeCo2Sfiato)
            setUscita(sfiato,False)
            #lcd.clear()

    #lcd.message('PREPARAZIONE\nCO2 '+str(timeCo2)+'s')
    setUscita(co2,True)
    time.sleep(timeCo2)
    setUscita(co2,False)
    lcd.clear()
    lcd.message('PREPARAZIONE\nPRONTO')
    time.sleep(0.5)


def riempimento():
    lcd.clear()
    lcd.message('RIEMPIMENTO '+str(timeBirraRiempimento)+'s')
    setUscita(birra,True)
    setUscita(spunding,True)
    time.sleep(timeBirraRiempimento)
    
    setUscita(birra,False)
    setUscita(spunding,False)
    lcd.clear()
    lcd.message('STABILIZZAZIONE\n'+str(timeBirraAttesa)+'s\n')
    time.sleep(timeBirraAttesa)
    lcd.clear()
    lcd.message('RIEMPIMENTO\nFINITO')
    time.sleep(0.5)

def riempimentoConTimer():
    global timeBirraRiempimento
    lcd.clear()
    lcd.message('RIEMPIMENTO\nCON TIMER')
    startTime = time.time()
    while GPIO.input(button3)==GPIO.LOW:
        setUscita(birra,True)
        setUscita(spunding,True)
        #time.sleep(timeBirraRiempimento)
    
    setUscita(birra,False)
    setUscita(spunding,False)
    endTime = time.time()
    diffTime = round(endTime-startTime,1)
    print ('Time Riempimento Rilevato: '+str(diffTime))
    timeBirraRiempimento=diffTime
    writetempi()
    
    #lcd.clear()
    #lcd.message('STABILIZZAZIONE\n'+str(timeBirraAttesa)+'s\n')
    #time.sleep(timeBirraAttesa)
    lcd.clear()
    lcd.message('RIEMPIMENTO\nFINITO '+str(diffTime)+'s')
    time.sleep(0.5)

def sfiata():
    lcd.clear()
    lcd.message('RILASCIO SCHIUMA\n'+str(timeSfiato)+'s')
    setUscita(sfiato,True)
    time.sleep(timeSfiato)
    setUscita(sfiato,False)
    lcd.clear()
    lcd.message('RILASCIO SCHIUMA\nFINITO')


def processoCompleto():
    preparaCo2()
    riempimento()
    sfiata()

def pulizia():
    for x in range(0,numCicliPrepara):
        lcd.clear()
        lcd.message('CICLO PULIZIA N° \n'+str(x+1)+' DI '+str(numCicliPrepara))

        sleep = 4

        setUscita(birra,True)

        setUscita(sfiato,True)
        time.sleep(sleep)
        setUscita(sfiato,False)

        setUscita(spunding,True)
        time.sleep(sleep)
        setUscita(spunding,False)

        setUscita(co2,True)
        time.sleep(sleep)
        setUscita(co2,False)

        setUscita(vuoto1,True)
        time.sleep(sleep)
        setUscita(vuoto1,False)

        #######

        fastsleep=1

        for y in range(0, 3):
            setUscita(birra,False)
            time.sleep(fastsleep)
            setUscita(birra,True)

            setUscita(sfiato,True)
            time.sleep(fastsleep)
            setUscita(sfiato,False)

            setUscita(spunding,True)
            time.sleep(fastsleep)
            setUscita(spunding,False)

            setUscita(co2,True)
            time.sleep(fastsleep)
            setUscita(co2,False)

            setUscita(vuoto1,True)
            time.sleep(fastsleep)
            setUscita(vuoto1,False)

            setUscita(birra,False)

        lcd.clear()
        lcd.message('AMMOLLO N° \n'+str(x+1)+' DI '+str(numCicliPrepara))

        time.sleep(10)

    lcd.clear()
    lcd.message('CICLI PULIZIA\nFINITI')

def loop():
    while True:
        time.sleep(0.1)

def destroy():
    lcd.clear()
    #GPIO.cleanup() # Release all GPIO


class thread_with_exception(threading.Thread):        
    def __init__(self, name): 
        threading.Thread.__init__(self) 
        self.name = name
        
    def run(self):
  
        # target function of the thread class 
        try:
            global running
            readtempi()
            chiudiTutto()
            
            if self.name=='preparaCo2':
                preparaCo2()
            if self.name=='riempimento':
                riempimento()
            if self.name=='riempimentoConTimer':
                riempimentoConTimer()
            if self.name=='sfiata':
                sfiata()
            if self.name=='processoCompleto':
                processoCompleto()
            if self.name=='pulizia':
                pulizia()
                
            writerunning(False)
            #GPIO.remove_event_detect(button6)
                
        finally:
            #GPIO.remove_event_detect(button6)
            print('--- ENDED ---') 
           
    def get_id(self): 
  
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
   
    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 

#pill2kill = threading.Event()
#t1 = threading.Thread(target=preparaCo2, args=())
    
def threadCo2(channel):
    if debounceinput(button1):
        global running
        if not servizio:
            readrunning(1)
            
        if not running:
            writerunning(True)
            GPIO.remove_event_detect(button6)
            thCo2 = thread_with_exception('preparaCo2') 
            GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thCo2), bouncetime=1000)
            thCo2.start()

def threadRiempimento(channel):
    if debounceinput(button2):
        global running
        if not servizio:
            readrunning(1)
            
        if not running:
            writerunning(True)
            GPIO.remove_event_detect(button6)
            thRiempimento = thread_with_exception('riempimento') 
            GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thRiempimento), bouncetime=1000)
            thRiempimento.start()

def threadRiempimentoConTimer(channel):
    if debounceinput(button3):
        global running
        if not servizio:
            readrunning(1)
        if not running:
            writerunning(True)
            GPIO.remove_event_detect(button6)
            thRiempimentoConTimer = thread_with_exception('riempimentoConTimer')
            GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thRiempimentoConTimer), bouncetime=1000)
            thRiempimentoConTimer.start()
    
def threadSfiata(channel):
    if debounceinput(button4):
        global running
        if not servizio:
            readrunning(1)
            
        if not running:
            writerunning(True)
            GPIO.remove_event_detect(button6)
            thSfiata = thread_with_exception('sfiata') 
            GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thSfiata), bouncetime=1000)
            thSfiata.start()

def threadProcessoCompleto(channel):
    if debounceinput(button5):
        global running
        if not servizio:
            readrunning(1)
            
        if not running:
            writerunning(True)
            GPIO.remove_event_detect(button6)
            thProcessoCompleto = thread_with_exception('processoCompleto')
            GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thProcessoCompleto), bouncetime=1000)
            thProcessoCompleto.start()

def threadPulizia(channel):
    global running
    if not servizio:
        readrunning(1)
        
    if not running:
        writerunning(True)
        GPIO.remove_event_detect(button6)
        thPulizia = thread_with_exception('pulizia') 
        GPIO.add_event_detect(button6, GPIO.FALLING, callback=lambda a:threadReset(thPulizia), bouncetime=1000)
        thPulizia.start()


def threadReset(t1):
    global running
    #per ora non viene usata da web
    #if not servizio:
     #   readrunning(1)

    t1.raise_exception()
    writerunning(False)
    chiudiTutto()
    lcd.clear()
    lcd.message('INTERROTTO\nMANUALMENTE')
    print('threadReset')
    GPIO.remove_event_detect(button6)
    t1.join()

    
def external_call(argv):
    channel=''
    azione=''
    try:
        opts, args = getopt.getopt(argv,"ha:",["azione="])
    except getopt.GetoptError:
        print ('Raspbeery.py -a <azione>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('Raspbeery.py -a <preparaCo2> <riempimento> <sfiata> <processoCompleto> <pulizia> <threadReset>')
            sys.exit()
        elif opt in "-a":
            azione = arg
            print ('Azione selezionata: '+azione)
            
        if azione=='preparaCo2':
            threadCo2(channel)
        if azione=='riempimento':
            threadRiempimento(channel)
        if azione=='sfiata':
            threadSfiata(channel)
        if azione=='processoCompleto':
            threadProcessoCompleto(channel)
        if azione=='threadReset':
            threadReset(channel)
        if azione=='pulizia':
            threadPulizia(channel)


if __name__ == '__main__': # Program entrance
    print ('Program is starting ... \n')
    if servizio:
        setuprunning()
        setuplcd()
        setup()
        lcdmessage()
        writerunning(False)
        try:
            loop()
        except KeyboardInterrupt: # Press ctrl-c to end the program.
            destroy()
            
    if not servizio:
        setuprunning()
        readrunning(1)
        if not running:
            setuplcd()
            setup()
            try:
                external_call(sys.argv[1:])
            except KeyboardInterrupt: # Press ctrl-c to end the program.
                destroy()
