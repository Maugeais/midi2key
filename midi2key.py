#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mido
import logging
import argparse
import configparser

import evdev 
from time import sleep

import sys

def message2code(msg):
    if msg.type == "control_change":
        return(f"cc-{msg.channel}-{msg.control}", msg.value)
    elif msg.type == "program_change" :
        return(f"pc-{msg.channel}-{msg.program}", 0)

    return("", 0)

def set_input(keymap, msg) :

    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            print("Add", message2code(msg), "=", evdev.ecodes.KEY[event.code])
            break


def midi2key(keymap, msg) :
    ui = evdev.UInput()

    code, value = message2code(msg)
    if code in keymap :
        print(keymap[code])
        ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[keymap[code]], 1)
        ui.write(evdev.ecodes.EV_SYN, 0, 0)
        sleep(0.01)
        ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[keymap[code]], 0)
        ui.write(evdev.ecodes.EV_SYN, 0, 0)
    else :
        print("Unknown", code)


def main_loop(config_object, callback) :

    keymap = {}
    
    # Open the MIDI objects for the nanKONTROL2 device
    inport = mido.open_input(config_object.get('inputs', "midi"))

    # Keymap to dictionnary
    for keyname in config_object.options('keymap') :
        keymap[keyname] = config_object.get('keymap', keyname)

    print(keymap)

    # Main loop
    for msg in inport:
       
        callback(keymap, msg)
       
if __name__ == "__main__" :

    # Parse command line args, of which we only care about one - debug mode
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--set_input', action='store_true', help='Set')
    parser.add_argument('-l', '--list-devices', action='store_true', help='List all PulseAudio devices')
    args = parser.parse_args()


    # It the user just wanted a list of PA devices, dump them and move on
    if args.list_devices:
        print("Output devices:")
        for n in mido.get_output_names() :
            print("   ", n)
        print("Input devices:")
        for n in mido.get_input_names() :
            print("   ", n)
        sys.exit(0)

    # Read config 
    config_object = configparser.ConfigParser()
    config_object.optionxform = str # Need case sensitivity

    config_object.read("~/.config/midi2key.ini")

    if args.set_input :
        dev = evdev.InputDevice(config_object.get('inputs', "keyboard"))
        print(dev)
        main_loop(config_object, set_input)

    ui = evdev.UInput()
    main_loop(config_object, midi2key)