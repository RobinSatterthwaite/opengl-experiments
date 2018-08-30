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

from io import open
from json import load as load_json
from math import pi
from sets import Set

import pyglfw.pyglfw as glfw
from pyglfw.pyglfw.window import Window as GlfwWindow

from renderer import Renderer
from cameras import Camera, OrbitalCamera
from events import DispatchTable
from models import Model
from clocks import Clock



class GameData(object):
	"""
	This class contains game characters and other things that collectively make up the game state.
	"""

	def __init__(self):
		self.camera = None
		self.characters = Set()
	
	
	def addCharacter(self, character):
		self.characters.add(character)
	
	def removeCharacter(self, character):
		self.characters.discard(character)
	
	
	def setCamera(self, camera):
		self.camera = camera
	
	
	def update(self, time_passed):
		self.camera.update(time_passed)
		
		for character in self.characters:
			try:
				character.update(time_passed)
			except AttributeError:
				pass



class Game(object):
	"""
	The object containing all information about the game.
	"""

	def __init__(self):
		
		with open("config.json") as cfg_file:
			game_cfg = load_json(cfg_file)
		
		if not glfw.init():
			raise RuntimeError("Failed to initialise GLFW")
		
		GlfwWindow.hint(samples = game_cfg["aaSamples"])
		GlfwWindow.hint(context_ver_major = 3)
		GlfwWindow.hint(context_ver_minor = 3)
		GlfwWindow.hint(forward_compat = True)
		GlfwWindow.hint(resizable = True)
		GlfwWindow.hint(opengl_profile = GlfwWindow.CORE_PROFILE)
		
		primary_monitor = None
		if game_cfg["fullscreen"]:
			primary_monitor = glfw.get_primary_monitor()
		
		self.window = GlfwWindow(game_cfg["screenWidth"], game_cfg["screenHeight"], "Tutorial", primary_monitor)
		if not self.window:
			raise RuntimeError("Failed to initialise window.")
		
		self.window.make_current()
		
		self.clock = Clock()
		
		self.dispatchTable = DispatchTable(self.window)
		
		# setup keyboard and mouse controls
		self.dispatchTable.registerKey(glfw.Keys.ESCAPE, self.escape)
		self.dispatchTable.registerKey(glfw.Keys.W, self.moveForward)
		self.dispatchTable.registerKey(glfw.Keys.S, self.moveBackward)
		self.dispatchTable.registerKey(glfw.Keys.A, self.moveLeft)
		self.dispatchTable.registerKey(glfw.Keys.D, self.moveRight)
		
		self.dispatchTable.registerMouseButton(glfw.Mice.RIGHT, self.toggleMouseLook)
		
		self.renderer = Renderer(self.window)
		self.renderer.fov = pi/4.
		
		self.camera = None
		
		self.gameData = GameData()
		
		self._mouseLook = False
		
		self._terminate = False
	
	
	def __del__(self):
		glfw.terminate()
		
		
	def run(self):
		""" Runs the game.  This method returns when the terminate flag is set. """
		
		while not self._terminate:
			
			time_passed = self.clock.tick(60.)
			print "{0:.3f}\r".format(self.clock.fps),
			
			self.gameData.update(time_passed)
			
			self.renderer.update(time_passed)
			
			glfw.poll_events()
			
			if self.window.should_close:
				self._terminate = True
	
	
	def terminate(self):
		""" Set the terminate flag, causing the program to tear-down and exit. """
		self._terminate = True
			
			
	def addEntity(self, entity):
		self.renderer.addEntity(entity)
	
	def removeEntity(self, entity):
		self.renderer.removeEntity(entity)
	
	
	def addCharacter(self, character):
		self.gameData.addCharacter(character)
		self.addEntity(character)
	
	def removeCharacter(self, character):
		self.gameData.removeCharacter(character)
		self.removeEntity(character)
	
	
	def setPlayerCharacter(self, pc):
		""" Set the specified items as the player character entity. """
		
		self.pc = pc
		self.addCharacter(pc)
		
		# set up third person camera following player entity
		camera = OrbitalCamera(self.pc, (0.,0.,5.))
		self.setCamera(camera)
		self.pc.setCamera(camera)
		
		
	def setCamera(self, camera):
		self.camera = camera
		self.renderer.camera = camera
		self.gameData.setCamera(camera)
		
	
	## Control Methods ##
	
	def escape(self, key, action, mods):
		if action == GlfwWindow.PRESS:
			self.terminate()
		
		
	def toggleMouseLook(self, key, action, mods):
		if action == GlfwWindow.RELEASE:
			if not self._mouseLook:
				self.window.cursor_mode = None
				self.dispatchTable.registerMouseMotion(self.mouseLook)
				self._mouseLook = True
				self.window.cursor_pos = (1, 1)
				
			else:
				self.window.cursor_mode = True
				self.dispatchTable.unregisterMouseMotion()
				self._mouseLook = False
	
	
	def mouseLook(self, xpos, ypos):
		self.camera.yaw((xpos-1)*0.01)
		self.camera.pitch((ypos-1)*0.01)
		self.window.cursor_pos = (1, 1)
		
		
	def moveForward(self, key, action, mods):
		if   action == GlfwWindow.PRESS:
			self.pc.forwardsBackwards(+1)
		elif action == GlfwWindow.RELEASE:
			self.pc.forwardsBackwards(-1)
		
		
	def moveBackward(self, key, action, mods):
		if   action == GlfwWindow.PRESS:
			self.pc.forwardsBackwards(-1)
		elif action == GlfwWindow.RELEASE:
			self.pc.forwardsBackwards(+1)
			
			
	def moveLeft(self, key, action, mods):
		if   action == GlfwWindow.PRESS:
			self.pc.leftRight(-1)
		elif action == GlfwWindow.RELEASE:
			self.pc.leftRight(+1)
			
			
	def moveRight(self, key, action, mods):
		if   action == GlfwWindow.PRESS:
			self.pc.leftRight(+1)
		elif action == GlfwWindow.RELEASE:
			self.pc.leftRight(-1)



GameInstance = Game()
