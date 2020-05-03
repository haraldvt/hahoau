import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
import paho.mqtt.client as mqtt
import logging
import time

import buttons
import sunscreens

class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return False

def init():
  global logger

  my_filter = NoRunningFilter()
  logging.getLogger("apscheduler.scheduler").addFilter(my_filter)
  logging.getLogger("apscheduler.executors.default").addFilter(my_filter)
  
  logging.basicConfig(filename='/home/pi/share/pr/hahoau/headless/logging.log',level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)
  logger.info('Start')
  buttons.init()
  sunscreens.init()
  
def exit():
  buttons.exit()
  sunscreens.exit()
  logger.info('Stop\n\n\n')

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    sunscreens.control(4, str(message.payload.decode("utf-8")), 100) 

init()

#client =mqtt.Client("pi_device")
#client.on_message=on_message        #attach function to callback
#client.username_pw_set("esp32", "hH809814")
#client.connect("hassio.local")
#client.subscribe("homeassistant/pi/no1/sunscreen4")
#client.loop_start()    #start the loop

while True:
  time.sleep(0.3)

#message = raw_input("Press enter to quit\n\n") # Run until someone presses enter
exit()
GPIO.cleanup() # Clean up
#client.loop_stop() #stop the loop
