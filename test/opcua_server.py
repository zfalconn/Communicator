import sys
sys.path.insert(0, "..")
import time


from opcua import ua, Server


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
        myobj = objects.add_object(idx, "MyObject")
        myobj2 = objects.add_object(idx, "MyObject2")
        myvar = myobj.add_variable(idx, "MyVariable", "abcxyz")
        myvar.set_writable()    # Set MyVariable to be writable by clients
        myvar2 = myobj2.add_variable(idx, "MyVariable2", "12345")
        myvar2.set_writable()    # Set MyVariable to be writable by clients

        # starting!
        server.start()
    except KeyboardInterrupt:
        pass
    