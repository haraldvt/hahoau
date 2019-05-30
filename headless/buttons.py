import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import sunscreens

class Knop:
  def __init__(self, pin, status, text, sunscreemcmd):
    self.pin = pin
    self.status = status
    self.text = text
    self.cmd = sunscreemcmd
    
status_op = "OP"
status_neer = "NEER"
KNOP_NEER = Knop(4, status_neer, "Neergelaten", "down")
KNOP_OP = Knop(7, status_op, "Opgehaald", "up")
sunscreenStatus = KNOP_OP # default status
knopPushed = None
busy = False
sched = BackgroundScheduler() #daemon=True

def button_op_callback(channel):
  check_knop_pushed(KNOP_OP)

def button_neer_callback(channel):
  check_knop_pushed(KNOP_NEER)

def check_knop_pushed(knop):
  global knopPushed
  if (knopPushed == None):
    time.sleep(0.02)  # debounce
    if (GPIO.input(knop.pin) == 0):
      logger.info("Button " + knop.text + " was pushed!")
      knopPushed = knop

def handle_knop_pushed():
  global knopPushed
  if (busy is True):
    return
  if (knopPushed != None):
    sunscreen(knopPushed)
    knopPushed = None

def sunscreen(gedrukteKnop):
  global sunscreenStatus
  global busy
  busy = True
  
  if (gedrukteKnop.status == status_neer and sunscreenStatus.status == status_neer): 
    logger.info("==>  scherm is al " + gedrukteKnop.text)
    time.sleep(0.3)
    busy = False
    return  # niet meerdere keren NEER. OP is niet erg, die is begrensd door de overload functie

  logger.info("start: actie zonnescherm " + gedrukteKnop.status)
  if (gedrukteKnop.status == status_neer):
    sunscreens.control(4, "down", 100, 15000)
    sunscreenStatus = KNOP_NEER
  else: 
    sunscreens.control(4, "up", 100, 26000)
    sunscreens.control(4, "down", 100, 300)
    sunscreenStatus = KNOP_OP
  
  logger.info("Actie gestopt; status is nu " + sunscreenStatus.text + "\n")
  busy = False;


def init():
  global logger
  logger = logging.getLogger(__name__)
  logger.info('init')
  GPIO.setup(KNOP_NEER.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KNOP_OP.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
  GPIO.add_event_detect(KNOP_NEER.pin, GPIO.FALLING, callback=button_neer_callback)
  GPIO.add_event_detect(KNOP_OP.pin, GPIO.FALLING, callback=button_op_callback)
  
  sched.add_job(handle_knop_pushed, 'interval', seconds = 1, id = 'handle_knop_pushed')
  sched.start()

def exit():
  logger.info('exit')
  sched.remove_job('handle_knop_pushed')
