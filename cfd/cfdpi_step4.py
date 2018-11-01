
import os


def step4_run_cfd_simulation(project_name, hostfile, nprocs):
    print("step4_run_cfd_simulation")

    project_dir="./" + project_name + "/"

    # create the ELMERSOLVER_STARTINFO file
    #
    #######################################
    #os.chdir(project_dir)

    file = open("ELMERSOLVER_STARTINFO", "w") 

    sif_fname = project_name + ".sif"

    file.write(sif_fname) 
    file.write("\n1") 
    file.close()

    # copy the .sif file
    #######################################

    cmd="cp ../test.sif " + sif_fname
    os.system(cmd)

    # run the simulation with Elmer solver
    #######################################

    if(nprocs == 1):
      cmd="ElmerSolver"
    else:
      # Here copy the files over to pi@10.0.0.254:/nfs/nodeimg/home/pi/
      cmd="mpirun --hostfile ../"+hostfile+" -np "+ str(nprocs) + " ElmerSolver_mpi"
    os.system(cmd)

    return
##################################################
##################################################

