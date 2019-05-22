import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
import paho.mqtt.client as mqtt

import buttons
import sunscreens

def init():
  buttons.init()
  sunscreens.init()

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    sunscreens.control(4, str(message.payload.decode("utf-8")), 100) 

init()

client =mqtt.Client("pi_device")
client.on_message=on_message        #attach function to callback
client.username_pw_set("esp32", "hH809814")
client.connect("hassio.local")
client.subscribe("homeassistant/pi/no1/sunscreen4")
client.loop_start()    #start the loop

message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up
client.loop_stop() #stop the loop
