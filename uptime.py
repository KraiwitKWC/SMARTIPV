import csv
import paho.mqtt.client as mqtt
import psutil
import time
from datetime import datetime
import requests
import json

# MQTT broker details
MQTT_BROKER = 'mqtt.nxge.co'
MQTT_PORT = 1883
MQTT_TOPIC = 'SMATIPC/UPTIME'
MQTT_TOPIC_STATUS = 'SMATIPC/STATUS'

client = mqtt.Client()

def connect_mqtt():
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def read_temperatures_and_calculate_avg(log_file_path):
    core_temps = {f"Core {i} Temp.": [] for i in range(10)}
    try:
        with open(log_file_path, 'r') as file:
            reader = csv.reader(file)
            last_row = None
            for row in reader:
                last_row = row
            if last_row and len(last_row) >= 11:
                for i in range(10):
                    try:
                        temp = float(last_row[i + 1])
                        core_temps[f"Core {i} Temp."].append(temp)
                    except ValueError:
                        continue
        avg_temps = {}
        all_temps = []
        for core, temps in core_temps.items():
            if temps:
                avg_temps[core] = sum(temps) / len(temps)
                all_temps.extend(temps)
            else:
                avg_temps[core] = None
        if all_temps:
            avg_all = sum(all_temps) / len(all_temps)
        else:
            avg_all = None
        return avg_temps, avg_all
    except Exception as e:
        print(f"Error reading temperatures: {e}")
        return None, None

def get_system_metrics():
    cpu_load = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    timestamp = datetime.now().isoformat()
    uptime_seconds = time.time() - psutil.boot_time()
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_formatted = f"{int(days):02}:{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    cpu_freq = psutil.cpu_freq().current / 1000
    return {
        'cpu_load': cpu_load,
        'ram_usage': ram_usage,
        'uptime': uptime_formatted,
        'timestamp': timestamp,
        'CPU_GHz': cpu_freq
    }

def publish_metrics(log_file_path):
    avg_temperatures, avg_all_temperature = read_temperatures_and_calculate_avg(log_file_path)
    metrics = get_system_metrics()
    payload = {
        'cpu_load': metrics['cpu_load'],
        'ram_usage': metrics['ram_usage'],
        'uptime': metrics['uptime'],
        'timestamp': metrics['timestamp'],
        'CPU_GHz': metrics['CPU_GHz']
    }
    if avg_temperatures:
        for i in range(10):
            core_key = f'core{i + 1}'
            payload[core_key] = avg_temperatures.get(f"Core {i} Temp.", None)
        payload['avg_all_temperature'] = avg_all_temperature
    return payload

def publish_status():
    payload = "Online"
    client.publish(MQTT_TOPIC, payload)

def login():
    url = "http://172.16.1.110:8080/api/auth/login"
    payload = {"username": "tenant@thingsboard.org", "password": "tenant"}
    headers = {"Content-Type": "application/json", "User-Agent": "insomnia/9.2.0"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def post_thingboard(data):
    try:
        entityType = 'DEVICE'
        entityId = '953037d0-6f40-11ef-ada4-619820209fa2'
        scope = 'ANY'
        url = f'http://100.70.74.89:8080/api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope}'
        token = login()
        headers = {'accept': 'application/json', 'Content-Type': 'application/json', 'X-Authorization': f'Bearer {token}'}
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
    except Exception as e:
        print(f"Error posting to ThingBoard: {e}")

if __name__ == "__main__":
    log_file_path = r'C:\Program Files\Core Temp\CT-Log 2024-09-11 09-03-47.csv'
    connect_mqtt()
    try:
        while True:
            try:
                publish_status()
                data = publish_metrics(log_file_path)
                client.publish(MQTT_TOPIC_STATUS, json.dumps(data))
                post_thingboard(data)
                print(data)
                print("Metrics published successfully.")
            except Exception as e:
                print(f"Error in main loop: {e}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
        client.loop_stop()
        client.disconnect()
