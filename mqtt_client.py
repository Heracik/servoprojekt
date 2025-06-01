import os
import django
import asyncio
from gmqtt import Client as MQTTClient

# Globálny stav pripojenia
is_connected = False

# Nastavenie Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mqtt_project_sub.settings')
django.setup()

# Callbacky pre MQTT
def on_connect(client, userdata, flags, rc):
    global is_connected
    is_connected = True
    print(f"Pripojený s kódom {rc}")
    client.subscribe('esp32/led_status')

def on_disconnect(client, userdata,rc):
    global is_connected
    is_connected = False
    print(f"MQTT odpojené, kód: {rc}")

def on_message(client, topic, payload, qos, properties):
    print(f"Téma: {topic}")
    print(f"Payload: {payload.decode()}")


# Funkcia na spustenie MQTT klienta
async def mqtt_loop():
    client = MQTTClient("my_client")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    print("Pripájam sa na MQTT broker...")
    await client.connect('broker.hivemq.com', 1883)

    # Zabezpečenie bežiacej slučky
    try:
        while True:
            await asyncio.sleep(1)  # Udržuje klienta aktívneho
    except asyncio.CancelledError:
        print("MQTT klient bol zastavený")
    finally:
        await client.disconnect()

# Hlavná slučka
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mqtt_loop())
    except KeyboardInterrupt:
        print("Ukončenie programu...")

