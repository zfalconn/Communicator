import util
import model
import asyncio
from asyncua import Client, Node
import json


async def main() -> None:
    
    output_path = "output.json"
    data = [100,200]
    util.dump_output("CC", data, output_path) #Generate test output "2" to json file

    connector = model.Connector("opc.tcp://localhost:4840",node_id=['ns=2;i=2','ns=2;i=4']) #Create Connector
    

    if await connector.connect(): #Check if connected to the server
        cvmodel = model.Model("CC",connector) #Attach Connector to Model
        message_to_send = util.retrieve_output(output_path) #Grab output from json file


        print(f'Data from JSON file: {message_to_send}')
        print(f'NodeID: {connector.node_id}\n')

        print(f'Value before of {connector.node_id[0]}: {await connector.read_value(0)}') #Print output at NodeID to console
        print(f'Value before of {connector.node_id[1]}: {await connector.read_value(1)}\n')

        await cvmodel.send(message_to_send[0],0)
       
        print(f'Value after of {connector.node_id[0]}: {await connector.read_value(0)}') #Print output at NodeID to console
        print(f'Value after of {connector.node_id[1]}: {await connector.read_value(1)}\n')
        print('Some time passed...')

        await cvmodel.send(message_to_send[1],1)
        print(f'Value after of {connector.node_id[0]}: {await connector.read_value(0)}') #Print output at NodeID to console
        print(f'Value after of {connector.node_id[1]}: {await connector.read_value(1)}\n')
    await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
