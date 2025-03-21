import os
import time
import board
import busio
import adafruit_sht31d

def initialize_w1():
    """Ensure the 1-Wire modules are loaded."""
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

def read_temperature(sensor_id):
    """Read temperature from a DS18B20 sensor."""
    sensor_path = f'/sys/bus/w1/devices/{sensor_id}/w1_slave'
    try:
        with open(sensor_path, 'r') as f:
            lines = f.readlines()
            if 'YES' in lines[0]:
                temp_str = lines[1].split('t=')[-1].strip()
                return float(temp_str) / 1000.0
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error reading {sensor_id}: {e}")
    return None
  
def initialize_sht31():
    """Initialize SHT31 sensors."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensors = {
        "sht31_1": adafruit_sht31d.SHT31D(i2c, address=0x44),
        "sht31_2": adafruit_sht31d.SHT31D(i2c, address=0x45)
    }
    return sensors

def read_sht31(sensor):
    """Read temperature and humidity from an SHT31 sensor."""
    try:
        return sensor.temperature, sensor.relative_humidity
    except Exception as e:
        print(f"Error reading SHT31: {e}")
    return None, None

def main():
    initialize_w1()

    sensors_ds18b20 = {
        "temp_low": "28-20320c525027",
        "temp_mid": "28-0115c2a512ff",
        "temp_high": "28-0115c271d9ff",
        "temp_rtn": "28-0215c2a45bff",
        "temp_fwd": "28-0115c2a6e4ff"
    }

    sensors_sht31 = initialize_sht31()

    print("Reading fixed DS18B20 sensors...")
    for name, sensor_id in sensors_ds18b20.items():
        temp = read_temperature(sensor_id)
        if temp is not None:
            print(f"{name}: {temp:.2f}°C")
        else:
            print(f"{name}: Error reading temperature")

    print("\nReading SHT31 sensors...")
    for name, sensor in sensors_sht31.items():
        temp, humidity = read_sht31(sensor)
        if temp is not None and humidity is not None:
            print(f"{name}: {temp:.2f}°C, {humidity:.2f}% RH")
        else:
            print(f"{name}: Error reading temperature and humidity")

if __name__ == '__main__':
    main()
