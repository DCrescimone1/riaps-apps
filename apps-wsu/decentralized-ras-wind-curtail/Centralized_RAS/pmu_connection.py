from pypmu.pdc import Pdc

import socket
import threading
import struct
import time
import math

RTDS_IP = "192.168.1.102"
RTDS_PORT = 4575

PMU_IP = "192.168.1.111"
PMU_PORTS = [4712, 4722, 4732, 4742]

HARDWARE_PMU_IP = "192.168.1.51"
HARDWARE_PMU_PORT = 5011
HARDWARE_PMU_ID = 11

PMUS = [[PMU_IP, 4712, 1], [PMU_IP, 4722, 2], [PMU_IP, 4732, 3], [PMU_IP, 4742, 4], [PMU_IP, 4752, 5], [PMU_IP, 4762, 6], [PMU_IP, 4772, 7], [PMU_IP, 4782, 8], ['192.168.1.51', 5011, 11]]


V_LEN = 15
I_LEN = 26

V_BASE = ([69000/math.sqrt(3)] * 6) + ([13800/math.sqrt(3)] * 2) + ([18000/math.sqrt(3)]) + ([13800/math.sqrt(3)] * 6)
I_BASE = [1, 1, 1, 2, 2, 2, 3, 5, 5, 4, 4, 6, 6, 12, 13, 13, 11, 11, 14, 10, 10, 9, 9, 7, 8, 3]

PMU_PHASOR_MAP = {1: ([1, 10, 11], [1, 2, 3]), 2: ([2, 12, 13], [4, 5, 6]), 3: ([3, 14], [7, 8, 9]), 4: ([4], [10, 11, 12]), 5: ([5], [13, 14, 15]), 6: ([6], [16, 17, 18]), 7: ([7], [19, 20, 22]), 8: ([8], [23, 24, 25]), 9: ([9], [21])}
        

class PMUConnection():

        def __init__(self):
                self.s = None
                self.pdc = None        
                self.dframes = None
                self.lock = threading.Lock()
                self.connect_pmu()

        def connect_pmu(self):
                #Connect to all the PMUs
                if self.pdc is None:
                        self.pdc = list()
                        for PMU in PMUS:
                                print("CONNECTING " + str(PMU))
                                pmu = Pdc(pmu_ip = PMU[0], pmu_port = PMU[1], pdc_id = PMU[2])
                                pmu.run()
                                self.pdc.append(pmu)

                for pmu in self.pdc:
                        if not pmu.is_connected():
                                return False
                        print("STARTING " + str(pmu))
                        pmu.start()

                dframe_thread = threading.Thread(target = self.recv_dframes)
                dframe_thread.start()

                return True

        def recv_dframes(self):
                if self.pdc is None:
                        return False
                while(True):
                        dataframelist = list()
                        for pmu in self.pdc:
                                dataframelist.append(pmu.get())
                        self.lock.acquire()
                        self.dframes = dataframelist[:]
                        self.lock.release()

        def parse_data_frame(self, data):
                v_mag = struct.unpack('>f', data[16:20])
                v_ang = struct.unpack('>f', data[20:24])
                i_mag = struct.unpack('>f', data[24:28])
                i_ang = struct.unpack('>f', data[28:32])

                return v_mag[0], v_ang[0], i_mag[0], i_ang[0]


        def get_dframes(self):
                if self.dframes is None:
                    return None
                self.lock.acquire()
                dframes = self.dframes[:]
                self.lock.release()
                return dframes

        def close(self):
                for pmu in self.pdc:
                        pmu.stop()
                        pmu.quit()

        def get_phasor(self, dataframe, phasor_index):
                start_index = 16 + (phasor_index * 8)
                phasor_mag = struct.unpack('>f', dataframe[start_index:start_index + 4])[0]
                phasor_ang = struct.unpack('>f', dataframe[start_index + 4: start_index + 8])[0]
                phasor = (phasor_mag * math.cos(phasor_ang)) + (phasor_mag * math.sin(phasor_ang) * 1j)
                return [phasor_mag, phasor_ang]
                

        def get_V_I(self):
                dataframes = self.get_dframes()
                if dataframes is None:
                    return None
                #Data frames of all the PMUs as input
                V = [None for i in range(V_LEN)]
                I = [None for i in range(I_LEN)]
                for j in range(len(dataframes)):
                        #We have a funtion get_phasor(frame, phasor_num) that can get a phasor from the frame
                        pmu_id = j + 1
                        dataframe = dataframes[j]
                        voltage_phasors, current_phasors = PMU_PHASOR_MAP[pmu_id]
                        for i in range(len(voltage_phasors)):
                                V_index = voltage_phasors[i]
                                V[V_index] = self.get_phasor(dataframe, i)
                                
                
                slack_bus_angle = V[1][1]
                
                for i in range(1, len(V)):
                    V[i][1] -= slack_bus_angle
                    V[i] = V[i][0] * math.cos(V[i][1]) + (V[i][0] * math.sin(V[i][1]) * 1j)
                    V[i] /= V_BASE[i]
                    
                for j in range(len(dataframes)):
                        pmu_id = j + 1
                        dataframe = dataframes[j]
                        voltage_phasors, current_phasors = PMU_PHASOR_MAP[pmu_id]
                        for i in range(len(current_phasors)):
                                I_index = current_phasors[i]
                                I[I_index] = self.get_phasor(dataframe, i + len(voltage_phasors))

                for i in range(1, len(I)):
                    I[i][1] -= slack_bus_angle
                    mag = I[i][0]
                    ang = I[i][1]
                    I[i] = mag * math.cos(ang) + mag * math.sin(ang) * 1j
                    I[i] /= (10 ** 8)/V[I_BASE[i]]

                return V, I

