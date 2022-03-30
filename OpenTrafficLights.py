#!/usr/bin/env python3
import FakeGPIO as GPIO
# import RPi.GPIO as GPIO
import platform, time, threading, argparse


VERSION = "0.0.1"
parser = argparse.ArgumentParser(description="Commandline arguments for OpenTrafficLights")
parser.add_argument('-v', "--version", action='store_true',
                    help='Show the current app version and exit.')
parser.add_argument("--dev-mode", action='store_true',
                    help='Ignore checking for dependencies.')

# Parse them all!
args = parser.parse_args()
# Handle arguments before start.
if args.version: # Show version and exit.
    print("OpenTrafficLights v" + VERSION)
    exit(0)
try:
    if platform.system() != "Linux":
        if args.dev_mode:
            print("[INFO] Running in dev mode on non-linux (raspberry pi) system.")
            try:
                if GPIO.FAKE: print("[INFO] FakeGPIO library is loaded.")
            except AttributeError:
                print("[INFO] To simulate the GPIO, use the FakeGPIO library.")
        else:
            print("""
[WARNING] You're using this program on a non-Linux/Raspberry Pi machine.\n
To disable this warning, use the --dev-mode argument. Example: python3 OpenTrafficLights.py --dev-mode\n
For testing purposes, you can use the FakeGPIO library. Otherwise the script won't function as intended.\n
            """)
            input("Press Enter to continue...")
except KeyboardInterrupt:
    print("\n[INFO] Exiting...")
    exit(0)
print(f"""
   ____                 ______           _________      __    _       __    __      
  / __ \____  ___  ____/_  __/________ _/ __/ __(_)____/ /   (_)___ _/ /_  / /______
 / / / / __ \/ _ \/ __ \/ / / ___/ __ `/ /_/ /_/ / ___/ /   / / __ `/ __ \/ __/ ___/
/ /_/ / /_/ /  __/ / / / / / /  / /_/ / __/ __/ / /__/ /___/ / /_/ / / / / /_(__  ) 
\____/ .___/\___/_/ /_/_/ /_/   \__,_/_/ /_/ /_/\___/_____/_/\__, /_/ /_/\__/____/  
    /_/                                                     /____/                  

                                      v{VERSION}
                                  -=By LP & PM=-
                                -=Made For TEJ4M=-
=====================================================================================
""")

# The ACTUAL driver code begins here.
# Right now, it's only an example.

print(GPIO.BOARD)
print(GPIO.getmode())
GPIO.setmode(GPIO.BOARD)
print(GPIO.getmode())
GPIO.input(1)
GPIO.cleanup()