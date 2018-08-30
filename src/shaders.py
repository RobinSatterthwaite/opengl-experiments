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

from sets import Set
from OpenGL.GL import *



class ShaderError(Exception):
	pass


class Shader(object):
	"""
	
	"""

	def __init__(self, shader_src=None, shader_file=None, consts={}):
		self.shader = glCreateShader(self.ShaderType)
		
		if not shader_src and not shader_file:
			raise TypeError("No source file or string provided.")
		
		if not shader_src:
			with open(shader_file, 'r') as f:
				shader_src = f.read()
				
			for key, value in consts.items():
				shader_src = shader_src.replace('@'+key+'@', str(value))
		
		self.compileSrc(shader_src)
			
		
	def __del__(self):
		glDeleteShader(self.shader)
		
	
	def compileSrc(self, src):
		glShaderSource(self.shader, src)
		glCompileShader(self.shader)
		
		# check shader compilation
		if not glGetShaderiv(self.shader, GL_COMPILE_STATUS):
			raise ShaderError(glGetShaderInfoLog(self.shader))
		
		
	def attachToProgram(self, program):
		glAttachShader(program, self.shader)
		
		
	def detachFromProgram(self, program):
		glDetachShader(program, self.shader)
		
		
		
class VertexShader(Shader):
	ShaderType = GL_VERTEX_SHADER
	
	
class FragmentShader(Shader):
	ShaderType = GL_FRAGMENT_SHADER
		
		
		
class VertexAttribute(object):

	def __init__(self, program, var_name):
		self.location = glGetAttribLocation(program, var_name)
		
	def enable(self):
		glEnableVertexAttribArray(self.location)
	
	def disable(self):
		glDisableVertexAttribArray(self.location)



class ShaderUniformVariable(object):

	def __init__(self, program, var_name):
		self.location = glGetUniformLocation(program, var_name)
		

class ShaderUniformInt(ShaderUniformVariable):
		
	def set(self, val):
		glUniform1i(self.location, val)
		

class ShaderUniformFloat(ShaderUniformVariable):
		
	def set(self, val):
		glUniform1f(self.location, val)
		

class ShaderUniformVector3(ShaderUniformVariable):
		
	def set(self, v):
		if isinstance(v, list):	count = len(v)
		else:  									count = 1
		glUniform3fv(self.location, count, v)
		

class ShaderUniformMatrix3(ShaderUniformVariable):
		
	def set(self, m, transpose=False):
		if isinstance(m, list):	count = len(m)
		else:  									count = 1
		glUniformMatrix3fv(self.location, count, transpose, m)
		
		
class ShaderUniformMatrix4(ShaderUniformVariable):
		
	def set(self, m, transpose=False):
		if isinstance(m, list):	count = len(m)
		else:  									count = 1
		glUniformMatrix4fv(self.location, count, transpose, m)
		
		
class ShaderUniformBlockVariable(object):
	
	def __init__(self, program, block_name):
		self.location = glGetUniformBlockIndex(program, block_name)

		
class ShaderUniformSampler(ShaderUniformVariable):

	def __init__(self, program, var_name, texture_unit):
		super(ShaderUniformSampler, self).__init__(program, var_name)
		self.textureUnit = texture_unit
		glUniform1i(self.location, self.textureUnit)
		
	def set(self, val):
		glActiveTexture(GL_TEXTURE0 + self.textureUnit)
		glBindTexture(GL_TEXTURE_2D, val)



class ShaderProgram(object):

	def __init__(self, *args):
		self.program = glCreateProgram()
		self.shaders = args
		
		self.fsTextureUnitPool = Set(range(glGetInteger(GL_MAX_TEXTURE_IMAGE_UNITS)))
		
		for shader in self.shaders:
			shader.attachToProgram(self.program)
		
		glLinkProgram(self.program)
		
		if not glGetProgramiv(self.program, GL_LINK_STATUS):
			raise ShaderError(glGetProgramInfoLog(self.program))
			
	
	def __del__(self):
		for shader in self.shaders:
			shader.detachFromProgram(self.program)
		
		glDeleteProgram(self.program)
		
		
	def uniformInt(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = ShaderUniformInt(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def uniformFloat(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = ShaderUniformFloat(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def uniformMatrix3(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = ShaderUniformMatrix3(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def uniformMatrix4(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = ShaderUniformMatrix4(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def uniformVector3(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = ShaderUniformVector3(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def uniformSampler(self, var_name):
		if var_name not in self.__dict__:
			texture_unit = self.fsTextureUnitPool.pop()
			self.__dict__[var_name] = ShaderUniformSampler(self.program, var_name, texture_unit)
		
		return self.__dict__[var_name]
		
		
	def attribute(self, var_name):
		if var_name not in self.__dict__:
			self.__dict__[var_name] = VertexAttribute(self.program, var_name)
			
		return self.__dict__[var_name]
		
		
	def use(self):
		glUseProgram(self.program)
