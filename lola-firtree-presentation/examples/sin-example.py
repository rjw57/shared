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

(sinkernel, sin_sampler) = compile_kernel("""
  kernel vec4 sinexample()
  {
    return vec4( 0.5 + 0.5 * sin( destCoord() ), 0, 1 );
  }
""")

print ft.debug_dump_sampler_function(sin_sampler)

# Create an output surface similar to the input
output_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        300, 300)

# Create a CPU render engine.
engine = ft.CpuRenderer()

# Use the engine to render the output.
engine.set_sampler(sin_sampler)
engine.render_into_cairo_surface(
        (0,0,20,20),
        output_surface             # into what
        )

# Write the output
output_surface.write_to_png('sin-example.png')
