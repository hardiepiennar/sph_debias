"""
Sperical coordinate debiasing functions. Coordinate systems defined by
theta phi angles are usually more dense around their theta = 0 pole 
when considering constant theta/phi steps. This library contains 
functions to generate a debiasing grid given a theta/phi coordinate 
grid. This grid can be multiplied into the theta/phi dataset before 
integration step. Therefore simplifying the aformentioned step into 
a simple summation and division operation.

Note:
    Using integrate currently has a 0.5% error against the active power 
    calculated in FEKO.

Hardie Pienaar
Bosmans Crossing
May 2018
"""

import numpy as np

def calc_coord_area(theta_grid, phi_grid):
    """
    Calculate the area for every coordinate region. A region is defined
    by a quad around the coordinate with the trapazoids spaced 
    equally between coordinates. 

    Limitations:
        1 - grid[0,0] should be theta==0 coordinate
        2 - Only handles half spheres at the moment    

    arguments:
        theta_grid - numpy array [Np, Nt] of theta points in 
                     grid format. Where Nt and Np are the number of 
                     theta and phi points respectively. [radians]
        phi_grid   - numpy array [Np, Nt] of phi points in 
                     grid format. Where Nt and Np are the number of 
                     theta and phi points respectively. [radians]

    return:
        area_grid  - numpy array [Np, Nt] of area values. The areas are
                     calculated on a unit sphere and should therefore 
                     sum to 4*pi. [m^2]
    """

    Nt = theta_grid.shape[1]  # No of theta steps
    Np = theta_grid.shape[0]  # No of phi steps

    dt = theta_grid[0,1] - theta_grid[0,0]  # Theta step in rad
    dp = phi_grid[1,0] - phi_grid[0,0]      # Phi step in rad

    area_grid = np.zeros((Np, Nt))

    # Calculate area of theta==0 pole (approximated as a spherical cap)
    # Only one of these theta==0 coords are set to non-zero. The
    # remaining phi positions are duplicates of the same point.
    area_grid[0,0] = 2*np.pi*(1-np.cos(dt/2)) 

    # Calculate band regions
    for i in range(1, Nt):
        top_height = np.cos(dt/2 + (i-1)*dt)
        if i < Nt - 1:
            bot_height = np.cos(dt/2+i*dt)
        else:
            # Stop quad at equator
            bot_height = np.cos(i*dt)
            
        band_height = top_height-bot_height
        band_area = 2*np.pi*band_height
        band_sector_area = band_area/Np

        # Insert area into grid (area stays the same for constant theta)
        area_grid[:,i] = band_sector_area

    return area_grid


def integrate(theta_grid, phi_grid, value_grid):
    """
    Integrate using a staircase approximation over the sphere. The 
    value_grid is multiplied by the area_grid and summed to perform
    a simple but fast integration.

    arguments:
        theta_grid - numpy array [Np, Nt] of theta points in 
                     grid format. Where Nt and Np are the number of 
                     theta and phi points respectively. [radians]
        phi_grid   - numpy array [Np, Nt] of phi points in 
                     grid format. Where Nt and Np are the number of 
                     theta and phi points respectively. [radians]
        value_grid - numpy array [Np, Nt] of values on the sphere that
                     need to be integrated. Example: poynting vector for
                     calculating total radiated power on an antenna 

    return:
        integrand  - result of the staircase integration over the 
                     value_grid.

    """

    area_grid = calc_coord_area(theta_grid, phi_grid)

    return np.sum(area_grid*value_grid)