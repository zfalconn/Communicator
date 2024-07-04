import util
import model
import asyncio
from asyncua import Client, Node, ua
import json
import numpy as np

#Dimension work space in um: 250 000 um x 250 000 um

async def main() -> None:
    
    output_path = "output.json"
    data = [100,200]
    util.dump_output("CC", data, output_path) #Generate test output "2" to json file

    #connector = model.Connector("opc.tcp://localhost:4840",node_ids=['ns=2;i=2','ns=2;i=4']) #Create Connector
    connector = model.Connector("opc.tcp://192.168.137.2:4840",node_ids=['ns=3;s="C-OFF_X_int"','ns=3;s="C-OFF_Y_int"'])

    dv = ua.DataValue(ua.Variant(100, ua.VariantType.Double)) #convert python type to opcua type
    dv.ServerTimestamp = None
    dv.SourceTimestamp = None

    if await connector.connect(): #Check if connected to the server
        cvmodel = model.Model("CC",connector) #Attach Connector to Model
        message_to_send = util.retrieve_output(output_path) #Grab output from json file

        await cvmodel.send(dv,0)
       

        await cvmodel.send(dv,1)
    await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
