from typing import Any, Awaitable
from asyncua import Client, Node
import asyncio

"""
To run async function, use await in front of this function.
"""

class Connector: 

    """
    Assign OPCUA server to a separate object, which can be dealt with independent of the actual Model. 

    """

    def __init__(self, opcua_url : str, node_id = None):
        """
        Create Connector object with specified url and node_id(s).

        Parameters:
            opcua_url(str) : OPCUA server url
            node_ids(list or str) : List of node_ids to be monitored
        """
        
        self.url = opcua_url
        self.client = Client(opcua_url)
        self.node_id = node_id
        self.var = self.register_node()

    def register_node(self):
        """
        Create Node object(s) from defined node_id(s). 
        """

        match self.node_id:
            case list():
                return [self.client.get_node(self.node_id[i]) for i in range(len(self.node_id))] #List of Nodes
            case str():
                return self.client.get_node(self.node_id)   #Single Node
            case _:          
                print("No node(s) assigned.")
                return None
   

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
    
    def select_node(self, index : int = 0) -> Node:
        """
        Select specific Node using list indexing. Return same Node if only one Node is defined.

        Parameters:
            index(int) : index of list of node_ids list
        
        Return:
            self.var(Node) : Node object
        """

        match self.var:
            case list():
                #print(f"Selecting node {self.var[index]}.")
                return self.var[index]
            case _:
                #print(f"Selecting node {self.var}.")
                return self.var 

    async def read_value(self, index : int = 0):
        """
        Return value of at node_id.
        """
        print(await self.select_node(index).read_value())
        return await self.select_node(index).read_value()

    def pubsub(self):
        raise NotImplementedError

class Model:
    """
    Model object use Connector object to access Nodes. Different Model can have different Connector.
    """
    
    def __init__(self, model_id : str, connector : Connector = None):
        """
        Create Model object.

        Parameters:
            model_id(str) : model name
            connector(Connector) : Connector object
        """
        
        self.model_id = model_id
        self.connector = connector
        if self.connector is None:
            print("Please connect to Client to Server.")
    
    def select_node(self, index : int = 0) -> Node:
        """
        Wrap select_node function of Connector class.
        """

        return self.connector.select_node(index)

    async def send(self, message, index = None) -> None:
        """
        Change value of node_ID with the value of 'message'.
        Multiple messages can be sent to multiple nodes.
        """
        match message:
            case list():
                if len(message) == len(index):
                    await run_parallel(
                        *[self.connector.select_node(i).write_value(message[i]) for i in index]
                    )
                    # for i in range(len(message)):
                    #     await self.select_node(index[i]).write_value(message[i])
                else:
                    print("Length of message and node list must be the same.")
            case _: 
                await self.select_node(index).write_value(message)
                # await asyncio.sleep(1)

    async def send_coord(self, coord : tuple, index) -> None:
        """
        Send coordinate (x,y) to two nodes
        """

        if len(coord) != 2:
            print("Coordinate must be a tuple of two values.")
            return
        if len(index) != 2:
            print("Node list must have two elements.")
            return
        await self.send(coord, index)
        # for i in range(2):
        #     await self.send(coord[i], index[i])

    def run_inference(self) -> None: 
        #Maybe pass computer vision / machine learning object in here (or in __init__)
        #Image can also be passed here
        #Return result of model
        raise NotImplementedError

#Helper function to run async sequentially
async def run_sequential(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function

#Helper function to run async parallely
async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

#Test function
async def test_connector():
    try:  
         
        #Send to multiple node ID 
        
        cntor = Connector("opc.tcp://localhost:4840",node_id=['ns=2;i=3','ns=2;i=4'])
        #Send to single node ID
        #cntor = Connector(opcua_url="opc.tcp://localhost:4840",node_ids='ns=2;i=3')
        await cntor.connect()
        mod = Model("CC", cntor)

        
        await run_sequential(
                # mod.send_coord((1,2),[0,1]),
                mod.send([0,1], [0,1]),
                run_parallel(cntor.read_value(0), cntor.read_value(1)),
                # mod.send_coord((3,4),[0,1]), 
                # run_parallel(cntor.read_value(0), cntor.read_value(1)),
            )
        
    finally:
        await cntor.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(test_connector())
    except KeyboardInterrupt:
        pass
