import subprocess

print("lab1 thinkboard")
import paho.mqtt.client as mqttclient
import subprocess as sp
import time
import re
import json


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
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

accuracy = 3

def getCoordinate():
    pshellcomm = ['powershell']
    pshellcomm.append('add-type -assemblyname system.device; ' \
                      '$loc = new-object system.device.location.geocoordinatewatcher;' \
                      '$loc.start(); ' \
                      'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) ' \
                      '{start-sleep -milliseconds 100}; ' \
                      '$acc = %d; ' \
                      'while($loc.position.location.horizontalaccuracy -gt $acc) ' \
                      '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; ' \
                      '$loc.position.location.latitude; ' \
                      '$loc.position.location.longitude; ' \
                      '$loc.position.location.horizontalaccuracy; ' \
                      '$loc.stop()' % (accuracy))

    p = sp.Popen(pshellcomm, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    (out, err) = p.communicate()
    out = re.split('\n', out)
    return out

def check_CPU_temp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*',msg)
        try:
            temp = float(m.group())
        except:
            pass

    return temp, msg

client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

humi = 50
light_intesity = 100
counter = 0




while True:
    location = getCoordinate()
    latitude = float(location[0])
    longitude = float(location[1])
    temp, msg = check_CPU_temp()

    collect_data = {'temperature': temp, 'humidity': humi, 'light':light_intesity,
                    'longitude': longitude , 'latitude': latitude}
    humi += 1

    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(5)