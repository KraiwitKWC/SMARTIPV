import csv
import paho.mqtt.client as mqtt
import psutil
import time
from datetime import datetime
import requests
import json
# MQTT broker details
MQTT_BROKER = 'mqtt.nxge.co'  # เปลี่ยนเป็น broker ของคุณ
MQTT_PORT = 1883
MQTT_TOPIC = 'SMATIPC/UPTIME'
MQTT_TOPIC_STATUS = 'SMATIPC/STATUS'

# Create an MQTT client instance
client = mqtt.Client()

# Connect to the MQTT broker
def connect_mqtt():
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def read_last_row_and_calculate_avg(log_file_path):
    # สร้างดิกชันนารีเพื่อเก็บข้อมูลอุณหภูมิของแต่ละคอร์
    core_temps = {f"Core {i} Temp.": [] for i in range(10)}
    
    try:
        with open(log_file_path, 'r') as file:
            reader = csv.reader(file)

            # อ่านบรรทัดสุดท้าย
            last_row = None
            for row in reader:
                last_row = row
            
            if last_row and len(last_row) >= 11:  # ตรวจสอบว่ามีข้อมูลเพียงพอ
                for i in range(10):
                    try:
                        temp = float(last_row[i + 1])  # ดึงค่าของอุณหภูมิแต่ละคอร์จากคอลัมน์ที่เกี่ยวข้อง
                        core_temps[f"Core {i} Temp."].append(temp)
                    except ValueError:
                        continue  # ข้ามค่าที่ไม่ใช่ตัวเลข

        # คำนวณค่าเฉลี่ยของอุณหภูมิแต่ละคอร์
        avg_temps = {}
        all_temps = []  # ใช้เพื่อคำนวณค่าเฉลี่ยรวม

        for core, temps in core_temps.items():
            if temps:
                avg_temps[core] = sum(temps) / len(temps)
                all_temps.extend(temps)  # รวมข้อมูลอุณหภูมิทั้งหมดเพื่อคำนวณค่าเฉลี่ยรวม
            else:
                avg_temps[core] = None

        # คำนวณค่าเฉลี่ยรวมของอุณหภูมิทุกคอร์
        if all_temps:
            avg_all = sum(all_temps) / len(all_temps)
        else:
            avg_all = None

        return avg_temps, avg_all

    except Exception as e:
        print(f"Error: {e}")
        return None, None

def read_temperatures_and_calculate_avg(log_file_path):
    # สร้างดิกชันนารีเพื่อเก็บข้อมูลอุณหภูมิของแต่ละคอร์
    core_temps = {f"Core {i} Temp.": [] for i in range(10)}
    
    try:
        with open(log_file_path, 'r') as file:
            reader = csv.reader(file)

            # อ่านบรรทัดสุดท้าย
            last_row = None
            for row in reader:
                last_row = row
            
            if last_row and len(last_row) >= 11:  # ตรวจสอบว่ามีข้อมูลเพียงพอ
                for i in range(10):
                    try:
                        temp = float(last_row[i + 1])  # ดึงค่าของอุณหภูมิแต่ละคอร์จากคอลัมน์ที่เกี่ยวข้อง
                        core_temps[f"Core {i} Temp."].append(temp)
                    except ValueError:
                        continue  # ข้ามค่าที่ไม่ใช่ตัวเลข

        # คำนวณค่าเฉลี่ยของอุณหภูมิแต่ละคอร์
        avg_temps = {}
        all_temps = []  # ใช้เพื่อคำนวณค่าเฉลี่ยรวม

        for core, temps in core_temps.items():
            if temps:
                avg_temps[core] = sum(temps) / len(temps)
                all_temps.extend(temps)  # รวมข้อมูลอุณหภูมิทั้งหมดเพื่อคำนวณค่าเฉลี่ยรวม
            else:
                avg_temps[core] = None

        # คำนวณค่าเฉลี่ยรวมของอุณหภูมิทุกคอร์
        if all_temps:
            avg_all = sum(all_temps) / len(all_temps)
        else:
            avg_all = None

        return avg_temps, avg_all

    except Exception as e:
        print(f"Error: {e}")
        return None, None

def get_system_metrics():
    cpu_load = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    uptime = time.time() - psutil.boot_time()
    timestamp = datetime.now().isoformat()
    cpu_freq = psutil.cpu_freq()

    # แสดงความเร็ว CPU (MHz และแปลงเป็น GHz)
    current_speed_mhz = cpu_freq.current
    current_speed_ghz = current_speed_mhz / 1000
    metrics = {
        'cpu_load': cpu_load,
        'ram_usage': ram_usage,
        'uptime': uptime,
        'timestamp': timestamp,
        'CPU_GHz':current_speed_ghz
    }
    return metrics

def publish_metrics(log_file_path):
    avg_temperatures, avg_all_temperature = read_temperatures_and_calculate_avg(log_file_path)

    metrics = get_system_metrics()
    
    # Create payload
    payload = {
        'cpu_load': metrics['cpu_load'],
        'ram_usage': metrics['ram_usage'],
        'uptime': metrics['uptime'],
        'timestamp': metrics['timestamp'],
        'CPU_GHz':metrics['CPU_GHz']
    }
    
    for i in range(10):
        core_key = f'core{i + 1}'
        payload[core_key] = avg_temperatures.get(f"Core {i} Temp.", None)
    
    payload['avg_all_temperature'] = avg_all_temperature

    # Print payload for debugging
    

    return payload

def publish_status():
    # ส่งสถานะการเชื่อมต่อ
    payload = "Online"
    client.publish(MQTT_TOPIC, payload)
    # payload2 = publish_metrics(log_file_path)
    # client.publish(MQTT_TOPIC_STATUS, payload2)

def login():
    url = "http://172.16.1.110:8080/api/auth/login"
 
    payload = {
        "username": "tenant@thingsboard.org",
        "password": "tenant"
    }
   
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/9.2.0"
    }
 
    response = requests.post(url, json=payload, headers=headers)
 
    if response.status_code == 200:
        result = response.json()
        token = result.get("token")
        return token
    
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
def post_thingboard():
    entityType = 'DEVICE'
    entityId = '953037d0-6f40-11ef-ada4-619820209fa2'
    scope ='ANY'
    log_file_path = r'C:\Program Files\Core Temp\CT-Log 2024-09-11 09-03-47.csv'  # เปลี่ยนเป็นเส้นทางไฟล์ log ของคุณ
    data = publish_metrics(log_file_path)
    print(data)
    url = f'http://100.70.74.89:8080/api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope}'
    token = login()
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Authorization': f'Bearer {token}'
    }

    response = requests.post(url, json=data, headers=headers)
    # Print the response

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

# Main loop
if __name__ == "__main__":
    log_file_path = r'C:\Program Files\Core Temp\CT-Log 2024-09-11 09-03-47.csv'  # เปลี่ยนเป็นเส้นทางไฟล์ log ของคุณ
    connect_mqtt()
    try:
        while True:
            publish_status()
            publish_metrics(log_file_path)
            payload2 = publish_metrics(log_file_path)
            payload2_json = json.dumps(payload2)  # แปลง payload เป็น JSON string
            client.publish(MQTT_TOPIC_STATUS, payload2_json)
            
            post_thingboard()
            print("Metrics published successfully.")
            
            time.sleep(5)  # ส่งข้อมูลทุก 5 วินาที
    except KeyboardInterrupt:
        print("Exiting...")
        client.loop_stop()
        client.disconnect()
