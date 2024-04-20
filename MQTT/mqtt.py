import time
import paho.mqtt.client as paho
from paho import mqtt
import requests
import json

# MQTT Configuration
MQTT_BROKER_HOST = "1d53307376844525a0d5f47716515a9a.s2.eu.hivemq.cloud"  # HiveMQ's public MQTT broker
MQTT_BROKER_PORT = 8883
MQTT_TOPIC = "esp8266/sensor"  # Replace with the specific topic you want to subscribe to
USER = "peerapat"
PASSWD = "Peerapat1/"
# FastAPI Configuration
FASTAPI_ENDPOINT = "http://127.0.0.1:8000/devices/sensor/store"

def get_all_sensors():
    sensors = requests.get("http://127.0.0.1:8000/get_all_sensors")
    data = sensors.json()
    return data

def on_connect(mqtt_client, userdata, flags, rc, properties=None):
    if rc == 0: # success connect
        print("Connected with result code "+str(rc))
        mqtt_client.subscribe(MQTT_TOPIC, qos= 1)
    
    
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
# MQTT Callback when a message is received
def on_message(mqtt_client, userdata, message):
    # payload = message.payload.decode("utf-8")
    print(f"Received message on topic '{message.topic}': {str(message.payload)}")

    # Send a POST request to the FastAPI endpoint
    #try:
    data = json.loads(message.payload)
    response = requests.post(FASTAPI_ENDPOINT, json=data)

    if response.status_code == 200:
        print("Data sent to FastAPI successfully!")
    else:
        print(f"Failed to send data to FastAPI. Status code: {response.status_code}")
    #except Exception as e:
        #print(f"Error sending data to FastAPI: {str(e)}")

if __name__=="__main__":
    # MQTT Client setup
    mqtt_client = paho.Client(client_id="Paho-MQTT_XLR82", userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect= on_connect
    
    mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    mqtt_client.username_pw_set(USER, PASSWD)
    mqtt_client.on_message = on_message
    # mqtt_client.enable_logger()
    # sensors = get_all_sensors()
    mqtt_client.subscribe(MQTT_TOPIC, qos=1)
    # print(sensors)
    # print("Loop started!")
    # Connect to HiveMQ's MQTT broker
    mqtt_client.connect(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    # Start the MQTT loop
    mqtt_client.loop_forever()