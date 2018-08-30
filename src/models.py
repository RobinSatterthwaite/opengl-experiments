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

from numpy import array, identity, zeros, ones
from OpenGL.GL import *

import pyassimp

from materials import Material, AssimpMaterial

from matrix_transforms import *



class Mesh(object):
	"""
	This object encapsulates the opengl buffers that are needed for a specific 3d
	mesh.  These include the vertex, UV, normal and index buffers.  It also
	provides a vertex array object for binding these in a single call.  The
	material is also owned by the mesh object.
	"""

	def __init__(self, vertex_buf_data, uv_buf_data, normal_buf_data, index_buf_data, material):
		self.vao = glGenVertexArrays(1)
		
		self.vertexBuf, self.uvBuf, self.normalBuf, self.indexBuf = glGenBuffers(4)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuf)
		glBufferData(GL_ARRAY_BUFFER, vertex_buf_data, GL_STATIC_DRAW)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.uvBuf)
		glBufferData(GL_ARRAY_BUFFER, uv_buf_data, GL_STATIC_DRAW)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.normalBuf)
		glBufferData(GL_ARRAY_BUFFER, normal_buf_data, GL_STATIC_DRAW)
		
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuf)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, array(index_buf_data, dtype='uint16'), GL_STATIC_DRAW)
		
		self.material = material
		
		self.numIndices = len(index_buf_data)
		
		
	def __del__(self):
		glDeleteBuffers(4, [self.vertexBuf, self.uvBuf, self.normalBuf, self.indexBuf])
		glDeleteVertexArrays(1, [self.vao])
		
		
	def bindAttributes(self, shader_program):
		# type: (ShaderProgram) -> None
		"""
		Binds the mesh's vao and binds the buffers to the attribute points in the
		shader program.  After this is done the mesh can be bound simply by binding
		the vao.
		"""
		glBindVertexArray(self.vao)
		
		shader_program.vertexPosition.enable()
		glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuf)
		glVertexAttribPointer(shader_program.vertexPosition.location,
		                      3, GL_FLOAT, False, 0, None)
		
		shader_program.vertexUv.enable()
		glBindBuffer(GL_ARRAY_BUFFER, self.uvBuf)
		glVertexAttribPointer(shader_program.vertexUv.location,
		                      2, GL_FLOAT, False, 0, None)
		
		shader_program.vertexNormal.enable()
		glBindBuffer(GL_ARRAY_BUFFER, self.normalBuf)
		glVertexAttribPointer(shader_program.vertexNormal.location,
		                      3, GL_FLOAT, False, 0, None)
		
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuf)
		
		
	def draw(self):
		""" Bind the texture and vertex array object, then draw the elements. """
		#glActiveTexture(GL_TEXTURE0)
		#glBindTexture(GL_TEXTURE_2D, self.material.texture)
		
		glBindVertexArray(self.vao)
		glDrawElements(GL_TRIANGLES, self.numIndices, GL_UNSIGNED_SHORT, None)
		

		
#class TestMesh(Mesh):
#	def draw(self):
#		super(TestMesh, self).draw()
#		import sys
#		sys.stderr.write(str(self.numIndices)+'\n')




class Model(object):
	"""
	The model object encapsulates a number of meshes that make up the model and
	the model matrix defining the models position, orientation and scaling.
	"""
	
	def __init__(self):
		self.meshes = []
		self._pos = zeros(3)
		self._rot = zeros(3)
		self._scl = ones(3)
	
	
	def scale(self, s):
		self._scl *= s
	
	def translate(self, t):
		self._pos += t
		
	def rotate(self, r):
		self._rot += r
	
	
	def matrix(self, input_matrix):
		""" Returns the model matrix for use by the shader program. """
		matrix = input_matrix.copy()
		m_translate_in_place(matrix, self._pos)
		m_rotate_in_place   (matrix, self._rot)
		m_scale_in_place    (matrix, self._scl)
		return matrix



class AssimpModel(Model):
	"""
	This model class is initialised from an AssImp scene.
	"""
	
	def __init__(self, ai_scene):
		super(AssimpModel, self).__init__()
		
		materials = [AssimpMaterial(ai_mat) for ai_mat in ai_scene.materials]
		
		for ai_mesh in ai_scene.meshes:
			#import sys
			#sys.stderr.write(repr(ai_mesh.__dict__.keys())+'\n')
			
			# texturecoords is returned as an array of 3 elements, but we only want the first 2
			uv_buf_data = [coord for uv_coords in ai_mesh.texturecoords[0] for coord in uv_coords[0:2]]
			
			self.meshes.append(Mesh(ai_mesh.vertices.flatten(),
			                        array(uv_buf_data, dtype='float32'),
															ai_mesh.normals.flatten(),
															ai_mesh.faces.flatten(),
			                        materials[ai_mesh.materialindex]))

	

class UiModel(Model):

	def __init__(self, mat = None):
		super(UiModel, self).__init__()
		
		if mat == None:
			mat = Material([1.,1.,1.])
			mat.alpha = 0.5
		
		self.meshes.append(Mesh(array([[.5,.5,0.], [-.5,.5,0.], [-.5,-.5,0.], [.5,-.5,0.]], dtype='float32').flatten(),
		                        array([[1.,1.],    [0.,1.],     [0.,0.],      [1.,0.]    ], dtype='float32').flatten(),
		                        array([[0.,0.,0.], [0.,0.,0.],  [0.,0.,0.],   [0.,0.,0.] ], dtype='float32').flatten(),
		                        array([[0,1,2], [2,3,0], [0,2,1], [2,0,3]], dtype='uint16').flatten(),
		                        mat))