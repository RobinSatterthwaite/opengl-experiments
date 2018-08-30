#=============================================================================#
#                                                                             #
# Copyright (c) 2005 - 2015 G-Truc Creation (www.g-truc.net)                  #
#                                                                             #
# This module is a derivative work of the OpenGL Mathematics                  #
# (glm.g-truc.net) gtc/matrix_transform module.                               #
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
# Restrictions:                                                               #
#		By making use of the Software for military purposes, you choose to make   #
#		a Bunny unhappy.                                                          #
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

from math import sin, cos, tan
from numpy import array, identity, zeros, ones, copyto
from numpy.linalg import norm



def m_translate(m, v):
	"""
	Builds a translation 4 * 4 matrix created from a vector of 3 components.
	
	\param m  Input matrix multiplied by this translation matrix.
	\param v  Coordinates of a translation vector.
	"""
	t = array(m)
	t[3] = m[0]*v[0] + m[1]*v[1] + m[2]*v[2] + m[3]
	return t
	
	
	
def m_translate_in_place(m, v):
	"""
	Translates a 4 * 4 matrix created from a vector of 3 components.
	
	\param m  Input matrix multiplied by this translation matrix.
	\param v  Coordinates of a translation vector.
	"""
	m[3] = m[0]*v[0] + m[1]*v[1] + m[2]*v[2] + m[3]



def m_rotate_axis(m, theta, axis):
	"""
	Builds a rotation 4 * 4 matrix created from an axis vector and an angle.
	
	\param m      Input matrix multiplied by this rotation matrix.
	\param theta (rad) Rotation angle.
	\param axis   Rotation axis, recommended to be normalized.
	"""
	c = cos(theta)
	s = sin(theta)
	
	v = array(axis)
	v /= norm(v)
	
	tmp = v * (1-c)
	
	rotation = identity(3)
	
	rotation[0,0] = tmp[0]*v[0] + c
	rotation[0,1] = tmp[0]*v[1] + s*v[2]
	rotation[0,2] = tmp[0]*v[2] - s*v[1]
	
	rotation[1,0] = tmp[1]*v[0] - s*v[2]
	rotation[1,1] = tmp[1]*v[1] + c
	rotation[1,2] = tmp[1]*v[2] + s*v[0]
	
	rotation[2,0] = tmp[2]*v[0] + s*v[1]
	rotation[2,1] = tmp[2]*v[1] - s*v[0]
	rotation[2,2] = tmp[2]*v[2] + c
	
	r = m.copy()
	
	r[0] = m[0]*rotation[0,0] + m[1]*rotation[0,1] + m[2]*rotation[0,2]
	r[1] = m[0]*rotation[1,0] + m[1]*rotation[1,1] + m[2]*rotation[1,2]
	r[2] = m[0]*rotation[2,0] + m[1]*rotation[2,1] + m[2]*rotation[2,2]
	
	return r



def m_rotate(m, r):
	"""
	http://www.opengl-tutorial.org/assets/faq_quaternions/index.html
	"""
	A = cos(r[0])
	B = sin(r[0])
	C = cos(r[1])
	D = sin(r[1])
	E = cos(r[2])
	F = sin(r[2])
	
	AD = A*D
	BD = B*D
	
	mat = array([[  C*E      ,  -C*F      ,    D,  0.],
	             [ BD*E + A*F, -BD*F + A*E, -B*C,  0.],
	             [-AD*E + B*F,  AD*F + B*E,  A*C,  0.],
	             [         0.,          0.,   0.,  1.]])
	
	return mat.dot(m)

	

def m_rotate_in_place(m, r):
	"""
	http://www.opengl-tutorial.org/assets/faq_quaternions/index.html
	"""
	A = cos(r[0])
	B = sin(r[0])
	C = cos(r[1])
	D = sin(r[1])
	E = cos(r[2])
	F = sin(r[2])
	
	AD = A*D
	BD = B*D
	
	mat = array([[  C*E      ,  -C*F      ,    D,  0.],
	             [ BD*E + A*F, -BD*F + A*E, -B*C,  0.],
	             [-AD*E + B*F,  AD*F + B*E,  A*C,  0.],
	             [         0.,          0.,   0.,  1.]])
	
	copyto(m, mat.dot(m))



def m_scale(m, v):
	"""
	Builds a scale 4 * 4 matrix created from 3 scalars. 
	
	\param m  Input matrix multiplied by this scale matrix.
	\param v  Ratio of scaling for each axis.
	"""
	s = array(m)
	s[0] = m[0]*v[0]
	s[1] = m[1]*v[1]
	s[2] = m[2]*v[2]
	s[3] = m[3]
	return s



def m_scale_in_place(m, v):
	"""
	Builds a scale 4 * 4 matrix created from 3 scalars. 
	
	\param m  Input matrix multiplied by this scale matrix.
	\param v  Ratio of scaling for each axis.
	"""
	m[0] *= v[0]
	m[1] *= v[1]
	m[2] *= v[2]



def m_perspective(fov, aspect, min_z, max_z):
	"""
	Creates a matrix for a symetric perspective-view frustum based on the default
	handedness.
	
	\param fov    (rad) Specifies the field of view angle in the y direction.
	\param aspect  Specifies the aspect ratio that determines the field of view
                 in the x direction. The aspect ratio is the ratio of x (width)
	               to y (height).
	\param min_z   Specifies the distance from the viewer to the near clipping
	               plane (always positive).
	\param max_z   Specifies the distance from the viewer to the far clipping
	               plane (always positive).
	"""
	
	if aspect == 0.:
		raise ValueError("Invalid aspect ratio.")
	if min_z > max_z:
		raise ValueError("Minimum draw distance cannot be greater than maximum.")
	
	f = tan(fov/2.)
	
	m = zeros((4,4))
	
	m[0,0] = 1./(aspect*f)
	m[1,1] = 1./f
	m[2,2] = -(max_z+min_z)/(max_z-min_z)
	m[2,3] = -1.
	m[3,2] = -(2.*max_z*min_z)/(max_z-min_z)
	
	return m



def m_orthographic(left, right, bottom, top, min_z, max_z):
	"""
	Creates a matrix for an orthographic parallel viewing volume, using
	right-handed coordinates. 	The near and far clip planes correspond to z
	normalized device coordinates of -1 and +1 respectively.
	
	
	"""
	
	m = identity(4)
	
	m[0,0] = 2./(right-left)
	m[1,1] = 2./(top-bottom)
	m[2,2] = -2./(max_z-min_z)
	m[3,0] = -(right+left)/(right-left)
	m[3,1] = -(top+bottom)/(top-bottom)
	m[3,2] = -(max_z+min_z)/(max_z-min_z)
	
	return m

