from flask import Flask, escape, request, render_template
import RPi.GPIO as GPIO
import time
import datetime
import os

app = Flask(__name__)

ALARM_SOUND_FILE_WAV = '/home/pi/AlArmPiT/airhorn.wav'

#https://pinout.xyz/
RELAY_BOARD_PIN = 13 # GPIO 27
BUTTON_BOARD_PIN = 38 #GPIO 20
SERVO_BOARD_PIN = 11 #GPIO 17
LIGHTS_OFF_ANGLE = 125
LIGHTS_ON_ANGLE = 170

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY_BOARD_PIN, GPIO.OUT)

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
lightsOn = True
relayOn = False

def relay(value):
    global relayOn
    relayOn = value
    GPIO.output(RELAY_BOARD_PIN, value)


@app.route('/relay_on')
def relay_on():
    relay(True)
    return 'relay on!'

@app.route('/relay_off')
def relay_off():
    relay(False)
    return 'relay off!'

@app.route('/relay_toggle')
def relay_toggle():
    relay(not relayOn)
    if relayOn:
        return 'relay on! (toggled)'
    else:
        return 'relay off! (toggled)'

@app.route('/lights_on')
def lights_on():
    global busy, lightsOn
    if not busy:
        busy = True
        setAngle(servo, LIGHTS_ON_ANGLE)
        lightsOn = True
        busy = False
        return 'lights on!'
    else:
        return 'busy, cannot turn on'

@app.route('/lights_off')
def lights_off():
    global busy, lightsOn
    if not busy:
        busy = True
        setAngle(servo, LIGHTS_OFF_ANGLE)
        lightsOn = False
        busy = False
        return 'lights off!'
    else:
        return 'busy, cannot turn off'

@app.route('/lights_toggle')
def lights_toggle():
    global busy, lightsOn
    if not busy:
        if lightsOn:
            if not "busy" in lights_off():
                lightsOn = False
                return 'lights off! (toggled)'
        else:
            if not "busy" in lights_on():
                lightsOn = True
                return 'lights on! (toggled)'
    return 'busy, cannot toggle'

def button_callback(_):
    lights_toggle()

GPIO.setup(BUTTON_BOARD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_BOARD_PIN, GPIO.RISING, bouncetime=1000)
GPIO.add_event_callback(BUTTON_BOARD_PIN, button_callback)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

