from typing import Any, Awaitable
from asyncua import Client, Node, ua
import asyncio
import time

"""
To run async function, use await in front of this function.
"""

class Connector: 

    """
    Assign OPCUA server to a separate object, which can be dealt with independent of the actual Model. 

    """

    def __init__(self, opcua_url : str, node_ids : list): #maybe use strictly list for node_id in order to easily check input validity?
        """
        Create Connector object with specified url and node_id(s).

        Parameters:
            opcua_url (str) : OPCUA server url
            node_ids (list of str) : List of node_ids to be monitored
        """
        
        self.url = opcua_url
        self.client = Client(opcua_url)
        self.var = self.register_node(node_ids)

    async def connect(self) -> bool: 
        
        """
        Connect Client to OPCUA Server specified by 'opcua_url'.
        """
       
        try:
            await self.client.connect()
            print(f"Client connected to {self.url}.")    
            return True
        except Exception as e:
            print(f"An error has occurred: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect Client from OPCUA Server.
        """

        try:    
            await self.client.disconnect()
            print(f"Client disconnected from {self.url}.")
            return True  
        except Exception as e:
            print(f"An error has occurred: {e}")
            return False
    
    def register_node(self, node_ids : list):
        """
        Create Node object(s) from defined node_id(s).

        Parameters:
            node_ids (list) : List of node_ids to be registered

        Return:
            list of Node objects
        """
        try:
            return [self.client.get_node(node_id) for node_id in node_ids]
        except Exception as e:
            print(f'An error occurred: {e}')   
            
    # def select_node(self, index : int = 0) -> Node:
    #     """
    #     Select specific Node using list indexing. Return first Node if only one Node is defined.

    #     Parameters:
    #         index (int) : index of node_ids list
        
    #     Return:
    #         self.var (Node) : Node object
    #     """
    #     return self.var[index]


    def pubsub(self):
        raise NotImplementedError

class Model:
    """
    Model object use Connector object to access Nodes.
    """
    
    def __init__(self, model_id : str, connector : Connector):
        """
        Create Model object.

        Parameters:
            model_id (str) : model name
            connector (Connector) : Connector object
        """
        
        self.model_id = model_id
        self.connector = connector

    def select_node(self, index : int = 0) -> Node:
        """
        Choose specific Node via index.

        Parameters:
            index (int) : index of node_ids list
        Return:
            Node object (Node) : Node Object with respective NodeId 
        """
        return self.connector.var[index]
    
    async def get_node_data_type(self, index : int = 0) -> ua.VariantType:
        """
        Get Node variable data type.

        Parameters:
            index (int) : index of node_ids list
        Return:
            Varient Type (ua.VariantType) : Node variable data type
        """
        return await self.select_node(index).read_data_type_as_variant_type()
    
    @staticmethod
    def create_message_as_variant_type(message, vartype) -> ua.DataValue: 
        """
        Convert message in Python data type to OPC UA varient data type.
        
        Parameters:
            message : input message
            vartype : OPC UA varient data type
        Return:
            DataValue Object (ua.DataValue) : converted message
        """
        dv = ua.DataValue(ua.Variant(message, vartype))
        return dv
    @staticmethod
    def type_is_valid(arg1 : ua.VariantType, arg2 : ua.VariantType) -> bool:
        if arg1 == arg2:
            return True
        return False

    async def send(self, message, index : int = 0, vartype : ua.VariantType = None) -> None:
        """
        Write value of node_ID with the value of 'message'.

        Parameters:
            message : value to send to Node
            index (int) : index of node_ids list
            vartype (ua.VariantType) : OPC UA Variant Type
        Return:
            None
        """
        if vartype is None:
            vartype = await self.get_node_data_type(index)
        
        if Model.type_is_valid(vartype,await self.get_node_data_type(index)):
            new_message = Model.create_message_as_variant_type(message, vartype)
            print(new_message)
            await self.select_node(index).write_value(new_message)
        else:
            print("Invalid data type")
        #new_message = ua.DataValue(message) #Test this also with PLC
        
        #ADD CHECKER IN CASE VARTYPE RETURNS NONE
        
        #await self.select_node(index).write_value(message)
        
        

    async def send_multiple(self, messages : list, indices : list) -> None:
        """
        Send multiple message at once. 

        Parameters:
            messages : list of message
            indices : list of indices of defined node_ids in chosen order (ex. [3,2,1,0], [1,3,2,0], etc.)
        Return:
            None
        """
        if len(messages) != len(indices):
            raise ValueError("Length of messages and indices must be same")
        
        await run_parallel(*[self.send(messages[i], indices[i]) for i in indices])

    async def read_value(self, index : int = 0):
        """
        Return value of at specific node_id in the list.
        """
        return await self.select_node(index).read_value()


async def run_sequential(*functions: Awaitable[Any]) -> None: #Helper function to run async sequentially
    for function in functions:
        await function


async def run_parallel(*functions: Awaitable[Any]) -> None: #Helper function to run async parallely
    await asyncio.gather(*functions)

#Test function
async def test1():
    
    start_time = time.time() #start time to check function call duration

    try:  
        nodes_1 = ['ns=2;i=2','ns=2;i=8'] #defining target Nodes
        nodes_2 = ['ns=2;i=4','ns=2;i=6'] #defining other target Nodes for different Connector
        cntor1 = Connector("opc.tcp://localhost:4840",node_ids=nodes_1)
        #cntor2 = Connector("opc.tcp://localhost:4840",node_ids=['ns=2;i=6','ns=2;i=8'])
        await cntor1.connect()
        #await cntor2.connect()

        mod1 = Model("CC", cntor1)
        #await mod1.send_multiple([100,200],[0,1])
        await mod1.send(6000,0,vartype=ua.VariantType.Int64)
        #print(mod1.connector.var[0])
        #print(type(await mod1.read_value(0)))
        print(await mod1.get_node_data_type(0))
        #mod2 = Model("TIP", cntor2)
        # await mod1.send(41412241421, 0),
        # await mod2.send(142142141414,0),
        # await mod1.send(75674, 1),
        # await mod2.send("something",1)
        
    finally:
        await cntor1.disconnect()
        #await cntor2.disconnect()
    
    end_time= time.time()
    elapsed_time = end_time - start_time #calculate time takes to call function
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    try:
        asyncio.run(test1())
    except KeyboardInterrupt:
        pass
