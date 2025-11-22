import matplotlib.image as mpimg
import numpy as np

def domain(map_file, Nx:int=None, Ny:int=None):
    map = mpimg.imread(map_file) # read map data
    # ---------------------------
    # Domain / discretization
    # ---------------------------
    # Lx, Ly = 1000.0, 600.0   # domain size in meters (downwind x, crosswind y)
    # Nx, Ny = 201, 121        # grid cells
    Lx, Ly = map.shape[1], map.shape[0]
    if Nx is None:
        Nx = Lx
    if Ny is None:
        Ny = Ly
    dx = Lx / (Nx - 1)
    dy = Ly / (Ny - 1)
    x = np.linspace(0, Lx, Nx)
    y = np.linspace(-Ly/2, Ly/2, Ny)
    return map, x, y, Lx, Ly, Nx, Ny, dx, dy