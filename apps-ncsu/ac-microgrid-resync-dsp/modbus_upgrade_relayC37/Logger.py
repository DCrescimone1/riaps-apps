'''
Created on Mar 17, 2017

@author: riaps
'''
from riaps.run.comp import Component
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import json
import logging
from datetime import datetime
import os

BATCH_SIZE = 50

class Logger(Component):
    def __init__(self, db_host, db_port, db_name, db_user, db_password):
        super().__init__()
        self.pid = os.getpid()
        self.logger.info("%s - starting modbus logger",str(self.pid))
        self.point_values = []
        self.client = InfluxDBClient(host=db_host, port=db_port,
            database=db_name, username=db_user, password=db_password)

    def on_rx_modbusData(self):
        data = self.rx_modbusData.recv_pyobj()
        # self.logger.info("on_rx_modbusData()[%s]: %s", str(self.pid), repr(msg))
        # MM TODO:  update based on what is being logged and how we want to use it
           
        timestamp = int(1e9 * data['timestamp'])
        # alternative:
        # timestamp = datetime.utcfromtimestamp(data['timestamp'])  
        self.point_values.append({
                "time": timestamp,
                "measurement": "pmu",
                "fields":  {
                    "grid_v_mag": data["grid_v_mag"],
                    "grid_ph_angle": data["grid_ph_angle"],
                    "ugrid_v_mag": data["ugrid_v_mag"],
                    "ugrid_ph_angle": data["ugrid_ph_angle"],
                    "mag_diff": data["mag_diff"],
                    "angle_diff": data["angle_diff"],
                    "ugrid_frequency": data["ugrid_frequency"],
                    "grid_frequency": 60,
                },
                "tags": {
                    "Actor" : "ModbusIOActor"
                },
            })
        
        
        if len(self.point_values) >= BATCH_SIZE:
            self.client.write_points(self.point_values)
            self.point_values = []

