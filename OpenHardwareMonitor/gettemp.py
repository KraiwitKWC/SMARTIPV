import clr
import os

# Path to OpenHardwareMonitorLib.dll
dll_path = os.path.join(os.getcwd(), 'OpenHardwareMonitorLib.dll')

# Print path to verify
print(f"DLL Path: {dll_path}")

try:
    clr.AddReference(dll_path)
except Exception as e:
    print(f"Error loading DLL: {e}")

from OpenHardwareMonitor import Hardware

def get_cpu_temperature():
    computer = Hardware.Computer()
    computer.CPUEnabled = True
    computer.Open()

    temperature = None
    for hardware in computer.Hardware:
        hardware.Update()
        if hardware.HardwareType == Hardware.HardwareType.CPU:
            for sensor in hardware.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    temperature = sensor.Value
                    break
    return temperature

if __name__ == "__main__":
    temp = get_cpu_temperature()
    print(f"CPU Temperature: {temp} °C")
