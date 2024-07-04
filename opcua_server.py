import sys
sys.path.insert(0, "..")
import time


from opcua import ua, Server, Node

class Object:
    def __init__(self, idx, server : Server, node_name, var_name, value):
        self.objects : Node = server.get_objects_node()
        self.obj : Node     = self.objects.add_object(idx, node_name)
        self.var : Node     = self.obj.add_variable(idx, var_name, value)
        self.var.set_writable()
    
    def get_node(self):
        return self.var.nodeid
    
if __name__ == "__main__":

    # setup our server
    try:
        server = Server()
        server.set_endpoint("opc.tcp://localhost:4840")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        idx = server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        objects = server.get_objects_node()

        # populating our address space
        myobj1=Object(idx, server, "MyObject1", "MyVariable1",0)
        myobj2=Object(idx, server, "MyObject2", "MyVariable2","56789")
        myobj3=Object(idx, server, "MyObject3", "MyVariable3",200)
        myobj4=Object(idx, server, "MyObject4", "MyVariable4","hello world")   
        # starting!
        #print(myobj1.get_node())
        server.start()
    except KeyboardInterrupt:
        pass
    
