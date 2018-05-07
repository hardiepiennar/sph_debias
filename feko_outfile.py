"""
Functions to read data from outfile. Some of the scraping functions are a bit 
cowboy, but it works.

Hardie Pienaar
Cavendish Lab
March 2018 

Would be nice to have:
Load geometry connectivity data with basis functions
VSH loading function
Farfield loading function
"""

import numpy as np

def load_wire_currents(feko_filename):
    """
    Reads a feko .out file and extracts the wire currents. The wire currents
    are stored in a dictionary dataset. 
    
    arguments:
        feko_filename

    returns: 
        dataset - list of {Frequency, Data}(see dictionary layout below)

    Data = {Segment, X, Y, Z, Current_X, Current_Y, Current_Z}
    Frequency - frequency in Hz
    Segment - Wire segment number
    X,Y,Z - spatial coordinates in m
    Current_X,Y,Z - complex currents in each axis
    Length - length of wire segment in m
    """

    # Initialise logic
    found_currents_start = False
    segment_data_countdown = -1


    # Create storage structures
    frequency = 0
    dataset = []
    length = []

    # Open file and start reading
    f = open(feko_filename,'r')

    # Loop over every row in the file
    with open(feko_filename) as f:
        for line in f:
            # Filter empty strings
            row_raw = line.split(' ')
            row = list(filter(None, row_raw))

            # Read the currents into the current frequency object
            if found_currents_start and len(row) != 1:
                seg_no.append(int(row[0]))
                pos_x.append(float(row[1]))
                pos_y.append(float(row[2]))
                pos_z.append(float(row[3]))
                curr_x.append(float(row[4])*np.exp(1j*np.pi/180*float(row[5])))
                curr_y.append(float(row[6])*np.exp(1j*np.pi/180*float(row[7])))
                curr_z.append(float(row[8])*np.exp(1j*np.pi/180*float(row[9])))





            # Logic to detect certain parts of the file
            # Scrape logic to grab line lengths
            if segment_data_countdown == 0: # Store length
                length.append(float(row[5]))
                segment_data_countdown = 3
            if segment_data_countdown >= 0: # Skip until we reach length data
                segment_data_countdown = segment_data_countdown - 1
            if "SEGMENTS\n" in row and len(row)==4: # Detect the start of length data
                segment_data_countdown = 5
                length = []
            if len(row) == 1 and len(length) > 0: # Detect the end of length data
                segment_data_countdown = -1 
            if "Frequency" in row and frequency != float(row[5]):
                frequency = float(row[5])
                print("Reading freq: "+str(frequency/1e6)+" MHz", end="\r")
            if "x/m" in row and len(row) == 10: # Start of wire data
                found_currents_start = True
                 # Create intemedietary storage variables
                seg_no = []
                pos_x = []
                pos_y = []
                pos_z = []
                curr_x = []
                curr_y = []
                curr_z = []
            elif found_currents_start and len(row) == 1:
                found_currents_start = False

                # Create the data block and append it to our dataset
                data = {"Segment":np.array(seg_no), 
                        "X":np.array(pos_x), 
                        "Y":np.array(pos_y), 
                        "Z":np.array(pos_z),
                        "Length":np.array(length),
                        "Current_X":np.array(curr_x), 
                        "Current_Y":np.array(curr_y), 
                        "Current_Z":np.array(curr_z)}
                dataset.append({"Frequency":frequency, "Data":data.copy()})


                frequency == None

    return dataset

def load_rwg_currents(feko_filename):
    """
    Reads a feko .out file and extracts the currents on triangle basis functions. The trianlge currents
    are stored in a dictionary dataset. 
    
    arguments:
        feko_filename

    returns: 
        dataset - list of {Frequency, Data}(see dictionary layout below)

    Data = {Segment, X, Y, Z, Current_X, Current_Y, Current_Z}
        Frequency - frequency in Hz
        Segment - Triangle number
        X,Y,Z - spatial coordinates in m
        Current_X,Y,Z - complex currents in each axis
        Triangle_1,2,3 - spatial coordinates for triangle points
        Area - area of triangle in m^2
    """

    # Initialise logic
    found_currents_start = False
    segment_data_countdown = -1


    # Create storage structures
    frequency = 0
    dataset = []
    length = []
    trianlge_1 = []
    trianlge_2 = []
    trianlge_3 = []

    # Open file and start reading
    f = open(feko_filename,'r')

    # Loop over every row in the file
    with open(feko_filename) as f:
        for line in f:
            # Filter empty strings
            row_raw = line.split(' ')
            row = list(filter(None, row_raw))

            # Read the currents into the current frequency object
            if found_currents_start and len(row) != 1:
                seg_no.append(int(row[0]))
                pos_x.append(float(row[1]))
                pos_y.append(float(row[2]))
                pos_z.append(float(row[3]))
                curr_x.append(float(row[4])*np.exp(1j*np.pi/180*float(row[5])))
                curr_y.append(float(row[6])*np.exp(1j*np.pi/180*float(row[7])))
                curr_z.append(float(row[8])*np.exp(1j*np.pi/180*float(row[9])))

            # Logic to detect certain parts of the file
            # Scrape logic to grab line lengths
            if segment_data_countdown == 0: # Store length
                length.append(float(row[3]))
                segment_data_countdown = 4
            if  segment_data_countdown == 1 and len(row) > 1:
                triangle_3.append([float(row[2]), float(row[3]), float(row[4])])
            if  segment_data_countdown == 2 and len(row) > 1:
                triangle_2.append([float(row[2]), float(row[3]), float(row[4])])
            if  segment_data_countdown == 3 and len(row) > 1:
                triangle_1.append([float(row[2]), float(row[3]), float(row[4])])
                
            if segment_data_countdown >= 0: # Skip until we reach length data
                segment_data_countdown = segment_data_countdown - 1
            if "TRIANGLES\n" in row and len(row)==5: # Detect the start of length data
                segment_data_countdown = 8
                length = []  
                triangle_1 = []
                triangle_2 = []
                triangle_3 = []
            if len(row) == 1 and len(length) > 0: # Detect the end of length data
                segment_data_countdown = -1 
            if "Frequency" in row and frequency != float(row[5]):
                frequency = float(row[5])
                print("Reading freq: "+str(frequency/1e6)+" MHz", end="\r")
            if "x/m" in row and len(row) == 13: # Start of wire data
                found_currents_start = True
                 # Create intemedietary storage variables
                seg_no = []
                pos_x = []
                pos_y = []
                pos_z = []
                curr_x = []
                curr_y = []
                curr_z = []
            elif found_currents_start and len(row) == 1:
                found_currents_start = False

                # Create the data block and append it to our dataset
                data = {"Segment":np.array(seg_no), 
                        "X":np.array(pos_x), 
                        "Y":np.array(pos_y), 
                        "Z":np.array(pos_z),
                        "Triangle_1":np.array(triangle_1),
                        "Triangle_2":np.array(triangle_2),
                        "Triangle_3":np.array(triangle_3),
                        "Area":np.array(length),
                        "Current_X":np.array(curr_x), 
                        "Current_Y":np.array(curr_y), 
                        "Current_Z":np.array(curr_z)}
                dataset.append({"Frequency":frequency, "Data":data.copy()})


                frequency == None

    return dataset

def load_farfield(feko_filename):
    """
    Reads a feko .out file and extracts the farfield data
    
    arguments:
        feko_filename

    returns: 
        dataset - list of {Frequency, Data}(see dictionary layout below)

    Data = {Theta, Phi, E_Theta, E_Phi}
        Theta - numpy array of angles in radians
        Phi = numpy array of angles in radians
        E_Theta = numpy array of electric fields (Farfield approx V/m) 
        E_Phi = numpy array of electric fields (Farfield approx V/m) 
    """

    # Initialise logic
    found_farfield_start = False

    # Create storage structures
    frequency = 0
    dataset = []
    theta = []
    phi = []
    e_theta = []
    e_phi = []

    # Open file and start reading
    f = open(feko_filename,'r')

    # Loop over every row in the file
    with open(feko_filename) as f:
        for line in f:
            # Filter empty strings
            row_raw = line.split(' ')
            row = list(filter(None, row_raw))

            # Read the currents into the current frequency object
            if found_farfield_start and len(row) != 1:
                theta.append(float(row[0])*np.pi/180)
                phi.append(float(row[1])*np.pi/180)
                e_theta.append(float(row[2])*np.exp(1j*float(row[3])*np.pi/180))
                e_phi.append(float(row[4])*np.exp(1j*float(row[5])*np.pi/180))

            # Logic to detect certain parts of the file
            if "Frequency" in row and frequency != float(row[5]):
                frequency = float(row[5])
                print("Reading freq: "+str(frequency/1e6)+" MHz", end="\r")
            if "THETA" in row and len(row)==13: # Detect the start of length data
                theta = []  
                phi = []
                e_theta = []
                e_phi = []
                found_farfield_start = True
            elif found_farfield_start and len(row) == 1:
                found_farfield_start = False

                # Create the data block and append it to our dataset
                data = {"Theta":np.array(theta), 
                        "Phi":np.array(phi), 
                        "E_Theta":np.array(e_theta), 
                        "E_Phi":np.array(e_phi)}
                dataset.append({"Frequency":frequency, "Data":data.copy()})

                frequency == None

    return dataset