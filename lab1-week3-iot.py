print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import geocoder
import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "QAEx1raB9qFklr5t04WJ"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            client.publish('v1/devices/me/BUTTON_LED', json.dumps(temp_data), 1)
            if isMicrobitConnected:
                # ser.write((str(0) + "#").encode())
                if temp_data['valueLED'] == True:
                    ser.write((str(1) + "#").encode())
                elif temp_data['valueLED'] == False:
                    ser.write((str(0) + "#").encode())
        if jsonobj['method'] == "setFAN":
            temp_data['valueFAN'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            client.publish('v1/devices/me/BUTTON_FAN', json.dumps(temp_data), 1)
            if isMicrobitConnected:
                # ser.write((str(0) + "#").encode())
                if temp_data['valueFAN'] == True:
                    ser.write((str(1) + "#").encode())
                elif temp_data['valueFAN'] == False:
                    ser.write((str(0) + "#").encode())
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")
        
def getLocation():
    g = geocoder.ip('me')
    # print(g)
    return {'latitude': g.latlng[0], 'longitude': g.latlng[1]}
  
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial( port=getPort(), baudrate=115200)
    isMicrobitConnected = True  

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    if splitData [1] == "TEMP":
        collect = {'temperature': int(splitData[2])}
        client.publish ("v1/devices/me/telemetry", json.dumps(collect), 1)
    elif splitData [1] == "LIGHT":
        collect = {'humidity': int(splitData[2])}
        client.publish ("v1/devices/me/telemetry", json.dumps(collect), 1)

mess = "" 
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]
                


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 22
humi = 105
light_intesity = 100
longitude = 106.7
latitude = 10.6
counter = 0
res=getLocation()

print(isMicrobitConnected)
collect_data = {'temperature': temp, 'humidity': humi, 'light':light_intesity, 'longitude' : res['longitude'], 'latitude': res['latitude']}
client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
time.sleep(3)
while True:
    # res=getLocation()
    # temp += 1
    # humi += 1
    # light_intesity += 1
    # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # time.sleep(10)
    if isMicrobitConnected:
        readSerial()
    time.sleep(1)
    
