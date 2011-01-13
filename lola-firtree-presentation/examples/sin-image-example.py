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
lena_surface = cairo.ImageSurface.create_from_png('reduce/lena.png')

# Create a sampler for the surface
lena_sampler = ft.CairoSurfaceSampler()
lena_sampler.set_cairo_surface(lena_surface)

(sinkernel, sin_sampler) = compile_kernel("""
  kernel vec4 sinexample(sampler src)
  {
    vec2 dc = destCoord() + 5 * sin(destCoord() / 10);
    return sample(src, samplerTransform(src, dc));
  }
""")

sinkernel['src'] = lena_sampler

print ft.debug_dump_kernel_function(sinkernel)

# Create an output surface similar to the input
output_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        lena_surface.get_width(),
        lena_surface.get_height() )

# Create a CPU render engine.
engine = ft.CpuRenderer()

# Use the engine to render the output.
engine.set_sampler(sin_sampler)
engine.render_into_cairo_surface(
        lena_sampler.get_extent(), # what area to render
        output_surface             # into what
        )

# Write the output
output_surface.write_to_png('sin-example-2.png')
