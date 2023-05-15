#Add title and legend to igraph plots
from igraph import Graph, Plot
from igraph.drawing.text import TextDrawer
import cairo

shape = (4, 4)
colsep, rowsep = 40, 40
width, height = 250, 250

# Construct the plot
plot = Plot("plot.png", bbox=(4*width, 4*height), background="white")

# Create the graph and add it to the plot
for i in range(shape[0]):
    for j in range(shape[1]):
        n, radius = 20 * (1+i), 0.2 * (j+1)
        g = Graph.GRG(n, radius)
        # g['vertex_size'] = 10
        # g['vertex_label_size'] = 6
        plot.add(g, bbox=(colsep/2 + width*i, rowsep/2 + height*j, -colsep/2 + width*(i+1), -rowsep/2 + height*(j+1)))

        # Make the plot draw itself on the Cairo surface
        plot.redraw()

        ##Grab the surface, construct a drawing context, TextDrawer on surface
        # ctx = cairo.Context(plot.surface)
        # ctx.set_font_size(36)
        # drawer = TextDrawer(ctx, f'Graph.GRG({n}, {radius})', halign=TextDrawer.CENTER)
        # drawer.draw_at(width*i, 36 + height*j, width=200)
                            
plot.show()