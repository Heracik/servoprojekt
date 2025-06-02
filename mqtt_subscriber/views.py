from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from .mqtt_client import send_current_time
import pytz
from gmqtt import Client as MQTTClient
from django.views.decorators.csrf import csrf_exempt
import json
import asyncio
import logging

#broker.emqx.io
#broker.hivemq.com

cities_timezones = {
    'bakerisland': 'Etc/UTC-12:00',
    'pagopago': 'Pacific/UTC-11:00',
    'honolulu': 'Pacific/UTC-10:00',
    'anchorage': 'America/UTC-09:00',
    'losangeles': 'America/UTC-08:00',
    'denver': 'America/UTC-07:00',
    'mexico': 'America/UTC-06:00',
    'newyork': 'America/UTC-05:00',
    'caracas': 'America/UTC-04:00',
    'buenosaires': 'America/UTC-03:00',
    'saopaulo': 'America/UTC-02:00',
    'azores': 'Atlantic/UTC-01:00',
    'london': 'Europe/UTC±00:00',
    'bratislava': 'Europe/UTC+01:00',
    'athens': 'Europe/UTC+02:00',
    'moscow': 'Europe/UTC+03:00',
    'dubai': 'Asia/UTC+04:00',
    'islamabad': 'Asia/UTC+05:00',
    'almaty': 'Asia/UTC+06:00',
    'bangkok': 'Asia/UTC+07:00',
    'beijing': 'Asia/UTC+08:00',
    'tokyo': 'Asia/UTC+09:00',
    'sydney': 'Australia/UTC+10:00',
    'honiara': 'Pacific/UTC+11:00',
}


def home(request):
    
    capitalized_cities_timezones = {city.capitalize(): timezone for city, timezone in cities_timezones.items()}
    return render(request, 'mqtt_subscriber/home.html', {'cities_timezones': capitalized_cities_timezones})


def get_time_for_city(city, timezone):
    try:
        tz = pytz.timezone(timezone)
        city_time = datetime.now(tz).strftime("%H:%M")
        return city_time
    except pytz.UnknownTimeZoneError:
        return None  #

def send_time_for_city(request, city, timezone):
    
    city_time = get_time_for_city(city, timezone)
    
    if city_time:
        
        send_current_time(city)  
        return JsonResponse({'message': f'Čas pre {city.capitalize()} ({timezone}) bol úspešne odoslaný! Čas: {city_time}'})
    else:
        return JsonResponse({'message': 'Nastala chyba pri získavaní času pre vybrané mesto a časové pásmo.'}, status=400)

def send_time(request, city):
    send_current_time(city)
    return JsonResponse({'message': f'Time for {city} has been sent successfully!'})


async def send_mqtt_message(custom_time):
    
    client = MQTTClient("django_client")

    
    def on_connect(client, flags, rc, properties):
        print(f"Pripojenie úspešné, kód: {rc}")

    try:
        
        await client.connect('broker.hivemq.com', 1883)
        print("Pripojené k MQTT brokeru")

       
        topic = "esp32/projekt1"
        message = f"{custom_time}"

        
        await client.publish(topic, message)
        print(f"Správa '{message}' odoslaná do témy '{topic}'")

        await client.disconnect()
        print("Odpojené od MQTT brokeru")
    except Exception as e:
        print(f"Chyba pri odosielaní do MQTT: {e}")
        raise

@csrf_exempt
async def send_custom_time(request):
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
            custom_time = data.get('time')

            
            if not custom_time:
                return JsonResponse({"message": "Chýba hodnota 'time'."}, status=400)

            
            await send_mqtt_message(custom_time)

            return JsonResponse({"message": f"Vlastný čas {custom_time} bol odoslaný na MQTT!"})
        except Exception as e:
            
            print(f"Chyba pri odosielaní vlastného času: {e}")
            return JsonResponse({"message": "Nastala chyba pri odosielaní času."}, status=500)

    return JsonResponse({"message": "Nesprávna požiadavka!"}, status=400)

async def send_shutdown_command():
    client = MQTTClient("shutdown-client")

    async def connect_and_publish():
        await client.connect('broker.hivemq.com', 1883)
        await client.publish("esp32/projekt1", "000000000000", qos=1)
        await client.disconnect()

    try:
        await connect_and_publish()
        print("Príkaz na vypnutie bol odoslaný!")
    except Exception as e:
        print(f"Chyba pri odosielaní príkazu na vypnutie: {e}")
        raise

@csrf_exempt
def send_shutdown_command_view(request):
    if request.method == 'POST':
        try:
            
            asyncio.run(send_shutdown_command())
            return JsonResponse({'status': 'success', 'message': 'Príkaz na vypnutie bol odoslaný!'})
        except Exception as e:
            print(f"Chyba pri spracovaní príkazu na vypnutie: {e}")
            return JsonResponse({'status': 'error', 'message': 'Chyba pri odosielaní príkazu.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Nesprávna požiadavka!'}, status=400)


async def send_sync_command():
    client = MQTTClient("sync-client")

    async def connect_and_publish():
        await client.connect('broker.hivemq.com', 1883)
        await client.publish("esp32/projekt1", "0000000000", qos=1)
        await client.disconnect()

    try:
        await connect_and_publish()
        print("Príkaz na synchronizáciu bol odoslaný!")
    except Exception as e:
        print(f"Chyba pri odosielaní príkazu na synchronizáciu: {e}")
        raise

@csrf_exempt
def send_sync_command_view(request):
    if request.method == 'POST':
        try:
            asyncio.run(send_sync_command())
            return JsonResponse({'status': 'success', 'message': 'Synchronizácia bola úspešne spustená!'})
        except Exception as e:
            print(f"Chyba pri spracovaní príkazu na synchronizáciu: {e}")
            return JsonResponse({'status': 'error', 'message': 'Chyba pri odosielaní príkazu na synchronizáciu.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Nesprávna požiadavka!'}, status=400)

async def send_desync_command():
    client = MQTTClient("desync-client")

    async def connect_and_publish():
        await client.connect('broker.hivemq.com', 1883)
        await client.publish("esp32/projekt1", "1111111111", qos=1)
        await client.disconnect()

    try:
        await connect_and_publish()
        print("Príkaz na desynchronizáciu bol odoslaný!")
    except Exception as e:
        print(f"Chyba pri odosielaní príkazu na desynchronizáciu: {e}")
        raise

@csrf_exempt
def send_desync_command_view(request):
    if request.method == 'POST':
        try:
            asyncio.run(send_desync_command())
            return JsonResponse({'status': 'success', 'message': 'Desynchronizácia bola úspešne spustená!'})
        except Exception as e:
            print(f"Chyba pri spracovaní príkazu na desynchronizáciu: {e}")
            return JsonResponse({'status': 'error', 'message': 'Chyba pri odosielaní príkazu na desynchronizáciu.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Nesprávna požiadavka!'}, status=400)
