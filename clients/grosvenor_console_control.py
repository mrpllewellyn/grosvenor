#!/usr/bin/python

import smbus
import sys, tty, termios, time, os
import struct

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

address = 0x04

initial_command = [1, 0, 1, 0]
initial_inputarray = [0, 0, 0, 0, 0, 0]
inputarray = bytearray(initial_inputarray)
cmd_bytearray = bytearray(initial_command)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def writeNumber(value):
	bus.write_byte(address, int(value))
	return -1
	
def readValues():
	inputarray = bus.read_i2c_block_data(address, 0)
	return inputarray

def sendCommand():
	writeNumber(cmd_bytearray[0])		
	writeNumber(cmd_bytearray[1])		
	writeNumber(cmd_bytearray[2])		
	writeNumber(cmd_bytearray[3])
	print(cmd_bytearray[0])
	print(cmd_bytearray[1])
	print(cmd_bytearray[2])
	print(cmd_bytearray[3])

print("w/s: speed")
print("a/d: steering")
print("x: reset")
print("z: quit")
leftspeed = 0
rightspeed = 0
leftmode = 2
rightmode = 2
speed = 0
steer = 0
brake = 0
direction = 1
quitnow = 0

volts = 0
leftamps = 0 
rightamps = 0

while True:
	
# sleep one second
#	time.sleep(5)
	try:
		char = getch()
 
		if(char == "z"):
			print("quit")
			quitnow = 1
		if(char == "w"):
			if speed < 251:
				speed = speed + 5

		if(char == "a"):
			steer = steer - 5

		if(char == "s"):
			if speed > 4:
				speed = speed - 5

		if(char == "d"):
			steer = steer + 5
		if(char == "b"):
			brake = not brake
		if(char == "r"):
			direction = not direction
		if(char == "x"):
			speed = 0
			steer = 0

		char = ""
		os.system('clear')
		print('speed (w/s): %d' % speed)
		print('steer (a/d): %d' % steer)
		print('direction: %d' % direction)
		print('brake: %d' % brake)
		print('Reset(x)/Quit(z)')

		leftspeed = speed + steer
		if leftspeed > 255:
			leftspeed = 255
		elif leftspeed < 0:
			leftspeed = 0
		rightspeed = speed - steer
		if rightspeed > 255:
			rightspeed = 255
		elif rightspeed < 0:
			rightspeed = 0
		
		print(leftspeed)
		print(rightspeed)
		
		if(brake == 1):
			leftmode = 1
			rightmode = 1
		else:
			if(direction == 1):
				leftmode = 2
				rightmode = 2
			else:
				leftmode = 0
				rightmode = 0
		cmd_bytearray[0] = leftmode
		cmd_bytearray[1] = leftspeed
		cmd_bytearray[2] = rightmode
		cmd_bytearray[3] = rightspeed
	except ValueError:
		print("OOR!")
	if(quitnow == 1):
		break
	sendCommand()
	inputarray = readValues()
	volts = inputarray[0] | inputarray[1]<<8
	leftamps = inputarray[2] | inputarray[3]<<8
	rightamps = inputarray[4] | inputarray[5]<<8
	print("Left motors current draw:")
	print(leftamps)
	print("Left motors current draw:")
	print(rightamps)
	print("Battery voltage:")	
	print(volts)

