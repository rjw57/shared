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
        
        if kernel.get_target() == ft.KERNEL_TARGET_RENDER:
                kernel_sampler = ft.KernelSampler()
                kernel_sampler.set_kernel(kernel)
        else:
                kernel_sampler = None

        return (kernel, kernel_sampler)

# Firstly, load the lena image
lena_surface = cairo.ImageSurface.create_from_png('lena.png')

# Create a sampler for the surface
lena_sampler = ft.CairoSurfaceSampler()
lena_sampler.set_cairo_surface(lena_surface)

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
                vec4 p00 = pixel_at(src, vec2( -1, -1 ));
                vec4 p10 = pixel_at(src, vec2(  0, -1 ));
                vec4 p20 = pixel_at(src, vec2(  1, -1 ));
                vec4 p01 = pixel_at(src, vec2( -1,  0 ));
                vec4 p21 = pixel_at(src, vec2(  1,  0 ));
                vec4 p02 = pixel_at(src, vec2( -1,  1 ));
                vec4 p12 = pixel_at(src, vec2(  0,  1 ));
                vec4 p22 = pixel_at(src, vec2(  1,  1 ));

                float src_alpha = sample(src, samplerCoord(src)).a;

                // Find the sobel response in X- and Y-directions.
                vec4 dx = p00 - p20 + 2 * (p01 - p21) + p02 - p22;
                vec4 dy = p00 - p02 + 2 * (p10 - p12) + p20 - p22;

                // Calculate the magnitude of the response, we
                // multiply by 0.25 so that the filter does not
                // give a response > 1.
                vec4 mag = 0.25 * sqrt( dx*dx + dy*dy );

                return premultiply( vec4( mag.rgb, src_alpha ) );
        }
""")

edge['src'] = lena_sampler

# Create a reduce kernel which looks for areas of high red.
reduce = compile_kernel("""
        kernel __reduce void high_red(sampler src)
        {
                vec4 src_colour = unpremultiply( sample(src, samplerCoord(src)) );
                if( src_colour.r - max(src_colour.g, src_colour.b) > 0.1 ) 
                {
                        emit( vec4( destCoord(), 0, 0 ) );
                }
        }
""") [0] # Note the '[0]'

reduce['src'] = edge_sampler

# Create a CPU reduce engine.
engine = ft.CpuReduceEngine()
engine.set_kernel(reduce)

valid_extents = lena_sampler.get_extent()
valid_extents = (
        valid_extents[0] + 1, valid_extents[1] + 1,
        valid_extents[2] - 2, valid_extents[3] - 2 )

# Find the matching points
edge_points = engine.run(
        valid_extents,           # what area of the input to render
        int(valid_extents[2]),   # how many horizontal samples
        int(valid_extents[3]),   # how many vertical samples
        )

# Draw them on the surface
cr = cairo.Context(lena_surface)
cr.set_source_rgba(0,1,0,1)
for point in edge_points:
        cr.move_to(point[0] - 2, point[1] - 2)
        cr.line_to(point[0] + 2, point[1] + 2)
        cr.move_to(point[0] + 2, point[1] - 2)
        cr.line_to(point[0] - 2, point[1] + 2)
        cr.stroke()

# Write the output
lena_surface.write_to_png('output.png')
