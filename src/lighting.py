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

from numpy import array, zeros, identity, cross
from numpy.linalg import norm
from OpenGL.GL import *

from matrix_transforms import *


class LightType:
	Disabled    = 0
	Directional = 1
	Point       = 2


class AmbientLight(object):

	def __init__(self, amplitude_binding, colour_binding):
		self._amplitude = amplitude_binding
		self._colour    = colour_binding
	
	
	def setAmplitude(self, a):
		self._amplitude.set(a)
	
	def setColour(self, c):
		self._colour.set(array(c))
		


class IndexedLight(AmbientLight):

	ShadowMappingEnabled = False
	
	def __init__(self, type_binding, amplitude_binding, colour_binding, index):
		super(IndexedLight, self).__init__(amplitude_binding, colour_binding)
		self._type = type_binding
		self.index = index
	
	def enable(self):
		raise NotImplementedError("Abstract method")
	
	def disable(self):
		self._type.set(LightType.Disabled)



class DirectionalLight(IndexedLight):
	
	ShadowMappingEnabled = True
	ShadowResolutionX = 2048
	ShadowResolutionY = 2048
	
	def __init__(self, type_binding,
	                   amplitude_binding,
	                   colour_binding,
	                   direction_binding,
	                   matrix_binding,
	                   shadow_map_binding,
	                   index):
		super(DirectionalLight, self).__init__(type_binding, amplitude_binding, colour_binding, index)
		self._direction = direction_binding
		self._matrixBinding = matrix_binding
		
		self._type.set(LightType.Directional)
		self._directionVec = array([0., 0., -1.])
		self._lightViewMatrix = identity(4)
		
		self.matrix = identity(4)
		
		# create depth buffer for shadow calculations
		self.depthBuffer  = glGenFramebuffers(1)
		self.depthTexture = glGenTextures(1)
		
		glBindTexture(GL_TEXTURE_2D, self.depthTexture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
		             self.ShadowResolutionX, self.ShadowResolutionY, 0, GL_DEPTH_COMPONENT,
		             GL_FLOAT, None)
		
		self._shadowMapBinding = shadow_map_binding
		
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, array([1.,1.,1.,1.]))
		
		glBindFramebuffer(GL_FRAMEBUFFER, self.depthBuffer)
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthTexture, 0)
		glDrawBuffer(GL_NONE)
		glReadBuffer(GL_NONE)
		glBindFramebuffer(GL_FRAMEBUFFER, 0)

	
	def enable(self):
		self._type.set(LightType.Directional)
	
	
	def setDirection(self, d):
		self._directionVec = array(d)/norm(d)
		self._direction.set(self._directionVec)
		
		f = self._directionVec
		s = cross(f, array([0.,1.,0.]))
		u = cross(s, f)
		
		# fixme - make this follow the camera, currently centered on 0,0,0 
		pos = -f*20

		self._lightViewMatrix[0,0] =  s[0]
		self._lightViewMatrix[1,0] =  s[1]
		self._lightViewMatrix[2,0] =  s[2]
		self._lightViewMatrix[0,1] =  u[0]
		self._lightViewMatrix[1,1] =  u[1]
		self._lightViewMatrix[2,1] =  u[2]
		self._lightViewMatrix[0,2] = -f[0]
		self._lightViewMatrix[1,2] = -f[1]
		self._lightViewMatrix[2,2] = -f[2]
		self._lightViewMatrix[3,0] = -s.dot(pos)
		self._lightViewMatrix[3,1] = -u.dot(pos)
		self._lightViewMatrix[3,2] =  f.dot(pos)
		self.matrix = self._lightViewMatrix.dot(m_orthographic(-10., 10., -10., 10., 1., 40.))
		
		self._matrixBinding.set(self.matrix)
		
		
	def rotate(self, r):
		pass # fixme
	
	
	def setShadowMap(self):
		self._shadowMapBinding.set(self.depthTexture)



class PointLight(IndexedLight):
	
	def __init__(self, type_binding, position_binding, amplitude_binding, colour_binding, index):
		super(PointLight, self).__init__(type_binding, amplitude_binding, colour_binding, index)
		self._position = position_binding
		self._type.set(LightType.Point)
		
	
	def enable(self):
		self._type.set(LightType.Point)
	
	
	def setPosition(self, p):
		self._position.set(array(p))
	