from machine import ADC, Pin, SoftI2C
from dht import DHT22
from ssd1306 import SSD1306_I2C
import time
import json
from umqtt.simple import MQTTClient

mqtt_broker = "mosquitto.nodered-fi.ipv64.net"
mqtt_port = 1883
mqtt_user = "FI"
mqtt_password = "FI"
mqtt_topic = "Met/FI/krause"
client_id = "krause2003"

sensor = DHT22(Pin(15))
pir = Pin(2)
photo_sensor = Pin(32)
led = Pin(33, Pin.OUT)
led_red = Pin(25, Pin.OUT)
led_yellow = Pin(26, Pin.OUT)
led_green = Pin(27, Pin.OUT)
i2c = SoftI2C(scl=Pin(22), sda=Pin(23), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)


def oled_show(temperature, humidity):
    oled.fill(0)
    oled.text("Temperature:", 10, 0)
    oled.text(f"{temperature} C", 10, 20)
    oled.text(f"Humidity:", 10, 40)
    oled.text(f"{humidity}%", 10, 55)
    oled.show()


def measure_temperature():
    sensor.measure()
    return sensor.temperature()

def temperature_led():
    if measure_temperature() >= 30:
        led_red.on()
        led_green.off()
        led_yellow.off()
    elif measure_temperature() >= 25:
        led_yellow.on()
        led_red.off()
        led_green.off()
    elif measure_temperature() >= 20:
        led_green.on()
        led_yellow.off()
        led_red.off()


def measure_humidity():
    sensor.measure()
    return sensor.humidity()


def measure_photo():
    rl10 = 50
    gamma = 0.7
    dings = ADC(photo_sensor)
    voltage = dings.read() / 4096 * 5
    resistance = voltage * 2000 / (1 - voltage / 5)
    lux = round(pow(rl10 * 1e3 * pow(10, gamma) / resistance, 1 / gamma), 0)

    return lux


def json_store(temperature, humidity, lux):
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "lux": lux,
        "motion": pir.value()
    }

    return json.dumps(data)

def send_json_data():
    try:
        client = MQTTClient(client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password)
        client.connect()
        json_data = json_store(measure_temperature(), measure_humidity(), measure_photo())
        client.publish(mqtt_topic, json_data)
        client.disconnect()
        print("JSON Daten erfolgreich gesendet.")
    except Exception as e:
        print("Fehler beim Senden der JSON Daten:", e)

def motion_sensor():
    if pir.value() == 1:
        led.on()
    else:
        led.off()


def print_to_terminal(temperature, humidity, lux):
    print(f"Temperature: {temperature}C")
    print(f"Humidity: {humidity}%")
    print(f"Lux: {lux}")
    print("-----------------------")

while True:
    temperature_led()
    oled_show(measure_temperature(), measure_humidity())
    motion_sensor()
    print_to_terminal(measure_temperature(), measure_humidity(), measure_photo())
    send_json_data()
    time.sleep(2)


