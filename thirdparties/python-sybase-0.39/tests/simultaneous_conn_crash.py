import threading, Sybase, Queue, time

Sybase._ctx.debug = 1
Sybase.set_debug(open('sybase_debug.log', 'w'))

NUMBER=20

# we'll signal threads to create a connection via this queue
queue = Queue.Queue()

def connect():
    # wait till an item appears in the queue
    queue.get()
    # time.sleep(1)
    # return Sybase.Connection('ECMPROD', 'ecmquery', 'ecmquery')
    return Sybase.Connection("RCT_125_NEPTUNE", "SSA", "sungard", "TESTUNI")


# start 5 threads
threads = [threading.Thread(target=connect) for i in range(NUMBER)]
for t in threads: t.start()

# time.sleep(1)

# kick them all off and then wait for them
print "Signalling ..."
for i in range(NUMBER): queue.put(i)

print "Waiting ..."
for i, t in enumerate(threads):
    print "Waiting on thread", i
    t.join()
