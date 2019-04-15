
from riaps.run.comp import Component
import logging
import time
import os
import random
import threading
import zmq
#from gridlabdagentlib.gridlabdagent import gridlabdagent

class SwitchControllerThread(threading.Thread):
    '''
    Inner SwitchController thread
    '''
    def __init__(self,trigger,ip, pub_port, sub_port, topic,logger):
        threading.Thread.__init__(self)
        self.logger = logger
        self.active = threading.Event()
        self.active.clear()
        self.waiting = threading.Event()
        self.terminated = threading.Event()
        self.terminated.clear()
        self.trigger = trigger              # inside RIAPS port
        self.pub_port = pub_port 
        self.sub_port = sub_port
        self.logger.info("pub_port = %s" % self.pub_port)
        self.logger.info("sub_port = %s" % self.sub_port)  
        self.topic = topic      
        self.ip = ip
        self.logger.info("ip = %s" % self.ip)            # port number for socket to connect to connect to console client 
        self.context = zmq.Context()
        self.cons = self.context.socket(zmq.SUB)    # Create zmq REP socket 
        self.cons.connect("tcp://%s:%s" % (self.ip,self.sub_port))
        self.cons.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.grid = self.context.socket(zmq.PUB)
        self.grid.connect("tcp://localhost:%s" % self.pub_port)
        self.logger.info('IODeviceThread _init()_ed')

    
    def run(self):
        self.logger.info('SwitchControllerThread starting')
        self.plug = self.trigger.setupPlug(self)    # Ask RIAPS port to make a plug (zmq socket) for this end
        self.poller = zmq.Poller()                  # Set up poller to wait for messages from either side
        self.poller.register(self.cons, zmq.POLLIN) # console socket (connects to console client)
        self.poller.register(self.plug, zmq.POLLIN) # plug socket (connects to trigger port of parent device comp)
        while 1:
            self.active.wait(None)                  # Events to handle activation/termination
            if self.terminated.is_set(): break
            if self.active.is_set(): 
                self.logger.info("polling...")               # If we are active
                socks = dict(self.poller.poll(1000))  # Run the poller: wait input from either side, timeout if none
                if len(socks) == 0:
                    self.logger.info('SwitchControllerThread timeout')
                else:
                    self.logger.info("received something")
                if self.terminated.is_set(): break
                if self.cons in socks: #and socks[self.cons] == zmq.POLLIN:   # Input from the console
                    message = self.cons.recv_string()
                    self.logger.info("received")
                    self.plug.send_pyobj(message)                           # Send it to the plug
                if self.plug in socks: #and socks[self.plug] == zmq.POLLIN:   # Input from the plug
                    message = self.plug.recv_pyobj()
                    self.logger.info("received command %s" % str(message))
                    topic, value = message.split()
                    self.grid.send_string("%s %s" % (topic, value))
                                               # Send it to the console
        self.logger.info('SwitchControllerThread ended')
               

    def activate(self):
        self.active.set()
        self.logger.info('SwitchControllerThread activated')
                    
    def deactivate(self):
        self.active.clear()
        self.logger.info('SwitchControllerThread deactivated')
    
    def terminate(self):
        self.active.set()
        self.terminated.set()
        self.logger.info('SwitchControllerThread terminating')


class SwitchController(Component):
    def __init__(self, ip, pub_port, sub_port, topic):
        super(SwitchController, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting SwitchController, %s" % (str(self.pid),str(now)))
        self.comm = 1
        self.ip = ip
        self.pub_port = pub_port
        self.sub_port = sub_port
        self.topic = topic
#         self.gridagent = gridlabdagent()
#         self.gridagent.create_sub(sub1, "localhost", "5559")
#         self.gridagent.create_pub(pub1, "localhost", "5560")
#         self.logger.info("agent created")
        
    def handleActivate(self):
        self.SwitchControllerThread = SwitchControllerThread(self.trigger, self.ip,self.pub_port, self.sub_port, self.topic, self.logger) # Inside port, external zmq port
        self.SwitchControllerThread.start() # Start thread
        time.sleep(0.1)
        self.logger.info("started thread")
        self.trigger.activate()
        
    def __destroy__(self):
        self.logger.info("__destroy__")
        self.SwitchControllerThread.deactivate()
        self.SwitchControllerThread.terminate()
        self.SwitchControllerThread.join()
        self.logger.info("__destroy__ed")
        
    def on_trigger(self):                      # Internally triggered operation (
        msg = self.trigger.recv_pyobj()         # Receive message from internal thread
        self.logger.info('on_trigger():%s' % msg)
        #topic, value = msg.split()
        self.sendrdg.send_pyobj(msg)               # Send it to the echo server


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
            
#     def on_recvsensorreq(self):
#             msg = self.recvsensorreq.recv_pyobj()
#             self.logger.info("on_recvsensorreq(): PID %s" % (str(self.pid)))
#             self.logger.info("%d" %self.gridagent.time_granted)
#             if self.gridagent.time_granted < self.gridagent.time_stop:
#                 #self.time_granted = fncs.time_request(self.time_granted+1800)
#                 self.gridagent.get_simulation_time(self.gridagent.time_stop)
#     #             self.time_granted = fncs.time_request(self.time_stop)
#                 self.logger.info("time granted: %f" % self.gridagent.time_granted)
#                 self.gridagent.get_values()
#                 
#                 for topic, value in self.gridagent.valuelist.items():
#                     if topic == msg:
#                         print('%s received' % topic)
# #                         self.comm = 1 - self.comm
#                         self.logger.info("sending reply")
#                         self.recvsensorreq.send_pyobj(value)
#                     
#     #                     self.logger.info("sending command to gridlab-d")
#     #                     self.gridagent.publish_gridlabd("sw_status", str(self.comm))
#                         break
#                         
#             else:
#                 self.logger.info("simulation ended")

                    
    def on_recvcmd(self):
        msg = self.recvcmd.recv_pyobj()
#         self.gridagent.time_granted = self.gridagent.get_simulation_time(self.gridagent.time_granted + 10)
        self.logger.info("sending command to gridlab-d")
        self.trigger.send_pyobj("%s %s" % (msg["topic"], msg["value"]))
        self.recvcmd.send_pyobj("ok")

    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping SwitchController, %s" % (str(self.pid),now))
        self.SwitchControllerThread.deactivate()
        self.SwitchControllerThread.terminate()
        self.SwitchControllerThread.join()
        self.logger.info("__destroy__ed")
#         self.gridagent.terminate()
