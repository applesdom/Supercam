#!/bin/python3

from device import *

def main():
    for device in poll_devices():
        print(device)

if __name__ == '__main__':
    main()
