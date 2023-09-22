import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation
import os
import csv
import datetime
import time
import threading

class Gradebook(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window, padding=(20, 10))
        self.pack(fill=BOTH, expand=YES)
        self.name = ttk.StringVar(value="")
        self.student_id = ttk.StringVar(value="")
        self.course_name = ttk.StringVar(value="")
        self.final_score = ttk.DoubleVar(value=0)
        self.elapsed_time = 0
        self.start_time = None
        self.stop_event = threading.Event()  # Evento para controlar el temporizador
        self.data = []
        self.colors = master_window.style.colors

        instruction_text = "Por favor introduce la información de la máquina: "
        instruction = ttk.Label(self, text=instruction_text, width=100)
        instruction.pack(fill=X, pady=10)

        self.create_form_entry("Nombre del trabajo: ", self.name)
        self.create_form_entry("Cliente: ", self.student_id)
        self.create_form_entry("Tiempo de corte aproximado: ", self.course_name)
        self.final_score_input = self.create_form_entry("Detalle: ", self.final_score)
        self.create_meter()
        self.create_buttonbox()
        self.create_realtime_label()

        self.table = self.create_table()

    def create_form_entry(self, label, variable):
        form_field_container = ttk.Frame(self)
        form_field_container.pack(fill=X, expand=YES, pady=5)

        form_field_label = ttk.Label(master=form_field_container, text=label, width=15)
        form_field_label.pack(side=LEFT, padx=12)

        form_input = ttk.Entry(master=form_field_container, textvariable=variable)
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')

        return form_input

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

        cancel_btn = ttk.Button(
            master=button_container,
            text="Cancelar",
            command=self.on_cancel,
            bootstyle=DANGER,
            width=6,
        )

        cancel_btn.pack(side=RIGHT, padx=5)

        submit_btn = ttk.Button(
            master=button_container,
            text="Enviar",
            command=self.on_submit,
            bootstyle=SUCCESS,
            width=6,
        )

        submit_btn.pack(side=RIGHT, padx=5)

    def create_meter(self):
        meter = ttk.Meter(
            master=self,
            metersize=150,
            padding=5,
            amounttotal=100,
            amountused=50,
            metertype="full",
            subtext="Tiempo de corte aproximado ",
            interactive=True,
        )

        meter.pack()

        self.final_score.set(meter.amountusedvar)
        self.final_score_input.configure(textvariable=meter.amountusedvar)

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

        # Cargar datos desde el archivo CSV
        self.load_data_from_csv()

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

        # Actualizar explícitamente el diseño
        self.update()

        return table

    def load_data_from_csv(self):
        csv_file = "data.csv"

        # Crear el archivo CSV si no existe
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                # Escribir la fila de encabezado
                writer.writerow(["Fecha", "Hora", "Nombre del trabajo", "Cliente", "Tiempo de corte aproximado", "Detalles", "Tiempo Transcurrido (s)"])
        else:
            # Cargar datos desde el archivo CSV
            with open(csv_file, 'r', newline='') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Obtener la fila de encabezado
                if header:
                    self.data = [header]  # Establecer el encabezado en la lista de datos
                self.data.extend([row for row in reader])

    def create_realtime_label(self):
        self.realtime_label = ttk.Label(
            self,
            text="Tiempo Transcurrido (s): 0.00",  # Valor inicial
            width=30,
        )
        self.realtime_label.pack(pady=5)

    def update_realtime_label(self):
        while not self.stop_event.is_set():
            if self.start_time is not None:
                current_time = time.time()
                elapsed_time = round(current_time - self.start_time, 2)
                self.realtime_label.config(text=f"Tiempo Transcurrido (s): {elapsed_time}")
            time.sleep(0.1)  # Actualizar cada 0.1 segundos

    def start_counter(self):
        """Iniciar el temporizador cuando se hace clic en el botón y comenzar el hilo de actualización en tiempo real."""
        self.start_time = time.time()
        self.stop_event.clear()  # Borrar el evento de detención
        threading.Thread(target=self.update_realtime_label).start()

    def stop_counter(self):
        """Detener el temporizador y actualizar el tiempo transcurrido."""
        if self.start_time is not None:
            self.elapsed_time = round(time.time() - self.start_time, 2)
            self.start_time = None
            self.stop_event.set()  # Establecer el evento de detención

    def on_submit(self):
        """Imprimir el contenido en la consola, almacenar en el archivo CSV con fecha, hora y tiempo transcurrido, y devolver los valores."""
        name = self.name.get()
        student_id = self.student_id.get()
        course_name = self.course_name.get()
        final_score = self.final_score_input.get()  # Obtener el valor del widget de entrada

        # Obtener la fecha y hora actual
        current_datetime = datetime.datetime.now()
        formatted_date = current_datetime.strftime("%Y-%m-%d")
        formatted_time = current_datetime.strftime("%H:%M:%S")

        print("Fecha:", formatted_date)
        print("Hora:", formatted_time)
        print("Nombre del trabajo:", name)
        print("Cliente: ", student_id)
        print("Tiempo de corte aproximado:", course_name)
        print("Detalles:", final_score)
        print("Tiempo Transcurrido (s):", self.elapsed_time)  # Imprimir tiempo transcurrido

        # Almacenar los datos en un archivo CSV con fecha, hora y tiempo transcurrido
        csv_file = "data.csv"

        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([formatted_date, formatted_time, name, student_id, course_name, final_score, self.elapsed_time])

        # Mostrar una notificación emergente
        toast = ToastNotification(
            title="Envío exitoso",
            message="Tu información ha sido enviada exitosamente.",
            duration=3000,
        )
        toast.show_toast()

        # Actualizar la tabla
        self.data.append([formatted_date, formatted_time, name, student_id, course_name, final_score, self.elapsed_time])
        self.table.destroy()
        self.table = self.create_table()

    def on_cancel(self):
        """Cancelar y cerrar la aplicación."""
        self.quit()

    def on_logout(self):
        """Manejar la funcionalidad de cierre de sesión si es necesario."""
        pass

def start_forms():
    app = ttk.Window("Monitoreo de la máquina", "superhero", resizable=(True, True))
    app.geometry("1000x600")  # Establecer el tamaño inicial de la ventana
    Gradebook(app)
    app.mainloop()

if __name__ == "__main__":
    start_forms()
