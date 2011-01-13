#!/usr/bin/env python

import cairo
import pyfirtree as ft

def compile_kernel(source):
        """
        A simple function which compiles a kernel, checks that the
        compilation succeeded and returns a pair containing the kernel and a
        sampler for it. 
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
                vec4 src_colour = unpremultiply( sample(src, samplerCoord(src)) );
                float luminance = dot(src_colour, vec4(0.299,0.587,0.114,0));
                return premultiply(
                        vec4(luminance,luminance,luminance,src_colour.a)
                );
        }
""")

# Wire the lena sampler into the desaturate kernel.
desat['src'] = lena_sampler

# Create an edge detector kernel.
(edge, edge_sampler) = compile_kernel("""
        // Return the (unpremultiplied) value of the pixel
        // at a particular offset.
        vec4 pixel_at(sampler src, vec2 offset) 
        {
                return unpremultiply( sample( src,
                        samplerTransform( src, destCoord() + offset) ) );
        }

        kernel vec4 edge_detect(sampler src)
        {
                // We use a sobel filter. This works on the 3x3 neighbourhood
                // of the pixel.

                // Get the neighbourhood.
                float p00 = pixel_at(src, vec2( -1, -1 )).r;
                float p10 = pixel_at(src, vec2(  0, -1 )).r;
                float p20 = pixel_at(src, vec2(  1, -1 )).r;
                float p01 = pixel_at(src, vec2( -1,  0 )).r;
                float p21 = pixel_at(src, vec2(  1,  0 )).r;
                float p02 = pixel_at(src, vec2( -1,  1 )).r;
                float p12 = pixel_at(src, vec2(  0,  1 )).r;
                float p22 = pixel_at(src, vec2(  1,  1 )).r;

                float src_alpha = sample(src, samplerCoord(src)).a;

                // Find the sobel response in X- and Y-directions.
                float dx = p00 - p20 + 2 * (p01 - p21) + p02 - p22;
                float dy = p00 - p02 + 2 * (p10 - p12) + p20 - p22;

                // Calculate the magnitude of the response, we
                // multiply by 0.25 so that the filter does not
                // give a response > 1.
                float mag = 0.25 * length( vec2( dx, dy ) );

                return premultiply(
                        vec4(mag,mag,mag,src_alpha)
                );
        }
""")

edge['src'] = desat_sampler

# Create an output surface similar to the input
output_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        lena_surface.get_width(),
        lena_surface.get_height() )

# Create a CPU render engine.
engine = ft.CpuRenderer()

# Use the engine to render the output.
engine.set_sampler(edge_sampler)
engine.render_into_cairo_surface(
        lena_sampler.get_extent(), # what area to render
        output_surface             # into what
        )

# Write the output
output_surface.write_to_png('output.png')
