import thread
import time

class Timer:
    def __init__(self):
        self.tickInc=0.2
        self.tickRate=0.2
        self.now=0
        self.events=[]
        self.stop=0
        thread.start_new_thread(self.tick,())
    def addEvent(self,delay,func,args=()):
        finishTime=self.now+delay
        self.events.append((finishTime,func,args))
        self.events.sort()
    def stopTimer(self):
        self.stop=1
    def tick(self):
        while not self.stop:
            time.sleep(self.tickRate)
            self.now=self.now+self.tickInc
            while len(self.events)>0 and self.events[0][0]<=self.now:
                t,func,args=self.events.pop(0)
                apply(func,args)
