from flask import Flask, escape, request, render_template
import RPi.GPIO as GPIO
import time
import datetime
import os

app = Flask(__name__)

ALARM_SOUND_FILE_WAV = '/home/pi/AlArmPiT/airhorn.wav'

#https://pinout.xyz/
SERVO_BOARD_PIN = 11 #GPIO 17
LIGHTS_OFF_ANGLE = 125
LIGHTS_ON_ANGLE = 170

GPIO.setmode(GPIO.BOARD)

def setupPwmPin(pin, rate):
    GPIO.setup(pin, GPIO.OUT)
    pwm=GPIO.PWM(pin, rate) #Hz
    pwm.start(0)
    return (pin, pwm)

servo = setupPwmPin(SERVO_BOARD_PIN, 50)

def sendPulse((pin, pwm), duty, length):
    GPIO.output(pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(length)
    GPIO.output(pin, False)
    pwm.ChangeDutyCycle(0)

def setAngle(servo, angle):
    sendPulse(servo, duty=angle/18+2, length=0.5)

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/ring')
def ring():
    os.system('aplay ' + ALARM_SOUND_FILE_WAV)
    return 'alarm go ringgggg'

alarmHour = 0
alarmMinute = 0

#add to crontab -e"
#* * * * * curl localhost:5000/cron
@app.route('/cron')
def cron():
    # print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
    if alarmHour == int(datetime.datetime.today().strftime("%H")) and alarmMinute == int(datetime.datetime.today().strftime("%M")):
        return 'alarm right now ' + lights_on() + ' ' + ring()
    print('no alarm')
    return 'no alarm right now, next alarm is at {:02d}:{:02d}'.format(alarmHour, alarmMinute)

@app.route('/set_time')
def set_time():
    global alarmHour, alarmMinute
    hourStr = request.args.get('hour')
    minuteStr = request.args.get('minute')
    if hourStr is None:
        return 'alarm not set, invalid hour'
    if minuteStr is None:
        return 'alarm not set, invalid minute'
    
    alarmHour = int(hourStr)
    alarmMinute = int(minuteStr)

    return 'alarm time set to {:02d}:{:02d}'.format(alarmHour, alarmMinute)

busy = False

@app.route('/lights_on')
def lights_on():
    global busy
    if not busy:
        busy = True
        setAngle(servo, LIGHTS_ON_ANGLE)
        busy = False
        return 'lights on!'
    else:
        return 'busy, cannot turn on'

@app.route('/lights_off')
def lights_off():
    global busy
    if not busy:
        busy = True
        setAngle(servo, LIGHTS_OFF_ANGLE)
        busy = False
        return 'lights off!'
    else:
        return 'busy, cannot turn off'

if __name__ == "__main__":
    app.run(host='0.0.0.0')

