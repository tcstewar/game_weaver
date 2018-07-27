import server
import client

s=server.runServer()
c=client.runClient()
s.startApp(c,'weaver')





