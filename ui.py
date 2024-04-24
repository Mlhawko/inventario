import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from tkcalendar import DateEntry  # Importamos el widget de calendario

class FormularioIngreso:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Inventario")

        # Crear el menú principal
        self.menu_principal = tk.Menu(root)
        root.config(menu=self.menu_principal)

        # Opción Archivo
        self.menu_archivo = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Archivo", menu=self.menu_archivo)
        self.menu_archivo.add_command(label="Ingresar", command=self.mostrar_formulario_ingreso)
        self.menu_archivo.add_command(label="Modificar")
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=root.quit)

        # Frame principal
        self.main_frame = ttk.Frame(root, padding=(20, 20))

        # Cargar imagen
        self.imagen = ImageTk.PhotoImage(Image.open("logo.jpg"))
        self.imagen_label = ttk.Label(root, image=self.imagen)

        # Frame secundario para mensaje de éxito
        self.exito_frame = ttk.Frame(root, padding=(20, 20))
        ttk.Label(self.exito_frame, text="¡Ingreso exitoso!", font=("Helvetica", 16)).pack()

        # Variables para almacenar los datos del formulario secundario
        self.tipo_var = tk.StringVar()
        self.marca_var = tk.StringVar()
        self.modelo_var = tk.StringVar()
        self.s_n_var = tk.StringVar()
        self.n_producto_var = tk.StringVar()
        self.nombre_equipo_var = tk.StringVar()
        self.accesorios_var = tk.StringVar()
        self.n_sello_var = tk.StringVar()

        # Variables para almacenar los datos del formulario principal
        self.fecha_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.area_var = tk.StringVar()
        self.correo_var = tk.StringVar()
        self.adjunto_var = tk.StringVar()
        self.argumentos_var = tk.StringVar()

        # Campos del formulario principal
        ttk.Label(self.main_frame, text="Fecha:").grid(row=0, column=0, sticky="w")
        self.fecha_entry = DateEntry(self.main_frame, textvariable=self.fecha_var, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self.main_frame, text="Nombre:").grid(row=1, column=0, sticky="w")
        self.nombre_entry = ttk.Entry(self.main_frame, textvariable=self.nombre_var)
        self.nombre_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self.main_frame, text="Área:").grid(row=2, column=0, sticky="w")
        self.area_entry = ttk.Entry(self.main_frame, textvariable=self.area_var)
        self.area_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self.main_frame, text="Correo:").grid(row=3, column=0, sticky="w")
        self.correo_entry = ttk.Entry(self.main_frame, textvariable=self.correo_var)
        self.correo_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self.main_frame, text="Adjunto:").grid(row=4, column=0, sticky="w")
        self.adjunto_combo = ttk.Combobox(self.main_frame, textvariable=self.adjunto_var, values=["Celular", "Línea Telefónica", "Notebook", "PC Escritorio"], state="readonly")
        self.adjunto_combo.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        self.adjunto_combo.bind("<<ComboboxSelected>>", self.mostrar_formulario_secundario)

        ttk.Label(self.main_frame, text="Argumentos:").grid(row=5, column=0, sticky="w")
        self.argumentos_text = tk.Text(self.main_frame, width=40, height=5)
        self.argumentos_text.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        # Botones
        ttk.Button(self.main_frame, text="Ingresar", command=self.mostrar_exito).grid(row=6, column=0, columnspan=2, pady=10, sticky="we")

        # Configurar pesos de las filas y columnas para hacer que la ventana sea redimensionable
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        # Inicializar el atributo formulario_secundario como None
        self.formulario_secundario = None

    def mostrar_formulario_ingreso(self):
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.exito_frame.grid_remove()
        self.imagen_label.grid_forget()

    def mostrar_formulario_secundario(self, event):
        adjunto_seleccionado = self.adjunto_var.get()
        if adjunto_seleccionado:
            if self.formulario_secundario:
                self.formulario_secundario.destroy()
            self.formulario_secundario = tk.Toplevel(self.root)
            self.formulario_secundario.title(f"Detalles de {adjunto_seleccionado}")

            ttk.Label(self.formulario_secundario, text="Tipo:").grid(row=0, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.tipo_var).grid(row=0, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="Marca:").grid(row=1, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.marca_var).grid(row=1, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="Modelo:").grid(row=2, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.modelo_var).grid(row=2, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="S/N:").grid(row=3, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.s_n_var).grid(row=3, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="N° de Producto:").grid(row=4, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.n_producto_var).grid(row=4, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="Nombre del Equipo:").grid(row=5, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.nombre_equipo_var).grid(row=5, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="Accesorios:").grid(row=6, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.accesorios_var).grid(row=6, column=1, sticky="w")

            ttk.Label(self.formulario_secundario, text="N° de Sello:").grid(row=7, column=0, sticky="w")
            ttk.Entry(self.formulario_secundario, textvariable=self.n_sello_var).grid(row=7, column=1, sticky="w")

            # Botones
            ttk.Button(self.formulario_secundario, text="Agregar", command=self.agregar_datos).grid(row=8, column=0, pady=10, sticky="we")
            ttk.Button(self.formulario_secundario, text="Cancelar", command=self.cancelar_ingreso).grid(row=8, column=1, pady=10, sticky="we")

    def agregar_datos(self):
        # Aquí puedes escribir la lógica para agregar los datos a alguna estructura de datos o base de datos
        print("Datos agregados exitosamente.")
        self.formulario_secundario.destroy()  # Cerrar el formulario secundario después de agregar los datos

    def cancelar_ingreso(self):
        self.formulario_secundario.destroy()  # Cerrar el formulario secundario si se cancela el ingreso

    def mostrar_exito(self):
        self.main_frame.grid_remove()
        self.exito_frame.grid(row=0, column=1, sticky="nsew")

if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioIngreso(root)
    app.imagen_label.grid(row=0, column=0, sticky="nsew")
    root.mainloop()