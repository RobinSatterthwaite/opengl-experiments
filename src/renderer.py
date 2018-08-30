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

from math import pi, tan, sqrt
from sets import Set
from numpy import transpose, identity
from numpy.linalg import inv
from OpenGL.GL import *

from shaders import VertexShader, FragmentShader, ShaderProgram
from lighting import *
from models import Model

from matrix_transforms import m_perspective, m_orthographic



class Renderer(object):
	"""
	This class is the top level point for all rendering operations in the game.
	
	It encompasses:
	-	the shader program(s)
	- a list of the models to be rendered
	"""
	
	MaxFov = pi/3.
	MinFov = pi/100.
	
	NumLights = 20
	
	def __init__(self, window):
		# type: (GlfwWindow) -> None
		"""
		Initialises the renderer, compiling the shader(s) and setting up the OpenGL
		instance.
		
		\param window  A GLFW window instance.
		"""
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LESS)
		
		glEnable(GL_CULL_FACE)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		glClearColor(1., 1., 1., 0.)
		
		vertex_shader   = VertexShader(  shader_file='src/shaders/vertex_shader.glsl',
		                                 consts={'NUM_LIGHTS': self.NumLights})
		fragment_shader = FragmentShader(shader_file='src/shaders/fragment_shader.glsl',
		                                 consts={'NUM_LIGHTS': self.NumLights})
		
		self.renderShader = ShaderProgram(vertex_shader, fragment_shader)
		
		self.renderShader.use()
		
		self.renderShader.uniformInt('useLighting')
		self.renderShader.uniformMatrix4('modelMatrix')
		self.renderShader.uniformMatrix4('normalMatrix')
		self.renderShader.uniformMatrix4('viewMatrix')
		self.renderShader.uniformSampler('matTextureSampler')
		self.renderShader.uniformVector3('matDiffuseColour')
		self.renderShader.uniformFloat('matAlpha')
		self.renderShader.uniformVector3('cameraPosition')
		self.renderShader.attribute('vertexPosition')
		self.renderShader.attribute('vertexUv')
		self.renderShader.attribute('vertexNormal')
		
		self.aLight = AmbientLight(self.renderShader.uniformFloat('ambientLightAmplitude'),
		                           self.renderShader.uniformVector3('ambientLightColour'))
		
		depth_vertex_shader = VertexShader(shader_file='src/shaders/depth_vertex_shader.glsl')
		depth_fragment_shader = FragmentShader(shader_file='src/shaders/depth_fragment_shader.glsl')
		
		self.depthShader = ShaderProgram(depth_vertex_shader, depth_fragment_shader)
		
		self.depthShader.uniformMatrix4('modelMatrix')
		self.depthShader.uniformMatrix4('viewMatrix')
		
		self._lightIndexPool = Set(range(self.NumLights))
		self._lights = {}
		
		self.window = window
		self.aspectRatio = float(window.size[0])/float(window.size[1])
		window.set_window_size_callback(self.resize)
		
		self.perspectiveMatrix = None
		self.viewMatrix = None
		
		self.camera = None
		
		self.models = {}
		self.entities = Set()
		self.uiEntities = Set()
		
		
		#self.once = True
		
		
	
	@property
	def fov(self):
		# type: () -> float
		return self._fov
		
	@fov.setter
	def fov(self, val):
		# type: (float) -> None
		"""
		Set the field-of-view, this will also set the maximum draw distance appropriately.
		The fov is clamped to [MinFov..MaxFov].
		"""
		self._fov = val
		if self._fov > self.MaxFov:  self._fov = self.MaxFov
		if self._fov < self.MinFov:  self._fov = self.MinFov
		
		# to keep the area of display constant, max_z is inversely proportional to sqrt(tan(fov))
		self.max_z = 100. / sqrt(tan(self._fov))
		self.min_z = .1
		
		self.perspectiveMatrix = m_perspective(self._fov, self.aspectRatio, self.min_z, self.max_z)
		
	
	def resize(self, w, width, height):
		# type: (GlfwWindow, int, int) -> None
		""" Modifies the perspective matrix for the new aspect ratio. """
		
		if height != 0:
			self.aspectRatio = float(width)/float(height)
			
			self.perspectiveMatrix = m_perspective(self._fov, self.aspectRatio, self.min_z, self.max_z)
		
		
	def getDirectionalLight(self):
		index = self._lightIndexPool.pop()
		s_index = str(index)
		light = DirectionalLight(self.renderShader.uniformInt    ('lightType['+s_index+']'),
		                         self.renderShader.uniformFloat  ('lightAmplitude['+s_index+']'),
		                         self.renderShader.uniformVector3('lightColour['+s_index+']'),
														 self.renderShader.uniformVector3('lightVector['+s_index+']'),
		                         self.renderShader.uniformMatrix4('lightViewMatrix['+s_index+']'),
		                         self.renderShader.uniformSampler('lightShadowMapSampler['+s_index+']'),
														 index)
		self._lights[index] = light
		return light
	
	def getPointLight(self):
		index = self._lightIndexPool.pop()
		s_index = str(index)
		light = PointLight(self.renderShader.uniformInt    ('lightType['+s_index+']'),
		                   self.renderShader.uniformVector3('lightVector['+s_index+']'),
		                   self.renderShader.uniformFloat  ('lightAmplitude['+s_index+']'),
		                   self.renderShader.uniformVector3('lightColour['+s_index+']'),
		                   index)
		self._lights[index] = light
		return light
	
	def releaseLight(self, light):
		if light.index in self._lightIndexPool:
			raise Exception("Attempt to release light already in pool.")
		del self._lights[light.index]
		self._lightIndexPool.add(light.index)
		self.renderShader.uniformInt('lightType['+str(light.index)+']').set(LightType.Disabled)
	
	
	def addModel(self, model_class):
		# type: (Class) -> None
		""" Adds the model to the set and binds the buffers associated with the meshes. """
		
		if model_class not in self.models:
			model = model_class()
			self.models[model_class] = model
			for mesh in model.meshes:
				mesh.bindAttributes(self.renderShader)
				
			glBindVertexArray(0)
	
	def removeModel(self, model_class):
		# type: (Class) -> None
		""" Removes the specified model from the set. """
		
		del self.models[model_class]
	
	
	def addEntity(self, entity):
		self.entities.add(entity)
	
	def removeEntity(self, entity):
		self.entities.discard(entity)
	
	
	def addUiEntity(self, entity):
		self.uiEntities.add(entity)
	
	def removeUiEntity(self, entity):
		self.uiEntities.discard(entity)
			
		
	def update(self, interval):
		# type: (float) -> None
		"""
		Clears the screen and redraws all models.
		
		\param interval (s) The time passed since the previous frame.
		"""
		# generate shadow maps for each light source
		self.depthShader.use()
		glCullFace(GL_FRONT)
		
		for i in self._lights:
			light = self._lights[i]
			if light.ShadowMappingEnabled:
				glViewport(0, 0, light.ShadowResolutionX, light.ShadowResolutionY)
				glBindFramebuffer(GL_FRAMEBUFFER, light.depthBuffer)
				glClear(GL_DEPTH_BUFFER_BIT)
				
				self.depthShader.viewMatrix.set(light.matrix)
				
				for entity in self.entities:
					model = self.models[entity.modelClass]
					model_matrix = model.matrix(entity.matrix)
					self.depthShader.modelMatrix.set(model_matrix)
					
					for mesh in model.meshes:
						mesh.draw()
				
				light.setShadowMap()
			
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		
		self.renderShader.use()
		glCullFace(GL_BACK)
		
		glViewport(0, 0, *self.window.size)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self.viewMatrix = self.camera.matrix.dot(self.perspectiveMatrix)
		self.renderShader.viewMatrix.set(self.viewMatrix)
		self.renderShader.cameraPosition.set(self.camera.pos)
		self.renderShader.useLighting.set(1)
		
		for entity in self.entities:
			self.drawEntity(entity)
		
		self.renderShader.viewMatrix.set(identity(4))
		self.renderShader.useLighting.set(0)
		
		for entity in self.uiEntities:
			self.drawEntity(entity)
		
		self.window.swap_buffers()
		
		
	def drawEntity(self, entity):
		
		model = self.models[entity.modelClass]
		model_matrix = model.matrix(entity.matrix)
		self.renderShader.modelMatrix.set(model_matrix)
		
		normal_matrix = transpose(inv(model_matrix))
		self.renderShader.normalMatrix.set(normal_matrix)
		
		for mesh in model.meshes:
			self.renderShader.matTextureSampler.set(mesh.material.texture)
			self.renderShader.matDiffuseColour.set(mesh.material.colour)
			self.renderShader.matAlpha.set(mesh.material.alpha)
			
			mesh.draw()
	
	
