#!/usr/bin/env python

import cairo
import pyfirtree as ft

def compile_kernel(source):
        """
        A simple function which compiles a kernel, checks that 
        the compilation succeeded and returns a pair containing 
        the kernel and a sampler for it. 
        """

        kernel = ft.Kernel()
        kernel.compile_from_source(source)
        if not kernel.get_compile_status():
                print("Error compiling kernel:")
                print("\n".join(kernel.get_compile_log()))
                return
        
        kernel_sampler = ft.KernelSampler()
        kernel_sampler.set_kernel(kernel)

        return (kernel, kernel_sampler)

# Firstly, load the lena image
lena_surface = cairo.ImageSurface.create_from_png('lena.png')

# Create a sampler for the surface
lena_sampler = ft.CairoSurfaceSampler()
lena_sampler.set_cairo_surface(lena_surface)

# Create a desaturate kernel.
(desat, desat_sampler) = compile_kernel("""
  kernel vec4 desaturate(sampler src)
  {
    vec4 src_colour = 
      unpremultiply( sample(src, samplerCoord(src)) );
    float luminance =
      dot(src_colour, vec4(0.299,0.587,0.114,0));
    return premultiply(
      vec4(luminance,luminance,luminance,src_colour.a)
    );
  }
""")

# Wire the lena sampler into the desaturate kernel.
desat['src'] = lena_sampler

# Create an output surface similar to the input
output_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        lena_surface.get_width(),
        lena_surface.get_height() )

# Create a CPU render engine.
engine = ft.CpuRenderer()

# Use the engine to render the output.
engine.set_sampler(desat_sampler)
engine.render_into_cairo_surface(
        lena_sampler.get_extent(), # what area to render
        output_surface             # into what
        )

# Write the output
output_surface.write_to_png('output.png')
