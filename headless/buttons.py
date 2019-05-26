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
sched = BackgroundScheduler() #daemon=True

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

  if (action == "NEER"):
    sunscreens.control(4, "down", 100, 13300)
  else: 
    sunscreens.control(4, "up", 100, 22000)
    sunscreens.control(4, "down", 100, 30)
  
  sunscreenStatus = action
  print("stop; status is " + sunscreenStatus + "\n")
  busy = False;


def init():
  GPIO.setup(KNOP_NEER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KNOP_OP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
  GPIO.add_event_detect(KNOP_NEER, GPIO.FALLING, callback=button_neer_callback, bouncetime=200)
  GPIO.add_event_detect(KNOP_OP, GPIO.FALLING, callback=button_op_callback, bouncetime=200)
  
  sched.add_job(check_knop_pushed, 'interval', seconds = 1, id= 'buttons_interval')
  sched.start()

def exit():
  sched.remove_job('buttons_interval')
