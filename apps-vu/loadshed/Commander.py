from riaps.run.comp import Component
import logging
import os
import time
from riaps.run.exc import PortError

class Commander(Component):
    def __init__(self):
        super(Commander, self).__init__()
        self.pid = os.getpid()
        self.logger.info("Starting commander: process_id: [%s]" % self.pid)
        self.comm = 1
        self.pending = 0
        
    def on_clock(self):
        
        now = self.clock.recv_pyobj()
#         time.sleep(10)
        if self.pending == 0:
            self.logger.info("on_clock(): PID %s, %s" % (str(self.pid),str(now)))
            try:
                self.sensorvalrecd.send_pyobj("distribution_load")
                self.pending = 1
                self.logger.info("sent")
            except PortError as e:
                self.logger.error("Error sending: %d"  % e.errno )
                self.pending = 0
        
    def on_sensorvalrecd(self):
        msg = self.sensorvalrecd.recv_pyobj()
        self.logger.info("Load value: %s" % msg)
        self.comm = 1 - self.comm
        self.logger.info("sending switch command")
        msg = {"topic": "sw_status", "value": str(self.comm)}
        self.sendcmd.send_pyobj(msg)
        
    def on_sendcmd(self):
        msg = self.sendcmd.recv_pyobj()
        self.logger.info("Command executed")
        self.pending = 0
        
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping commander, %s" % (str(self.pid),now))