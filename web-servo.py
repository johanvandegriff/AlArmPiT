from flask import Flask, escape, request, render_template
import RPi.GPIO as GPIO
import time
import datetime
import os
import json

app = Flask(__name__)

ALARM_SOUND_FILE_WAV = '/home/pi/AlArmPiT/airhorn.wav'
SETTINGS_FILE = '/home/pi/AlArmPiT/settings.json'


class SettingsFile:
    def __init__(self, file):
        self.file = file
        if os.path.exists(self.file):
            self._read_file()
        else:
            self.data = {}
        defaults = {
            "alarmHour": 0,
            "alarmMinute": 0,
            "lightsOn": True,
            "relayOn": False
        }
        changed = False
        for k in defaults:
            if k not in self.data:
                self.data[k] = defaults[k]
                changed = True
        if changed:
            self._write_file()

    def getAlarmHour(self):
        return self.data["alarmHour"]

    def getAlarmMinute(self):
        return self.data["alarmMinute"]

    def getLightsOn(self):
        return self.data["lightsOn"]

    def getRelayOn(self):
        return self.data["relayOn"]

    def setAlarmHour(self, alarmHour):
        self.data["alarmHour"] = alarmHour
        self._write_file()

    def setAlarmMinute(self, alarmMinute):
        self.data["alarmMinute"] = alarmMinute
        self._write_file()

    def setLightsOn(self, lightsOn):
        self.data["lightsOn"] = lightsOn
        self._write_file()

    def setRelayOn(self, relayOn):
        self.data["relayOn"] = relayOn
        self._write_file()

    def _write_file(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)

    def _read_file(self):
        with open(self.file, 'r') as f:
            self.data = json.load(f)

settingsFile = SettingsFile(SETTINGS_FILE)

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

#add to crontab -e"
#* * * * * curl localhost:5000/cron
@app.route('/cron')
def cron():
    alarmHour, alarmMinute = settingsFile.getAlarmHour(), settingsFile.getAlarmMinute()
    # print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
    if alarmHour == int(datetime.datetime.today().strftime("%H")) and alarmMinute == int(datetime.datetime.today().strftime("%M")):
        res = 'alarm right now ' + lights_on() + ' ' + ring()
    else:
        res = 'no alarm right now, next alarm is at ' + get_time()
    print(res)
    return res

@app.route('/set_time')
def set_time():
    hourStr = request.args.get('hour')
    minuteStr = request.args.get('minute')
    if hourStr is None:
        return 'alarm not set, invalid hour'
    if minuteStr is None:
        return 'alarm not set, invalid minute'
    
    settingsFile.setAlarmHour(int(hourStr))
    settingsFile.setAlarmMinute(int(minuteStr))

    return 'alarm time set to ' + get_time()

@app.route('/get_time')
def get_time():
    return '{:02d}:{:02d}'.format(settingsFile.getAlarmHour(), settingsFile.getAlarmMinute())

busy = False

def relay(value):
    settingsFile.setRelayOn(value)
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
    relay(not settingsFile.getRelayOn())
    if settingsFile.getRelayOn():
        return 'relay on! (toggled)'
    else:
        return 'relay off! (toggled)'

@app.route('/lights_on')
def lights_on():
    global busy
    if not busy:
        busy = True
        setAngle(servo, LIGHTS_ON_ANGLE)
        settingsFile.setLightsOn(True)
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
        settingsFile.setLightsOn(False)
        busy = False
        return 'lights off!'
    else:
        return 'busy, cannot turn off'

@app.route('/lights_toggle')
def lights_toggle():
    global busy
    if not busy:
        if settingsFile.getLightsOn():
            if not "busy" in lights_off():
                settingsFile.setLightsOn(False)
                return 'lights off! (toggled)'
        else:
            if not "busy" in lights_on():
                settingsFile.setLightsOn(True)
                return 'lights on! (toggled)'
    return 'busy, cannot toggle'

def button_callback(_):
    lights_toggle()

GPIO.setup(BUTTON_BOARD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_BOARD_PIN, GPIO.RISING, bouncetime=1000)
GPIO.add_event_callback(BUTTON_BOARD_PIN, button_callback)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

