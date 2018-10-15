from riaps.run.comp import Component
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import json
import logging
from datetime import datetime
import os

BATCH_SIZE =  300

class Logger(Component):
    def __init__(self, db_host, db_port, db_name, db_user, db_password):
        super().__init__()
        self.pid = os.getpid()
        self.logger.info("%s - starting",str(self.pid))
        self.point_values = []
        self.avaiDic = {'111':0.0,'112':0.0}
        self.client = InfluxDBClient(host=db_host, port=db_port,
            database=db_name, username=db_user, password=db_password)

    def on_rx_phasorData(self):
        raw, data = self.rx_phasorData.recv_pyobj()
        # self.logger.info("on_rx_c37data()[%s]: %s", str(self.pid), repr(data))
        timestamp = int(1e9 * data['timestamp'])
        # alternative:
        # timestamp = datetime.utcfromtimestamp(data['timestamp'])		
        self.point_values.append({
                "time": timestamp,
                "measurement": "pmu",
                "fields":  {
                    "VAGA": data["VAGA"],
                    "VASA": data["VASA"],
                    "VASM": data["VASM"],
                    "VAGM": data["VAGM"],
                    "VMdiff": data["VAGM"] - data["VASM"],
                    "VAdiff": data["VAGA"] - data["VASA"],
                    "DDD111enable": self.avaiDic['111'],
                    "DDD112enable": self.avaiDic['112'],
                },
                "tags": {
                    "Actor" : "OpalIOActor"
                },
            })
        if len(self.point_values) >= BATCH_SIZE:
            self.client.write_points(self.point_values)
            self.point_values = []

    def on_rx_globalAvaiResyncDecision(self):
        ip,avai = self.rx_globalAvaiResyncDecision.recv_pyobj()
        print (ip)
        self.avaiDic[str(ip)] = float(avai)
