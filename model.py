from typing import Any, Awaitable
from asyncua import Client, Node
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
            opcua_url(str) : OPCUA server url
            node_ids(list of str) : List of node_ids to be monitored
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
        """
        try:
            return [self.client.get_node(node_id) for node_id in node_ids]
        except Exception as e:
            print(f'An error occurred: {e}')   
            
    def select_node(self, index : int = 0) -> Node:
        """
        Select specific Node using list indexing. Return same Node if only one Node is defined.

        Parameters:
            index(int) : index of list of node_ids list
        
        Return:
            self.var(Node) : Node object
        """
        return self.var[index]

    async def read_value(self, index : int = 0):
        """
        Return value of at node_id.
        """
        return await self.select_node(index).read_value()

    def pubsub(self):
        raise NotImplementedError

class Model:
    """
    Model object use Connector object to access Nodes. Different Model can have different Connector.
    """
    
    def __init__(self, model_id : str, connector : Connector):
        """
        Create Model object.

        Parameters:
            model_id(str) : model name
            connector(Connector) : Connector object
        """
        
        self.model_id = model_id
        self.connector = connector
    
    def select_node(self, index : int = 0) -> Node:
        """
        Wrap select_node function of Connector class.
        """
        return self.connector.select_node(index)

    async def send(self, message, index : int = 0) -> None:
        """
        Change value of node_ID with the value of 'message'.
        Multiple messages can be sent to multiple nodes.
        """
        await self.select_node(index).write_value(message)

    async def send_multiple(self, messages : list, indices : list) -> None:
        """
        Send coordinate (x,y) to two nodes
        """
        if len(messages) != len(indices):
            raise ValueError("Length of messages and indices must be same")
        
        await run_parallel(*[self.send(messages[i], indices[i]) for i in indices])

#Helper function to run async sequentially
async def run_sequential(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function

#Helper function to run async parallely
async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

#Test function
async def test_connector():
    start_time = time.time()

    try:  
        nodes_1 = ['ns=2;i=2','ns=2;i=8']
        nodes_2 = ['ns=2;i=4','ns=2;i=6']
        cntor1 = Connector("opc.tcp://localhost:4840",node_ids=nodes_1)
        #cntor2 = Connector("opc.tcp://localhost:4840",node_ids=['ns=2;i=6','ns=2;i=8'])
        await cntor1.connect()
        #await cntor2.connect()

        mod1 = Model("CC", cntor1)
        await mod1.send_multiple([100,200],[0,1])
        
        #mod2 = Model("TIP", cntor2)
        # await mod1.send(41412241421, 0),
        # await mod2.send(142142141414,0),
        # await mod1.send(75674, 1),
        # await mod2.send("something",1)
        
    finally:
        await cntor1.disconnect()
        #await cntor2.disconnect()
    
    end_time= time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    try:
        asyncio.run(test_connector())
    except KeyboardInterrupt:
        pass
