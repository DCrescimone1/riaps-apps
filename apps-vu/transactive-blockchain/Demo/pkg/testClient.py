import zmq
import libs.config as cfg

grid = zmq.Context().socket(zmq.REQ)
grid.connect('tcp://%s:5555' %cfg.__GRID__)

msg = {"request": "postTrade",
       "interval" :1,
       "power" : 10,
       "ID" : str(101)
       }
grid.send_pyobj(msg)
response = grid.recv_pyobj()
print(response)

for i in range(96):

    msg = {"request": "step"}
    grid.send_pyobj(msg)
    response = grid.recv_pyobj()
    print(response)

    msg = {"request":"charge",
           "ID" : str(101),
           "interval": i}
    grid.send_pyobj(msg)
    charge = grid.recv_pyobj().split(" ")[0][1:]
    print(charge)
