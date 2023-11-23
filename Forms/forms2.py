import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json

class MachineMonitor(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window, padding=(20, 10))
        self.pack(fill=tk.BOTH, expand=tk.YES)

        self.piezas_cortadas = tk.StringVar(value="")
        self.piezas_defectuosas = tk.StringVar(value="")
        self.selected_option = tk.StringVar(value="Funcionamiento normal")
        
        title_text = "Monitoreo de la Máquina"
        title = ttk.Label(self, text=title_text, font=("Helvetica", 20), anchor='center')
        title.pack(pady=10)

        self.create_form_entry("Piezas Cortadas:", self.piezas_cortadas)
        self.create_form_entry("Piezas Defectuosas:", self.piezas_defectuosas)
        self.create_option_menu("Estado de la Máquina:", self.selected_option)

        submit_btn = ttk.Button(
            self,
            text="Enviar",
            command=self.on_submit,
        )
        submit_btn.pack(pady=10)

    def create_form_entry(self, label, variable):
        form_field_container = ttk.Frame(self)
        form_field_container.pack(fill=tk.X, pady=5)

        form_field_label = ttk.Label(master=form_field_container, text=label, anchor="w")
        form_field_label.pack(side=tk.LEFT, padx=12)

        form_input = ttk.Entry(master=form_field_container, textvariable=variable)
        form_input.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)

    def create_option_menu(self, label, variable):
        option_menu_container = ttk.Frame(self)
        option_menu_container.pack(fill=tk.X, pady=5)

        option_menu_label = ttk.Label(master=option_menu_container, text=label, anchor="w")
        option_menu_label.pack(side=tk.LEFT, padx=12)

        estado_maquina_options = [
            "Funcionamiento normal",
            "Falla de bomba",
            "Falla de la máquina",
            "Fallas de consumibles",
            "Emergencia",
            "Mantenimiento",
        ]

        option_menu = ttk.OptionMenu(
            option_menu_container,
            variable,
            estado_maquina_options[0],
            *estado_maquina_options
        )
        option_menu.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)

    def on_submit(self):
        piezas_cortadas = self.piezas_cortadas.get()
        piezas_defectuosas = self.piezas_defectuosas.get()
        selected_option = self.selected_option.get()

        # Define different topics for each option
        topic_mapping = {
            "Funcionamiento normal": "normal_operation",
            "Falla de bomba": "pump_failure",
            "Falla de la máquina": "machine_failure",
            "Fallas de consumibles": "consumable_failure",
            "Emergencia": "emergency",
            "Mantenimiento": "maintenance",
        }

        # Get the topic based on the selected option
        topic = topic_mapping.get(selected_option, "unknown_topic")

        # Create a dictionary with the data
        data_dict = {
            "Piezas Cortadas": piezas_cortadas,
            "Piezas Defectuosas": piezas_defectuosas,
            "Estado de la Máquina": selected_option,
        }

        # Convert the data to JSON
        json_data = json.dumps(data_dict)

        # Publish the JSON data to the MQTT topic (use your MQTT client configuration)
        mqtt_client = mqtt.Client()
        mqtt_client.connect("localhost", 1883)  # Replace with your MQTT broker address
        mqtt_client.publish(topic, json_data)

        print(f"Published data to topic '{topic}': {json_data}")

def start_monitor():
    app = tk.Tk()
    app.title("Machine Monitor")
    app.geometry("500x600")
    MachineMonitor(app)
    app.mainloop()

if __name__ == "__main__":
    start_monitor()
