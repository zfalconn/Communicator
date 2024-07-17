from typing import Any, Awaitable
from asyncua import Client, Node, ua
import asyncio
import time
import json

"""
To run async function, use await in front of this function.
"""

class Connector: 

    """
    Assign OPCUA server to a separate object, which can be dealt with independent of the actual Model. 

    """

    def __init__(self, opcua_url : str, node_ids : list):
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

    def login(self, username : str, password : str) -> None:
        self.client.set_user(username)
        self.client.set_password(password)

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
        try:
            dv = ua.DataValue(ua.Variant(message, vartype))
            return dv
        except Exception as e:
            print(f'An error occurred: {e}')
    
    @staticmethod
    def type_is_valid(arg1 : ua.VariantType, arg2 : ua.VariantType) -> bool:
        if arg1 == arg2:
            return True
        return False

    async def send(self, message, index : int = 0, vartype : ua.VariantType = None) -> None:
        """
        Write value of node_ID with the value of 'message'.
        1. Get Node variable data type
        2. Check if vartype is the same as Node 
        3. If yes, convert message to OPC UA VariantType and attempt to send
        4. If no, raise error

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
            try:
                await self.select_node(index).write_value(new_message)
            except Exception as e:
                print(f'An error occurred: {e}')
        else:
            print("Invalid data type")
        
    async def send_multiple(self, messages : list, indices : list, vartype : ua.VariantType = None) -> None:
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
        
        await run_parallel(*[self.send(messages[i], indices[i], vartype) for i in indices])

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

async def test1():
    """
    Test OPC UA functionalities with simulated Server.
    """
    start_time = time.time() #start time to check function call duration
    ############################################################################
    try:  
        nodes_1 = ['ns=2;i=2','ns=2;i=6'] #defining target Nodes
        localip = "opc.tcp://localhost:4840"

        cntor1 = Connector(localip,node_ids=nodes_1)
        await cntor1.connect()

        #nodes_2 = ['ns=2;i=4','ns=2;i=8'] #defining other target Nodes for different Connector
        #cntor2 = Connector("opc.tcp://localhost:4840",node_ids=['ns=2;i=6','ns=2;i=8'])
        #await cntor2.connect()

        mod1 = Model("CC", cntor1)
        await mod1.send("6000",0,vartype=ua.VariantType.Int64)
        #print(mod1.connector.var[0])
        #print(type(await mod1.read_value(0)))
        #print(await mod1.get_node_data_type(0))

    finally:
        await cntor1.disconnect()
    ############################################################################
    end_time= time.time()
    elapsed_time = end_time - start_time #calculate time takes to call function
    print(f"Elapsed time: {elapsed_time} seconds")

async def test_robot():
    """
    Test the OPC UA communication between Python script and PLC, controlling Robot movement.
    """
    start_time = time.time() #start time to check function call duration
    ############################################################################
    try:  
        #Initialization
        nodes_ROBOT = ['ns=3;s="C-OFF_X_int"','ns=3;s="C-OFF_Y_int"','ns=3;s="CV_coordinates_ready"']
        PLC_ip = "opc.tcp://192.168.137.2:4840"
        cntor1 = Connector(PLC_ip,node_ids=nodes_ROBOT)
        await cntor1.connect()
        mod1 = Model("ROBOT_OPCUA_TEST", cntor1)

        #Send X and Y coordinates to PLC
        await mod1.send_multiple([2000000,0],[0,1], vartype=ua.VariantType.Int32)
        
        await asyncio.sleep(1) #wait 1s
        #Send "go ahead" to PLC
        await mod1.send(True, 2, vartype= ua.VariantType.Boolean)

        await asyncio.sleep(2.5) #wait 2.5s
        #Reset "go ahead" signal
        await mod1.send(False, 2, vartype= ua.VariantType.Boolean)
        #END
    finally:
        await cntor1.disconnect()
    ############################################################################
    end_time = time.time()
    elapsed_time = end_time - start_time #calculate time takes to call function
    print(f"Elapsed time: {elapsed_time} seconds")

try:
    with open('login.json', 'r') as json_file:
        data = json.load(json_file)
    username = data['user']
    password = data['password']
except:
    print("Error: login.json not found")
    

async def test_robot_auth():
    """
    Test the OPC UA communication between Python script and PLC, controlling Robot movement.
    """
    start_time = time.time() #start time to check function call duration
    ############################################################################
    try:  
        #Initialization
        nodes_ROBOT = ['ns=3;s="C-OFF_X_int"','ns=3;s="C-OFF_Y_int"','ns=3;s="CV_coordinates_ready"']
        PLC_ip = "opc.tcp://192.168.137.2:4840"
        cntor1 = Connector(PLC_ip,node_ids=nodes_ROBOT)
        #cntor1.client.application_uri = "urn:freeopcua:client"
        cntor1.login(username,password)
        # cntor1.client.set_user('user')
        # cntor1.client.set_password('ISCfraunhofer021')
        #await cntor1.client.set_security_string("Basic256Sha256,SignAndEncrypt,AAK-OPCUA-Client-cert.pem,AAK-OPCUA-Client-key.pem")
        
        
        
        #await cntor1.connect()
        print(await cntor1.connect())
        mod1 = Model("ROBOT_OPCUA_TEST", cntor1)

        await mod1.send_multiple([2000000,0],[0,1], vartype=ua.VariantType.Int32)
        #END
    finally:
        await cntor1.disconnect()
    ############################################################################
    end_time = time.time()
    elapsed_time = end_time - start_time #calculate time takes to call function
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    try:
        #asyncio.run(test_robot_auth())
        print(username,password)
    except KeyboardInterrupt:
        pass
