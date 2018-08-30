/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                             *
* Copyright (c) 2016                                                          *
*                                                                             *
* Permission is hereby granted, free of charge, to any person obtaining a     *
* copy of this software and associated documentation files (the "Software"),  *
* to deal in the Software without restriction, including without limitation   *
* the rights to use, copy, modify, merge, publish, distribute, sublicense,    *
* and/or sell copies of the Software, and to permit persons to whom the       *
* Software is furnished to do so, subject to the following conditions:        *
*                                                                             *
* The above copyright notice and this permission notice shall be included in  *
* all copies or substantial portions of the Software.                         *
*                                                                             *
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  *
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    *
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE *
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      *
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     *
* FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         *
* DEALINGS IN THE SOFTWARE.                                                   *
*                                                                             *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

#version 330 core


in vec2 uv;
in vec3 normal;
in vec3 modelPosition;
in vec4 modelPositionLightView[@NUM_LIGHTS@];

out vec4 colour;


uniform bool use3d;
uniform bool useLighting;

uniform vec3 cameraPosition;

uniform sampler2D matTextureSampler;
uniform float     matAlpha          = 1.0;
uniform vec3      matAmbientColour  = vec3(1.0, 1.0, 1.0);
uniform vec3      matDiffuseColour  = vec3(1.0, 1.0, 1.0);
uniform vec3      matSpecularColour = vec3(1.0, 1.0, 1.0);

uniform float ambientLightAmplitude = float(0.0);
uniform vec3  ambientLightColour    = vec3(1.0, 1.0, 1.0);

uniform int       lightType[@NUM_LIGHTS@];
uniform vec3      lightVector[@NUM_LIGHTS@];
uniform float     lightAmplitude[@NUM_LIGHTS@];
uniform vec3      lightColour[@NUM_LIGHTS@];
uniform sampler2D lightShadowMapSampler[@NUM_LIGHTS@];


float calculate_shadow_coef(vec4      model_pos_light_view,
                            sampler2D shadow_map_sampler,
                            vec3      light_direction)
{
	vec3 model_pos_light_view_proj = (model_pos_light_view.xyz/model_pos_light_view.w)*0.5 + 0.5;
	float frag_depth = model_pos_light_view_proj.z;
	
	if (frag_depth > 1.0) return 0.0;
	
	float bias = 0.002;//max(0.002*(1.0 - dot(normal, light_direction)), 0.0002);
	//bias *= 1.0 - dot(normal, light_direction);
	float shadow_coef = 0.0;
	vec2 texel_size = 1.0/textureSize(shadow_map_sampler, 0);
	
	for (int x = -1; x <= 1; x++)
	{
		for (int y = -1; y <= 1; y++)
		{
			vec2 frag_coords = model_pos_light_view_proj.xy + vec2(x, y)*texel_size;
			float light_depth = texture(shadow_map_sampler, frag_coords).r;
			shadow_coef += frag_depth-bias > light_depth ? 1.0 : 0.0;
		}
	}
	
	shadow_coef /= 9.0;
	
	//float light_depth = texture(shadow_map_sampler, model_pos_light_view_proj.xy).r;
	//float bias = 0.002;//max(0.002*(1.0 - dot(normal, light_direction)), 0.0002);
	////bias *= 1.0 - dot(normal, light_direction);
	//
	////float shadow_coef = (frag_depth-bias) > light_depth ? 1.0 : 0.0;
	//float shadow_coef = frag_depth-bias > light_depth ? 1.0 : 0.0;
	////if (frag_depth > 1.0) shadow_coef = 0.0;
	
	return shadow_coef;
}


vec3 calculate_diffuse_light(vec3 base_colour,
                             vec3 colour_amplitude,
                             vec3 light_direction,
                             vec3 normalized_normal)
{
	float normal_coef = clamp(dot(normalized_normal, -light_direction), 0.0, 1.0);
	return normal_coef*base_colour*matDiffuseColour*colour_amplitude;
}


vec3 calculate_specular_light(vec3 base_colour,
                              vec3 colour_amplitude,
                              vec3 camera_direction,
                              vec3 light_direction,
                              vec3 normalized_normal)
{
	float specular_coef = clamp(dot(camera_direction, reflect(light_direction, normalized_normal)), 0.0, 1.0);
	return pow(specular_coef, 10)*matSpecularColour*colour_amplitude;
}


vec3 apply_lighting(vec3 base_colour)
{
	vec3 lit_colour = vec3(0.0, 0.0, 0.0);
	vec3 camera_direction = normalize(cameraPosition-modelPosition);
	vec3 normalized_normal = normalize(normal);
	float shadow_coef;
	vec3 shadowed_light;
	int i;
	
	for (i = 0; i < @NUM_LIGHTS@; i++)
	{
		switch (lightType[i])
		{
		case 1: // directional
			shadow_coef = calculate_shadow_coef(modelPositionLightView[i],
			                                    lightShadowMapSampler[i],
			                                    lightVector[i]);
			shadowed_light = lightColour[i]*(1.0 - shadow_coef);
			
			lit_colour += calculate_diffuse_light(base_colour,
			                                      shadowed_light,
			                                      lightVector[i],
			                                      normalized_normal);
		
			lit_colour += calculate_specular_light(base_colour,
			                                       shadowed_light,
			                                       camera_direction,
			                                       lightVector[i],
			                                       normalized_normal);
			break;
		
		case 2: // point
			vec3 light_to_model = modelPosition-lightVector[i];
			float r = length(light_to_model);
			
			vec3 colour_amplitude = lightColour[i]/((0.1/lightAmplitude[i])*r*r+(1/(lightAmplitude[i]*lightAmplitude[i]))*r+1);
			vec3 specular_amplitude = colour_amplitude*lightAmplitude[i];
			vec3 light_direction = normalize(light_to_model);
			
			lit_colour += calculate_diffuse_light(base_colour,
			                                      colour_amplitude,
			                                      light_direction,
			                                      normalized_normal);
		
			lit_colour += calculate_specular_light(base_colour,
			                                       specular_amplitude,
			                                       camera_direction,
			                                       light_direction,
			                                       normalized_normal);
			break;
		}
	}
	
	lit_colour += base_colour*ambientLightColour*ambientLightAmplitude;
	
	return lit_colour;
}


void main()
{
	vec3 tex_colour = texture(matTextureSampler, uv).rgb;
	if (useLighting)
	{
		colour = vec4(apply_lighting(tex_colour), matAlpha);
	}
	else
	{
		//colour = vec4(vec3(texture(lightShadowMapSampler[0], uv).r), matAlpha);
		colour = vec4(matDiffuseColour*tex_colour, matAlpha);
	}
}
