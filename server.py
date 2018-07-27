import simpleCS
import apps

import time

def runServer():
    server=apps.admin.Server(apps.admin.Config())
    simpleCS.startServer(server.config.adminPort,server)
    return server

if __name__ == '__main__':
    runServer()
    while 1:
        time.sleep(100)
