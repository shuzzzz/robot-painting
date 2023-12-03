import time

s = time.time()

def calTime(id):
    global s
    print(id,int((time.time()-s)*1000))
    s = time.time()