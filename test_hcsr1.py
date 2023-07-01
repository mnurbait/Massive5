import RPi.GPIO as GPIO
import time
import requests

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Ubidots Configuration
TOKEN = "BBFF-zvImWzh94GrcXXzlr9Pn338s8hDxd5"
DEVICE_LABEL = "bismillah-jadi"
VARIABLE_LABEL = "volume-trash-1"

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    distance = distance / 30 
    distance = distance * 100
 
    return distance

def send_data_to_ubidots(value):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{device_label}/{variable_label}/values"
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    payload = {"value": value}

    try:
        response = requests.post(url.format(device_label=DEVICE_LABEL, variable_label=VARIABLE_LABEL), headers=headers, json=payload)
        if response.status_code == 201:
            print("Data sent to Ubidots successfully.")
        else:
            print("Failed to send data to Ubidots. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred while sending data to Ubidots:", str(e))

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print("Jarak Terukur = %.1f cm" % dist)
            send_data_to_ubidots(dist)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
