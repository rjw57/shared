/* glsl-example.glsl */
uniform sampler2D inputTex;

vec4 shader_function()
{
  vec2 pixel_coord = gl_MultiTexCoord[0];
  vec4 input = texture2D(inputTex, pixel_coord);
  return sqrt(input);
}
