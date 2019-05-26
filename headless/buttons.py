import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import sunscreens

KNOP_NEER = 4
KNOP_OP = 7
knopNeerPushed = 0
knopOpPushed = 0
sunscreenStatus = "OP" # default status
busy = False
sched = BackgroundScheduler() #daemon=True

def button_op_callback(channel):
  global knopOpPushed
  if (knopOpPushed == 0):
    logger.info("Button OP was pushed!")
    knopOpPushed = 1

def button_neer_callback(channel):
  global knopNeerPushed
  if (knopNeerPushed == 0):
    logger.info("Button NEER was pushed!")
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
    logger.info("==>  scherm is al NEER")
    time.sleep(0.3)
    return  # niet meerdere keren NEER. OP is niet erg, die is begrensd door de overload functie

  logger.info("start: actie zonnescherm " + action)
  busy = True

  if (action == "NEER"):
    sunscreens.control(4, "down", 100, 1500)
  else: 
    sunscreens.control(4, "up", 100, 26000)
    sunscreens.control(4, "down", 100, 70)
  
  sunscreenStatus = action
  logger.info("\nActie gestopt; status is nu " + sunscreenStatus + "\n")
  busy = False;


def init():
  global logger
  logger = logging.getLogger(__name__)
  logger.info('init')
  GPIO.setup(KNOP_NEER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KNOP_OP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
  GPIO.add_event_detect(KNOP_NEER, GPIO.FALLING, callback=button_neer_callback, bouncetime=200)
  GPIO.add_event_detect(KNOP_OP, GPIO.FALLING, callback=button_op_callback, bouncetime=200)
  
  sched.add_job(check_knop_pushed, 'interval', seconds = 1, id= 'buttons_interval')
  sched.start()

def exit():
  logger.info('exit')
  sched.remove_job('buttons_interval')
