from opcua import Client, Node, ua
from queue import Queue

class Connector: 

    """
    Assign OPCUA server to a separate object, which can be dealt with independent of the actual Model 

    """


    def __init__(self, opcua_url : str, node_id = None):
        
        """
        Create Connector object with specified url and node_id.
        """
        
        self.url = opcua_url
        self.client = Client(opcua_url)
        self.node_id = node_id
        self.var = self.register_node()

    def register_node(self) -> Node:
        match self.node_id:
            case list():
                return [self.client.get_node(self.node_id[i]) for i in range(len(self.node_id))]
                # print(self.var)
                # for i in range(len(self.var)):
                #     print(self.var[i])
                # print("case list()")
            case str():
                return self.client.get_node(self.node_id)
                # print("case str()")
                # print(self.var)
            case _:
                
                print("No node(s) assigned.")
                return None

                

    def connect(self) -> bool: 
        
        """
        Connect Client to OPCUA Server specified by 'opcua_url'.
        """
       
        try:
            self.client.connect()
            print(f"Client connected to {self.url}.")
            return True
        except:
            print(f"An error has occurred. Client did not connect to {self.url}")
            return False
        
        
    

    def disconnect(self) -> None:
        try:    
            self.client.disconnect()
            print(f"Client disconnected from {self.url}.")
        except:
            print(f"An error has occurred. Client did not disconnect from {self.url}")
class Model:
    
    def __init__(self, model_id : str, connector : Connector = None):

        self.model_id = model_id
        self.connector = connector
    
    def send(self, message) -> None:
        """
        Change value of node_ID with the value of 'message'
        """
        if self.connector is None:
            print("Please connect to client to server.")
            return

        
        #self.connector.var.set_attribute(ua.AttributeIds.Value, ua.DataValue(message))
        print(message)

class Classification(Model):
    def __init__(self, model_id: str, node_id: str, connector: Connector, algorithm_output_classification : int ):
        super().__init__(model_id, node_id, connector)
        self.output = algorithm_output_classification
    
class Count(Model):
    def __init__(self, model_id: str, node_id: str, connector: Connector, algorithm_output_count = None ):
        super().__init__(model_id, node_id, connector)
        self.output = algorithm_output_count

    


def test_connector():
    try:  
         
        #Send to multiple node ID 
        cntor = Connector("opc.tcp://localhost:4840",node_id=['ns=2;i=3','ns=2;i=4'])
        
        #Send to single node ID
        #cntor = Connector(opcua_url="opc.tcp://localhost:4840",node_id='ns=2;i=3')
        if cntor.connect(): 
            mod = Model("CC", cntor)
            msg = "new message"
            mod.send(msg)

            #Send to multiple node ID 
            cntor.var[0].set_attribute(ua.AttributeIds.Value, ua.DataValue(msg)) 
            cntor.var[1].set_attribute(ua.AttributeIds.Value, ua.DataValue(msg))

            #Send to single node ID
            # cntor.var.set_attribute(ua.AttributeIds.Value, ua.DataValue(msg))
            


            
            
    finally:
        cntor.disconnect()

    # var = connector.client.get_node(connector.node_id)
    # var.set_attribute(ua.AttributeIds.Value, ua.DataValue('blahblah'))





if __name__ == "__main__":
    #Test output
    ##########################################
    # mod1 = Model("CC",output=1) #only output
    # mod2 = Model("CC",count=40) #only count
    # mod3 = Model("CC",output=2, count=200) #both output and count
    # mod4 = Model(1,output=1) #No model name
    # mod5 = Model("Tip") #None, None
    # mod6 = Model("CC",output= [0,1], count=[200,40]) #arrays of input

    # print(mod1.create_string())
    # print(mod2.create_string())
    # print(mod3.create_string())
    # print(mod4.create_string())
    # print(mod5.is_valid())
    # print(mod6.create_string())
    ##########################################
    try:
        test_connector()
    except KeyboardInterrupt:
        pass
#nodes = ['node1', 'node2', 'node3']
#outputs = [a,b,c]
