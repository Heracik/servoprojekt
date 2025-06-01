import asyncio
import os
import django
from threading import Thread
from django.utils import timezone
from gmqtt import Client as MQTTClient
from asgiref.sync import sync_to_async


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mqtt_project.settings')
django.setup()

from mqtt_subscriber.models import MQTTMessage

is_connected = False

def on_connect(client, userdata, flags, rc):
    global is_connected
    is_connected = True
    print(f"Pripojený s kódom {rc}")
    client.subscribe('esp32/test')

def on_disconnect(client, userdata, rc):
    global is_connected
    is_connected = False
    print(f"MQTT odpojené, kód: {rc}")

@sync_to_async
def save_message(topic, payload):
    message = MQTTMessage(
        topic=topic,
        payload=payload,
        timestamp=timezone.now()
    )
    message.save()
    print("Správa bola uložená do databázy")

async def on_message(client, topic, payload, qos, properties):
    print(f"Téma: {topic}")
    print(f"Payload: {payload.decode()}")

    # Uloženie správy do databázy asynchrónne
    await save_message(topic, payload.decode())

async def mqtt_loop():
    client = MQTTClient("my_client")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    print("Pripájam sa na broker...")
    await client.connect('broker.hivemq.com', 1883)

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("MQTT klient zastavený")
    finally:
        await client.disconnect()

def start_mqtt():
    asyncio.run(mqtt_loop())
