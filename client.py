import simpleCS
import apps

def runClient(address=None,port=None):
#    print dir(apps)
#    print dir(apps.admin)
    client=apps.admin.Client()
    config=apps.admin.Config()

    if address!=None: config.serverAddress=address
    if port!=None: config.adminPort=port
    
    simpleCS.startClient(config.serverAddress,config.adminPort,client)
    return client


if __name__ == '__main__':
    import sys
    import time
    a=None
    p=None
    if len(sys.argv)>1: a=sys.argv[1]
    if len(sys.argv)>2: p=int(sys.argv[2])
    runClient(a,p)

    while 1:
        time.sleep(100)
