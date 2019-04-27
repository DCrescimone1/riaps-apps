import zmq
import libs.config as cfg

grid = zmq.Context().socket(zmq.REQ)
grid.connect('tcp://%s:5555' %cfg.__GRID__)


msg = {"request": "postTrade",
       "interval":1,
       "power" : 100
       }
grid.send_pyobj(msg)
response = grid.recv_pyobj()

msg = {"request":"charge",
       "ID" : 101,
       "interval": 2}

grid.send_pyobj(msg)
charge = grid.recv_pyobj()


msg = {"step" :4}
grid.send_pyobj(msg)
response = grid.recv_pyobj()
