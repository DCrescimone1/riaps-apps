
from riaps.run.comp import Component
import logging
import time
import os
import random
from gridlabdagentlib.gridlabdagent import gridlabdagent

class SwitchController(Component):
    def __init__(self):
        super(SwitchController, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting SwitchController, %s" % (str(self.pid),str(now)))
        self.comm = 1
        self.gridagent = gridlabdagent()
        self.logger.info("agent created")
        
#     def handleActivate(self):
#         self.gridagent = gridlabdagent()
#         self.logger.info("agent created")


    '''def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_recvsensorreq(): PID %s" % (str(self.pid)))
#         msg = self.clock.recv_pyobj()
#         self.temperature = self.temperature + 1
#         msg = str(self.temperature)
#         msg = (now,msg)
        self.logger.info("%d" %self.gridagent.time_granted)
        if self.gridagent.time_granted < self.gridagent.time_stop:
            #self.time_granted = fncs.time_request(self.time_granted+1800)
            self.gridagent.get_simulation_time(self.gridagent.time_stop)
#             self.time_granted = fncs.time_request(self.time_stop)
            self.logger.info("time granted: %f" % self.gridagent.time_granted)
#             events = fncs.get_events()
#             for topic in events:
#                 value = fncs.get_value(topic)
            self.gridagent.get_values()
            
            for topic, value in self.gridagent.valuelist.items():
                if topic == "distribution_load":
                    print('%s received' % topic)
                    self.comm = 1 - self.comm
                    self.logger.info("on_clock): Command - %s, PID %s, %s" % (str(self.comm),str(self.pid),str(now)))
#                 self.recvsensorreq().send_pyobj(value)
                
                    self.logger.info("sending command to gridlab-d")
                    self.gridagent.publish_gridlabd("sw_status", str(self.comm))
                    break
                    
        else:
            self.logger.info("simulation ended")'''
            
    def on_recvsensorreq(self):
            msg = self.recvsensorreq.recv_pyobj()
            self.logger.info("on_recvsensorreq(): PID %s" % (str(self.pid)))
            self.logger.info("%d" %self.gridagent.time_granted)
            if self.gridagent.time_granted < self.gridagent.time_stop:
                #self.time_granted = fncs.time_request(self.time_granted+1800)
                self.gridagent.get_simulation_time(self.gridagent.time_stop)
    #             self.time_granted = fncs.time_request(self.time_stop)
                self.logger.info("time granted: %f" % self.gridagent.time_granted)
                self.gridagent.get_values()
                
                for topic, value in self.gridagent.valuelist.items():
                    if topic == msg:
                        print('%s received' % topic)
#                         self.comm = 1 - self.comm
                        self.logger.info("sending reply")
                        self.recvsensorreq.send_pyobj(value)
                    
    #                     self.logger.info("sending command to gridlab-d")
    #                     self.gridagent.publish_gridlabd("sw_status", str(self.comm))
                        break
                        
            else:
                self.logger.info("simulation ended")

                    
    def on_recvcmd(self):
        msg = self.recvcmd.recv_pyobj()
#         self.gridagent.time_granted = self.gridagent.get_simulation_time(self.gridagent.time_granted + 10)
        self.logger.info("sending command to gridlab-d")
        self.gridagent.publish_gridlabd(msg["topic"], msg["value"])
        self.recvcmd.send_pyobj("ok")

    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping SwitchController, %s" % (str(self.pid),now))
        self.gridagent.terminate()
