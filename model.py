from opcua import Client, ua
from queue import Queue

class Connector: 

    """
    Assign OPCUA server to a separate object, which can be dealt with independent of the actual Model 

    """


    def __init__(self, opcua_url, node_id):
        
        """
        Create Connector object with specified url and node_id.
        """
        
        self.url = opcua_url
        self.client = Client(opcua_url)
        self.node_id = node_id
        self.var = self.client.get_node(node_id)

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
        self.client.disconnect()
        print(f"Client disconnected from {self.url}.")


class Model:
    
    def __init__(self, model_id : str, output = None, count = None, coord = None, connector : Connector = None):

        """
        Create Model with parameters:

        model_id: str
            Name of model
        
        output: int or list
            Number of output classes

        count: int or list
            Count of output class (Ex: cell counts, etc.)

        connector: Connector
            Connect Model to OPCUA server / specific node_ID
        """

        self.model_id = model_id
        self.output = output
        self.count = count
        self.connector = connector
        
    def create_string(self) -> str:
        """
        Make string from 'model_id', 'output' and 'count' in format [model_id]$[output1]:[count1]/[output2]:[count2]/...
        """

        try:
            match (self.output, self.count):
                case (None, None):
                    print("No value defined")
                    return None

                case (None, int()):
                    temp_str = f"{self.model_id}$:{str(self.count)}"

                case (int(), None):
                    temp_str = f"{self.model_id}${str(self.output)}"

                case (list(),list()):
                    temp_str = self.model_id + "$"

                    for i in range(len(self.output)):
                        temp_str += f"{str(self.output[i])}:{str(self.count[i])}"
                        if i != len(self.output)-1:
                            temp_str += "/" 
                
                case _:
                    temp_str = f'{self.model_id}${str(self.output)}:{str(self.count)}'

                #To be extended

            return temp_str
               
        except Exception as e:
            print(f'An error occured when attempting to create string: {e}')
            return None

    
    def is_valid(self) -> bool:
        """
        Check if create_string() returns a valid string
        """
        if self.create_string() is not None:
            return True
        return False
    

    def set_value(self, message) -> None:
        """
        Change value of node_ID with the value of 'message'
        """


        if self.connector is None:
            print("Please connect to client to server.")
            return

        
        self.connector.var.set_attribute(ua.AttributeIds.Value, ua.DataValue(message))



def test_connector():
    cntor = Connector("opc.tcp://localhost:4840",'ns=2;i=2')
    cntor.connect()

    #cntor.register_node('ns=2;i=2')

    mod = Model("CC",output= 1, count=40)
    msg = mod.create_string()
    mod.set_value(msg)

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

    test_connector()


