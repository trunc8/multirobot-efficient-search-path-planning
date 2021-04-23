from igraph import Graph, Plot
from igraph.drawing.text import TextDrawer
import cairo

# Construct the plot
plot = Plot("plot.png", bbox=(600, 650), background="white")

# Create the graph and add it to the plot
g = Graph.GRG(100, 0.2)
plot.add(g, bbox=(20, 70, 580, 630))

# Make the plot draw itself on the Cairo surface
plot.redraw()

# Grab the surface, construct a drawing context and a TextDrawer
ctx = cairo.Context(plot.surface)
ctx.set_font_size(36)
drawer = TextDrawer(ctx, "Test title", halign=TextDrawer.CENTER)
drawer.draw_at(0, 40, width=600)

# Save the plot
plot.save()