from machine import ADC, Pin, I2C
from dht import DHT22
from ssd1306 import SSD1306_I2C
from time import sleep
import json

sensor = DHT22(Pin(15))
pir = Pin(2)
photo = Pin(32)
led = Pin(33, Pin.OUT)
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

def oled_show(temperature, humidity):
    oled.fill(0)
    oled.text("Temperature:", 10, 0)
    oled.text(f"{temperature}°C", 10, 20)
    oled.text(f"Humidity:", 10, 40)
    oled.text(f"{humidity}%", 10, 55)
    oled.show()

def sensor_measure_temperature():
    sensor.measure()
    return sensor.temperature()

def sensor_measure_humidity():
    sensor.measure()
    return sensor.humidity()

def photo():
    photo = ADC(Pin(32))
    return photo.read()

def json_store(temperature, humidity, lux):

    data = {
        "temperature": temperature,
        "humidity": humidity,
        "lux": lux,
     }

    # json export der nicht in wokwi funktioniert
    # with open("data.json", "w") as f:
    #    json.dump(data, f)

def motion_sensor():
    if pir.value() == 1:
        led.on()
    else:
        led.off()

def print_to_terminal(temperature, humidity):
    print(f"Temperature: {temperature}C")
    print(f"Humidity: {humidity}%")
    print("-----------------------")

while True:

  json_store(sensor_measure_temperature(), sensor_measure_humidity(), photo()) 
  oled_show(sensor_measure_temperature(), sensor_measure_humidity())
  motion_sensor()
  print_to_terminal(sensor_measure_temperature(), sensor_measure_humidity())

  sleep(2)
