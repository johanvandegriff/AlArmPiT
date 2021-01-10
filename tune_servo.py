import RPi.GPIO as GPIO
from time import sleep

PIN = 11 #GPIO 17

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.OUT)
pwm=GPIO.PWM(PIN, 50) #50Hz
pwm.start(0)


def setAngle(angle):
        duty = angle / 18 + 2
        GPIO.output(PIN, True)
        pwm.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(PIN, False)
        pwm.ChangeDutyCycle(0)

angle = 170
while angle > 0:
  angle = int(raw_input())
  setAngle(angle)


#sleep(.5)
#setAngle(15)

pwm.stop()
GPIO.cleanup()