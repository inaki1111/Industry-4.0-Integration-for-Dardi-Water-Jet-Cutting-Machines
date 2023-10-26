#!/bin/bash

# Specify the full paths to your Python scripts
script1="$HOME/send Data/startcutting.py"
script2="$HOME/send Data/recieve_sensor_data.py"

# MQTT subscription commands with the full path to mosquitto_sub
command_run_machine_state="mosquitto_sub -t machine_state"
command_run_start_process="mosquitto_sub -t start_process"
command_run_Acceleration="mosquitto_sub -t Acceleration"

# Launch MQTT subscribers in separate terminal windows
gnome-terminal -- bash -c "$command_run_machine_state; read -p 'Press Enter to exit'; exec bash"
gnome-terminal -- bash -c "$command_run_start_process; read -p 'Press Enter to exit'; exec bash"
gnome-terminal -- bash -c "$command_run_Acceleration; read -p 'Press Enter to exit'; exec bash"

# Launch Python scripts in separate terminal windows
gnome-terminal -- bash -c "python3 '$script1'; read -p 'Press Enter to exit'; exec bash"
gnome-terminal -- bash -c "python3 '$script2'; read -p 'Press Enter to exit'; exec bash"
