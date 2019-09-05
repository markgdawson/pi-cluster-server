##################################################################
#
# Complete wrapper for running CFD jobs on Pi
#
# Author:    Dr Chennakesava Kadapa
# Date:      17-Oct-2018
# Copyright: @SA2C
##################################################################

#
# Step 1: Knect          -->   Depth Map
# Step 2: Depth Map      -->   Model Outline
# Step 3: Model Outline  -->   CFD Mesh
# Step 4: CFD Mesh       -->   CFD Results
# Step 5: CFD Results    -->   VTK files
# Step 6: VTK files      -->   Images
#
#
##################################################

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cfdpi_step3 import *
from cfdpi_step4 import *
from cfdpi_step5 import *
from createcontoureps import *
import computedrag
import model

# Read the project name and other flags from the command line arguments
#

# Default entries
sim_id = "Square"
nprocs = 1
hostfile = "hostfile1"

if len(sys.argv) > 1:
    sim_id = sys.argv[1]

if len(sys.argv) > 2:
    nprocs = int(sys.argv[2])

if len(sys.argv) > 3:
    hostfile = sys.argv[3]

print("Starting Step 1 (Model Outline  -->  CFD Mesh)")
print("###################################################################\n")
#
# Step 1: Read the outline and generate the mesh
#
#################################################

generate_mesh_from_outline(sim_id, nprocs)

print("Step 1 completed successfully\n\n")
print("Starting Step 2 (CFD Mesh  -->  CFD Results)")
print("###################################################################\n")
#
# Step 2: Run Elmer with the mesh file generated in Step 1
#
##########################################################

run_cfd_simulation(sim_id, hostfile, nprocs)

print("Step 2 completed successfully\n\n")
print("Starting Step 3 (CFD Results  -->  VTK files)")
print("###################################################################\n")
#
# Step 3: Create .vtk files from Elmer output
#
#####################################################

generate_vtk_files(sim_id, nprocs)

print("Step 3 completed successfully\n\n")
print("Starting Step 4 (VTK files  -->  Images)")
print("###################################################################\n")
#
# Step 4: Process .vtk files and generate images for visualisation
#
##################################################################

num_timesteps = 10

generate_images_vtk(sim_id, nprocs, num_timesteps)

print("Step 4 completed successfully\n\n")
print("Starting Step 5 (Compute drag)")
print("###################################################################\n")
#
# Step 5: Compute drag from simulation output
#
##################################################################

drag = computedrag.compute_drag(sim_id, nprocs, num_timesteps)

model.set_drag(sim_id, drag)


print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")
