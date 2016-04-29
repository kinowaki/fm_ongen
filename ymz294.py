# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

dict_pin = {"WR":15, "CS":16, "A0":18, "RST":13, 
	    "D0":29, "D1":31, "D2":33, "D3":35,
	    "D4":36, "D5":37, "D6":38, "D7":40}
dict_port = {"D0":0b00000001,"D1":0b00000010,"D2":0b00000100,"D3":0b00001000,
	    "D4":0b00010000,"D5":0b00100000,"D6":0b01000000,"D7":0b10000000}

note_freq = [
	    8,9,9,10,10,11,12,12,13,14,15,15,
	    16,17,18,19,21,22,23,25,26,28,29,31,
	    33,35,37,39,41,44,46,49,52,55,58,62,
	    65,69,73,78,82,87,92,98,104,110,117,123,131,
	    131,139,147,156,165,175,185,196,208,220,233,247,
	    262,277,294,311,330,349,370,392,415,440,466,494,
	    523,554,587,622,659,698,740,784,831,880,932,988,
	    1047,1109,1175,1245,1319,1397,1480,1568,1661,1760,1865,1976,
	    2093,2217,2349,2489,2637,2794,2960,3136,3322,3520,3729,3951,
	    4186,4435,4699,4978,5274,5588,5920,6272,6645,7040,7459,7902,
	    8372,8870,9397,9956,10548,11175,11840,12543]

note_freq.reverse()   


def init():
    set_ctrl(0,0,0)
    set_port(0b11111111)
    set_port(0b00001111)
    time.sleep(0.1)
    GPIO.output(dict_pin["RST"],1)
    time.sleep(0.2)
    

def rst():
    GPIO.output(dict_pin["RST"],0)
    time.sleep(0.01)
    GPIO.output(dict_pin["RST"],1)
	    
def setup():
    GPIO.setmode(GPIO.BOARD)
    for pin in dict_pin.values():
	GPIO.setup(pin, GPIO.OUT)

def set_ctrl(wr, cs, a0):
    GPIO.output(dict_pin["WR"], wr)
    GPIO.output(dict_pin["CS"], cs)
    GPIO.output(dict_pin["A0"], a0)

def set_port(port_val):
    for key, val in dict_port.items():
	if (val & port_val)==val:
	    GPIO.output(dict_pin[key],1)
	else:
	    GPIO.output(dict_pin[key],0)

	#print key, val, (val & port_val), (val & port_val)==val
	
def set_resister(addr, val):
    #set address
    set_ctrl(0,0,0)
    set_port(addr)
    set_ctrl(1,1,1)
    #set data
    set_ctrl(0,0,1)
    set_port(val)
    set_ctrl(1,1,1)
    set_ctrl(0,0,0)

def set_freq(channel, freq):
    '''channel A:0,B:1,C:2'''
    if channel > 2:
	return

    set_resister(2*channel, freq & 0b11111111)
    set_resister(2*channel+1, (freq & 0b111100000000) >> 8)

def set_real_freq(channel, freq):
    freq = int(125000/freq) 
    set_freq(channel, freq)

def set_noise_freq(freq):
    set_resister(0x06, freq&0b11111)

def set_noise_real_freq(freq):
    freq = int(125000/freq)
    set_noise_freq(freq)

def set_pause(channel):
    set_freq(channel, 0)

def set_mixer(noisemsk, tonemsk):
    if (noisemsk > 0b111) or (tonemsk > 0b111):
	return

    set_resister(0x07, (noisemsk << 3) | tonemsk)	

def set_volume(env, channel, level):
    set_resister(0x08+channel, (env << 4) | (level & 0b1111))

def calc_freq_mml(octave, note, sharp):
    pos = 0
    if note == "C" or note == "c":
	pos = 0	
    elif note == "D" or note == "d":
	pos = 2
    elif note == "E" or note == "e":
	pos = 4
    elif note == "F" or note == "f":
	pos = 5
    elif note == "G" or note == "g":
	pos = 7
    elif note == "A" or note == "a":
	pos = 9
    elif note == "B" or note == "b":
	pos = 11
    
    return note_freq[octave*12+pos+sharp] 
    
def sound(channel, freq, length):
    set_freq(channel, freq)
    time.sleep(length/1000.0)
    set_pause(channel) 

def main():
    setup()
    
    GPIO.cleanup()

def sample_music():
    rst()
    set_mixer(0b111, 0b000)
    set_volume(0, 0, 0b00011111)
    set_freq(0, 0)
    set_volume(0, 1, 0b00011111)
    set_freq(1, 0)
    set_volume(0, 2, 0b00011111)
    set_freq(2, 0)
    set_noise_freq(0)
    time.sleep(0.3)

    length = 150
    for channel in range(3):

	for i in range(4, 8): 
	    sound(channel, calc_freq_mml(i, "C", 0), length)
	    sound(channel, calc_freq_mml(i, "D", 0), length)
	    sound(channel, calc_freq_mml(i, "E", 0), length)
	    sound(channel, calc_freq_mml(i, "G", 0), length)
	
	for i in range(7, 3, -1):
	    sound(channel, calc_freq_mml(i+1, "C", 0), length)
	    sound(channel, calc_freq_mml(i, "G", 0), length)
	    sound(channel, calc_freq_mml(i, "E", 0), length)
	    sound(channel, calc_freq_mml(i, "D", 0), length)
	
	for i in range(4, 8):
	    sound(channel, calc_freq_mml(i-1, "A", 0), length)
	    sound(channel, calc_freq_mml(i-1, "B", 0), length)
	    sound(channel, calc_freq_mml(i, "C", 0), length)
	    sound(channel, calc_freq_mml(i, "E", 0), length)
	
	for i in range(7, 3, -1):
	    sound(channel, calc_freq_mml(i, "A", 0), length)
	    sound(channel, calc_freq_mml(i, "E", 0), length)
	    sound(channel, calc_freq_mml(i, "C", 0), length)
	    sound(channel, calc_freq_mml(i-1, "B", 0), length)
	
def test():
    setup()
    set_port(0)
    set_port(0x0)
    set_port(1)


if __name__ == "__main__":
    setup()
    init()
    sample_music()
    GPIO.cleanup()
    
