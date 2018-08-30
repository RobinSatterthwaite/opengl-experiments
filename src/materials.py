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

from PIL import Image
from numpy import array
from OpenGL.GL import *

import sys


class Material(object):

	def __init__(self, colour, texture_img=None):
		self.colour = array(colour)
		self.alpha = 1.
		
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		
		if texture_img != None:
			if texture_img.mode == "RGB":
				gl_format = GL_RGB
			elif texture_img.mode == "RGBA":
				gl_format = GL_RGBA
			else:
				raise TypeError("Texture mode "+texture_img.mode+" not supported")
				
			glTexImage2D(GL_TEXTURE_2D, 0, GL_BGRA,
			             texture_img.width, texture_img.height, 0, gl_format,
			             GL_UNSIGNED_BYTE, texture_img.tobytes())

		else:
			glTexImage2D(GL_TEXTURE_2D, 0, GL_BGRA,
			             1, 1, 0, GL_RGB,
			             GL_UNSIGNED_BYTE, bytearray([255,255,255]))
		
		#glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		#glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
		glGenerateMipmap(GL_TEXTURE_2D)



class AssimpMaterial(Material):

	def __init__(self, ai_mat):
		texture_img = None
		
		try:
			filename = ai_mat.properties.get(('file', 1))
			if filename:
				texture_img = Image.open(filename)
				
		except IOError as e:
			sys.stderr.write(str(e)+'\n')
			pass
	
		super(AssimpMaterial, self).__init__([1.,1.,1.], texture_img)
		
		if texture_img != None:
			texture_img.close()
	