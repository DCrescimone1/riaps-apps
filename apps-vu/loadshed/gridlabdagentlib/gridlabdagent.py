import logging
import time
import os
import gridlabdagentlib.fncs as fncs
import random
import subprocess
from spdlog import ConsoleLogger, LogLevel


class gridlabdagent(object):
    
    def __init__(self):
        self.time_stop = 21600
        self.time_granted = 0
        os.environ['FNCS_CONFIG_FILE'] = "gridlabdagentlib/loadshedriaps.yaml"
        out = subprocess.check_output("echo $FNCS_CONFIG_FILE", shell=True)
        self.logger = ConsoleLogger('serial_logger', True, True, True)
        self.logger.set_level(LogLevel.INFO)
        self.logger.info(out.decode("utf-8"))
        fncs.initialize()
        
    def get_simulation_time(self, time_desired):
        self.time_granted = fncs.time_request(time_desired)
    
    def get_values(self):
        events = fncs.get_events()
        self.valuelist = {}
        for topic in events:
            self.valuelist[topic] = fncs.get_value(topic)
        
    def publish_gridlabd(self, topic, value):
        fncs.publish(topic, value)
        
    def terminate(self):
        fncs.finalize()
