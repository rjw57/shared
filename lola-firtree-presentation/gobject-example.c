/* firtree-gobject.c */

#include <firtree/firtree.h>

/* ... */

FirtreeKernel *k = firtree_kernel_new();
const char[] src = 
        "kernel vec4 redKernel() {"
        "  return vec4(1,0,0,1);"
        "}";
firtree_kernel_compile_from_source(k, &src, 1, NULL);

g_object_unref(k);
