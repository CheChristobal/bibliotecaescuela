import sys
import sqlite3

from PyQt5.QtGui import QStandardItem, QStandardItemModel, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout, QDialogButtonBox, QStackedWidget, QAction, QMenuBar, QMenu, \
    QHeaderView, QAbstractItemView, QComboBox, QMenu, QMessageBox, QWidget, QListView, QAbstractItemView, QPushButton, \
    QInputDialog, QFontDialog, QColorDialog, QSpinBox, QFileDialog
from PyQt5.QtCore import Qt
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class BibliotecaApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.conn = sqlite3.connect("biblioteca2.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT,
                autor TEXT,
                isbn TEXT,
                categoria TEXT,
                paginas INTEGER,
                genero TEXT,
                ejemplar INTEGER,
                ubicacion TEXT
            )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id INTEGER,
                lector TEXT,
                fecha_prestamo DATETIME,
                FOREIGN KEY (libro_id) REFERENCES libros (id)
            )
        ''')

        # Crear la tabla "devoluciones" si no existe
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS devoluciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prestamo_id INTEGER,
                fecha_devolucion DATETIME,
                FOREIGN KEY (prestamo_id) REFERENCES prestamos (id)
            )
        ''')


        self.conn.commit()

        self.setWindowTitle("Sistema de Biblioteca")
        self.setGeometry(100, 100, 800, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()
        self.pagina_principal = PaginaPrincipal(self)
        self.pagina_libros = PaginaLibros(self)
        self.pagina_lectores = PaginaLectores(self)
        self.pagina_prestamos = PaginaPrestamos(self)
        self.pagina_devoluciones = PaginaDevoluciones(self)
        self.pagina_alumnos = PaginaAlumnos(self)
        self.pagina_profesores = PaginaProfesores(self)
        self.pagina_ayuda = PaginaAyuda(self)
        self.pagina_ajustes = PaginaAjustes(self)
        self.pagina_informes = PaginaInformes(self)

        self.stacked_widget.addWidget(self.pagina_principal)
        self.stacked_widget.addWidget(self.pagina_libros)
        self.stacked_widget.addWidget(self.pagina_lectores)
        self.stacked_widget.addWidget(self.pagina_prestamos)
        self.stacked_widget.addWidget(self.pagina_devoluciones)
        self.stacked_widget.addWidget(self.pagina_alumnos)
        self.stacked_widget.addWidget(self.pagina_profesores)
        self.stacked_widget.addWidget(self.pagina_ayuda)
        self.stacked_widget.addWidget(self.pagina_ajustes)
        self.stacked_widget.addWidget(self.pagina_informes)

        self.layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(self.layout)

        self.cambiar_pagina(0)  # Página Principal

        self.menu_bar = self.menuBar()

        self.menu_principal = self.menu_bar.addMenu("Página Principal")
        self.lista_libros_action = QAction("Lista de Libros", self)
        self.lista_libros_action.triggered.connect(lambda: self.cambiar_pagina(1))
        self.menu_principal.addAction(self.lista_libros_action)

        self.menu_libros = self.menu_bar.addMenu("Libros")
        self.agregar_libro_action_libros = QAction("Agregar Libro", self)
        self.agregar_libro_action_libros.triggered.connect(self.mostrar_ventana_agregar_libro)
        self.menu_libros.addAction(self.agregar_libro_action_libros)

        self.menu_devoluciones = self.menu_bar.addMenu("Devoluciones")
        self.lista_devoluciones_action = QAction("Lista de Devoluciones", self)
        self.lista_devoluciones_action.triggered.connect(lambda: self.cambiar_pagina(4))
        self.menu_devoluciones.addAction(self.lista_devoluciones_action)

        self.menu_prestamos = self.menu_bar.addMenu("Préstamos")
        self.lista_prestamos_action = QAction("Lista de Préstamos", self)
        self.lista_prestamos_action.triggered.connect(lambda: self.cambiar_pagina(3))
        self.menu_prestamos.addAction(self.lista_prestamos_action)

        self.menu_profesores = self.menu_bar.addMenu("Profesores")
        self.lista_profesores_action = QAction("Lista de Profesores", self)
        self.lista_profesores_action.triggered.connect(lambda: self.cambiar_pagina(6))
        self.menu_profesores.addAction(self.lista_profesores_action)

        self.menu_alumnos = self.menu_bar.addMenu("Alumnos")
        self.lista_alumnos_action = QAction("Lista de Alumnos", self)
        self.lista_alumnos_action.triggered.connect(lambda: self.cambiar_pagina(5))
        self.menu_alumnos.addAction(self.lista_alumnos_action)

        self.menu_ayuda = self.menu_bar.addMenu("Ayuda")
        self.ayuda_action = QAction("Contenido de Ayuda", self)
        self.ayuda_action.triggered.connect(lambda: self.cambiar_pagina(7))
        self.menu_ayuda.addAction(self.ayuda_action)

        self.menu_ajustes = self.menu_bar.addMenu("Ajustes")
        self.ajustes_action = QAction("Configuración de Ajustes", self)
        self.ajustes_action.triggered.connect(lambda: self.cambiar_pagina(8))
        self.menu_ajustes.addAction(self.ajustes_action)

        self.menu_informes = self.menu_bar.addMenu("Informes")
        self.informes_action = QAction("Generar Informes", self)
        self.informes_action.triggered.connect(lambda: self.cambiar_pagina(9))
        self.menu_informes.addAction(self.informes_action)

        self.crear_tabla_devoluciones_prestamos()

    def cambiar_pagina(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def mostrar_ventana_agregar_libro(self):
        ventana_agregar_libro = DialogoAgregarLibro(self)
        if ventana_agregar_libro.exec_() == QDialog.Accepted:
            libro = ventana_agregar_libro.obtener_libro()
            if libro:
                self.agregar_libro_db(*libro)

    def agregar_libro_db(self, titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion):
        self.c.execute(
            "INSERT INTO libros (titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion))
        self.conn.commit()
        self.pagina_libros.actualizar_tabla_libros()

    def eliminar_libro_db(self, row):
        try:
            # Obtener el ID del libro desde la columna 0 (primer columna) de la fila seleccionada
            libro_id = self.tabla.item(row, 0).text()

            # Eliminar el libro de la base de datos
            self.parent.c.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
            self.parent.conn.commit()

            # Eliminar la fila de la tabla
            self.tabla.removeRow(row)

        except Exception as e:
            print("Error al eliminar el libro desde la base de datos:", str(e))

    def crear_tabla_devoluciones_prestamos(self):
        try:
            # Ejecutar la consulta SQL para crear la nueva tabla
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS devoluciones_prestamos AS
                SELECT prestamos.id AS prestamo_id, libros.titulo, prestamos.lector, prestamos.fecha_prestamo, devoluciones.fecha_devolucion
                FROM prestamos
                JOIN libros ON prestamos.libro_id = libros.id
                LEFT JOIN devoluciones ON prestamos.id = devoluciones.prestamo_id
                WHERE devoluciones.fecha_devolucion IS NOT NULL
            ''')
            self.conn.commit()
        except Exception as e:
            print("Error al crear la tabla devoluciones_prestamos:", str(e))

class PaginaPrincipal(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()

        # Fondo de color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(255, 223, 186))  # Color RGB
        self.setPalette(p)

        # Etiqueta de bienvenida
        self.label = QLabel("¡Bienvenido a la Biblioteca!")
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; color: darkblue;")
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Botón llamativo
        self.boton_ingresar = QPushButton("Ingresar al Sistema")
        self.boton_ingresar.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        self.boton_ingresar.clicked.connect(self.ingresar_sistema)
        self.layout.addWidget(self.boton_ingresar, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    def ingresar_sistema(self):
        self.parent.cambiar_pagina(1)  # Cambiar al índice 1 que representa la página de lista de libros
        pass


class PaginaLibros(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Libros")
        self.layout.addWidget(self.label)
        self.agregar_libro_button = QPushButton("Agregar Libro")
        self.agregar_libro_button.clicked.connect(self.mostrar_ventana_agregar_libro)
        self.layout.addWidget(self.agregar_libro_button)
        self.refrescar_libros_button = QPushButton("Refrescar Lista")
        self.refrescar_libros_button.clicked.connect(self.actualizar_tabla_libros)
        self.layout.addWidget(self.refrescar_libros_button)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Título", "Autor", "ISBN", "Categoría", "Páginas", "Género", "Ejemplar", "Ubicación"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.layout.addWidget(self.tabla)
        self.setLayout(self.layout)
        self.actualizar_tabla_libros()

    def mostrar_menu_contextual(self, position):
        row = self.tabla.currentRow()
        if row >= 0:
            menu = QMenu(self)
            eliminar_action = menu.addAction("Eliminar Libro")
            action = menu.exec_(self.tabla.mapToGlobal(position))
            if action == eliminar_action:
                self.eliminar_libro_db(row)
                self.tabla.removeRow(row)

    def mostrar_ventana_agregar_libro(self):
        ventana_agregar_libro = DialogoAgregarLibro(self)
        if ventana_agregar_libro.exec_() == QDialog.Accepted:
            libro = ventana_agregar_libro.obtener_libro()
            if libro:
                self.agregar_libro_db(*libro)

    def actualizar_tabla_libros(self):
        self.tabla.setRowCount(0)
        try:
            self.parent.c.execute("SELECT * FROM libros")
            libros = self.parent.c.fetchall()
            for libro in libros:
                row_position = self.tabla.rowCount()
                self.tabla.insertRow(row_position)
                for col, value in enumerate(libro):
                    item = QTableWidgetItem(str(value))
                    self.tabla.setItem(row_position, col, item)
        except Exception as e:
            print("Error al actualizar tabla de libros:", str(e))

    def agregar_libro_db(self, titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion):
        try:
            self.parent.c.execute("INSERT INTO libros (titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion))
            self.parent.conn.commit()
            self.actualizar_tabla_libros()
        except Exception as e:
            print("Error al agregar libro a la base de datos:", str(e))

    def eliminar_libro_db(self, row):
        try:
            libro_id = int(self.tabla.item(row, 0).text())
            self.parent.c.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
            self.parent.conn.commit()
        except Exception as e:
            print("Error al eliminar el libro desde la base de datos:", str(e))


class DialogoAgregarLibro(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.parent = parent
        self.setWindowTitle("Agregar Libro")
        self.layout = QVBoxLayout()
        self.titulo_label = QLabel("Título del Libro:")
        self.titulo_input = QLineEdit()
        self.autor_label = QLabel("Autor del Libro:")
        self.autor_input = QLineEdit()
        self.isbn_label = QLabel("ISBN:")
        self.isbn_input = QLineEdit()
        self.categoria_label = QLabel("Categoría:")
        self.categoria_input = QLineEdit()
        self.paginas_label = QLabel("Páginas:")
        self.paginas_input = QLineEdit()
        self.genero_label = QLabel("Género:")
        self.genero_input = QLineEdit()
        self.ejemplar_label = QLabel("Ejemplar:")
        self.ejemplar_input = QLineEdit()
        self.ubicacion_label = QLabel("Ubicación:")
        self.ubicacion_input = QLineEdit()
        self.dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialog_button_box.accepted.connect(self.aceptar)
        self.dialog_button_box.rejected.connect(self.rechazar)
        self.layout.addWidget(self.titulo_label)
        self.layout.addWidget(self.titulo_input)
        self.layout.addWidget(self.autor_label)
        self.layout.addWidget(self.autor_input)
        self.layout.addWidget(self.isbn_label)
        self.layout.addWidget(self.isbn_input)
        self.layout.addWidget(self.categoria_label)
        self.layout.addWidget(self.categoria_input)
        self.layout.addWidget(self.paginas_label)
        self.layout.addWidget(self.paginas_input)
        self.layout.addWidget(self.genero_label)
        self.layout.addWidget(self.genero_input)
        self.layout.addWidget(self.ejemplar_label)
        self.layout.addWidget(self.ejemplar_input)
        self.layout.addWidget(self.ubicacion_label)
        self.layout.addWidget(self.ubicacion_input)
        self.layout.addWidget(self.dialog_button_box)
        self.setLayout(self.layout)

    def aceptar(self):
        self.accept()

    def rechazar(self):
        self.reject()

    def obtener_libro(self):
        titulo = self.titulo_input.text()
        autor = self.autor_input.text()
        isbn = self.isbn_input.text()
        categoria = self.categoria_input.text()
        paginas = self.paginas_input.text()
        genero = self.genero_input.text()
        ejemplar = self.ejemplar_input.text()
        ubicacion = self.ubicacion_input.text()
        if titulo:
            return (titulo, autor, isbn, categoria, paginas, genero, ejemplar, ubicacion)
        return None


class PaginaLectores(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Lectores")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class PaginaPrestamos(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.prestamos = []
        self.libros = []
        self.conn = sqlite3.connect("biblioteca2.db")
        self.c = self.conn.cursor()
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Préstamos")
        self.layout.addWidget(self.label)
        self.tabla_prestamos = QTableWidget()
        self.tabla_prestamos.setColumnCount(3)
        self.tabla_prestamos.setHorizontalHeaderLabels(["Título del Libro", "Nombre del Lector", "Fecha de Préstamo"])
        self.tabla_prestamos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_prestamos.setEditTriggers(QTableWidget.NoEditTriggers)  # Los campos no son editables
        self.tabla_prestamos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_prestamos.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.layout.addWidget(self.tabla_prestamos)
        self.lector_input = QLineEdit()
        self.lector_input.setPlaceholderText("Nombre del Lector")
        self.layout.addWidget(self.lector_input)
        self.libros_combo = QComboBox()
        self.layout.addWidget(self.libros_combo)
        self.leer_libros_db()
        self.agregar_libro_button = QPushButton("Agregar Libro")
        self.agregar_libro_button.clicked.connect(self.agregar_libro_prestamo)
        self.layout.addWidget(self.agregar_libro_button)
        self.hacer_prestamo_button = QPushButton("Hacer Préstamo")
        self.hacer_prestamo_button.clicked.connect(self.hacer_prestamo)
        self.layout.addWidget(self.hacer_prestamo_button)
        self.refrescar_prestamos_button = QPushButton("Refrescar Lista")
        self.refrescar_prestamos_button.clicked.connect(self.actualizar_tabla_prestamos)
        self.layout.addWidget(self.refrescar_prestamos_button)
        self.setLayout(self.layout)
        self.actualizar_tabla_prestamos()

    def leer_libros_db(self):
        try:
            self.libros_combo.clear()
            self.libros.clear()
            self.c.execute("SELECT id, titulo, ejemplar FROM libros")
            libros = self.c.fetchall()
            for libro in libros:
                if libro[2] > 0:
                    self.libros_combo.addItem(f"{libro[1]} (ID:{libro[0]})")
                    self.libros.append(libro)
        except Exception as e:
            print("Error al leer libros desde la base de datos:", str(e))

    def agregar_libro_prestamo(self):
        try:
            self.leer_libros_db()
        except Exception as e:
            print("Error al agregar libro al préstamo:", str(e))

    def hacer_prestamo(self):
        try:
            lector = self.lector_input.text()
            libro_index = self.libros_combo.currentIndex()
            if lector and libro_index >= 0:
                libro_id = self.libros[libro_index][0]
                fecha_prestamo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.c.execute("UPDATE libros SET ejemplar = ejemplar - 1 WHERE id = ?", (libro_id,))
                self.conn.commit()
                self.c.execute("INSERT INTO prestamos (libro_id, lector, fecha_prestamo) VALUES (?, ?, ?)",
                               (libro_id, lector, fecha_prestamo))
                self.conn.commit()
                self.limpiar_prestamo()
                self.actualizar_tabla_prestamos()
        except Exception as e:
            print("Error al realizar el préstamo:", str(e))

    def limpiar_prestamo(self):
        self.lector_input.clear()
        self.libros_combo.setCurrentIndex(0)

    def actualizar_tabla_prestamos(self):
        self.tabla_prestamos.setRowCount(0)
        try:
            self.c.execute(
                "SELECT libros.titulo, prestamos.lector, prestamos.fecha_prestamo "
                "FROM prestamos "
                "JOIN libros ON prestamos.libro_id = libros.id")
            prestamos = self.c.fetchall()
            for prestamo in prestamos:
                row_position = self.tabla_prestamos.rowCount()
                self.tabla_prestamos.insertRow(row_position)
                self.tabla_prestamos.setItem(row_position, 0, QTableWidgetItem(prestamo[0]))
                self.tabla_prestamos.setItem(row_position, 1, QTableWidgetItem(prestamo[1]))
                self.tabla_prestamos.setItem(row_position, 2, QTableWidgetItem(prestamo[2]))
        except Exception as e:
            print("Error al actualizar tabla de préstamos:", str(e))

    def mostrar_menu_contextual(self, position):
        row = self.tabla_prestamos.indexAt(position).row()
        if row >= 0:
            menu = QMenu(self)
            devolver_action = menu.addAction("Devolver Libro")
            action = menu.exec_(self.tabla_prestamos.mapToGlobal(position))
            if action == devolver_action:
                libro = self.tabla_prestamos.item(row, 0).text()
                lector = self.tabla_prestamos.item(row, 1).text()
                fecha_prestamo = self.tabla_prestamos.item(row, 2).text()

                # Lógica para devolver el libro
                try:
                    # 1. Obtener el ID del libro que se está devolviendo
                    libro_id = self.c.execute("SELECT id FROM libros WHERE titulo = ?", (libro,)).fetchone()[0]

                    # 2. Eliminar el registro de préstamo
                    self.c.execute(
                        "DELETE FROM prestamos WHERE libro_id = ? AND lector = ? AND fecha_prestamo = ?",
                        (libro_id, lector, fecha_prestamo))
                    self.conn.commit()

                    # 3. Incrementar el contador de ejemplares del libro en la tabla de libros
                    self.c.execute("UPDATE libros SET ejemplar = ejemplar + 1 WHERE id = ?", (libro_id,))
                    self.conn.commit()

                    # 4. Agregar un registro a la tabla de devoluciones
                    fecha_devolucion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.c.execute("INSERT INTO devoluciones (prestamo_id, fecha_devolucion) VALUES (?, ?)",
                                   (libro_id, fecha_devolucion))
                    self.conn.commit()

                    self.actualizar_tabla_prestamos()
                except Exception as e:
                    print("Error al devolver el libro:", str(e))



class PaginaDevoluciones(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.conn = sqlite3.connect("biblioteca2.db")
        self.c = self.conn.cursor()
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Devoluciones")
        self.layout.addWidget(self.label)

        self.tabla_devoluciones = QTableWidget()
        self.tabla_devoluciones.setColumnCount(4)
        self.tabla_devoluciones.setHorizontalHeaderLabels(
            ["ID Devolución", "Título del Libro", "Nombre del Lector", "Fecha de Devolución"])
        self.tabla_devoluciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabla_devoluciones)

        self.nombre_lector_input = QLineEdit()
        self.nombre_lector_input.setPlaceholderText("Nombre del Lector")
        self.layout.addWidget(self.nombre_lector_input)

        self.buscar_devoluciones_button = QPushButton("Buscar Devoluciones")
        self.buscar_devoluciones_button.clicked.connect(self.buscar_devoluciones)
        self.layout.addWidget(self.buscar_devoluciones_button)

        self.refrescar_devoluciones_button = QPushButton("Refrescar Lista")
        self.refrescar_devoluciones_button.clicked.connect(self.actualizar_tabla_devoluciones)
        self.layout.addWidget(self.refrescar_devoluciones_button)

        self.setLayout(self.layout)

    def buscar_devoluciones(self):
        lector = self.nombre_lector_input.text()
        self.mostrar_devoluciones(lector)

    def actualizar_tabla_devoluciones(self):
        self.mostrar_devoluciones()

    def mostrar_devoluciones(self, lector=None):
        self.tabla_devoluciones.setRowCount(0)
        try:
            if lector:
                self.c.execute(
                    "SELECT devoluciones.id, libros.titulo, prestamos.lector, devoluciones.fecha_devolucion "
                    "FROM prestamos "
                    "JOIN libros ON prestamos.libro_id = libros.id "
                    "LEFT JOIN devoluciones ON prestamos.id = devoluciones.prestamo_id "
                    "WHERE prestamos.lector = ? AND devoluciones.fecha_devolucion IS NOT NULL", (lector,))
            else:
                self.c.execute(
                    "SELECT devoluciones.id, libros.titulo, prestamos.lector, devoluciones.fecha_devolucion "
                    "FROM prestamos "
                    "JOIN libros ON prestamos.libro_id = libros.id "
                    "LEFT JOIN devoluciones ON prestamos.id = devoluciones.prestamo_id "
                    "WHERE devoluciones.fecha_devolucion IS NOT NULL"
                )
            devoluciones = self.c.fetchall()
            for devolucion in devoluciones:
                row_position = self.tabla_devoluciones.rowCount()
                self.tabla_devoluciones.insertRow(row_position)
                for col, value in enumerate(devolucion):
                    item = QTableWidgetItem(str(value))
                    self.tabla_devoluciones.setItem(row_position, col, item)
        except Exception as e:
            print("Error al mostrar devoluciones:", str(e))

    def closeEvent(self, event):
        self.conn.close()
class PaginaAlumnos(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Conexión a la base de datos y creación de la tabla de alumnos
        self.conn = sqlite3.connect("biblioteca2.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                codigo TEXT,
                edad INTEGER
            )
        ''')
        self.conn.commit()

        # Diseño de la interfaz de usuario
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Alumnos")
        self.layout.addWidget(self.label)

        # Campos de entrada para datos del alumno
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        self.layout.addWidget(self.nombre_input)

        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Apellido")
        self.layout.addWidget(self.apellido_input)

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código")
        self.layout.addWidget(self.codigo_input)

        self.edad_input = QLineEdit()
        self.edad_input.setPlaceholderText("Edad")
        self.layout.addWidget(self.edad_input)

        # Botón para agregar un alumno
        self.agregar_alumno_button = QPushButton("Agregar Alumno")
        self.agregar_alumno_button.clicked.connect(self.agregar_alumno)
        self.layout.addWidget(self.agregar_alumno_button)

        # Tabla para mostrar la lista de alumnos
        self.tabla_alumnos = QTableWidget()
        self.tabla_alumnos.setColumnCount(4)
        self.tabla_alumnos.setHorizontalHeaderLabels(["Nombre", "Apellido", "Código", "Edad"])
        self.tabla_alumnos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabla_alumnos)

        self.actualizar_tabla_alumnos()  # Cargar datos de alumnos existentes al inicio

        self.setLayout(self.layout)

    def agregar_alumno(self):
        nombre = self.nombre_input.text()
        apellido = self.apellido_input.text()
        codigo = self.codigo_input.text()
        edad = self.edad_input.text()

        try:
            self.c.execute("INSERT INTO alumnos (nombre, apellido, codigo, edad) VALUES (?, ?, ?, ?)",
                           (nombre, apellido, codigo, edad))
            self.conn.commit()
            self.limpiar_campos()
            self.actualizar_tabla_alumnos()
        except Exception as e:
            print("Error al agregar alumno:", str(e))

    def limpiar_campos(self):
        self.nombre_input.clear()
        self.apellido_input.clear()
        self.codigo_input.clear()
        self.edad_input.clear()

    def actualizar_tabla_alumnos(self):
        self.tabla_alumnos.setRowCount(0)
        try:
            self.c.execute("SELECT nombre, apellido, codigo, edad FROM alumnos")
            alumnos = self.c.fetchall()
            for alumno in alumnos:
                row_position = self.tabla_alumnos.rowCount()
                self.tabla_alumnos.insertRow(row_position)
                self.tabla_alumnos.setItem(row_position, 0, QTableWidgetItem(alumno[0]))
                self.tabla_alumnos.setItem(row_position, 1, QTableWidgetItem(alumno[1]))
                self.tabla_alumnos.setItem(row_position, 2, QTableWidgetItem(alumno[2]))
                self.tabla_alumnos.setItem(row_position, 3, QTableWidgetItem(str(alumno[3])))
        except Exception as e:
            print("Error al actualizar tabla de alumnos:", str(e))


class PaginaProfesores(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Conexión a la base de datos y creación de la tabla de profesores
        self.conn = sqlite3.connect("biblioteca2.db")
        self.c = self.conn.cursor()
        self.create_profesores_table()

        # Diseño de la interfaz de usuario
        self.layout = QVBoxLayout()
        self.label = QLabel("Página de Profesores")
        self.layout.addWidget(self.label)

        # Campos de entrada para datos del profesor
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        self.layout.addWidget(self.nombre_input)

        self.especialidad_input = QLineEdit()
        self.especialidad_input.setPlaceholderText("Especialidad")
        self.layout.addWidget(self.especialidad_input)

        # Botón para agregar un profesor
        self.agregar_profesor_button = QPushButton("Agregar Profesor")
        self.agregar_profesor_button.clicked.connect(self.agregar_profesor)
        self.layout.addWidget(self.agregar_profesor_button)

        # Tabla para mostrar la lista de profesores
        self.tabla_profesores = QTableWidget()
        self.tabla_profesores.setColumnCount(3)
        self.tabla_profesores.setHorizontalHeaderLabels(["ID", "Nombre", "Especialidad"])
        self.tabla_profesores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabla_profesores)

        self.actualizar_tabla_profesores()  # Cargar datos de profesores existentes al inicio

        self.setLayout(self.layout)

    def create_profesores_table(self):
        try:
            # Ejecuta la consulta SQL para crear la tabla profesores si no existe
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS profesores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    especialidad TEXT
                )
            ''')
            self.conn.commit()

        except Exception as e:
            print("Error creating profesores table:", str(e))

    def agregar_profesor(self):
        nombre = self.nombre_input.text()
        especialidad = self.especialidad_input.text()

        try:
            self.c.execute("INSERT INTO profesores (nombre, especialidad) VALUES (?, ?)",
                           (nombre, especialidad))
            self.conn.commit()
            self.limpiar_campos()
            self.actualizar_tabla_profesores()
        except Exception as e:
            print("Error al agregar profesor:", str(e))

    def limpiar_campos(self):
        self.nombre_input.clear()
        self.especialidad_input.clear()

    def actualizar_tabla_profesores(self):
        self.tabla_profesores.setRowCount(0)
        try:
            self.c.execute("SELECT id, nombre, especialidad FROM profesores")
            profesores = self.c.fetchall()
            for profesor in profesores:
                row_position = self.tabla_profesores.rowCount()
                self.tabla_profesores.insertRow(row_position)
                for col, value in enumerate(profesor):
                    item = QTableWidgetItem(str(value))
                    self.tabla_profesores.setItem(row_position, col, item)
        except Exception as e:
            print("Error al actualizar tabla de profesores:", str(e))

    def closeEvent(self, event):
        self.conn.close()

class PaginaAyuda(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()

        self.label = QLabel("Contenido de Ayuda\n\n"
                            "1. Página de Libros:\n"
                            "   - Puedes ver la lista de libros y realizar diversas acciones como eliminar y agregar libros.\n\n"
                            "2. Página de Préstamos:\n"
                            "   - Realiza préstamos de libros a los lectores y gestiona las devoluciones.\n\n"
                            "3. Página de Devoluciones:\n"
                            "   - Visualiza y busca devoluciones realizadas por los lectores.\n\n"
                            "4. Página de Alumnos:\n"
                            "   - Gestiona la información de los alumnos, incluyendo agregar nuevos alumnos.\n\n"
                            "5. Página de Profesores:\n"
                            "   - Gestiona la información de los profesores, incluyendo agregar nuevos profesores.\n\n"
                            "6. Página de Ayuda:\n"
                            "   - Aquí estás ahora. Consulta este contenido para obtener ayuda sobre el sistema.\n\n"
                            "7. Página de Ajustes:\n"
                            "   - Configura ajustes del sistema.\n\n"
                            "8. Página de Informes:\n"
                            "   - Genera informes relacionados con la biblioteca.\n\n"
                            "9. Página de Lectores:\n"
                            "   - Información sobre los lectores.\n\n"
                            "10. Menú Contextual:\n"
                            "    - Haz clic derecho en la tabla de libros o préstamos para acceder a opciones adicionales.\n\n"
                            "Esperamos que encuentres útil esta guía de ayuda. ¡Disfruta usando el sistema!")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
class PaginaAjustes(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()

        self.label = QLabel("Configuración de Ajustes")
        self.layout.addWidget(self.label)

        # Create a form layout for settings
        self.form_layout = QFormLayout()

        # Font Settings
        self.font_label = QLabel("Tipo de Letra:")
        self.font_button = QPushButton("Seleccionar Tipo de Letra")
        self.font_button.clicked.connect(self.seleccionar_tipo_letra)
        self.form_layout.addRow(self.font_label, self.font_button)

        # Font Size
        self.font_size_label = QLabel("Tamaño de Letra:")
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(1, 50)
        self.form_layout.addRow(self.font_size_label, self.font_size_input)

        # Font Color
        self.font_color_label = QLabel("Color de Letra:")
        self.font_color_button = QPushButton("Seleccionar Color de Letra")
        self.font_color_button.clicked.connect(self.seleccionar_color_letra)
        self.form_layout.addRow(self.font_color_label, self.font_color_button)

        # Background Color
        self.bg_color_label = QLabel("Color de Fondo:")
        self.bg_color_button = QPushButton("Seleccionar Color de Fondo")
        self.bg_color_button.clicked.connect(self.seleccionar_color_fondo)
        self.form_layout.addRow(self.bg_color_label, self.bg_color_button)

        self.layout.addLayout(self.form_layout)

        # Add a button to save and apply settings
        self.save_button = QPushButton("Guardar y Aplicar Ajustes")
        self.save_button.clicked.connect(self.guardar_y_aplicar_ajustes)
        self.layout.addWidget(self.save_button)

        # Load settings when the page is initialized
        self.cargar_ajustes()
        self.aplicar_ajustes()

        self.setLayout(self.layout)

    def seleccionar_tipo_letra(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.settings['font'] = font
            self.aplicar_ajustes()

    def seleccionar_color_letra(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings['font_color'] = color
            self.aplicar_ajustes()

    def seleccionar_color_fondo(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings['bg_color'] = color
            self.aplicar_ajustes()

    def guardar_y_aplicar_ajustes(self):
        # Save settings
        self.guardar_ajustes()
        # Apply settings
        self.aplicar_ajustes()

    def cargar_ajustes(self):
        # Load settings from a file or database, for example
        # This is a simulated example, use your own logic to load settings
        self.settings = {
            'font': QFont('Arial', 12),
            'font_color': QColor('black'),
            'bg_color': QColor('white'),
            'font_size': 12,
        }

    def guardar_ajustes(self):
        # Save settings to a file or database, for example
        # This is a simulated example, use your own logic to save settings
        print("Settings saved:", self.settings)

    def aplicar_ajustes(self):
        # Apply settings to the UI or any other components
        font = self.settings.get('font', QFont('Arial', 12))
        font_color = self.settings.get('font_color', QColor('black'))
        bg_color = self.settings.get('bg_color', QColor('white'))
        font_size = self.settings.get('font_size', 12)

        # Apply font settings
        self.font_button.setFont(font)
        self.font_size_input.setValue(font_size)
        self.font_color_button.setStyleSheet(f"background-color: {font_color.name()}")
        self.bg_color_button.setStyleSheet(f"background-color: {bg_color.name()}")
        # Apply other settings as needed...

class PaginaInformes(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        self.label = QLabel("Generar Informes")
        self.layout.addWidget(self.label)

        # Add buttons for different types of reports
        self.report_buttons = {
            "Prestamos": QPushButton("Informe de Préstamos"),
            "Devoluciones": QPushButton("Informe de Devoluciones"),
            "Profesores": QPushButton("Lista de Profesores"),
            "Alumnos": QPushButton("Lista de Alumnos")
        }

        for report_type, button in self.report_buttons.items():
            button.clicked.connect(lambda _, rpt=report_type: self.generar_informe_pdf(rpt))
            self.layout.addWidget(button)

        self.setLayout(self.layout)

    def generar_informe_pdf(self, report_type):
        # Open a file dialog to choose the location to save the PDF file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar informe como PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)

        if file_name:
            # Create a PDF file and draw content based on the report type
            c = canvas.Canvas(file_name, pagesize=letter)

            # Fetch data from the database based on the report type
            if report_type == "Prestamos":
                self.generar_informe_prestamos(c)
            elif report_type == "Devoluciones":
                self.generar_informe_devoluciones(c)
            elif report_type == "Profesores":
                self.generar_lista_profesores(c)
            elif report_type == "Alumnos":
                self.generar_lista_alumnos(c)

            c.save()

            print(f"Informe de {report_type} generado en: {file_name}")

    def generar_informe_prestamos(self, c):
        # Fetch data from the 'prestamos' table
        self.parent.c.execute("SELECT libros.titulo, prestamos.lector, prestamos.fecha_prestamo FROM prestamos JOIN libros ON prestamos.libro_id = libros.id")
        prestamos = self.parent.c.fetchall()

        # Draw content on the PDF based on the fetched data
        c.drawString(100, 800, "Informe de Préstamos")
        row_position = 780
        for prestamo in prestamos:
            row_position -= 15
            c.drawString(100, row_position, f"Título: {prestamo[0]}, Lector: {prestamo[1]}, Fecha de Préstamo: {prestamo[2]}")

    def generar_informe_devoluciones(self, c):
        # Fetch data from the 'devoluciones' table
        self.parent.c.execute("SELECT libros.titulo, prestamos.lector, prestamos.fecha_prestamo, devoluciones.fecha_devolucion FROM prestamos JOIN libros ON prestamos.libro_id = libros.id LEFT JOIN devoluciones ON prestamos.id = devoluciones.prestamo_id WHERE devoluciones.fecha_devolucion IS NOT NULL")
        devoluciones = self.parent.c.fetchall()

        # Draw content on the PDF based on the fetched data
        c.drawString(100, 800, "Informe de Devoluciones")
        row_position = 780
        for devolucion in devoluciones:
            row_position -= 15
            c.drawString(100, row_position, f"Título: {devolucion[0]}, Lector: {devolucion[1]}, Fecha de Préstamo: {devolucion[2]}, Fecha de Devolución: {devolucion[3]}")

    def generar_lista_profesores(self, c):
        # Fetch data from the 'profesores' table (replace 'profesores' with the actual table name)
        self.parent.c.execute("SELECT * FROM profesores")
        profesores = self.parent.c.fetchall()

        # Draw content on the PDF based on the fetched data
        c.drawString(100, 800, "Lista de Profesores")

        # Define column widths and positions
        column_widths = [50, 150, 150]  # You can adjust the widths based on your needs
        column_positions = [100, 200, 350]  # Adjust positions accordingly

        # Draw table headers
        row_position = 780
        for i, header in enumerate(["ID", "Nombre", "Especialidad"]):
            c.drawString(column_positions[i], row_position, header)

        # Draw table rows
        for profesor in profesores:
            row_position -= 15
            for i, value in enumerate(profesor):
                c.drawString(column_positions[i], row_position, str(value))
    def generar_lista_alumnos(self, c):
        # Fetch data from the 'alumnos' table (replace 'alumnos' with the actual table name)
        self.parent.c.execute("SELECT * FROM alumnos")
        alumnos = self.parent.c.fetchall()

        # Draw content on the PDF based on the fetched data
        c.drawString(100, 800, "Lista de Alumnos")
        row_position = 780
        for alumno in alumnos:
            row_position -= 15
            c.drawString(100, row_position, f"Nombre: {alumno[1]}, Apellido: {alumno[2]}, Código: {alumno[3]}, Edad: {alumno[4]}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec_())
