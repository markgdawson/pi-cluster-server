import os
import time
import settings
import model


def run_cfd_simulation(sim_id, hostfile, nprocs):
    print("run_cfd_simulation")

    # create the ELMERSOLVER_STARTINFO file
    #
    #######################################

    run_dir = model.run_directory(sim_id)
    file = open('{run_dir}/ELMERSOLVER_STARTINFO'.format(run_dir=run_dir), "w")

    file.write(settings.elmer_sif_file)
    file.write("\n1")
    file.close()

    # run the simulation with Elmer solver
    #######################################

    if (nprocs == 1):
        cmd = "ElmerSolver"
        os.system(cmd)
    else:
        # First copy the mesh files over
        cmd = 'cd {run_dir} && mpirun --hostfile hostfile -np '.format(run_dir=run_dir) + str(
            nprocs) + " ElmerSolver_mpi"
        os.system(cmd)
        time.sleep(2)

        return


##################################################
##################################################
