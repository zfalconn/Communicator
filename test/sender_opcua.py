import sys
from opcua import Client
from opcua import ua
from model import Model





if __name__ == "__main__":

    #initialization
    #Connector("opc.tcp://localhost:4840",'ns=2;i=2')
    client = Client("opc.tcp://localhost:4840")
    node = 'ns=2;i=2'
    model = Model("CC")
    message = model.create_string()

    print(message)
    
    try:
        #All nodes can be visually seen via opcua client such as UAExpert
        #Connect client to URL
        client.connect()
        var = client.get_node(node)

        print("Before:",var.get_value())

        if model.is_valid() is True: #Check for validity of message before setting
            var.set_attribute(ua.AttributeIds.Value, ua.DataValue(message))

        print("After:", var.get_value())
        
    #Model.send()

    finally:
        print("Exiting...") 
        
        client.disconnect()
