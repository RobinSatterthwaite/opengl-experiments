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

from math import pi, sin, cos
from numpy import array, identity, zeros

from matrix_transforms import *

import sys



class Camera(object):
	"""
	This is the superclass for all Camera objects.  It is not abstract and can be
	used as a first person camera.
	"""

	movementSpeed = 3
	pitchCap = pi/2 - 0.1

	def __init__(self, pos, az = 0., el = 0.):
		self._pos = array(pos)
		self.az = az
		self.el = el
		self.heading = zeros(3)
		
	
	@property
	def pos(self):
		return self._pos
		
		
	@property
	def matrix(self):
		""" Get the camera matrix for use in the shader program. """
		m = identity(4)
		m = m_rotate_axis(m, self.el, (1., 0., 0.))
		m = m_rotate_axis(m, self.az, (0., 1., 0.))
		m = m_translate(m, -self._pos)
		return m
		
		
	def yaw(self, angle):
		self.az += angle
		if   self.az >  pi:
			while self.az >  pi: self.az -= 2*pi
		elif self.az < -pi:
			while self.az < -pi: self.az += 2*pi
		
	def pitch(self, angle):
		self.el += angle
		if self.el >  self.pitchCap: self.el =  self.pitchCap
		if self.el < -self.pitchCap: self.el = -self.pitchCap
	
	
	def forwardsBackwards(self, mag):
		self.heading[2] -= mag
		if abs(self.heading[2]) > abs(mag):
			self.heading[2] = -mag
		
		
	def leftRight(self, mag):
		self.heading[0] += mag
		if abs(self.heading[0]) > abs(mag):
			self.heading[0] = mag
		
		
	def update(self, time_passed):
		heading = array((self.heading[0]*cos(self.az)-self.heading[2]*sin(self.az),
		                 self.heading[1],
		                 self.heading[2]*cos(self.az)+self.heading[0]*sin(self.az)))
		movement = heading.dot(self.movementSpeed).dot(time_passed)
		self._pos += movement
		
		
		
class OrbitalCamera(Camera):
	"""
	A Camera which moves around the subject at a fixed distance.  Can be used as
	a third person camera.
	"""

	def __init__(self, subject, r, az = 0., el = 0.):
		
		super(OrbitalCamera, self).__init__((0.,0.,0.), az, el)
		self.subject = subject
		self._pos = self.subject.pos
		self.distance = array(r)
		
		
	@property
	def pos(self):
		m = identity(4)
		m = m_translate  (m, self._pos)
		m = m_rotate_axis(m, -self.az, (0., 1., 0.))
		m = m_rotate_axis(m, -self.el, (1., 0., 0.))
		m = m_translate  (m, self.distance)
		return m[3][0:3]
		
		
	@property
	def matrix(self):
		""" Get the camera matrix for use in the shader program. """
		m = identity(4)
		m = m_translate  (m, -self.distance)
		m = m_rotate_axis(m, self.el, (1., 0., 0.))
		m = m_rotate_axis(m, self.az, (0., 1., 0.))
		m = m_translate  (m, -self._pos)
		return m
		
		
	def update(self, time_passed):
		self._pos = self.subject.pos
