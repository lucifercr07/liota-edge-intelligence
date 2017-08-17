# Offline data storage
If the client faces network disconnectivity, publish message can be stored as a persistent storage or in a temmporary offline queue in which publish data will be added to an internal queue until the number of queued-up requests reaches the size limit of the queue. If the size of the queue is defined as less that zero it will act as a infinite queue. One can also choose the queue behaviour after it reaches it's specified size. If drop_oldest behaviour is set to be true, oldest publish message is dropped else the newest publish messages are dropped. One should specify the draining frequency in each case, which implies how data which has been stored will be published once the network connectivity is established. 

# Example
Suppose we want to create a persistent storage, while creating instance of DCC, we would pass the ```persistent_storage``` parameter as ```True```. 
By default ```persistent_storage``` parameter is set as ```True```
```
graphite = Graphite(SocketDccComms(ip=config['GraphiteIP'],port=8080),persistent_storage=True)
```
In case of ```persistent_storage``` as ```False``` the queueing mechanism will be used by default: 
```
offlineQ = offlineQueue(size=-1, comms=self.comms, draining_frequency=1)
```
will create a queueing mechanism with infinite size and drop_behaviour need not be set in this case, comms will be a DCCComms object, draining_frequency can be any positive int or float number.
For queue with size 3 and drop_oldest behaviour set to true, 
```
offlineQ = offlineQueue(size=3, drop_oldest=True, comms=self.comms, draining_frequency=1)
```
As the publish message arrives the queue will be like this after 3 publish message arrive:
```
['msg1', 'msg2', 'msg3']
```
As the fourth publish message arrives:
```
['msg2', 'msg3', 'msg4']
```
For the fifth publish message:
```
['msg3', 'msg4', 'msg5']
```
Similarly, if the drop_oldest behaviour is set to False:
```
['msg1', 'msg2', 'msg3']
```
After this any new coming publish message will be dropped.