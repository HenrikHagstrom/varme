import os
import time
import board
import busio
import adafruit_sht31d
import psycopg2
from datetime import datetime

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

def log_to_database(temp_data):
    """Log sensor data to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="varme",
            user="postgres",
            password="sveJsan83",
            host="192.168.1.10",
            port="5432"
        )
        cur = conn.cursor()

        insert_query = """
        INSERT INTO temp_data (
            timestamp_col, temp_low, temp_mid, temp_high, temp_rtn, temp_fwd,
            temp_eld, temp_rok, temp_inne, temp_ute, hum_inne, hum_ute, temp_kb_in, temp_kb_ut
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Prepare the values for the insert statement
        values = (
            datetime.now(),
            temp_data.get("temp_low"),
            temp_data.get("temp_mid"),
            temp_data.get("temp_high"),
            temp_data.get("temp_rtn"),
            temp_data.get("temp_fwd"),
            temp_data.get("temp_eld"),
            temp_data.get("temp_rok"),
            temp_data.get("temp_inne"),
            temp_data.get("temp_ute"),
            temp_data.get("hum_inne"),
            temp_data.get("hum_ute"),
            temp_data.get("temp_kb_in"),
            temp_data.get("temp_kb_ut")
        )

        cur.execute(insert_query, values)
        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error logging to database: {e}")

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

    temp_data = {
        "temp_low": None,
        "temp_mid": None,
        "temp_high": None,
        "temp_rtn": None,
        "temp_fwd": None,
        "temp_eld": None,
        "temp_rok": None,
        "temp_inne": None,
        "temp_ute": None,
        "hum_inne": None,
        "hum_ute": None,
        "temp_kb_in": None,
        "temp_kb_ut": None
    }

    # Read DS18B20 sensors
    print("Reading fixed DS18B20 sensors...")
    for name, sensor_id in sensors_ds18b20.items():
        temp = read_temperature(sensor_id)
        if temp is not None:
            temp_data[name] = temp
            print(f"{name}: {temp:.2f}°C")
        else:
            print(f"{name}: Error reading temperature")

    # Read SHT31 sensors
    print("\nReading SHT31 sensors...")
    for name, sensor in sensors_sht31.items():
        temp, humidity = read_sht31(sensor)
        if temp is not None and humidity is not None:
            if name == "sht31_1":
                temp_data["temp_inne"] = temp
                temp_data["hum_inne"] = humidity
            elif name == "sht31_2":
                temp_data["temp_ute"] = temp
                temp_data["hum_ute"] = humidity
            print(f"{name}: {temp:.2f}°C, {humidity:.2f}% RH")
        else:
            print(f"{name}: Error reading temperature and humidity")

    # Log data to the database
    log_to_database(temp_data)

if __name__ == '__main__':
    main()
