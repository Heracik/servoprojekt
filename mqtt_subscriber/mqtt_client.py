import gmqtt
import asyncio
import threading
import time
from datetime import datetime
import pytz

MQTT_BROKER = "broker.emqx.io"
TOPIC = "esp32/projekt"

client = None
message_queue = []

def on_connect(client, flags, rc, properties):
    print("MQTT Connected!")
    send_queued_messages()

def on_disconnect(client, userdata):
    print("MQTT Disconnected!")

async def connect_mqtt():
    global client
    if client is None:
        client = gmqtt.Client("django_mqtt")
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        await client.connect(MQTT_BROKER) 

def mqtt_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_mqtt())
    loop.run_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

def send_queued_messages():
    """Odosiela správy z fronty po jednej, keď je MQTT pripojený."""
    global client, message_queue

    while client and client.is_connected and message_queue:
        message = message_queue.pop(0)
        client.publish(TOPIC, message)
        print(f"Odoslané z fronty: {message}")
        time.sleep(1)

def get_city_time(city):
    """Získa aktuálny čas pre dané mesto."""
    city_timezones = {
    'bakerisland': 'Etc/GMT+12',
    'pagopago': 'Pacific/Pago_Pago',
    'honolulu': 'Pacific/Honolulu',
    'anchorage': 'America/Anchorage',
    'losangeles': 'America/Los_Angeles',
    'denver': 'America/Denver',
    'mexico': 'America/Mexico_City',
    'newyork': 'America/New_York',
    'caracas': 'America/Caracas',
    'buenosaires': 'America/Argentina/Buenos_Aires',
    'saopaulo': 'America/Sao_Paulo',
    'azores': 'Atlantic/Azores',
    'london': 'Europe/London',
    'bratislava': 'Europe/Bratislava',
    'athens': 'Europe/Athens',
    'moscow': 'Europe/Moscow',
    'dubai': 'Asia/Dubai',
    'islamabad': 'Asia/Karachi',
    'almaty': 'Asia/Almaty',
    'bangkok': 'Asia/Bangkok',
    'beijing': 'Asia/Shanghai',
    'tokyo': 'Asia/Tokyo',
    'sydney': 'Australia/Sydney',
    'honiara': 'Pacific/Honiara',
}

    

    if city not in city_timezones:
        return None  # Ak mesto nie je v zozname, vráti None

    timezone = pytz.timezone(city_timezones[city])
    city_time = datetime.now(timezone).strftime("%H:%M")
    return city_time

def send_current_time(city):
    city_time = get_city_time(city)
    if city_time:
        message = city_time  
        message_queue.append(message)
        print(f"Pridané do fronty: {message}")
        send_queued_messages()
