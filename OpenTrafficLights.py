#!/usr/bin/env python3
try:
    from gpiozero import LED
except ImportError:
    print("[ERROR] gpiozero is not installed. Please install it first.")
import platform, time, multiprocessing, argparse, os, subprocess, getpass, signal, random, serial
from subprocess import Popen, PIPE, STDOUT
# =====================================================================================
PARALLEL = "parallel"
PERPENDICULAR = "perpendicular"
SECRET = "secret"
GREEN = "green"
YELLOW = "yellow"
RED = "red"
PEDESTRIAN_GO = "pedestrian_go"
PEDESTRIAN_STOP = "pedestrian_stop"
GREEN_RELAY_PIN = LED(4)
YELLOW_RELAY_PIN = LED(17)
RED_RELAY_PIN = LED(27)
PED_GO_RELAY_PIN = LED(22)
PED_STOP_RELAY_PIN = LED(23)
STATUS_LED_PIN = LED(18)
# =====================================================================================
channels = [GREEN_RELAY_PIN, YELLOW_RELAY_PIN, RED_RELAY_PIN, PED_GO_RELAY_PIN, PED_STOP_RELAY_PIN, STATUS_LED_PIN]


def reset_lights():
    GREEN_RELAY_PIN.on()
    YELLOW_RELAY_PIN.on()
    RED_RELAY_PIN.on()
    PED_GO_RELAY_PIN.on()
    PED_STOP_RELAY_PIN.on()
    print("[INFO] Lights Reset!")


def flashing_light(color, duration):
    print("[INFO] Flashing " + str(color) + " light for " + str(duration) + " seconds.")
    for i in range(duration):
        color.off()
        time.sleep(0.5)
        color.on()
        time.sleep(0.5)
        print("[INFO] Flashing!")


def manage_traffic_lights(mode):
    if mode == PARALLEL:
        reset_lights()
        while True:
            GREEN_RELAY_PIN.off()
            PED_GO_RELAY_PIN.off()
            time.sleep(10)
            PED_GO_RELAY_PIN.on()
            flashing_light(PED_STOP_RELAY_PIN, 5)
            PED_STOP_RELAY_PIN.off()
            GREEN_RELAY_PIN.on()
            YELLOW_RELAY_PIN.off()
            time.sleep(3)
            YELLOW_RELAY_PIN.on()
            RED_RELAY_PIN.off()
            time.sleep(15)
            RED_RELAY_PIN.on()
            PED_STOP_RELAY_PIN.on()
    elif mode == PERPENDICULAR:
        reset_lights()
        while True:
            GREEN_RELAY_PIN.off()
            PED_STOP_RELAY_PIN.off()
            time.sleep(15)
            GREEN_RELAY_PIN.on()
            YELLOW_RELAY_PIN.off()
            time.sleep(3)
            YELLOW_RELAY_PIN.on()
            RED_RELAY_PIN.off()
            PED_GO_RELAY_PIN.off()
            time.sleep(10)
            PED_GO_RELAY_PIN.on()
            flashing_light(PED_STOP_RELAY_PIN, 5)
            PED_STOP_RELAY_PIN.off()
            RED_RELAY_PIN.on()
    elif mode == SECRET:  # Make the lights randomly flash and dance quickly
        reset_lights()
        while True:
            GREEN_RELAY_PIN.off()
            PED_STOP_RELAY_PIN.on()
            time.sleep(0.5)
            GREEN_RELAY_PIN.on()
            YELLOW_RELAY_PIN.off()
            time.sleep(0.5)
            YELLOW_RELAY_PIN.on()
            RED_RELAY_PIN.off()
            PED_GO_RELAY_PIN.off()
            time.sleep(0.5)
            PED_GO_RELAY_PIN.on()
            flashing_light(PED_STOP_RELAY_PIN, 5)
            PED_STOP_RELAY_PIN.off()
            RED_RELAY_PIN.on()
            GREEN_RELAY_PIN.off()
            time.sleep(0.5)
            GREEN_RELAY_PIN.on()
            YELLOW_RELAY_PIN.off()
            time.sleep(0.5)
            YELLOW_RELAY_PIN.on()
            RED_RELAY_PIN.off()
            PED_GO_RELAY_PIN.off()
            time.sleep(0.5)
            PED_GO_RELAY_PIN.on()
            flashing_light(PED_STOP_RELAY_PIN, 5)
            PED_STOP_RELAY_PIN.off()
            RED_RELAY_PIN.on()
    elif mode == GREEN:
        reset_lights()
        GREEN_RELAY_PIN.off()
    elif mode == YELLOW:
        reset_lights()
        YELLOW_RELAY_PIN.off()
    elif mode == RED:
        reset_lights()
        RED_RELAY_PIN.off()
    elif mode == PEDESTRIAN_GO:
        reset_lights()
        PED_GO_RELAY_PIN.off()
    elif mode == PEDESTRIAN_STOP:
        reset_lights()
        PED_STOP_RELAY_PIN.off()
    else:
        print("[ERROR] Invalid Mode!")


if __name__ == '__main__':
    VERSION = "0.0.1"
    parser = argparse.ArgumentParser(description="Commandline arguments for OpenTrafficLights")
    parser.add_argument('-v', "--version", action='store_true',
                        help='Show the current app version and exit.')
    parser.add_argument("--dev-mode", action='store_true',
                        help='Enable the developer mode to skip the warnings.')
    parser.add_argument("--record-serial", action='store_true',
                        help='Find the correct serial port.')

    # Parse them all!
    args = parser.parse_args()


    def new_serial_port(old, new):
        for old, new in zip(old, new):
            if old != new:
                return new


    # Handle arguments before start.
    if args.version:  # Show version and exit.
        print("OpenTrafficLights v" + VERSION)
        exit(0)
    try:
        if True:
            if args.dev_mode and platform.system() != "Linux":
                print("[INFO] Running in dev mode on non-linux (raspberry pi) system.")
                try:
                    if GPIO.FAKE: print("[INFO] FakeGPIO library is loaded.")
                except AttributeError:
                    print("[INFO] To simulate the GPIO, use the FakeGPIO library.")
            elif not args.dev_mode and platform.system() != "Linux":
                print("""
    [WARNING] You're using this program on a non-Linux/Raspberry Pi machine.\n
    To disable this warning, use the --dev-mode argument. Example: python3 OpenTrafficLights.py --dev-mode\n
    For testing purposes, you can use the FakeGPIO library. Otherwise the script won't function as intended.\n
                    """)
                input("Press Enter to continue...")
            serial_port = ""
            if args.record_serial or not os.path.exists("OpenTrafficLights.conf"):
                print("[INFO] Serial Port Detection Sequence Activated...")
                if os.path.exists("OpenTrafficLights.conf") and args.record_serial:
                    print("[INFO] Overwriting OpenTrafficLights.conf...")
                elif os.path.exists("OpenTrafficLights.conf"):
                    print("[INFO] Found OpenTrafficLights configuration file. Skipping serial port detection.")
                else:
                    print("[INFO] No OpenTrafficLights configuration file found. Creating one...")
                    input("[INFO] Please DISCONNECT the Arduino from the USB port and press Enter.\n")
                    process = subprocess.Popen("ls /dev/tty*", stdout=subprocess.PIPE, shell=True)
                    output, error = process.communicate()
                    no_arduino = output.decode("utf-8")
                    input("[INFO] Please CONNECT the Arduino to the USB port and press Enter.")
                    process = subprocess.Popen("ls /dev/tty*", stdout=subprocess.PIPE, shell=True)
                    output, error = process.communicate()
                    with_arduino = output.decode("utf-8")
                    print("[INFO] Comparing outputs...")
                    print("[INFO] No Arduino: " + no_arduino)
                    print("[INFO] With Arduino: " + with_arduino)
                    try:
                        serial_port = new_serial_port(no_arduino.split("\n"), with_arduino.split("\n"))
                        print("[INFO] Detected serial port: " + serial_port)
                        if serial_port == "": print(
                            "[ERROR] Could not find the serial port. Please try again. Hint: Try a different USB port.")
                    except:
                        print(
                            "[ERROR] An Unknown Error Occured. Check that you have permission to use the command 'ls /dev/tty*'.")
                        exit(1)
                    with open("OpenTrafficLights.conf", "w") as f:
                        f.write("serial_port=" + serial_port)
                        f.close()
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        try:
            os.killpg(os.getpgid(process.pid),
                      signal.SIGTERM)  # Send the signal to all the process groups and kills them.
        except NameError:
            pass
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
    try:
        # The ACTUAL driver code begins here.
        # Right now, it's only an example.
        def turn_off():
            for pin in channels:
                pin.on()


        def handle_ir_sensor():
            try:
                arduino_serial = serial.Serial(get_serial_port(), 9600, timeout=1)
                arduino_serial.reset_input_buffer()
            except serial.serialutil.SerialException:
                print(f"""[ERROR] Could not open the serial port. Make sure that you are part of the dialout group.\n
    You can become a member by executing: sudo adduser {getpass.getuser()} dialout\n
    OR you can let the script do it for you if you have access to the root password.\n
    OR you can manually specify the serial port in the OpenTrafficLights.conf file and restart the program.\n""")
                if input("Add you to the group? (y/n) -> ").lower() in ["y", "yes"]:
                    add_user_to_dialout = Popen([f"sudo adduser {getpass.getuser()} dialout"], stdout=PIPE, stdin=PIPE,
                                                stderr=PIPE)
                    stdout_data = add_user_to_dialout.communicate(input=getpass.getpass(prompt='Root Password: '))[0]
                    print(stdout_data.decode("utf-8"))
                else:
                    exit(1)

            power = False
            while True:
                try:
                    if arduino_serial.in_waiting > 0:
                        recieved = arduino_serial.readline().decode('utf-8').rstrip()
                        print("[INFO] Serial Input: " + recieved)
                        if recieved == "OK" and power == False:
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(PARALLEL,))
                            power = True
                            traffic_process.start()
                            print("[INFO] Power On!")
                        elif recieved == "OK" and power == True:
                            power = False
                            turn_off()
                            traffic_process.terminate()
                            print("[INFO] Power Off!")
                        elif recieved == "1":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(PARALLEL,))
                            traffic_process.start()
                            print("[INFO] Parallel Lights!")
                        elif recieved == "2":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights,
                                                                      args=(PERPENDICULAR,))
                            traffic_process.start()
                            print("[INFO] Perpendicular Lights!")
                        elif recieved == "3":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(SECRET,))
                            traffic_process.start()
                            print("[INFO] Secret Lights!")
                        # No More Automatic Traffic Lights After This Line
                        elif recieved == "4":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(GREEN,))
                            traffic_process.start()
                            print("[INFO] Green Lights!")
                        elif recieved == "5":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(YELLOW,))
                            traffic_process.start()
                            print("[INFO] Yellow Lights!")
                        elif recieved == "6":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights, args=(RED,))
                            traffic_process.start()
                            print("[INFO] Red Lights!")
                        elif recieved == "7":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights,
                                                                      args=(PEDESTRIAN_GO,))
                            traffic_process.start()
                            print("[INFO] Pedestrian Go!")
                        elif recieved == "8":
                            if traffic_process.is_alive():
                                traffic_process.terminate()
                            power = True
                            traffic_process = multiprocessing.Process(target=manage_traffic_lights,
                                                                      args=(PEDESTRIAN_STOP,))
                            traffic_process.start()
                            print("[INFO] Pedestrian Stop!")
                        # Reset Everything...
                        elif recieved == "ZERO" and power == True:
                            traffic_process.terminate(), turn_off(), traffic_process.start()
                        elif recieved == "PAWN":
                            print("Pawning...")
                            power = False
                            turn_off()
                            try:
                                traffic_process.terminate()
                                for p in multiprocessing.active_children():
                                    print("[INFO] Terminating " + str(p))
                                    os.killpg(os.getpgid(p.pid),
                                              signal.SIGTERM)  # Send the signal to all the process groups and kills them.
                                    p.terminate()
                            except NameError:
                                pass

                except KeyboardInterrupt:
                    print("\n[INFO] Powering off...")
                    arduino_serial.close()
                    turn_off()
                    exit(0)


        def get_serial_port():
            with open("OpenTrafficLights.conf") as config:
                print("[INFO] Reading Config File...")
                port = config.readline().split("=")
                # Read the config file and split from the equal sign.
                print("Read Serial Port: " + port[1])
                return port[1]


        turn_off()
        STATUS_LED_PIN.on()
        print("Ready!")
        turn_off()
        handle_ir_sensor()

    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        turn_off()
        try:
            for p in multiprocessing.active_children():
                print("[INFO] Terminating " + str(p))
                os.killpg(os.getpgid(p.pid),
                          signal.SIGTERM)  # Send the signal to all the process groups and kills them.
                p.terminate()
        except NameError:
            pass
        exit(0)
