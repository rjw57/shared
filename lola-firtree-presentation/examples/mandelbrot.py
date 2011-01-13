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

# Create a kernel which computes the mandelbrot set
(mandelbrot, mandelbrot_sampler) = compile_kernel("""
  vec2 complex_mul(vec2 a, vec2 b) {
    return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x);
  }

  kernel vec4 mandelbrot()
  {
    int max_iterations = 40;
    vec2 c = destCoord(), z = c;

    int num_its;
    float mag_z_sq = dot(z,z);
    for(num_its = 0; 
     (num_its < max_iterations) && (mag_z_sq < 4.0); ++num_its) {
        z = complex_mul(z,z) + c;
        mag_z_sq = dot(z,z);
    }

    float output_val = num_its / max_iterations;
    return vec4(output_val, output_val, output_val, 1);
  }
""")

# Create the output surface, render into it and save
output_surface = cairo.ImageSurface( 
        cairo.FORMAT_ARGB32, 
        1200, 800 )
engine = ft.CpuRenderer()
engine.set_sampler(mandelbrot_sampler)
engine.render_into_cairo_surface(
        (-2, -1, 3, 2),  # what area to render
        output_surface   # into what
        )
output_surface.write_to_png('mandelbrot.png')
