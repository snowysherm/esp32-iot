from machine import ADC, Pin, SoftI2C
from dht import DHT22
from ssd1306 import SSD1306_I2C
from time import sleep
import json

sensor = DHT22(Pin(15))
pir = Pin(2)
photo_sensor = Pin(32)
led = Pin(33, Pin.OUT)
led_red = Pin(25, Pin.OUT)
led_yellow = Pin(26, Pin.OUT)
led_green = Pin(27, Pin.OUT)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)


def oled_show(temperature, humidity):
    oled.fill(0)
    oled.text("Temperature:", 10, 0)
    oled.text(f"{temperature} C", 10, 20)
    oled.text(f"Humidity:", 10, 40)
    oled.text(f"{humidity}%", 10, 55)
    oled.show()


def sensor_measure_temperature():
    sensor.measure()
    return sensor.temperature()


def temperature_led():
    if sensor_measure_temperature() <= 20:
        led_green.on()
        led_yellow.off()
        led_red.off()
    elif sensor_measure_temperature() >= 30:
        led_red.on()
        led_green.off()
        led_yellow.off()
    elif sensor_measure_temperature() >= 25:
        led_yellow.on()
        led_red.off()
        led_green.off()


def sensor_measure_humidity():
    sensor.measure()
    return sensor.humidity()


def photo_measure():
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
    }

    return json.dumps(data)


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
    json_store(sensor_measure_temperature(),
               sensor_measure_humidity(), photo_measure())
    oled_show(sensor_measure_temperature(), sensor_measure_humidity())
    motion_sensor()
    print_to_terminal(sensor_measure_temperature(),
                      sensor_measure_humidity(), photo_measure())

    sleep(2)
