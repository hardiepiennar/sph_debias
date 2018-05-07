import unittest
import sph_debias as sphdebias
import numpy as np

class Tests(unittest.TestCase):
    def test_calc_coord_area(self):
        # Test the calculation of the coordinate region area calculation
        theta = np.linspace(0,np.pi/2,3)
        phi = np.linspace(0,2*np.pi,4)
        theta_grid, phi_grid = np.meshgrid(theta, phi)
        
        area_grid = sphdebias.calc_coord_area(theta_grid, phi_grid)
        # Test the shape of the output matrix
        self.assertEqual(area_grid.shape, theta_grid.shape) 

        # Test the cap area [0, 0]
        dt = np.pi/2/(3-1)
        dp = 2*np.pi/(4-1)
        cap_rad = np.sin(dt/2)
        self.assertEqual(area_grid[0,0], 2*np.pi*(1-np.cos(dt/2)) )

        # Test redundant theta==0 coords (should all be zero)
        self.assertEqual(np.sum(area_grid[1:,0]), 0)

        # Test first quad calculation
        top_height = np.cos(dt/2)
        bot_height = np.cos(dt/2+dt)
        height = top_height-bot_height
        band_area = 2*np.pi*height
        band_sector_area = band_area/4
        self.assertEqual(area_grid[0,1], band_sector_area)

        # Test half quad exception at 90 degree point
        top_height = np.cos(dt/2+dt)
        bot_height = np.cos(dt*2)
        height = top_height-bot_height
        band_area = 2*np.pi*height
        band_sector_area = band_area/4
        self.assertEqual(area_grid[0,-1], band_sector_area)

        # Make sure the area of all the sectors add up to the area of 
        # a sphere (half)
        self.assertEqual(np.sum(area_grid), 4*np.pi/2)

    def test_integrate(self):
        # Test the accuracy of the integration to results from a FEKO
        # simulation. Very weak test.
        # Load test data from FEKO file
        import feko_outfile as fo 
        farfield = fo.load_farfield("test_model.out")
        theta = farfield[0]["Data"]["Theta"]
        phi = farfield[0]["Data"]["Phi"]
        e_theta = farfield[0]["Data"]["E_Theta"]
        e_phi = farfield[0]["Data"]["E_Phi"]

        # Wrangle the data into our preferred grid format
        theta_pts = np.count_nonzero(phi == 0)
        phi_pts = np.count_nonzero(theta == 0)
        theta_grid = theta.reshape(phi_pts, theta_pts)
        phi_grid = phi.reshape(phi_pts, theta_pts)
        e_theta_grid = e_theta.reshape(phi_pts, theta_pts)
        e_phi_grid = e_phi.reshape(phi_pts, theta_pts)

        # Calculate poynting vector
        eta = 376.730313
        e_tot = np.sqrt(e_theta_grid*np.conj(e_theta_grid) + \
                           e_phi_grid*np.conj(e_phi_grid))
        poynting = np.abs(e_tot)**2/eta
        poynting = np.real(poynting)

        # Integrate to get power
        power = sphdebias.integrate(theta_grid, phi_grid, poynting)/2
        print(power)
        self.assertAlmostEqual(power, 8.5e-3,1)        

if __name__ == '__main__':
    unittest.main()