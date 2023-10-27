import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation
from PIL import Image, ImageTk
import os
import csv
import boto3
import json
import datetime
import time
import threading
import traceback
import sys


class Gradebook(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window, padding=(20, 10))
        self.pack(fill=BOTH, expand=YES)
        self.name = ttk.StringVar(value="")
        self.student_id = ttk.StringVar(value="")
        self.course_name = ttk.StringVar(value="")
        self.final_score = ttk.StringVar(value="")
        self.elapsed_time = 0
        self.start_time = None
        self.stop_event = threading.Event()
        self.data = []
        self.colors = master_window.style.colors


        title_text = "Monitoreo de la máquina"
        title = ttk.Label(self, text=title_text, font=("Helvetica", 20), anchor='center')
        title.pack(pady=10)

        self.load_image()

        instruction_text = "Por favor introduce la información de la máquina: "
        instruction = ttk.Label(self, text=instruction_text, width=100, font=("Helvetica", 16))
        instruction.pack(fill=X, pady=10)

        self.create_form_entry("Nombre del trabajo: ", self.name)
        self.create_form_entry("Cliente: ", self.student_id)
        self.create_form_entry("Tiempo de corte aproximado: ", self.course_name)
        self.final_score_input = self.create_form_entry("Detalle: ", self.final_score)
        self.create_stop_checkbutton()


        self.create_buttonbox()
        self.create_realtime_label()

        self.load_data_from_csv()  # Load data from CSV when the program starts
        self.table = self.create_table()  # Create the table with loaded data

        




    def load_image(self):
        # Load the image (assuming it's in the same directory and in PNG format)
        image_path = "/home/cimatec/Documentos/Sistema-de-industria-4.0-/Forms/waterjet.png"
    
        # Check if the file exists
        if not os.path.exists(image_path):
            print(f"Error: The image '{image_path}' does not exist.")
            return

        try:
            # Open the image using Pillow
            original_image = Image.open(image_path)
            
            # Resize the image to one-fifth of its dimensions
            width, height = original_image.size
            new_width = int(width * 0.3)  # Reduce original width by 80%
            new_height = int(height * 0.3)  # Reduce original height by 80%
            resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)
            
            # Convert the Pillow image to a format Tkinter can use
            self.img = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Create a label to display the image
        img_label = ttk.Label(self, image=self.img)
        img_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)  # place it at the top-left corner


    def create_form_entry(self, label, variable):
        form_field_container = ttk.Frame(self)
        form_field_container.pack(fill=X, pady=5)

        form_field_label = ttk.Label(master=form_field_container, text=label, anchor="w")
        form_field_label.pack(side=LEFT, padx=12)

        if label == "Detalle: ":
            form_input = ttk.Text(master=form_field_container, height=5)  # height determines the number of lines
        else:
            form_input = ttk.Entry(master=form_field_container, textvariable=variable)
            add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')

        form_input.pack(side=LEFT, fill=X, expand=YES, padx=5)

        return form_input

    def create_stop_checkbutton(self):
        checkbutton_container = ttk.Frame(self)
        checkbutton_container.pack(fill=X, pady=10)

        check_label = ttk.Label(master=checkbutton_container, text="Hubo paro?", anchor="w")
        check_label.pack(side=LEFT, padx=12)


    def create_buttonbox(self):
        button_container = ttk.Frame(self)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        start_btn = ttk.Button(
            master=button_container,
            text="Iniciar Contador",
            command=self.start_counter,
            bootstyle=INFO,
            width=12,
        )

        start_btn.pack(side=LEFT, padx=5)

        stop_btn = ttk.Button(
            master=button_container,
            text="Detener Contador",
            command=self.stop_counter,
            bootstyle=DANGER,
            width=12,
        )

        stop_btn.pack(side=LEFT, padx=5)

        submit_btn = ttk.Button(
            master=button_container,
            text="Enviar",
            command=self.on_submit,
            bootstyle=SUCCESS,
            width=12,  # Adjust the width to your preference
        )

        submit_btn.pack(side=RIGHT, padx=5)

    def create_table(self):
        coldata = [
            {"text": "Fecha"},
            {"text": "Hora"},
            {"text": "Nombre del trabajo"},
            {"text": "Cliente", "stretch": False},
            {"text": "Tiempo de corte aproximado", "stretch": False},
            {"text": "Detalles", "stretch": False},
            {"text": "Tiempo Transcurrido (s)", "stretch": False}
        ]

        table = Tableview(
            master=self,
            coldata=coldata,
            rowdata=self.data,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            stripecolor=(self.colors.light, None),
        )

        table.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.update()

        return table
    
    def upload_to_s3(self, file_path, bucket_name, s3_file_name=None):
        with open("/home/cimatec/Documentos/Sistema-de-industria-4.0-/Forms/config.json", "r") as file:
            config = json.load(file)

        session = boto3.Session(
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_access_key"]
        )

        s3 = session.resource('s3')
        if not s3_file_name:
            s3_file_name = os.path.basename(file_path)

        try:
            s3.Bucket(bucket_name).upload_file(file_path, s3_file_name)
            print(f"Successfully uploaded {file_path} to {bucket_name}/{s3_file_name}")
        except Exception as e:
            print(f"An error occurred: {e}")



    def load_data_from_csv(self):
        csv_file = "/home/cimatec/Documentos/Sistema-de-industria-4.0-/Forms/data.csv"

        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Fecha", "Hora", "Nombre del trabajo", "Cliente", "Tiempo de corte aproximado", "Detalles", "Tiempo Transcurrido (s)"])
        else:
            with open(csv_file, 'r', newline='') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip the header
                if header:
                    self.data = [header]  # Set the header in the data list
                for row in reader:
                    # Ensure the row has at least 7 elements
                    if len(row) >= 7:
                        self.data.append(row[:7])  # Only take the first 7 elements of the row
                    else:
                        # If the row has fewer than 7 elements, pad it with empty strings
                        while len(row) < 7:
                            row.append("")
                        self.data.append(row)

    def create_realtime_label(self):
        self.realtime_label = ttk.Label(
            self,
            text="Tiempo Transcurrido (s): 0.00",
            width=30,
        )
        self.realtime_label.pack(pady=5)

    def update_realtime_label(self):
        while not self.stop_event.is_set():
            if self.start_time is not None:
                current_time = time.time()
                elapsed_time = round(current_time - self.start_time, 2)
                self.realtime_label.config(text=f"Tiempo Transcurrido (s): {elapsed_time}")
            time.sleep(0.1)

    def start_counter(self):
        self.start_time = time.time()
        self.stop_event.clear()
        threading.Thread(target=self.update_realtime_label).start()

    def stop_counter(self):
        if self.start_time is not None:
            self.elapsed_time = round(time.time() - self.start_time, 2)
            self.start_time = None
            self.stop_event.set()

    def on_submit(self):
        name = self.name.get()
        student_id = self.student_id.get()
        course_name = self.course_name.get()
        final_score = self.final_score_input.get("1.0", "end-1c")  # This fetches all text from the widget




        current_datetime = datetime.datetime.now()
        formatted_date = current_datetime.strftime("%Y-%m-%d")
        formatted_time = current_datetime.strftime("%H:%M:%S")

        csv_file = "/home/cimatec/Documentos/Sistema-de-industria-4.0-/Forms/data.csv"
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([formatted_date, formatted_time, name, student_id, course_name, final_score, self.elapsed_time])
        
        # Upload the CSV to S3
        self.upload_to_s3(csv_file, 'mybucketcima', 'data.csv')
        
        toast = ToastNotification(
            title="Envío exitoso",
            message="Tu información ha sido enviada exitosamente.",
            duration=3000,
            
        )
        toast.show_toast()

        self.data.append([formatted_date, formatted_time, name, student_id, course_name, final_score, self.elapsed_time])
        self.table.destroy()
        self.table = self.create_table()

def handle_exception(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback)

def start_forms():
    sys.excepthook = handle_exception
    app = ttk.Window("Monitoreo de la máquina", "superhero", resizable=(True, True))
    app.geometry("1900x1000")  # Establecer el tamaño inicial de la ventana
    Gradebook(app)
    app.mainloop()

if __name__ == "__main__":
    start_forms()
