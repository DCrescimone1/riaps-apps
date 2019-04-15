import string;
import sys;
import fncs;
import zmq
import time
import threading
if sys.platform != 'win32':
	import resource
	
print("before entering")
	
def riaps_setupsocket():
	# Prepare our context and sockets
	context = zmq.Context()
	# Connect to task ventilator
	
	riaps_pub = context.socket(zmq.PUB)
	
	riaps_sub = context.socket(zmq.SUB)
	
	riaps_pub.bind("tcp://*:5569")
	
	print("pub bind complete")
	
	riaps_sub.bind("tcp://*:5786")
	riaps_sub.setsockopt_string(zmq.SUBSCRIBE, "sw_status")
	
	print("sub connect complete")
	
	return riaps_pub, riaps_sub

def riaps_subloop():
	
	global time_granted
	global time_stop
	global riaps_sub
	
	# Initialize poll set
	print("starting riaps subscriber")
	poller = zmq.Poller()
	poller.register(riaps_sub, zmq.POLLIN)
	
	# Process messages from both sockets
	while True:
		print("time granted %f" % time_granted)
		try:
			socks = dict(poller.poll(5000))
		except KeyboardInterrupt:
			break
		
		if len(socks) == 0:
			print("poller timed out")
			
		if riaps_sub in socks:
			
			msg = riaps_sub.recv_string()
			# process task
			topic, value = msg.split()
			print("Command received %s" % value)
			fncs.publish(topic, value)
	

global time_granted
global time_stop
global riaps_sub

time_stop = int(sys.argv[1])
time_granted = 0
print("here")
riaps_pub, riaps_sub = riaps_setupsocket()
thread = threading.Thread(target = riaps_subloop)
thread.start()
# requires yaml specificied in an envar
fncs.initialize()

while time_granted < time_stop:
	time_granted = fncs.time_request(time_granted+60)
	events = fncs.get_events()
	for topic in events:
		value = fncs.get_value(topic)
		print (time_granted, topic, value, flush=True)
		if topic == 'sw_status':
			fncs.publish('sw_status', value)
			
		if topic == 'distribution_load':
			print('distribution_load received')
			riaps_pub.send_string("%s %s" % (topic,value))
	time.sleep(2)

fncs.finalize()
thread.join()

if sys.platform != 'win32':
	usage = resource.getrusage(resource.RUSAGE_SELF)
	RESOURCES = [
	('ru_utime', 'User time'),
	('ru_stime', 'System time'),
	('ru_maxrss', 'Max. Resident Set Size'),
	('ru_ixrss', 'Shared Memory Size'),
	('ru_idrss', 'Unshared Memory Size'),
	('ru_isrss', 'Stack Size'),
	('ru_inblock', 'Block inputs'),
	('ru_oublock', 'Block outputs')]
	print('Resource usage:')
	for name, desc in RESOURCES:
		print('  {:<25} ({:<10}) = {}'.format(desc, name, getattr(usage, name)))
		
