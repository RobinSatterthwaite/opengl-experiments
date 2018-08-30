#=============================================================================#
#                                                                             #
# Copyright (c) 2016                                                          #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the "Software"),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
#                                                                             #
#=============================================================================#

import time


class Clock(object):

	fpsUpdateFreq = 30

	def __init__(self):
		self.tick_time = time.clock()
		self.fps = 0.0
		self.time_for_fps = 0.0
		self.nticks = 0
		
		
	def tick(self, fps):
		last_tick = self.tick_time
		self.tick_time = time.clock()
		time_to_sleep = 1./fps-(self.tick_time-last_tick)
		if time_to_sleep > 0:
			time.sleep(time_to_sleep)
			self.tick_time = time.clock()
			
		self.nticks += 1
		if self.nticks >= self.fpsUpdateFreq:
			self.fps = self.fpsUpdateFreq/(self.tick_time-self.time_for_fps)
			self.time_for_fps = self.tick_time
			self.nticks = 0
		
		return self.tick_time-last_tick

