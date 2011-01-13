#!/usr/bin/env python

import cairo
import pyfirtree as ft

# Firstly, load the lena image
lena_surface = cairo.ImageSurface.create_from_png('lena.png')

# Create a sampler for the surface
lena_sampler = ft.CairoSurfaceSampler()
lena_sampler.set_cairo_surface(lena_surface)

# Create an output surface similar to the input
output_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        lena_surface.get_width(),
        lena_surface.get_height() )

# Create a CPU render engine.
engine = ft.CpuRenderer()

# Use the engine to write the input to the output.
engine.set_sampler(lena_sampler)
engine.render_into_cairo_surface(
        lena_sampler.get_extent(), # what area to render
        output_surface             # into what
        )

# Write the output
output_surface.write_to_png('output.png')
