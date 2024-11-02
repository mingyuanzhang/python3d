# python3d

The repo contains many adhoc scripts for generating stl models for 3d printing. Much of the code is written by chatGPT, with me getting the geometry correct for my purpose. Many of the models are published at thingiverse: 
https://www.thingiverse.com/flowingdust/designs

(Obviously the code is very disorganized, but once I have enough usage patterns I will clean it up and make it more reusable.)

You will need to install some libraries.

> pip install trimesh
> 
> pip install solidpython
> 
> pip install shapely
> 
> pip install matplotlib
> 
> pip install numpy

You will also need OpenScad installed.

OpenSCAD - A software for creating 3D CAD objects, needed for generating and rendering 3D text. It will also convert .scad files to .stl.

You can download it from: https://www.openscad.org/downloads.html

Once installed, ensure openscad is available in your system’s PATH so the subprocess can call it from the command line.
