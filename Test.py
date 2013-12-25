import cv2
import pdb
from cv2 import cv
import math
import random as rnd
import numpy as np
import autopy
import os
import subprocess
import time
import ImageGrab
import Image
import timeit
import pdb
import scipy as sp
from scipy import signal
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import sys

global Screen

def findSharks():
	bmp= ImageGrab.grab()
	#rage=np.array(bmp)
	#bmp.format='png'
	#plt.imshow(rage)
	bmp.save('rage.bmp')
	bmp.show()
	
def getWordsTest():#TODO
	'''Get the words from the screen. (This will be the hard part.)'''
	global Screen
	screen=Screen.copy()
	cnt=0
	cnt=cnt+1
	#screen.show()
	(width,height)=screen.size
	blobs=screen.convert('L')
	blobs=np.array(blobs)
	(x,blobs)=(cv2.threshold(blobs, 20, 255, cv2.THRESH_BINARY_INV))
	leftmost=0
	for y in range(width):
		if(blobs[:,y].any()):
			leftmost=y
			break
	return leftmost
	
def getWordsOld():#TODO
	'''Get the words from the screen. (This will be the hard part.)'''
	global Screen
	screen=Screen.copy()
	cnt=0
	cnt=cnt+1
	#screen.show()
	(width,height)=screen.size
	blobs=screen.convert('L')
	blobs=np.array(blobs)
	(x,blobs)=(cv2.threshold(blobs, 20, 255, cv2.THRESH_BINARY_INV))
	leftmost=0
	for y in range(width):
		for x in range(height):
			if(blobs[x,y]==255):#&(x==0 or y==0 or x>=height-1 or y>=width-1 or blobs[x-1,y]==255 or blobs[x+1,y]<20 or blobs[x,y-1]==255 or blobs[x,y+1]<20)):
				leftmost=y
				break
		if(leftmost!=0):
			break
	return leftmost
	
def matchIms():
	bmp=Image.open('C:/Copy/workspace/TyperSharkAI/Images/Play4.png').convert('L')
	shark=Image.open('basic_template.gif')
	shark.load()
	#shark.show()
	bmp=np.array(bmp)
	shark=np.array(shark)
	#Image.fromarray(shark).show()
	Image.fromarray(bmp).show()
	#bmp.show()
	print(bmp.shape)
	print(shark.shape)
	signal.correlate2d(shark,bmp)
	
def splitScreen(screen):
	#Split the screen into multiple parts, so we can have other methods focus on them.
	start=time.time()
	x=0
	y=0
	(width,height)=screen.size
	midscreen = screen.crop((100,25,width, height-75))#100, 25, width-100, height-75);
	altscreen = screen.crop((x,y,x+25,height))#x, y, 100, height);
	bottscreen = screen.crop((x,height-38,width,height))#x, height-50, width, 50);
	diverscreen = screen.crop((32,height/3+75,width/7-15,3*height/4-45))
	(mwidth,mheight)=midscreen.size
	centScreen=midscreen.crop((width/2-125,height/2-50,width/2-100,height/2-10))
	screens=[screen,altscreen,bottscreen,midscreen,diverscreen,centScreen]
	return screens
	
def teethFinder():
	bmp=Image.open('C:/Copy/workspace/TyperSharkAI/Images/Play4.png')
	bmp=splitScreen(bmp)[3]
	(width,height)=bmp.size
	bmp=np.array(bmp)
	blobs=np.zeros((height,width),dtype=np.uint8)
	for y in range(width-1):
		for x in range(height-1):
			#print(type(screen[x,y]))
			s=sum(bmp[x,y])
			if(s<60):
				blobs[x,y]=1
	return blobs

def teethFinder2():
	bmp=Image.open('C:/Copy/workspace/TyperSharkAI/Images/Play4.png')
	bmp=splitScreen(bmp)[3]
	(width,height)=bmp.size
	bmp=np.array(bmp)
	blobs=bmp[:,:,0]
	leftmost=0
	for y in range(width):
		for x in range(height):
			if(blobs[x,y]<20):
				blobs[x,y]=255
				if leftmost==0:
					leftmost=y
			else:
				blobs[x,y]=0
	blobs=blobs[:,(20+leftmost):]
	Image.fromarray(blobs).save('wordsDetected.png')
	return blobs

def getTargets(screen):#TODO
	'''Get the words from the screen. (This will be the hard part.)'''
	(width,height)=screen.size
	#screen.save('screen'+str(cnt)+'.png')
	blobs=screen.convert('L')
	blobs=np.array(blobs)
	#blobs=screen.
	leftmost=0
	targets=[]
	for y in range(width):
		for x in range(height):
			if(blobs[x,y]<20):
				print(x,y)
				if(y+200<=width):
					targets.append(np.copy(blobs[x-20:x+20,y:y+200]))
				blobs[x-30:x+30,y:y+200]=255
				#Image.fromarray(blobs).show()
				#raw_input('')
				if leftmost==0:
					leftmost=y
	cnt=0
	for target in targets:
		Image.fromarray(target).save('target'+str(cnt)+'.png')
		cnt=cnt+1
	return targets
	'''words=[]
	if(leftmost+80<=width):
		blobs=blobs[:,(20+leftmost):]
		#print(type(blobs))
		Image.fromarray(blobs).save('wordsDetected'+str(cnt)+'.png')
		os.system('tesseract wordsDetected'+str(cnt)+'.png results'+str(cnt)+' nobatch letters.txt')
	#	lines=open('results'+str(cnt)+'.txt').readlines()
	#	#Pass wordsDetected to tesseract and parse output.
	#	words = [line.strip() for line in lines]
	#	print(len(words))
	#return words
	'''
def determineDead():
	bmp=Image.open('C:/Copy/workspace/TyperSharkAI/Images/Play4.png')
	screens=splitScreen(bmp)
	print(determineDeadHelper(screens[4]))

def determineDeadHelper():#diver):
	global Diver
	(width,height)=Diver.size
	diver=np.array(Diver)
	pixel1=[220, 170, 0]
	pixel2=[260, 210, 20]
	cnt=0
	#equals=[[(pixel1<=pixels).all()&(pixels<=pixel2).all() for pixels in row] for row in diver]
	for y in range(width):
		for x in range(height):
			pixels=diver[x,y]
			if((pixel1<=pixels).all()&(pixels<=pixel2).all()):
				cnt=cnt+1
	return cnt>650
	
def inThreshold(pixel,lowbound,upbound):
	return (lowbound<=pixel).all()&(pixel<=upbound).all()

def determineDeadHelperNew():#diver):
	global Diver
	(width,height)=Diver.size
	diver=np.array(Diver)
	pixel1=[220, 170, 0]
	pixel2=[260, 210, 20]
	cnt=0
	equals=[[(pixel1<=pixels).all()&(pixels<=pixel2).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	return sumz>650

def determineNotFighting(centscreen):
	#start=time.time()
	lowbound=[8, 32, 165]
	upbound=[12, 45, 220]
	diver=np.array(centscreen)
	equals=[[(lowbound<=pixels).all()&(pixels<=upbound).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	#print('time taken is:'+str(time.time()-start))
	return sumz>250

def preparingToDive(midscreen):
	start=time.time()
	(width,height)=midscreen.size
	lowbound=[175, 115, 70]
	upbound=[240, 150, 110]
	diver=np.array(midscreen)
	equals=[[(lowbound<=pixels).all()&(pixels<=upbound).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	print('time taken is:'+str(time.time()-start))
	return sumz>300

	
Screen=splitScreen(Image.open('C:/Copy/George Mason Classes/2013 3Winter/Typer Shark AIwc/Typer Shark AI/trunk/Play0.png'))[3]
print(timeit.timeit(getWordsTest,number=10))
print(timeit.timeit(getWordsOld,number=10))
assert(getWordsTest()==getWordsOld())