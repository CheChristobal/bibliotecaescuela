import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.ttk as ttk


from tkinter import font
import datetime
import mysql.connector
from ttkwidgets import Table


class BibliotecaApp:

    def get_title_from_entry(self, entry):
        parts = entry.split(" - ")
        return parts[0] if len(parts) > 0 else entry

    def update_filtered_listbox_with_stock(self, *args):
        filter_text = self.filter_var.get().lower()
        self.listbox.delete(0, tk.END)

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT titulo, stock
            FROM libros
            WHERE LOWER(titulo) LIKE %s
        """, ('%' + filter_text + '%',))

        filtered_books = cursor.fetchall()
        cursor.close()

        for libro, stock in filtered_books:
            entry_text = f"{libro} - Stock: {stock}"
            self.listbox.insert(tk.END, entry_text)

    def __init__(self, root):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bibliotecanz"
        )
        self.create_tables()  # Llama a la función para crear las tablas

        self.stock = {}  # Agrega un diccionario para mantener el stock de los libros

        self.root = root
        self.root.title("Sistema de Biblioteca")
        self.root.geometry("1000x600")  # Tamaño de la ventana
        self.root.config(bg="#003366")  # Color de fondo azul marino

        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        self.button_font = font.Font(family="Arial", size=14)

        self.create_menu()

        self.libros_reservados = []


        self.historial = []  # Inicializar la lista de historial

        self.modify_stock_var = tk.StringVar()  # Agrega esta línea para crear la variable

        self.listbox = None  # Agrega esta línea para inicializar la variable listbox



    def create_tables(self):
        cursor = self.conn.cursor()

        # Crear la tabla 'libros'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                categoria VARCHAR(255) NOT NULL,
                paginas INT NOT NULL,
                stock INT NOT NULL
            )
        """)

        # Crear la tabla 'reservas'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                libro_id INT,
                rut VARCHAR(20) NOT NULL,
                fecha_reserva DATE NOT NULL,
                FOREIGN KEY (libro_id) REFERENCES libros(id)
            )
        """)

        # Crear la tabla 'historial_libros'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_libros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                libro_id INT,
                fecha_devolucion DATETIME NOT NULL,
                fecha_reserva DATETIME NOT NULL,
                FOREIGN KEY (libro_id) REFERENCES libros(id)
            )
        """)

        self.conn.commit()
        cursor.close()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_menu(self):
        self.clear_frame()

        self.title_label = tk.Label(self.root, text="¡Bienvenido a la Biblioteca!", font=self.title_font, bg="#003366",
                                    fg="white")
        self.title_label.pack(pady=20)

        self.lista_libros_button = tk.Button(self.root, text="Ver Lista de Libros", font=self.button_font,
                                             command=self.ver_lista_libros, bg="#003366", fg="white")
        self.lista_libros_button.pack(pady=10)

        self.libros_reservados_button = tk.Button(self.root, text="Libros Reservados", font=self.button_font,
                                                  command=self.ver_libros_reservados, bg="#003366", fg="white")
        self.libros_reservados_button.pack(pady=10)

        self.historial_button = tk.Button(self.root, text="Ver Historial de Pedidos", font=self.button_font,
                                          command=self.ver_historial, bg="#003366", fg="white")
        self.historial_button.pack(pady=10)

        self.admin_button = tk.Button(self.root, text="Administrador", font=self.button_font,
                                      command=self.show_admin_login, bg="#003366", fg="white")
        self.admin_button.pack(pady=10)

        self.salir_button = tk.Button(self.root, text="Salir", font=self.button_font, command=self.root.quit,
                                      bg="#FF4500", fg="white")
        self.salir_button.pack(pady=20)

    def show_admin_login(self):
        self.clear_frame()

        self.admin_label = tk.Label(self.root, text="Ingrese la contraseña de administrador:", font=self.title_font,
                                    bg="#003366", fg="white")
        self.admin_label.pack(pady=20)

        self.admin_password_var = tk.StringVar()
        self.admin_password_entry = tk.Entry(self.root, font=self.button_font, show="*",
                                             textvariable=self.admin_password_var)
        self.admin_password_entry.pack()

        login_button = tk.Button(self.root, text="Iniciar Sesión", font=self.button_font, command=self.admin_login,
                                 bg="#FF4500", fg="white")
        login_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Volver al Menú Principal", font=self.button_font,
                                command=self.create_menu, bg="#FF4500", fg="white")
        back_button.pack(pady=10)

    def admin_login(self):
        password = self.admin_password_var.get()
        if password == "admin123":  # Contraseña de ejemplo (cámbiala por una más segura)
            self.show_admin_panel()
        else:
            messagebox.showwarning("Inicio de Sesión", "Contraseña incorrecta. Por favor, intenta de nuevo.")

    def show_admin_panel(self):
        self.clear_frame()

        self.add_book_label = tk.Label(self.root, text="Agregar Libro", font=self.title_font, bg="#003366", fg="white")
        self.add_book_label.pack(pady=20)

        self.book_title_var = tk.StringVar()
        self.book_title_label = tk.Label(self.root, text="Título del Libro:", font=self.button_font, bg="#003366",
                                         fg="white")
        self.book_title_label.pack()
        self.book_title_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.book_title_var)
        self.book_title_entry.pack()

        self.book_category_var = tk.StringVar()
        self.book_category_label = tk.Label(self.root, text="Categoría:", font=self.button_font, bg="#003366",
                                            fg="white")
        self.book_category_label.pack()
        self.book_category_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.book_category_var)
        self.book_category_entry.pack()

        self.book_pages_var = tk.IntVar()
        self.book_pages_label = tk.Label(self.root, text="Páginas:", font=self.button_font, bg="#003366",
                                         fg="white")
        self.book_pages_label.pack()
        self.book_pages_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.book_pages_var)
        self.book_pages_entry.pack()

        self.book_stock_var = tk.IntVar()
        self.book_stock_label = tk.Label(self.root, text="Stock Inicial:", font=self.button_font, bg="#003366",
                                         fg="white")
        self.book_stock_label.pack()
        self.book_stock_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.book_stock_var)
        self.book_stock_entry.pack()

        self.add_button = tk.Button(self.root, text="Agregar Libro", font=self.button_font, command=self.add_book,
                                    bg="#FF4500", fg="white")
        self.add_button.pack(pady=10)

        self.administrate_books_button = tk.Button(self.root, text="Administrar Libros", font=self.button_font,
                                                   command=self.administrate_books, bg="#FF4500", fg="white")
        self.administrate_books_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Volver al Menú Principal", font=self.button_font,
                                command=self.create_menu, bg="#FF4500", fg="white")
        back_button.pack(pady=10)

    def administrate_books(self):
        self.clear_frame()

        self.admin_books_label = tk.Label(self.root, text="Administrar Libros", font=self.title_font, bg="#003366",
                                          fg="white")
        self.admin_books_label.pack(pady=20)

        # Crear un Treeview para mostrar los libros en forma de tabla
        columns = ("Título", "Categoría", "Páginas", "Stock")
        self.admin_books_tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.admin_books_tree.heading(col, text=col)
            self.admin_books_tree.column(col, width=200)
        self.admin_books_tree.pack(fill=tk.BOTH, expand=True)

        # Obtener la lista de libros desde la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT titulo, categoria, paginas, stock FROM libros")
        libros = cursor.fetchall()
        cursor.close()

        # Insertar los datos en el Treeview
        for libro in libros:
            self.admin_books_tree.insert("", tk.END, values=libro)

        # Enlazar la función modify_book_window al evento de doble clic en la tabla
        self.admin_books_tree.bind("<<TreeviewOpen>>", self.modify_book_window)

        self.modify_book_button = tk.Button(self.root, text="Modificar Libro", font=self.button_font,
                                            command=self.modify_book_window, bg="#FF4500", fg="white")
        self.modify_book_button.pack(pady=10)

        self.delete_book_button = tk.Button(self.root, text="Eliminar Libro", font=self.button_font,
                                            command=self.delete_book, bg="#FF4500", fg="white")
        self.delete_book_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Volver al Menú de Administrador", font=self.button_font,
                                command=self.show_admin_panel, bg="#FF4500", fg="white")
        back_button.pack(pady=10)

    def modify_book_window(self, event=None):
        selected_item = self.admin_books_tree.selection()

        if selected_item:
            selected_values = self.admin_books_tree.item(selected_item, "values")
            selected_title = selected_values[0]
            selected_category = selected_values[1]
            selected_pages = selected_values[2]
            selected_stock = selected_values[3]

            # Crear una nueva ventana para editar el libro
            modify_window = tk.Toplevel(self.root)
            modify_window.title("Modificar Libro")

            title_label = tk.Label(modify_window, text="Título:")
            title_label.pack(pady=5)
            title_entry = tk.Entry(modify_window, font=self.button_font)
            title_entry.pack()
            title_entry.insert(0, selected_title)

            category_label = tk.Label(modify_window, text="Categoría:")
            category_label.pack(pady=5)
            category_entry = tk.Entry(modify_window, font=self.button_font)
            category_entry.pack()
            category_entry.insert(0, selected_category)

            pages_label = tk.Label(modify_window, text="Páginas:")
            pages_label.pack(pady=5)
            pages_entry = tk.Entry(modify_window, font=self.button_font)
            pages_entry.pack()
            pages_entry.insert(0, selected_pages)

            stock_label = tk.Label(modify_window, text="Stock:")
            stock_label.pack(pady=5)
            stock_entry = tk.Entry(modify_window, font=self.button_font)
            stock_entry.pack()
            stock_entry.insert(0, selected_stock)

            def save_changes():
                new_title = title_entry.get()
                new_category = category_entry.get()
                new_pages = pages_entry.get()
                new_stock = stock_entry.get()

                cursor = self.conn.cursor()
                try:
                    cursor.execute(
                        "UPDATE libros SET titulo = %s, categoria = %s, paginas = %s, stock = %s WHERE titulo = %s",
                        (new_title, new_category, new_pages, new_stock, selected_title))
                    self.conn.commit()
                    cursor.close()
                    messagebox.showinfo("Éxito", "Libro modificado exitosamente.")
                    modify_window.destroy()
                    self.administrate_books()
                except mysql.connector.Error as err:
                    cursor.close()
                    messagebox.showerror("Error", f"No se pudo modificar el libro: {err}")

            save_button = tk.Button(modify_window, text="Guardar Cambios", font=self.button_font, command=save_changes,
                                    bg="#FF4500", fg="white")
            save_button.pack(pady=10)
        else:
            messagebox.showwarning("Modificar Libro", "Por favor, selecciona un libro para modificar.")

    def delete_book(self):
        selected_item = self.admin_books_tree.selection()

        if selected_item:
            selected_values = self.admin_books_tree.item(selected_item, "values")
            selected_title = selected_values[0]

            if messagebox.askyesno("Confirmar Eliminación",
                                   f"¿Estás seguro de que quieres eliminar el libro '{selected_title}'?"):
                cursor = self.conn.cursor()

                try:
                    # Obtener el ID del libro
                    cursor.execute("SELECT id FROM libros WHERE titulo = %s", (selected_title,))
                    libro_id = cursor.fetchone()[0]

                    # Asegurarse de que no haya resultados no leídos pendientes
                    while cursor.nextset():
                        pass

                    # Eliminar el libro de la tabla libros
                    cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))

                    # Eliminar las entradas relacionadas con el libro en la tabla historial_libros
                    cursor.execute("DELETE FROM historial_libros WHERE libro_id = %s", (libro_id,))

                    self.conn.commit()
                    cursor.close()
                    messagebox.showinfo("Éxito", f"El libro '{selected_title}' ha sido eliminado correctamente.")
                    self.administrate_books()  # Actualizar la lista de libros después de eliminar uno
                except mysql.connector.Error as err:
                    cursor.close()
                    messagebox.showerror("Error", f"No se pudo eliminar el libro: {err}")
        else:
            messagebox.showwarning("Eliminar Libro", "Por favor, selecciona un libro para eliminar.")

    def confirm_delete_book(self):
        selected_item = self.delete_book_tree.selection()

        if selected_item:
            selected_libro = self.delete_book_tree.item(selected_item, "values")[0]

            if messagebox.askyesno("Confirmar Eliminación",
                                   f"¿Estás seguro de que deseas eliminar el libro '{selected_libro}'?"):
                cursor = self.conn.cursor()
                try:
                    # Obtener el ID del libro seleccionado
                    cursor.execute("SELECT id FROM libros WHERE titulo = %s", (selected_libro,))
                    libro_id = cursor.fetchone()[0]

                    # Eliminar el libro de la tabla 'libros'
                    cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))
                    self.conn.commit()

                    # Eliminar el libro seleccionado de la tabla Treeview
                    self.delete_book_tree.delete(selected_item)

                    # Mostrar mensaje de éxito
                    messagebox.showinfo("Eliminar Libro",
                                        f"El libro '{selected_libro}' ha sido eliminado correctamente.")
                except mysql.connector.Error as e:
                    self.conn.rollback()
                    messagebox.showerror("Error", f"Error al eliminar el libro: {e}")
                finally:
                    cursor.close()
        else:
            messagebox.showwarning("Eliminar Libro", "Por favor, selecciona un libro para eliminar.")

    def modify_book(self):
        # Obtener el índice seleccionado en el Treeview
        selected_item = self.admin_books_tree.selection()

        if not selected_item:
            # Si no se seleccionó ningún libro, mostrar un mensaje de error
            tk.messagebox.showerror("Error", "Por favor, selecciona un libro.")
            return

        # Obtener los valores seleccionados (título y stock) del libro
        selected_values = self.admin_books_tree.item(selected_item)["values"]
        selected_title = selected_values[0]
        selected_stock = selected_values[1]

        # Crear una ventana de modificación
        self.create_modify_window(selected_title, selected_stock)

    def create_modify_window(self, selected_title, selected_stock):
        # Crear una nueva ventana para la modificación
        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modificar Libro")

        # Crear etiquetas y campos de entrada para la modificación
        title_label = tk.Label(modify_window, text="Título:")
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        title_entry = tk.Entry(modify_window, textvariable=tk.StringVar(value=selected_title))
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        stock_label = tk.Label(modify_window, text="Stock:")
        stock_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        stock_entry = tk.Entry(modify_window, textvariable=tk.StringVar(value=selected_stock))
        stock_entry.grid(row=1, column=1, padx=10, pady=10)

        # Crear un botón para guardar la modificación
        save_button = tk.Button(modify_window, text="Guardar",
                                command=lambda: self.save_modification(modify_window, selected_title))
        save_button.grid(row=2, columnspan=2, padx=10, pady=10)

        def on_closing():
            # Habilitar la ventana principal cuando se cierre la ventana de modificación
            self.root.attributes('-disabled', False)
            modify_window.destroy()

        modify_window.protocol("WM_DELETE_WINDOW", on_closing)

        # Deshabilitar la ventana principal mientras se muestra la ventana de modificación
        self.root.attributes('-disabled', True)

    def save_modification(self, modify_window, original_title, title_entry=None, stock_entry=None):
        # Obtener los valores ingresados en la ventana de modificación
        new_title = title_entry.get()
        new_stock = stock_entry.get()

        # Validar que los valores no estén vacíos
        if not new_title or not new_stock:
            tk.messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return

        try:
            # Intentar actualizar los datos del libro en la base de datos
            cursor = self.conn.cursor()
            cursor.execute("UPDATE libros SET titulo = ?, stock = ? WHERE titulo = ?",
                           (new_title, new_stock, original_title))
            self.conn.commit()
            cursor.close()

            # Actualizar la tabla en la ventana principal
            self.update_admin_books_tree()

            # Cerrar la ventana de modificación
            modify_window.destroy()
        except sqlite3.Error as e:
            tk.messagebox.showerror("Error", f"Error al actualizar el libro: {str(e)}")

    def update_admin_books_tree(self):
        # Borrar todos los elementos actuales en el Treeview
        for item in self.admin_books_tree.get_children():
            self.admin_books_tree.delete(item)

        # Obtener la lista de libros actualizada desde la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, titulo, categoria, paginas, stock FROM libros")
        libros = cursor.fetchall()
        cursor.close()

        # Insertar los datos actualizados en el Treeview
        for libro in libros:
            libro_id, titulo, categoria, paginas, stock = libro
            self.admin_books_tree.insert("", tk.END, values=(libro_id, titulo, categoria, paginas, stock))

    def add_book(self):
        new_book_title = self.book_title_var.get()
        new_book_category = self.book_category_var.get()
        new_book_pages = self.book_pages_var.get()
        new_book_stock = self.book_stock_var.get()

        if new_book_title:
            cursor = self.conn.cursor()
            try:
                # Insertar el nuevo libro en la tabla 'libros'
                query = "INSERT INTO libros (titulo, categoria, paginas, stock) VALUES (%s, %s, %s, %s)"
                values = (new_book_title, new_book_category, new_book_pages, new_book_stock)
                cursor.execute(query, values)
                self.conn.commit()

                # Actualizar el stock en el diccionario
                self.stock[new_book_title] = new_book_stock

                # Mostrar mensaje de alerta
                messagebox.showinfo("Agregar Libro",
                                    f"El libro '{new_book_title}' ha sido agregado a la biblioteca con un stock inicial de {new_book_stock}.")

                self.update_filtered_listbox_with_stock()
                self.book_title_var.set("")  # Limpiar la entrada después de agregar
                self.book_category_var.set("")
                self.book_pages_var.set(0)
                self.book_stock_var.set(0)
            except mysql.connector.Error as e:
                print("Error:", e)
                self.conn.rollback()
            finally:
                cursor.close()
        else:
            # Mostrar mensaje de alerta si el título del libro está vacío
            messagebox.showwarning("Agregar Libro", "Por favor, ingrese el título del libro.")

    def ver_lista_libros(self):
        self.clear_frame()

        self.rut_var = tk.StringVar()
        self.rut_label = tk.Label(self.root, text="Ingrese su RUT:", font=self.button_font, bg="#003366", fg="white")
        self.rut_label.pack()
        self.rut_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.rut_var)
        self.rut_entry.pack()

        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", self.update_filtered_listbox_with_stock)
        self.filter_label = tk.Label(self.root, text="Filtrar Libros:", font=self.button_font, bg="#003366", fg="white")
        self.filter_label.pack()
        self.filter_entry = tk.Entry(self.root, font=self.button_font, textvariable=self.filter_var)
        self.filter_entry.pack()

        self.filter_button = tk.Button(self.root, text="Filtrar", font=self.button_font,
                                       command=self.update_filtered_listbox_with_stock, bg="#FF4500", fg="white")
        self.filter_button.pack(pady=10)

        self.title_label = tk.Label(self.root, text="Lista de Libros", font=self.title_font, bg="#003366", fg="white")
        self.title_label.pack(pady=20)

        # Crear la tabla para mostrar la lista de libros
        self.columns = ("Título", "Categoría", "Páginas", "Stock")
        self.table = ttk.Treeview(self.root, columns=self.columns, show="headings")
        self.table.heading("Título", text="Título")
        self.table.heading("Categoría", text="Categoría")
        self.table.heading("Páginas", text="Páginas")
        self.table.heading("Stock", text="Stock")

        # Ajustar el ancho de las columnas y centrar el contenido
        self.table.column("Título", width=300)
        self.table.column("Categoría", width=200)
        self.table.column("Páginas", width=100, anchor="center")
        self.table.column("Stock", width=100, anchor="center")

        self.table.pack(fill="both", expand=True)

        self.update_filtered_listbox_with_stock()

        reservar_button = tk.Button(self.root, text="Reservar", font=self.button_font, command=self.reservar_libro,
                                    bg="#FF4500", fg="white")
        reservar_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Volver al Menú Principal", font=self.button_font,
                                command=self.create_menu, bg="#FF4500", fg="white")
        back_button.pack(pady=10)

    def update_filtered_listbox_with_stock(self, *args):
        filter_text = self.filter_var.get().lower()
        self.table.delete(*self.table.get_children())  # Limpiar la tabla

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT titulo, categoria, paginas, stock
            FROM libros
            WHERE LOWER(titulo) LIKE %s
        """, ('%' + filter_text + '%',))

        filtered_books = cursor.fetchall()
        cursor.close()

        for libro, categoria, paginas, stock in filtered_books:
            self.table.insert("", "end", values=(libro, categoria, paginas, stock))

    def reservar_libro(self):
        selected_item = self.table.selection()

        if selected_item:
            selected_libro = self.table.item(selected_item, "values")[0]
            rut = self.rut_var.get()

            if rut:
                cursor = self.conn.cursor()

                try:
                    cursor.execute("SELECT id, stock FROM libros WHERE titulo = %s", (selected_libro,))
                    libro_data = cursor.fetchone()

                    if libro_data:
                        libro_id, libro_stock = libro_data

                        if libro_stock > 0:
                            cursor.execute("INSERT INTO reservas (libro_id, rut) VALUES (%s, %s)", (libro_id, rut))
                            cursor.execute("UPDATE libros SET stock = stock - 1 WHERE id = %s", (libro_id,))
                            self.conn.commit()
                            cursor.close()

                            self.update_filtered_listbox_with_stock()
                            self.mostrar_reservas()  # Llama a la función para mostrar las reservas
                            messagebox.showinfo("Reservar Libro",
                                                f"Has reservado el libro: {selected_libro}\nRUT: {rut}")
                            self.ver_libros_reservados()  # Actualizar la lista de libros reservados
                        else:
                            cursor.close()
                            messagebox.showwarning("Reservar Libro", "Lo sentimos, este libro está agotado.")
                    else:
                        cursor.close()
                        messagebox.showwarning("Reservar Libro", "El libro seleccionado no existe en la base de datos.")
                except mysql.connector.Error as err:
                    cursor.close()
                    messagebox.showerror("Error", f"Ocurrió un error al realizar la reserva: {err}")
            else:
                messagebox.showwarning("Reservar Libro", "Por favor, ingrese su RUT antes de reservar.")
        else:
            messagebox.showwarning("Reservar Libro", "Por favor, seleccione un libro para reservar.")

    def mostrar_reservas(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute("SELECT l.titulo, r.rut FROM reservas r JOIN libros l ON r.libro_id = l.id")
            reservas_data = cursor.fetchall()

            if reservas_data:
                # Limpiar la tabla antes de insertar nuevos datos
                for item in self.historial_tree.get_children():
                    self.historial_tree.delete(item)

                # Mostrar las reservas en la tabla
                for libro, rut in reservas_data:
                    self.historial_tree.insert("", tk.END, values=(libro, "-", "-", rut))
            else:
                # Limpiar la tabla si no hay reservas
                for item in self.historial_tree.get_children():
                    self.historial_tree.delete(item)
                messagebox.showinfo("Reservas Actuales", "No hay reservas en este momento.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Ocurrió un error al obtener las reservas: {err}")
        finally:
            cursor.close()

    def devolver_libro(self):
        selected_item = self.historial_tree.selection()

        if selected_item:
            selected_values = self.historial_tree.item(selected_item, "values")
            selected_libro = selected_values[0]
            rut = selected_values[2]

            cursor = self.conn.cursor()

            try:
                cursor.execute("SELECT id FROM libros WHERE titulo = %s", (selected_libro,))
                libro_id = cursor.fetchone()

                if libro_id:
                    libro_id = libro_id[0]

                    cursor.execute("DELETE FROM reservas WHERE libro_id = %s AND rut = %s", (libro_id, rut))
                    cursor.execute("UPDATE libros SET stock = stock + 1 WHERE id = %s", (libro_id,))

                    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute("INSERT INTO historial_libros (libro_id, fecha_devolucion) VALUES (%s, %s)",
                                   (libro_id, current_datetime))

                    self.conn.commit()
                    cursor.close()

                    # Eliminar el registro de la tabla y actualizar la vista
                    self.historial_tree.delete(selected_item)
                    self.mostrar_reservas()  # Llama a la función para mostrar las reservas
                    messagebox.showinfo("Devolver Libro", f"Has devuelto el libro: {selected_libro}")
                    self.ver_libros_reservados()  # Actualizar la lista de libros reservados
                else:
                    cursor.close()
                    messagebox.showwarning("Devolver Libro",
                                           "El libro seleccionado no se encuentra en la base de datos.")
            except mysql.connector.Error as err:
                cursor.close()
                messagebox.showerror("Error", f"Ocurrió un error al devolver el libro: {err}")
        else:
            messagebox.showwarning("Devolver Libro", "Por favor, selecciona un libro reservado para devolver.")

    def ver_libros_reservados(self):
        self.clear_frame()

        self.title_label = tk.Label(self.root, text="Libros Reservados", font=self.title_font, bg="#003366", fg="white")
        self.title_label.pack(pady=20)

        self.historial_frame = tk.Frame(self.root)
        self.historial_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.historial_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.historial_tree = ttk.Treeview(self.historial_frame,
                                           columns=("Libro", "Fecha Pedido", "Fecha Devolución", "RUT"),
                                           yscrollcommand=scrollbar.set)
        self.historial_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.historial_tree.yview)

        self.historial_tree.heading("#1", text="Libro")

        self.historial_tree.heading("#4", text="RUT")

        self.historial_tree.column("#1", width=200)
        self.historial_tree.column("#2", width=150)
        self.historial_tree.column("#3", width=150)
        self.historial_tree.column("#4", width=150)

        # Llamar a la función para mostrar las reservas en la tabla
        self.mostrar_reservas()

        devolver_button = tk.Button(self.root, text="Devolver Libro", font=self.button_font,
                                    command=self.devolver_libro, bg="#FF4500", fg="white")
        devolver_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Volver al Menú Principal", font=self.button_font,
                                command=self.create_menu, bg="#FF4500", fg="white")
        back_button.pack(pady=10)



    def ver_historial(self):
        self.clear_frame()

        self.title_label = tk.Label(self.root, text="Historial de Libros Pedidos", font=self.title_font, bg="#003366",
                                    fg="white")
        self.title_label.pack(pady=20)

        self.historial_frame = tk.Frame(self.root)
        self.historial_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.historial_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.historial_tree = ttk.Treeview(self.historial_frame,
                                           columns=("Libro", "Fecha Pedido", "Fecha Devolucion", "RUT"),
                                           yscrollcommand=scrollbar.set)
        self.historial_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.historial_tree.yview)

        self.historial_tree.heading("#1", text="Libro")
        self.historial_tree.heading("#2", text="Fecha Devolucion")
        self.historial_tree.heading("#3", text="Fecha Pedido")
        self.historial_tree.heading("#4", text="RUT")

        self.historial_tree.column("#1", width=200)
        self.historial_tree.column("#2", width=150)
        self.historial_tree.column("#3", width=150)
        self.historial_tree.column("#4", width=150)

        # Obtener el historial de libros desde la base de datos
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT libros.titulo, historial_libros.fecha_reserva, historial_libros.fecha_devolucion, reservas.rut
            FROM historial_libros
            INNER JOIN libros ON historial_libros.libro_id = libros.id
            INNER JOIN reservas ON historial_libros.libro_id = reservas.libro_id
        """)
        historial = cursor.fetchall()
        cursor.close()


        # Mostrar el historial de libros en la tabla
        for libro, fecha_pedido, fecha_devolucion, rut in historial:
            self.historial_tree.insert("", tk.END, values=(libro, fecha_pedido, fecha_devolucion, rut))

        back_button = tk.Button(self.root, text="Volver al Menú Principal", font=self.button_font,
                                command=self.create_menu, bg="#FF4500", fg="white")
        back_button.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()