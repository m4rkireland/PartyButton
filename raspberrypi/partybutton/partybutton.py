#!/usr/bin/env python
#
# Command Line usage:
#   partybutton.py


#Enable this for Visual Studio debugging
#import ptvsd
#ptvsd.enable_attach('party')

import RPi.GPIO as GPIO
import time
import sys
import pygame
from requests import get
import subprocess

# 00 - Tree GPIO21 pin_map[0]
# 01 - Fire GPIO10 pin_map[1]
# 02 - Ceiling GPIO26 pin_map[2]
# 03 - Laser GPIO19 pin_map[3]
# 04 - Strobe GPIO12 pin_map[4]
# 05 - Disco GPIO13 pin_map[5]
# 06 - 
# 07 - Smoke GPIO06 pin_map[7]
#
#
#
# Sign HTTP pi_sign[message] 192.168.1.224
#                            off, siren, finalcountdown
#
# TV HTTP tv
# WeMo HTTP WeMo
intro = True
installPath = "/home/pi/nye/partybutton"
signIP = "http://192.168.1.224/"

# Defines the mapping of the GPIO1-8 to the pin on the Pi
pin_map = [21,20,26,16,19,13,12,6]

# Setup the board
def initialiseGPIO():
    try:
        GPIO.setmode(GPIO.BCM)
        for i in range(8):
            GPIO.setup(pin_map[i], GPIO.OUT)
            if (i <= 2):
                #don't do anything to the Normally Open (NO) relays
                GPIO.output(pin_map[i],GPIO.LOW)
            else:
                GPIO.output(pin_map[i],GPIO.HIGH)
    except Exception as e: 
        print("initialiseGPIO: ")
        print(e)

def turnOffAllRelays():
    try:
        # Turn off all relays
        for i in range(3):
            #not the smoke relay
            GPIO.output(pin_map[i],GPIO.LOW)
    except Exception as e:
        print("turnOffAllRelays: ")
        print(e)
            
def changeSign(sign):
    try:
        s = get(signIP + sign)
    except Exception as e: 
        print("changeSign:" + sign + ": ")
        print(e)

def diningRelay(relay, mode):
    try:
        d = get(diningIP + relay + "?mode=" + mode)
    except Exception as e:
        print("diningRelay: ")
        print(e)

def servoMove(pos):
    try:
        g = get(servoIP + pos)
    except Exception as e:
        print("servoMove: ")
        print(e)

def turnOffTV():
    # Turn off TV
    # Run tv script without waiting for it to complete
    try:
        p = subprocess.Popen([sys.executable, installPath + '/tv.py', 'KEY_POWEROFF'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        print("turnOffTV: ")
        print(e)

def toggleWeMo(status):
    try:
        s = subprocess.Popen(['wemo', 'switch', 'lights', status])
    except Exception as e: 
        print("toggleWeMo:" + status + ": ")
        print(e)

def playSiren():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(installPath + '/music/siren.mp3')
        pygame.mixer.music.play()
    except Exception as e: 
        print("playSiren: ")
        print(e)

def flashFire():
    try:
        for i in range(7):
            GPIO.output(pin_map[2], GPIO.HIGH)
            time.sleep(0.6)
            GPIO.output(pin_map[2], GPIO.LOW)
            time.sleep(0.5)
    except Exception as e:
        print("flashFire: ")
        print(e)


if __name__ == '__main__':
    try:
        initialiseGPIO()
        if (intro):
            # Turn off WeMo
            toggleWeMo("off")

            #Turn off TV
            turnOffTV()
            # Start the siren
            playSiren()
            flashFire()
            #Wait 2 seconds for suspense to build
            time.sleep(2)

        # Open the input sequence file and read/parse it
        with open(installPath + "/finalcountdown.txt",'r') as f:
          seq_data = f.readlines()
          for i in range(len(seq_data)):
            seq_data[i] = seq_data[i].rstrip()
    
        # Load and play the music
        pygame.mixer.init()
        pygame.mixer.music.load(installPath + "/music/finalcountdown.mp3")
        pygame.mixer.music.play()

        # Start
        start_time = int(round(time.time() * 1000))
        step = 1 
        while True :
          next_step = seq_data[step].split(",")
          next_step[1] = next_step[1].rstrip().lstrip()
          cur_time = int(round(time.time() * 1000)) - start_time

          # time to run the command
          if int(next_step[0]) <= cur_time:

            print(next_step)
            # if the command is 0-2 (NC relays)
            if next_step[1] >= "0" and next_step[1] <= "2":
              if next_step[2] == "1":
                GPIO.output(pin_map[int(next_step[1])],GPIO.HIGH)
              else:
                GPIO.output(pin_map[int(next_step[1])],GPIO.LOW)
            
            # if the command is 3-7 (NO relays)
            if next_step[1] >= "3" and next_step[1] <= "7":
                if next_step[2] == "1":
                    GPIO.output(pin_map[int(next_step[1])],GPIO.LOW)
                else:
                    GPIO.output(pin_map[int(next_step[1])],GPIO.HIGH)



            # if the END command 
            if next_step[1].rstrip() == "END":
                toggleWeMo("on")

                #All back to default positions
                for i in range(8):
                    GPIO.output(pin_map[i],GPIO.HIGH)

                break

            step += 1
          

    except Exception as e: print(e)
    finally:
        toggleWeMo("on")
        GPIO.cleanup()
