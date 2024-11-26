import json
import os
import subprocess
from multiprocessing import Pool

def update_l1i_settings(config_path, l1i_prefetcher, l1i_replacement):
    """
    Updates the L1I prefetcher and replacement policy in the ChampSim configuration file.

    Parameters:
    - config_path (str): Path to the champsim_config.json file.
    - l1i_prefetcher (str): New prefetcher setting for L1I.
    - l1i_replacement (str): New replacement policy for L1I.
    """
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        if 'L1I' in config:
            config['L1I']['prefetcher'] = l1i_prefetcher
            config['L1I']['replacement'] = l1i_replacement
        else:
            print("L1I configuration not found in the provided JSON file.")
            return

        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"L1I settings updated to prefetcher: {l1i_prefetcher}, replacement: {l1i_replacement} in {config_path}")

    except FileNotFoundError:
        print(f"Error: The file {config_path} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file {config_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def create_executable(config_path, prefetcher, replacement):
    """
    Creates a unique executable for each prefetcher and replacement combination.

    Parameters:
    - config_path (str): Path to the champsim_config.json file.
    - prefetcher (str): Prefetcher policy for L1I.
    - replacement (str): Replacement policy for L1I.

    Returns:
    - executable_path (str): Path to the created executable.
    """
    # Update the configuration with specific prefetcher and replacement settings
    # update_l1i_settings(config_path, prefetcher, replacement)

    # Run the config.sh script to prepare for compilation
    # subprocess.run(["./config.sh", config_path])

    # Compile ChampSim
    # subprocess.run(["make"])

    # Rename the executable to include the prefetcher and replacement identifiers
    executable_path = f"./bin/champsim_{replacement}_{prefetcher}"
    # os.rename("./bin/champsim", executable_path)
    print(f"Executable created: {executable_path}")
    return executable_path

def run_executable(executable_path, trace_file, warmup_instructions, simulation_instructions):
    """
    Runs a ChampSim executable with the specified configuration and trace file.

    Parameters:
    - executable_path (str): Path to the ChampSim executable.
    - trace_file (str): Path to the trace file.
    - warmup_instructions (int): Number of instructions for warm-up.
    - simulation_instructions (int): Number of instructions for detailed simulation.
    """
    command = [
        executable_path,
        '--warmup_instructions', str(warmup_instructions),
        '--simulation_instructions', str(simulation_instructions),
        trace_file
    ]
    try:
        s = f"./results/{executable_path.split('/')[-1]}_{trace_file.split('/')[-1]}.txt"
        print(f"Saving output to {s}")
        result = subprocess.run(command, capture_output=True, text=True)
        # print(f"Output for {executable_path}:\n{result.stdout}")
        # now save the output to a file with name as replacement_prefetcher.txt
        with open(s, 'w') as file:
            file.write(result.stdout)
    except Exception as e:
        print(f"An error occurred while running the simulation: {e}")

def automate_simulations(config_path, trace_file, warmup_instructions, simulation_instructions, prefetchers, replacements, num_cores):
    """
    Automates the creation and simulation of different combinations of L1I replacement and prefetcher policies.

    Parameters:
    - config_path (str): Path to the champsim_config.json file.
    - trace_file (str): Path to the trace file.
    - warmup_instructions (int): Number of instructions for warm-up.
    - simulation_instructions (int): Number of instructions for detailed simulation.
    - prefetchers (list): List of prefetcher policies to test.
    - replacements (list): List of replacement policies to test.
    - num_cores (int): Number of parallel processes to use for running simulations.
    """
    executable_paths = []

    # Create executables for each combination of prefetcher and replacement
    for prefetcher in prefetchers:
        for replacement in replacements:
            print(f"\nCreating executable for prefetcher: {prefetcher}, replacement: {replacement}")
            executable_path = create_executable(config_path, prefetcher, replacement)
            executable_paths.append(executable_path)

    # Run simulations concurrently using multiprocessing
    args = [(executable, trace_file, warmup_instructions, simulation_instructions) for executable in executable_paths]
    with Pool(processes=num_cores) as pool:
        pool.starmap(run_executable, args)

# Define your parameters
config_file_path = './champsim_config.json'
trace_file_path = '../traces/ipc1_public/server_022.champsimtrace.xz'
warmup_instructions = 25000000
simulation_instructions = 25000000
prefetchers = ['no_instr', 'eip', 'ip_stride', 'next_line_instr']
replacements = ['lru', 'bip', 'drrip']
num_cores = 12  # Number of parallel processes
traces = [f"../traces/ipc1_public/server_0{i}.champsimtrace.xz" for i in range(21, 29)]
# Run the automation
for trace in traces:
    print(f"\nRunning simulations for trace: {trace}")
    trace_file_path = trace
    automate_simulations(config_file_path, trace_file_path, warmup_instructions, simulation_instructions, prefetchers, replacements, num_cores)
