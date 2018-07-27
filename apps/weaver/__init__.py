appType='R-t M:tG'


import server
Server=server.Server

try:
    import client2
    Client=client2.Client
except ImportError:
    pass