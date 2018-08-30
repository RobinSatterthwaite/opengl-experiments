#=============================================================================#
#                                                                             #
# Copyright (c) 2017                                                          #
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

from math import pi, sin, cos
from numpy import array, zeros, ones, identity

import os

os.environ['PATH'] += os.getcwd()+'\\assimp;'

import pyassimp
import pyassimp.postprocess

from src.matrix_transforms import *

from src.models import AssimpModel, UiModel
from src.game import GameInstance as game


import sys



class Entity(object):
	"""
	This class is for representing a 3d game object.
	"""
	
	def __init__(self, model_class):
		self._matrix = identity(4)
		self._modelClass = model_class
		
		
	@property
	def pos(self):
		return self._matrix[3][0:3]
		
	@property
	def matrix(self):
		""" Returns the current model matrix. """
		return self._matrix
		
	#@property
	#def normalMatrix(self):
	#	return self.model.normalMatrix
	
	@property
	def modelClass(self):
		return self._modelClass
	
	
	def translate(self, t):
		"""
		Move the entity relative to its current position /and rotation/.
		"""
		m_translate_in_place(self._matrix, t)
		
	def rotate(self, r):
		""" Rotate the entity relative to its current rotation. """
		m_rotate_in_place(self._matrix, r)



class Character(Entity):
	"""
	This class extends the #Entity class to add mobility to the object.
	"""
	
	def __init__(self, model_class):
		super(Character, self).__init__(model_class)
		
		self.movement = zeros(3)
		self.movementSpeed = 0.
		self.heading = 0.
		
		
	def update(self, time_passed):
		""" Update the position of the object. """
		movement = self.movement.dot(self.movementSpeed).dot(time_passed)
		self.translate(movement)
	
	

class PlayerCharacter(Character):
	"""
	This class extends the #Character class to add control methods.
	"""
	
	def __init__(self, model_class):
		super(PlayerCharacter, self).__init__(model_class)
		
		self.camera = None
	
	
	def setCamera(self, camera):
		self.camera = camera
	
	
	def forwardsBackwards(self, mag):
		self.movement[2] -= mag
		if abs(self.movement[2]) > abs(mag):
			self.movement[2] = -mag
		
	def leftRight(self, mag):
		self.movement[0] += mag
		if abs(self.movement[0]) > abs(mag):
			self.movement[0] = mag
	
	
	def update(self, time_passed):
		if (self.movement[0] != 0 or self.movement[2] != 0):
			if (self.camera):
				self.rotate((0., self.camera.az-self.heading, 0.))
			
			self.heading = self.camera.az
		
		super(PlayerCharacter, self).update(time_passed)



class UiModelVerticalAlignment:
	Top    = 0
	Centre = 1
	Bottom = 2

class UiModelHorizontalAlignment:
	Left   = 0
	Centre = 1
	Right  = 2


from re import compile, search

ui_meas_re = compile("^([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)(?:\s*)([%(?:px)]*)")

class UiMeas:
	def __init__(self, val, type="sc"):
		self.val  = val
		self.type = type


class UiEntity(Entity):

	def __init__(self, horiz_offset = UiMeas(0, "%"),
		                 vert_offset  = UiMeas(0, "%"),
		                 width        = UiMeas(50, "%"),
		                 height       = UiMeas(50, "%"),
		                 horiz_align  = UiModelHorizontalAlignment.Left,
		                 vert_align   = UiModelVerticalAlignment.Top):
		super(UiEntity, self).__init__(UiModel)
		
		translation = [0., 0., 0.]
		scale = [1., 1., 1.]
		pre_scale_translation  = [0., 0., 0.]
		post_scale_translation = [0., 0., 0.]
		
		if horiz_align == UiModelHorizontalAlignment.Left:
			pre_scale_translation[0] = -1.
			post_scale_translation[0] = .5
			horiz_offset_scl = 1.
		elif horiz_align == UiModelHorizontalAlignment.Right:
			pre_scale_translation[0] = 1.
			post_scale_translation[0] = -.5
			horiz_offset_scl = -1.
		
		if vert_align == UiModelVerticalAlignment.Top:
			pre_scale_translation[1] = 1.
			post_scale_translation[1] = -.5
			vert_offset_scl = -1.
		elif vert_align == UiModelVerticalAlignment.Bottom:
			pre_scale_translation[1] = -1.
			post_scale_translation[1] = .5
			vert_offset_scl = 1.
		
		if horiz_offset.type == "sc":
			translation[0] = horiz_offset_scl*horiz_offset.val
		elif horiz_offset.type == "%":
			translation[0] = horiz_offset_scl*horiz_offset.val/50.
		
		if vert_offset.type == "sc":
			translation[1] = vert_offset_scl*vert_offset.val
		elif vert_offset.type == "%":
			translation[1] = vert_offset_scl*vert_offset.val/50.
		
		if width.type == "sc":
			scale[0] = width.val
		elif width.type == "%":
			scale[0] = width.val/50.
		
		if height.type == "sc":
			scale[1] = height.val
		elif height.type == "%":
			scale[1] = height.val/50.
		
		m_translate_in_place(self._matrix, translation)
		m_translate_in_place(self._matrix, pre_scale_translation)
		m_scale_in_place(self._matrix, scale)
		m_translate_in_place(self._matrix, post_scale_translation)



game.renderer.aLight.setColour([1., 1., 1.])
game.renderer.aLight.setAmplitude(0.1)

dLight = game.renderer.getDirectionalLight()
dLight.setDirection([-0.707107, 0.0, -0.707107])
#dLight.setDirection([0.,0.,-1.])
dLight.setColour([0.75, 0.75, 0.75])

pLight = game.renderer.getPointLight()
pLight.setPosition([-3, 0, -3])
pLight.setAmplitude(5)
pLight.setColour([1,0.25,0])

pyassimp_processing_flags = (pyassimp.postprocess.aiProcess_Triangulate |
                             pyassimp.postprocess.aiProcess_OptimizeMeshes)


class Cube(AssimpModel):
	def __init__(self):
		asset = pyassimp.load("assets/obj/cube.obj", processing=pyassimp_processing_flags)
		super(Cube, self).__init__(asset)


class Sphere(AssimpModel):
	def __init__(self):
		asset = pyassimp.load("assets/obj/sphere.dae", processing=pyassimp_processing_flags)
		super(Sphere, self).__init__(asset)


class Spider(AssimpModel):
	def __init__(self):
		asset = pyassimp.load("assets/obj/spider.obj", processing=pyassimp_processing_flags)
		super(Spider, self).__init__(asset)
		
		self.rotate((0., pi/2, 0.))
		self.translate((-0.05, 0., 0.))
		self.scale((.01, .01, .01 ))


class Duck(AssimpModel):
	def __init__(self):
		asset = pyassimp.load("assets/obj/duck.dae", processing=pyassimp_processing_flags)
		super(Duck, self).__init__(asset)
		
		self.scale((.01, .01, .01))


game.renderer.addModel(Cube)
game.renderer.addModel(Sphere)
game.renderer.addModel(Spider)
game.renderer.addModel(Duck)
game.renderer.addModel(UiModel)

cube_1 = Entity(Cube)
cube_1.translate(( 0., 4., 0.))

cube_2 = Entity(Cube)
cube_2.translate(( -1.,  0., -3. ))

sphere_1 = Entity(Sphere)
sphere_1.translate((3., 0., -4.))

#sys.stderr.write(str(sphere.meshes[0].__dict__)+'\n')
#sys.stderr.write(str(sphere_q.meshes[0].__dict__)+'\n')

spider_1 = Entity(Spider)
spider_1.translate(( -3.,  0.,  0. ))
spider_1.rotate(( 0., -pi/2, 0. ))
spider_1.rotate(( pi/6, 0.,  0. ))

#sys.stderr.write(str(duck.meshes[0].__dict__)+'\n')

duck_1 = Entity(Duck)
duck_1.translate((5., 0., -1.))

spider_char = PlayerCharacter(Spider)
spider_char.movementSpeed = 3.
spider_char.translate((2., 0., 0.))


#cube_1.setColour(ones(108, dtype='float32'))
#cube_2.setColour(ones(108, dtype='float32'))

game.addEntity(cube_1)
game.addEntity(cube_2)
game.addEntity(spider_1)
game.addEntity(sphere_1)
game.addEntity(duck_1)

game.setPlayerCharacter(spider_char)

#render_screen = UiEntity(horiz_offset = UiMeas(5, "%"),
#                         vert_offset  = UiMeas(5, "%"),
#                         width        = UiMeas(90, "%"),
#                         height       = UiMeas(90, "%"))
#game.renderer.addUiEntity(render_screen)

game.run()

del game
