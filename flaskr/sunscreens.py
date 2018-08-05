from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import RPi.GPIO as GPIO
import time
import pigpio
import atexit

bp = Blueprint('sunscreens', __name__, url_prefix='/sunscreens')


@bp.route('/', methods=('GET', 'POST'))
def show():
    if request.method == 'POST':
        title = request.form['title']    
        flash("boeh!")
    return render_template('sunscreens/sunscreens.html')

@bp.route('/<int:screen_id>/up', methods=('POST',))
def up(screen_id):
    flash('up')
    print "relais on "
    GPIO.output(17,GPIO.HIGH)
    time.sleep(1)
    motor_event(255)
    time.sleep(3)
    motor_event(0)
    time.sleep(1)
    GPIO.output(17,GPIO.LOW)    
    return render_template('sunscreens/sunscreens.html')

@bp.route('/<int:screen_id>/down', methods=('POST',))
def down(screen_id):
    flash('down')
    print "relais off"
    GPIO.output(17,GPIO.HIGH)
    time.sleep(1)
    motor_event(-255)
    time.sleep(3)
    motor_event(0)
    time.sleep(1)
    GPIO.output(17,GPIO.LOW)    
    return render_template('sunscreens/sunscreens.html')


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

MOTOR_1_C   = 23
MOTOR_1_CC  = 24

# Motor speed 0 (off) to 255 (max speed)
currentMotorSpeed = 0

# create a pigpio object, that accesses the pigpiod deamon (which handles the PWM to the motors)
pi = pigpio.pi()
if not pi.connected:
    exit()
pi.set_mode(MOTOR_1_C  , pigpio.OUTPUT)
pi.set_mode(MOTOR_1_CC , pigpio.OUTPUT)

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
      time.sleep(0.02)

    if newSpeed == 0:
        pi.set_PWM_dutycycle(MOTOR_1_C,  0)
        pi.set_PWM_dutycycle(MOTOR_1_CC, 0)

    currentMotorSpeed = newSpeed
    print("Motor speed: ", currentMotorSpeed)


