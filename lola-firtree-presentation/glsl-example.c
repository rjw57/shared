/* glsl-example.c */
setup_and_load_shader();
use_shader();
glBegin(GL_QUADS);
  glTexCoord2f(0,0); glVertex2f(0,0);
  glTexCoord2f(0,1); glVertex2f(0,1);
  glTexCoord2f(1,1); glVertex2f(1,1);
  glTexCoord2f(1,0); glVertex2f(1,0);
glEnd();
