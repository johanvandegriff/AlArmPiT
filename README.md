# AlArmPiT
**Al**arm with a servo **Arm** connected to a raspberry **Pi** that **T**urns on my lights, or **AlArmPiT** for short.

[DevPost Page](https://devpost.com/software/alarmpit) (part of the devpost page is copied below)

## Inspiration
I find that it is easier to wake up after turning on the lights, so why not have it happen automatically?

## What it does
It turns on the lights and sounds an alarm! From the web interface, you can set the time for the alarm, turn the lights on and off with a button, and test out the alarm sound.

For this hackathon, I also set it up so you can control it from a public page: https://wake-up-and.study/ It includes a live stream of the device so you can see the lights change. I will remove this after a day or so so i can get some sleep without random people flipping my light switch. :)

## How I built it
AlArmPiT runs on a Raspberry Pi which controls a servo with the GPIO library, and presents a web page with Python Flask that you can get to from your local network. I designed a mount for the servo to flip the light switch in FreeCAD (open source CAD program) and 3D printed it.

For the demo, I made a cloud VM on DigitalOcean and SSH tunneled the Pi's web server port to it http://wake-up-and.study:28400/ Then I installed apache and wrote a quick main page with some info and the livestream embed: https://wake-up-and.study/

## Challenges I ran into
The hardest part was getting the servo to align with the switch. First I tried using some plastic pieces, but it wasn't reliable enough, so I decided to 3D print a custom part. I measured the desired position of the servo with dial calipers and drew a diagram on paper, then transferred it to a FreeCAD design. Since I am not very experienced with CAD, this part was also tough but luckily after a few hours I had a part design I was happy with. And after printing it, the only thing wrong was the screw hole size, which I drilled out. Whew! A lot of hardware work for a software guy. XD

## Accomplishments that I'm proud of
I am proud of my reliable design for flipping the switch, where the servo pushes it partway down to turn it off, and releases it to turn it back on. A plastic piece keeps the switch from going past the center point and getting stuck off.

I'm also super proud of making a working alarm that I will actually use! I've needed this for a while and finally got around to it.

## What I learned
I learned how to use the FreeCAD open source CAD software.
I also learned how to control a servo with a raspberry pi using PWM. (I had done it earlier but completely forgot)

## What's next for AlArmPiT
I want to clean up the UI using Vue.js
I also want to add more alarm clock features such as support for multiple alarms, a different alarm each day, custom alarm sound, etc. Maybe I can find a library or existing app for this.
I want to make it accessible outside the home network in a secure way.

## Built With
3dprinting apache digitalocean flask javascript python raspberry-pi servo ssh

## Try it out
https://codeberg.org/johanvandegriff/AlArmPiT
https://alarmpit.johanv.xyz/
