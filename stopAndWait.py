from threading import Thread
from queue import Queue
import time

timeoutAmount = 5
timeBetweenEachSend = 1
numberOfPackets = 10

def timer(timeoutAmount, queueTimer, s):
    time.sleep(timeoutAmount)
    queueTimer.put("timeout" + str(s))

def sender(queuePackets, queueAcks, queueTimer, timeoutAmount, numberOfPackets):
    ack = ""
    s = 0
    isReceived = False
    queuePackets.put("packet" + str(s))
    s += 1
    ack = queueAcks.get()
    print(ack)
    while s < numberOfPackets:
        if int(ack[-1]) == s - 1:
            time.sleep(timeBetweenEachSend)
            queuePackets.put("packet" + str(s))
            
            timerThread = Thread(target = timer, args =(timeoutAmount, queueTimer, s))
            timerThread.start()

            while not isReceived:
                try:
                    # for check timer timeout
                    timerMessage = queueTimer.get_nowait()
                    if int(timerMessage[-1]) == s:
                        print(timerMessage)
                        break
                except:
                    pass
                try:
                    ack = queueAcks.get_nowait()
                    isReceived = True
                except:
                    pass

            else: # if while loop end with false condition it runs (if break occur it dosen't run)
                isReceived = False
                print(ack)
                s += 1

def receiver(queuePackets, queueAcks):
    packet = ""
    sendingCounterForTest = 2
    packetNumberForTest = 3
    while True:
        packet = queuePackets.get()
        print(packet)
        if int(packet[-1]) == packetNumberForTest: # packet lost
            if sendingCounterForTest > 0:
                sendingCounterForTest -= 1
                continue
        time.sleep(timeBetweenEachSend)
        queueAcks.put("ack" + packet[-1])


queuePackets = Queue()
queueAcks = Queue()
queueTimer = Queue()

threadSender = Thread(target = sender, args =(queuePackets, queueAcks, queueTimer, timeoutAmount, numberOfPackets))
threadReceiver = Thread(target = receiver, args =(queuePackets, queueAcks))
threadSender.start()
threadReceiver.start()