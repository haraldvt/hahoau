import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import sunscreens

KNOP_NEER= 4
KNOP_OP= 7
knopNeerPushed = 0
knopOpPushed = 0
sunscreenStatus = "OP"
busy = False

def button_op_callback(channel):
  global knopOpPushed
  if (knopOpPushed == 0):
    print("  Button OP was pushed!")
    knopOpPushed = 1

def button_neer_callback(channel):
  global knopNeerPushed
  if (knopNeerPushed == 0):
    print("  Button NEER was pushed!")
    knopNeerPushed = 1

def check_knop_pushed():
  global knopNeerPushed
  global knopOpPushed
  if (busy is True) :
    return
  if (knopNeerPushed == 1):
    sunscreen("NEER")
  elif (knopOpPushed == 1):
    sunscreen("OP")
  knopNeerPushed = 0
  knopOpPushed = 0


def sunscreen(action):
  global sunscreenStatus
  global busy
  
  if (action == "NEER" and sunscreenStatus == "NEER"): 
    print("  scherm is al NEER\n")
    time.sleep(0.3)
    return  # niet meerdere keren NEER. OP is niet erg, die is begrensd door de overload functie

  print("start " + action)
  busy = True

  sunscreens.control(4, "down" if action == "NEER" else "up", 100) 
  
  sunscreenStatus = action
  print("stop; status is " + sunscreenStatus + "\n")
  busy = False;


def init():
  GPIO.setup(KNOP_NEER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(KNOP_OP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  GPIO.add_event_detect(KNOP_NEER, GPIO.RISING, callback=button_neer_callback)
  GPIO.add_event_detect(KNOP_OP, GPIO.RISING, callback=button_op_callback)
  
  sched = BackgroundScheduler() #daemon=True
  sched.add_job(check_knop_pushed, 'interval', seconds = 1)
  sched.start()

