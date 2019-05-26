from apscheduler.schedulers.background import BackgroundScheduler
from datetime import time 

import RPi.GPIO as GPIO
import time
import pigpio
import atexit
import logging


RELAY_SUNSCREEN = [17, 18, 27, 22]
RELAY_MOTOR_POWER = 25
RELAY_MOTOR_OVERLOAD = 8

MOTOR_1  = 23  
MOTOR_2  = 24

# Motor speed 0 (off) to 255 (max speed)
currentMotorSpeed = 0
timestamp_motor_power = 0
status_motor_power = GPIO.LOW

sched = BackgroundScheduler() #daemon=True
# create a pigpio object, that accesses the pigpiod deamon (which handles the PWM to the motors)
# to start the daemon: sudo pigpiod
pi = pigpio.pi()


def control(screen_id, movement, percentage, ms=5000.0):
    ensure_motor_power()
    
    ss = [screen_id]
    if (screen_id == 0):
      ss = [1, 2, 3, 4]
    print "relais ", ss, " on "
    for s in ss:
      GPIO.output(RELAY_SUNSCREEN[s-1], GPIO.LOW)
    time.sleep(1)
    
    direction = 1
    if (movement == 'down'):
      direction = -1
    motor_event( int(((255.0 / 100.0) * percentage) * direction) )
    
    # measure time, and measure overload
    start_time = time.time()
    overload = GPIO.input(RELAY_MOTOR_OVERLOAD)
    print(overload)
    while (((time.time() - start_time) < int(ms / 1000.0)) and (overload == 0)):
      time.sleep(0.1)
      overload = GPIO.input(RELAY_MOTOR_OVERLOAD)
      if (overload):
        logger.info("motor overload")
    
    motor_event(0)
    
    time.sleep(1)
    for s in ss:
      GPIO.output(RELAY_SUNSCREEN[s-1], GPIO.HIGH)
    print "relais ", ss, " off "


# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
  global pi
  if not pi is None:
      logger.info("All motors off")
      pi.set_PWM_dutycycle(MOTOR_1, 0)
      pi.set_PWM_dutycycle(MOTOR_2, 0)



def motor_event(newSpeed):
    global currentMotorSpeed
    global pi
    speedrange = range(0)
    if (newSpeed > currentMotorSpeed):
      speedrange = range(currentMotorSpeed, newSpeed, 20)
    else:
      speedrange = reversed(range(newSpeed, currentMotorSpeed, 20))
    
    for speed in speedrange:
      if speed == 0:
          pi.set_PWM_dutycycle(MOTOR_1,  0)
          pi.set_PWM_dutycycle(MOTOR_2, 0)
      elif speed > 0:
          pi.set_PWM_dutycycle(MOTOR_1,  speed)
          pi.set_PWM_dutycycle(MOTOR_2, 0)
      else:
          pi.set_PWM_dutycycle(MOTOR_1,  0)
          pi.set_PWM_dutycycle(MOTOR_2, abs(speed))
      time.sleep(0.01)

    if newSpeed == 0:
        pi.set_PWM_dutycycle(MOTOR_1,  0)
        pi.set_PWM_dutycycle(MOTOR_2, 0)

    currentMotorSpeed = newSpeed
    logger.debug("Motor speed: ", currentMotorSpeed)

def ensure_motor_power():
  global status_motor_power
  global timestamp_motor_power
  if (status_motor_power == GPIO.LOW):
    logger.info("Motor power switched on now")
    status_motor_power = GPIO.HIGH
    GPIO.output(RELAY_MOTOR_POWER, status_motor_power)
    timestamp_motor_power = time.time()
    time.sleep(4)  # give power supply time to power up
  else: 
    GPIO.output(RELAY_MOTOR_POWER, status_motor_power)
    timestamp_motor_power = time.time()


def check_motor_power():
    global status_motor_power
    global timestamp_motor_power
    if ((time.time() - timestamp_motor_power) > 60.0):
      if (status_motor_power == GPIO.HIGH):
        logger.info("Motor power switched off now")
        status_motor_power = GPIO.LOW
        GPIO.output(RELAY_MOTOR_POWER, status_motor_power)
        time.sleep(4)  # give power supply time to power down 



def init():
  global pi
  global logger
  
  logger = logging.getLogger(__name__)
  logger.info('init')
  for rs in RELAY_SUNSCREEN:
    GPIO.setup(rs, GPIO.OUT)
    GPIO.output(rs, GPIO.HIGH)
  GPIO.setup(RELAY_MOTOR_POWER, GPIO.OUT)
  GPIO.output(RELAY_MOTOR_POWER, status_motor_power)
  GPIO.setup(RELAY_MOTOR_OVERLOAD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  if not pi.connected:
      exit()
  pi.set_mode(MOTOR_1 , pigpio.OUTPUT)
  pi.set_mode(MOTOR_2 , pigpio.OUTPUT)
  
  sched.add_job(check_motor_power, 'interval', seconds = 20, id = 'suncscreens_interval')
  sched.start()

  atexit.register(turnOffMotors)

def exit():
  logger.info('exit')
  sched.remove_job('suncscreens_interval')
