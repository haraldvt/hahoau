from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import time 

import RPi.GPIO as GPIO
import time
import pigpio
import atexit

bp = Blueprint('sunscreens', __name__, url_prefix='/sunscreens')

RELAY_SUNSCREEN = [17, 18, 27, 22]
RELAY_MOTOR_POWER = 25
RELAY_MOTOR_OVERLOAD = 25

MOTOR_1_C   = 23  # clockwise
MOTOR_1_CC  = 24  # counterclockwise

# Motor speed 0 (off) to 255 (max speed)
currentMotorSpeed = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for rs in RELAY_SUNSCREEN:
  GPIO.setup(rs, GPIO.OUT)
  GPIO.output(rs, GPIO.HIGH)
GPIO.setup(RELAY_MOTOR_POWER, GPIO.OUT)
timestamp_motor_power = 0
status_motor_power = GPIO.LOW
GPIO.output(RELAY_MOTOR_POWER, status_motor_power)

# create a pigpio object, that accesses the pigpiod deamon (which handles the PWM to the motors)
pi = pigpio.pi()
if not pi.connected:
    exit()
pi.set_mode(MOTOR_1_C  , pigpio.OUTPUT)
pi.set_mode(MOTOR_1_CC , pigpio.OUTPUT)



@bp.route('/', methods=('GET', 'POST'))
def show():
    if request.method == 'POST':
        title = request.form['title']    
        flash("boeh!")
    return render_template('sunscreens/sunscreens.html')

@bp.route('/<int:screen_id>/up', methods=('POST',))
def up(screen_id):
    control(screen_id, 'up', 100)
    return render_template('sunscreens/sunscreens.html')

@bp.route('/<int:screen_id>/down', methods=('POST',))
def down(screen_id):
    control(screen_id, 'down', 100)
    return render_template('sunscreens/sunscreens.html')

def control(screen_id, movement, percentage):
    ensure_motor_power()
    
    ss = [screen_id]
    if (screen_id == 0):
      ss = [1, 2, 3, 4]
    flash('Sunscreen ' + str(ss) + ' going ' + movement + '...')
    print "relais ", ss, " on "
    for s in ss:
      GPIO.output(RELAY_SUNSCREEN[s-1], GPIO.LOW)
    time.sleep(1)
    
    direction = 1
    if (movement == 'down'):
      direction = -1
    motor_event( int(((255.0 / 100.0) * percentage) * direction) )
    time.sleep(3)
    motor_event(0)
    
    time.sleep(1)
    for s in ss:
      GPIO.output(RELAY_SUNSCREEN[s-1], GPIO.HIGH)
    print "relais ", ss, " off "
    flash('Sunscreen ' + str(ss) + ' is ' + movement + '.')


# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    if not pi is None:
        print(" All off")
        pi.set_PWM_dutycycle(MOTOR_1_C,  0)
        pi.set_PWM_dutycycle(MOTOR_1_CC, 0)

atexit.register(turnOffMotors)


def motor_event(newSpeed):
    global currentMotorSpeed
    speedrange = range(0)
    if (newSpeed > currentMotorSpeed):
      speedrange = range(currentMotorSpeed, newSpeed, 10)
    else:
      speedrange = reversed(range(newSpeed, currentMotorSpeed, 10))
    
    for speed in speedrange:
      if speed == 0:
          pi.set_PWM_dutycycle(MOTOR_1_C,  0)
          pi.set_PWM_dutycycle(MOTOR_1_CC, 0)
      elif speed > 0:
          pi.set_PWM_dutycycle(MOTOR_1_C,  speed)
          pi.set_PWM_dutycycle(MOTOR_1_CC, 0)
      else:
          pi.set_PWM_dutycycle(MOTOR_1_C,  0)
          pi.set_PWM_dutycycle(MOTOR_1_CC, abs(speed))
      time.sleep(0.01)

    if newSpeed == 0:
        pi.set_PWM_dutycycle(MOTOR_1_C,  0)
        pi.set_PWM_dutycycle(MOTOR_1_CC, 0)

    currentMotorSpeed = newSpeed
    print("Motor speed: ", currentMotorSpeed)

def ensure_motor_power():
  global status_motor_power
  global timestamp_motor_power
  if (status_motor_power == GPIO.LOW):
    print("Motor power switched on now")
    status_motor_power = GPIO.HIGH
  GPIO.output(RELAY_MOTOR_POWER, status_motor_power)
  timestamp_motor_power = time.time()


def check_motor_power():
    global status_motor_power
    global timestamp_motor_power
    if ((time.time() - timestamp_motor_power) > 60.0):
      if (status_motor_power == GPIO.HIGH):
        print("Motor power switched off now")
        status_motor_power = GPIO.LOW
        GPIO.output(RELAY_MOTOR_POWER, status_motor_power)


sched = BackgroundScheduler() #daemon=True
sched.add_job(check_motor_power, 'interval', seconds = 10)
sched.start()
