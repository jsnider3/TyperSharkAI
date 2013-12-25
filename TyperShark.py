import autopy
import cv2
from cv2 import cv
import ImageGrab
import Image
import math
import numpy as np
import os
import pdb
import random as rnd
import scipy as sp
from scipy import signal
import subprocess
import sys
import thread
import time

#BUGS
#Ignore shark corpses in OCR
#Detect if we've made a misspelling.
#Determine which shark we're fighting and concentrate on it if we misspell something.
#Don't fight sharks that aren't fully on the screen even if some are.

#Resolved
#Don't start fighting until sharks are fully on the screen. (12/20 12:38 AM)
#Determine that we're not fighting when our character isn't in the correct spot (12/20 2:53 PM)
#Determine that we're not fighting when PREPARE TO DIVE is on screen. (12/20 4:49 PM)

cnt=0
class Word:
	def __init__(self,str):
		self.text=str
		self.type=None
		self.x=0
		self.y=0

class Game:
	def __init__(self):
		self.score=0
		self.status="NOT_PLAYING"
		self.normSpeed=85
		self.burstSpeed=self.normSpeed
		self.zapperReady=False
		self.prevWords=[]
		
	def initialize(self):
		'''Open up the game and start playing.'''
		rCode=subprocess.Popen(["cmd","/C","C:/Program Files (x86)/Typer Shark Deluxe/TyperShark.exe"],shell=True)
		time.sleep(4)
		Click(500,50)#Click adventure mode.
		time.sleep(.51)
		Click(350,300)#175)#Click difficulty
		time.sleep(1.450)
		Click(210, 325)#Disable hints
		autopy.key.tap(" ")
		Click(1,1)#Move the mouse to the upperleft.
		time.sleep(.5)
	
	def play(self):#Do everything
		cnt=0
		while(True):
			#Read screen
			screen=ImageGrab.grab()
			screens=splitScreen(screen)
			self.status=getGameStatus(screens)
			if self.status=="NOT_PLAYING":#TODO
				self.initialize()
			elif self.status=="FIGHTING":
				cnt=cnt+1
				start=time.time()
				screens[0].save('fightScreen'+str(cnt)+'.bmp')
				self.fight(screens[3])
				print('time to fight: '+str(time.time()-start))
			else:#TODO
				pass
	
	def fight(self,screen):
		#TODO
		#0. Crop the screen to be relevant.
		#1. Match the screen with targets.
		print("getting words")
		words =self.getWords(screen)
		#2. Sort the words by length and by similarity to previous words.
		words.sort(key=(lambda x:self.getKey(self.prevWords,x)),reverse=True)
		#3. Kill the targets
		self.type(words)
		#thread.start_new_thread(self.type,(words,))
		
	def getKey(self,prWords,x):
		max=0
		for word in prWords:
			cslen=0
			while x[len(x)-cslen-1]==word[len(word)-cslen-1]:
				cslen=cslen+1
			if cslen>max:
				max=cslen
		return max+len(x)/20

	def type(self,words):
		#Limiter is 85 WPM
		#That is 7.08333333333 chars/second
		#Delay should
		print("typing words");
		delay=(1/(self.normSpeed*5.0/60.0))
		print words
		for text in words:
			for c in text:
				autopy.key.tap(c)
				time.sleep(delay)
		
	def getWords(self,screen):#TODO
		'''Get the words from the screen. (This will be the hard part.)'''
		global cnt
		cnt=cnt+1
		(width,height)=screen.size
		screen.save('screen'+str(cnt)+'.png')
		blobs=screen.convert('L')
		blobs=np.array(blobs)
		leftmost=0
		(x,blobs)=(cv2.threshold(blobs, 20, 255, cv2.THRESH_BINARY_INV))
		for y in range(width):
			if(blobs[:,y].any()):
				leftmost=y
				break
		words=[]
		if(leftmost+125<=width):
			#Pass words Detected to tesseract and parse output.
			blobs=blobs[:,(20+leftmost):]
			Image.fromarray(blobs).save('wordsDetected'+str(cnt)+'.png')
			os.system('tesseract wordsDetected'+str(cnt)+'.png results'+str(cnt)+' nobatch letters.txt')
			lines=open('results'+str(cnt)+'.txt').readlines()
			words = [line.strip() for line in lines if line.strip()!='']
			print(len(words))
		return words
	
	def getTargets(self,screen):#Helper method for getWords. Take the screen and put each shark in its own box.
		'''Get the words from the screen. (This will be the hard part.)'''
		global cnt
		(width,height)=screen.size
		blobs=screen.convert('L')
		blobs=np.array(blobs)
		#blobs=screen.
		leftmost=0
		targets=[]
		for y in range(width):
			for x in range(height):
				if  (blobs[x,y]<20):
					if(y+200<=width):
						targets.append(np.copy(blobs[x-20:x+20,y:y+200]))
					blobs[x-30:x+30,y:y+200]=255
		print('Targets\' length is '+str(len(targets)))
		for target in targets:
			print(target.shape)
			(width,height)=target.shape
			for y in range(height):
				for x in range(width):
					if(target[x,y]<20):
						target[x,y]=255
					else:
						target[x,y]=0
		return targets
	
	def makeMove(self,words):#Decide what to do based on game state and list of targets.
		return
	
	def getZapperStatus(self,bottomscreen):#Determine if the zapper is ready, based on an image of that part of the screen.
		return false
	
	def getDepth(self,leftscreen):#Determine our depth, based on an image of that part of the screen.
		return 0
	
def determineDeadHelper(diver):
	#DEBUG
	(width,height)=diver.size
	diver=np.array(diver)
	pixel1=[220, 170, 0]
	pixel2=[260, 210, 20]
	equals=[[(pixel1<=pixels).all()&(pixels<=pixel2).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	return sumz>650
	
def getGameStatus(screens):#TODO
	'''Determine if we're not playing the game, at the main menu, at a level select screen,
	fighting fish, doing a secret level, or doing bonus words.'''
	if(determineNotFighting(screens[5])):
		return "NOT_FIGHTING"
	#if(preparingToDive(screens[3])):
	#	return "PREPARING_TO_DIVE"
	#if(determineDeadHelper(screens[4])):
	#	return "DEAD"
	else:
		return "FIGHTING"
		
def preparingToDive(midscreen):
	(width,height)=midscreen.size
	lowbound=[175, 115, 70]
	upbound=[240, 150, 110]
	diver=np.array(midscreen)
	equals=[[(lowbound<=pixels).all()&(pixels<=upbound).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	return sumz>300
	
def determineNotFighting(centscreen):
	#start=time.time()
	lowbound=[8, 32, 165]
	upbound=[12, 45, 220]
	diver=np.array(centscreen)
	equals=[[(lowbound<=pixels).all()&(pixels<=upbound).all() for pixels in row] for row in diver]	
	sumz=np.sum(equals)
	#print('time taken is:'+str(time.time()-start))
	return sumz<=250

def splitScreen(screen):
	#Split the screen into multiple parts, so we can have other methods focus on them.
	x=0
	y=0
	global cnt
	cnt=cnt+1
	(width,height)=screen.size
	midscreen = screen.crop((100,25,width, height-75))
	leftscreen = screen.crop((0,0,25,height))
	bottscreen = screen.crop((0,height-38,width,height))
	diverscreen = screen.crop((32,height/3+75,width/7-15,3*height/4-45))
	centScreen=midscreen.crop((width/2-125,height/2-50,width/2-100,height/2-10))
	screens=[screen,leftscreen,bottscreen,midscreen,diverscreen,centScreen]
	cnt=cnt-1
	return screens

def Click(x,y):
	autopy.mouse.move(x, y)
	autopy.mouse.click()

game=Game()
game.initialize()
game.play()	

