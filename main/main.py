import subprocess

# List of Python scripts to run
scripts = ["/home/cimatec/Documentos/Sistema-de-industria-4.0-/live stream/main.py", "/home/cimatec/Documentos/Sistema-de-industria-4.0-/send Data/machine_state.py"]

# Create a list to hold the subprocesses
processes = []

# Start each script
for script in scripts:
    processes.append(subprocess.Popen(["python3", script]))

# Wait for all scripts to complete
for process in processes:
    process.wait()
