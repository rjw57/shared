/* c-example.c */

#include <stdlib.h> /* malloc */
#include <...>      /* load() and save() */

int main(int argc, char* argv[])
{
  unsigned char *input, *output;
  int row, col;

  input = load(); 
  output = malloc(sizeof(unsigned char) * WIDTH * HEIGHT);
  for(row = 0; row < 480; ++row)
    for(col = 0; col < 640; ++col) {
      float in =
        (float)(input[col + row*WIDTH]) / 256.f;
      float out = sqrtf(in);
      output[col + row*WIDTH] = (unsigned char)
        (out / 256.f);
    }
  save(output); 
  return 0;
}
