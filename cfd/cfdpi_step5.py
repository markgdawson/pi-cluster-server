import model
import settings
import os


def generate_vtk_files(sim_id, nprocs):
    print("generate_vtk_files")

    project_dir = model.run_directory(sim_id)

    if (nprocs == 1):
        fname_nodes = "simulation/mesh.nodes"
        fname_elems = "simulation/mesh.elements"
        fname_field = "simulation/ElmerOutput.ep"

        cmd = settings.elmer_postprocess_serial_exe + " " + fname_nodes + " " + fname_elems + " " + fname_field
    else:
        fname_elems = "simulation/partitioning." + str(nprocs) + "/part"
        fname_field = "simulation/ElmerOutput"
        cmd = f'cd {project_dir} && ' + \
              settings.elmer_postprocess_parallel_exe + \
              " " + fname_elems + " " + fname_field + " " + str(nprocs)

    os.system(cmd)

    return


##################################################
##################################################