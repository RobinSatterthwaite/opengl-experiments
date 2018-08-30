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

import pyglfw.pyglfw as glfw
from pyglfw.pyglfw.window import Window as GlfwWindow


class DispatchTable(object):
	"""
	A class to handle events and registering event handling functions and
	methods.  Registered functions should accept the event as the only argument.
	"""

	def __init__(self, window):
		window.set_key_callback(self.keyboardInput)
		window.set_mouse_button_callback(self.mouseButtonInput)
		window.set_cursor_pos_callback(self.mouseMove)
		
		self.keyDispatch = {}
		self.userEventDispatch = {}
		self.mouseMotionDispatch = None
		self.mouseButtonDispatch = {}
		
		
	def registerKey(self, key, func):
	  self.keyDispatch[key] = func
	
	def unregisterKey(self, key):
	  self.keyDispatch.pop(key)
	
	
	def registerMouseMotion(self, func):
		self.mouseMotionDispatch = func
	
	def unregisterMouseMotion(self):
		self.mouseMotionDispatch = None
	
	
	def registerMouseButton(self, button, func):
	  self.mouseButtonDispatch[button] = func
	
	def unregisterMouseButton(self, button):
	  self.mouseButtonDispatch.pop(button)
	
	
	def registerUserEvent(self, code, func):
		self.userEventDispatch[code] = func
	
	def unregisterUserEvent(self, code):
		self.userEventDispatch.pop(code)
	
	
	
	def keyboardInput(self, window, key, scan_code, action, mods):
		if key in self.keyDispatch:
			self.keyDispatch[key](key, action, mods)
	
	
	def mouseButtonInput(self, window, button, action, mods):
		if button in self.mouseButtonDispatch:
			self.mouseButtonDispatch[button](button, action, mods)
	
	
	def mouseMove(self, window, xpos, ypos):
		if self.mouseMotionDispatch:
			self.mouseMotionDispatch(xpos, ypos)

