import csv

def read_temperatures_and_calculate_avg(log_file_path):
    # สร้างดิกชันนารีเพื่อเก็บข้อมูลอุณหภูมิของแต่ละคอร์
    core_temps = {f"Core {i} Temp.": [] for i in range(10)}
    
    try:
        with open(log_file_path, 'r') as file:
            reader = csv.reader(file)

            # ข้ามบรรทัดหัวข้อ
            header = next(reader)
            
            for row in reader:
                if len(row) < 11:
                    continue  # ข้ามบรรทัดที่ไม่ครบข้อมูล
                
                # ดึงค่าของอุณหภูมิแต่ละคอร์จากคอลัมน์ที่เกี่ยวข้อง
                for i in range(10):
                    try:
                        temp = float(row[i + 1])
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

if __name__ == "__main__":
    log_file_path = r'C:\Program Files\Core Temp\CT-Log 2024-09-10 12-44-25.csv'  # เปลี่ยนเป็นเส้นทางไฟล์ log ของคุณ
    avg_temperatures, avg_all_temperature = read_temperatures_and_calculate_avg(log_file_path)

    if avg_temperatures:
        for core, avg_temp in avg_temperatures.items():
            if avg_temp is not None:
                print(f"{core}: {avg_temp:.2f}°C")
            else:
                print(f"{core}: No data available")

    if avg_all_temperature is not None:
        print(f"Average CPU Temperature (All Cores): {avg_all_temperature:.2f}°C")
    else:
        print("Unable to retrieve average temperatures.")
