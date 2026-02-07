"""
INTERFAZ GRÁFICA - SISTEMA DE CAFETERÍA
Usa Tkinter para crear una interfaz moderna y profesional
Autor: Sistema de Ventas
Fecha: Febrero 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
from sistema_gestion_productos import crear_catalogo_cafeteria
from sistema_ventas_cafeteria import Venta, HistorialVentas, SistemaPOS

# ============================================================
# COLORES Y ESTILOS
# ============================================================

COLORES = {
    'primario': '#6F4E37',      # Café oscuro
    'secundario': '#A0826D',    # Café claro
    'acento': '#D4A574',        # Crema
    'fondo': '#F5F5DC',         # Beige
    'texto': '#2C1810',         # Café muy oscuro
    'exito': '#4CAF50',         # Verde
    'error': '#F44336',         # Rojo
    'advertencia': '#FF9800',   # Naranja
    'blanco': '#FFFFFF'
}

# ============================================================
# CLASE PRINCIPAL - VENTANA
# ============================================================

class CafeteriaApp:
    """Aplicación principal con interfaz gráfica."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("☕ Sistema de Cafetería - Punto de Venta")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORES['fondo'])
        
        # Inicializar datos
        self.gestor = crear_catalogo_cafeteria()
        self.pos = SistemaPOS(self.gestor)
        self.cajero = "Cajero Principal"
        
        # Variables
        self.carrito_items = []
        self.productos_filtrados = []
        
        # Configurar estilo
        self.configurar_estilos()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Mostrar bienvenida
        self.mostrar_dialogo_cajero()
    
    def configurar_estilos(self):
        """Configura los estilos de ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Botones
        style.configure('Primary.TButton',
                       background=COLORES['primario'],
                       foreground=COLORES['blanco'],
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Secondary.TButton',
                       background=COLORES['secundario'],
                       foreground=COLORES['blanco'],
                       font=('Arial', 9),
                       padding=8)
        
        style.configure('Success.TButton',
                       background=COLORES['exito'],
                       foreground=COLORES['blanco'],
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Danger.TButton',
                       background=COLORES['error'],
                       foreground=COLORES['blanco'],
                       font=('Arial', 9),
                       padding=8)
        
        # Treeview
        style.configure('Treeview',
                       background=COLORES['blanco'],
                       foreground=COLORES['texto'],
                       fieldbackground=COLORES['blanco'],
                       font=('Arial', 9))
        
        style.configure('Treeview.Heading',
                       background=COLORES['primario'],
                       foreground=COLORES['blanco'],
                       font=('Arial', 10, 'bold'))
    
    def crear_interfaz(self):
        """Crea la interfaz principal."""
        
        # Frame superior - Header
        self.crear_header()
        
        # Frame principal - Dividido en 3 columnas
        main_frame = tk.Frame(self.root, bg=COLORES['fondo'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Columna 1: Productos (40%)
        self.crear_panel_productos(main_frame)
        
        # Columna 2: Carrito (35%)
        self.crear_panel_carrito(main_frame)
        
        # Columna 3: Acciones (25%)
        self.crear_panel_acciones(main_frame)
        
        # Frame inferior - Status bar
        self.crear_status_bar()
    
    def crear_header(self):
        """Crea el encabezado de la aplicación."""
        header = tk.Frame(self.root, bg=COLORES['primario'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Título
        titulo = tk.Label(header,
                         text="☕ SISTEMA DE CAFETERÍA",
                         font=('Arial', 24, 'bold'),
                         bg=COLORES['primario'],
                         fg=COLORES['blanco'])
        titulo.pack(side='left', padx=20, pady=20)
        
        # Info del cajero
        info_frame = tk.Frame(header, bg=COLORES['primario'])
        info_frame.pack(side='right', padx=20)
        
        self.lbl_cajero = tk.Label(info_frame,
                                   text=f"Cajero: {self.cajero}",
                                   font=('Arial', 12),
                                   bg=COLORES['primario'],
                                   fg=COLORES['blanco'])
        self.lbl_cajero.pack()
        
        self.lbl_fecha = tk.Label(info_frame,
                                  text=datetime.now().strftime("%d/%m/%Y %H:%M"),
                                  font=('Arial', 10),
                                  bg=COLORES['primario'],
                                  fg=COLORES['acento'])
        self.lbl_fecha.pack()
        
        # Actualizar hora cada segundo
        self.actualizar_hora()
    
    def crear_panel_productos(self, parent):
        """Crea el panel de productos."""
        frame = tk.LabelFrame(parent,
                             text="📦 PRODUCTOS DISPONIBLES",
                             font=('Arial', 12, 'bold'),
                             bg=COLORES['fondo'],
                             fg=COLORES['texto'],
                             padx=10, pady=10)
        frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Búsqueda y filtros
        search_frame = tk.Frame(frame, bg=COLORES['fondo'])
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame,
                text="Buscar:",
                bg=COLORES['fondo'],
                font=('Arial', 9)).pack(side='left')
        
        self.entry_buscar = tk.Entry(search_frame, font=('Arial', 10), width=20)
        self.entry_buscar.pack(side='left', padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.buscar_producto)
        
        # Categorías
        tk.Label(search_frame,
                text="Categoría:",
                bg=COLORES['fondo'],
                font=('Arial', 9)).pack(side='left', padx=(10, 0))
        
        self.combo_categoria = ttk.Combobox(search_frame,
                                           values=['Todas', 'Bebidas Calientes', 'Bebidas Frías',
                                                  'Panadería', 'Repostería', 'Desayunos', 'Comidas', 'Extras'],
                                           state='readonly',
                                           width=15)
        self.combo_categoria.set('Todas')
        self.combo_categoria.pack(side='left', padx=5)
        self.combo_categoria.bind('<<ComboboxSelected>>', self.filtrar_categoria)
        
        # Lista de productos
        self.tree_productos = ttk.Treeview(frame,
                                          columns=('Código', 'Nombre', 'Precio', 'Stock'),
                                          show='headings',
                                          height=20)
        
        self.tree_productos.heading('Código', text='Código')
        self.tree_productos.heading('Nombre', text='Nombre')
        self.tree_productos.heading('Precio', text='Precio')
        self.tree_productos.heading('Stock', text='Stock')
        
        self.tree_productos.column('Código', width=80)
        self.tree_productos.column('Nombre', width=200)
        self.tree_productos.column('Precio', width=80)
        self.tree_productos.column('Stock', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_productos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Doble clic para agregar
        self.tree_productos.bind('<Double-1>', lambda e: self.agregar_al_carrito())
        
        # Cargar productos
        self.cargar_productos()
        
        # Configurar grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=2)
    
    def crear_panel_carrito(self, parent):
        """Crea el panel del carrito de compras."""
        frame = tk.LabelFrame(parent,
                             text="🛒 CARRITO DE COMPRAS",
                             font=('Arial', 12, 'bold'),
                             bg=COLORES['fondo'],
                             fg=COLORES['texto'],
                             padx=10, pady=10)
        frame.grid(row=0, column=1, sticky='nsew', padx=5)
        
        # Lista del carrito
        self.tree_carrito = ttk.Treeview(frame,
                                        columns=('Código', 'Producto', 'Cant.', 'P.Unit', 'Subtotal'),
                                        show='headings',
                                        height=15)
        
        self.tree_carrito.heading('Código', text='Código')
        self.tree_carrito.heading('Producto', text='Producto')
        self.tree_carrito.heading('Cant.', text='Cant.')
        self.tree_carrito.heading('P.Unit', text='P.Unit')
        self.tree_carrito.heading('Subtotal', text='Subtotal')
        
        self.tree_carrito.column('Código', width=70)
        self.tree_carrito.column('Producto', width=150)
        self.tree_carrito.column('Cant.', width=50)
        self.tree_carrito.column('P.Unit', width=60)
        self.tree_carrito.column('Subtotal', width=70)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones del carrito
        btn_frame = tk.Frame(frame, bg=COLORES['fondo'])
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame,
                  text="➕ Agregar Seleccionado",
                  style='Secondary.TButton',
                  command=self.agregar_al_carrito).pack(side='left', padx=2)
        
        ttk.Button(btn_frame,
                  text="✏️ Modificar Cantidad",
                  style='Secondary.TButton',
                  command=self.modificar_cantidad).pack(side='left', padx=2)
        
        ttk.Button(btn_frame,
                  text="🗑️ Eliminar",
                  style='Danger.TButton',
                  command=self.eliminar_del_carrito).pack(side='left', padx=2)
        
        # Total
        total_frame = tk.Frame(frame, bg=COLORES['primario'], pady=15)
        total_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(total_frame,
                text="TOTAL:",
                font=('Arial', 16, 'bold'),
                bg=COLORES['primario'],
                fg=COLORES['blanco']).pack(side='left', padx=10)
        
        self.lbl_total = tk.Label(total_frame,
                                 text="$0.00",
                                 font=('Arial', 24, 'bold'),
                                 bg=COLORES['primario'],
                                 fg=COLORES['acento'])
        self.lbl_total.pack(side='right', padx=10)
        
        parent.grid_columnconfigure(1, weight=2)
    
    def crear_panel_acciones(self, parent):
        """Crea el panel de acciones."""
        frame = tk.LabelFrame(parent,
                             text="⚡ ACCIONES",
                             font=('Arial', 12, 'bold'),
                             bg=COLORES['fondo'],
                             fg=COLORES['texto'],
                             padx=10, pady=10)
        frame.grid(row=0, column=2, sticky='nsew', padx=(5, 0))
        
        # Botones principales
        ttk.Button(frame,
                  text="💰 COBRAR VENTA",
                  style='Success.TButton',
                  command=self.cobrar_venta).pack(fill='x', pady=5)
        
        ttk.Button(frame,
                  text="🆕 Nueva Venta",
                  style='Primary.TButton',
                  command=self.nueva_venta).pack(fill='x', pady=5)
        
        ttk.Button(frame,
                  text="🗑️ Vaciar Carrito",
                  style='Danger.TButton',
                  command=self.vaciar_carrito).pack(fill='x', pady=5)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Otras acciones
        tk.Label(frame,
                text="📊 CONSULTAS Y REPORTES",
                font=('Arial', 10, 'bold'),
                bg=COLORES['fondo']).pack(pady=(0, 10))
        
        ttk.Button(frame,
                  text="📋 Historial de Ventas",
                  style='Secondary.TButton',
                  command=self.ver_historial).pack(fill='x', pady=3)
        
        ttk.Button(frame,
                  text="📈 Reporte Diario",
                  style='Secondary.TButton',
                  command=self.reporte_diario).pack(fill='x', pady=3)
        
        ttk.Button(frame,
                  text="⚠️ Stock Bajo",
                  style='Secondary.TButton',
                  command=self.ver_stock_bajo).pack(fill='x', pady=3)
        
        ttk.Button(frame,
                  text="🏆 Top Productos",
                  style='Secondary.TButton',
                  command=self.ver_top_productos).pack(fill='x', pady=3)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Gestión
        tk.Label(frame,
                text="⚙️ GESTIÓN",
                font=('Arial', 10, 'bold'),
                bg=COLORES['fondo']).pack(pady=(0, 10))
        
        ttk.Button(frame,
                  text="📦 Ver Inventario",
                  style='Secondary.TButton',
                  command=self.ver_inventario).pack(fill='x', pady=3)
        
        ttk.Button(frame,
                  text="➕ Agregar Stock",
                  style='Secondary.TButton',
                  command=self.agregar_stock).pack(fill='x', pady=3)
        
        ttk.Button(frame,
                  text="💾 Guardar Datos",
                  style='Secondary.TButton',
                  command=self.guardar_datos).pack(fill='x', pady=3)
        
        # Salir
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)
        
        ttk.Button(frame,
                  text="🚪 Salir",
                  style='Danger.TButton',
                  command=self.salir).pack(fill='x', pady=5)
        
        parent.grid_columnconfigure(2, weight=1)
    
    def crear_status_bar(self):
        """Crea la barra de estado."""
        status = tk.Frame(self.root, bg=COLORES['secundario'], height=30)
        status.pack(fill='x', side='bottom')
        
        self.lbl_status = tk.Label(status,
                                   text="✓ Sistema listo",
                                   font=('Arial', 9),
                                   bg=COLORES['secundario'],
                                   fg=COLORES['blanco'],
                                   anchor='w')
        self.lbl_status.pack(side='left', padx=10, fill='x', expand=True)
        
        self.lbl_productos = tk.Label(status,
                                      text=f"Productos: {len(self.gestor.productos)}",
                                      font=('Arial', 9),
                                      bg=COLORES['secundario'],
                                      fg=COLORES['blanco'])
        self.lbl_productos.pack(side='right', padx=10)
        
        self.lbl_ventas = tk.Label(status,
                                   text=f"Ventas hoy: {len(self.pos.historial.ventas)}",
                                   font=('Arial', 9),
                                   bg=COLORES['secundario'],
                                   fg=COLORES['blanco'])
        self.lbl_ventas.pack(side='right', padx=10)
    
    # ============================================================
    # FUNCIONES DE PRODUCTOS
    # ============================================================
    
    def cargar_productos(self):
        """Carga los productos en el TreeView."""
        # Limpiar
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Cargar
        for producto in self.gestor.productos:
            self.tree_productos.insert('', 'end', values=(
                producto.get_codigo(),
                producto.get_nombre(),
                f"${producto.get_precio_venta():.2f}",
                producto.get_stock()
            ))
    
    def buscar_producto(self, event=None):
        """Busca productos por nombre o código."""
        busqueda = self.entry_buscar.get().lower()
        
        # Limpiar
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Filtrar y mostrar
        for producto in self.gestor.productos:
            if busqueda in producto.get_nombre().lower() or busqueda in producto.get_codigo().lower():
                self.tree_productos.insert('', 'end', values=(
                    producto.get_codigo(),
                    producto.get_nombre(),
                    f"${producto.get_precio_venta():.2f}",
                    producto.get_stock()
                ))
    
    def filtrar_categoria(self, event=None):
        """Filtra productos por categoría."""
        categoria = self.combo_categoria.get()
        
        # Limpiar
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Filtrar y mostrar
        for producto in self.gestor.productos:
            if categoria == 'Todas' or producto.get_categoria() == categoria:
                self.tree_productos.insert('', 'end', values=(
                    producto.get_codigo(),
                    producto.get_nombre(),
                    f"${producto.get_precio_venta():.2f}",
                    producto.get_stock()
                ))
    
    # ============================================================
    # FUNCIONES DEL CARRITO
    # ============================================================
    
    def agregar_al_carrito(self):
        """Agrega el producto seleccionado al carrito."""
        seleccion = self.tree_productos.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un producto")
            return
        
        # Obtener código del producto
        item = self.tree_productos.item(seleccion[0])
        codigo = item['values'][0]
        
        # Buscar producto
        producto = self.gestor.buscar_por_codigo(codigo)
        
        if not producto:
            return
        
        # Pedir cantidad
        cantidad = self.pedir_cantidad()
        
        if cantidad is None:
            return
        
        # Iniciar venta si no existe
        if not self.pos.venta_actual:
            self.pos.nueva_venta()
        
        # Agregar al carrito
        if self.pos.venta_actual.agregar_item(producto, cantidad):
            self.actualizar_carrito()
            self.actualizar_status(f"✓ Agregado: {cantidad}x {producto.get_nombre()}")
        else:
            messagebox.showerror("Error", "No se pudo agregar el producto")
    
    def modificar_cantidad(self):
        """Modifica la cantidad de un producto en el carrito."""
        seleccion = self.tree_carrito.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un producto del carrito")
            return
        
        item = self.tree_carrito.item(seleccion[0])
        codigo = item['values'][0]
        
        nueva_cantidad = self.pedir_cantidad()
        
        if nueva_cantidad is None:
            return
        
        if self.pos.venta_actual.modificar_cantidad_item(codigo, nueva_cantidad):
            self.actualizar_carrito()
            self.actualizar_status(f"✓ Cantidad actualizada")
    
    def eliminar_del_carrito(self):
        """Elimina un producto del carrito."""
        seleccion = self.tree_carrito.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un producto del carrito")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto del carrito?"):
            item = self.tree_carrito.item(seleccion[0])
            codigo = item['values'][0]
            
            if self.pos.venta_actual.eliminar_item(codigo):
                self.actualizar_carrito()
                self.actualizar_status("✓ Producto eliminado del carrito")
    
    def actualizar_carrito(self):
        """Actualiza la vista del carrito."""
        # Limpiar
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        if not self.pos.venta_actual:
            self.lbl_total.config(text="$0.00")
            return
        
        # Cargar items
        for item in self.pos.venta_actual.get_items():
            self.tree_carrito.insert('', 'end', values=(
                item['codigo'],
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
        
        # Actualizar total
        total = self.pos.venta_actual.get_total()
        self.lbl_total.config(text=f"${total:.2f}")
    
    def vaciar_carrito(self):
        """Vacía todo el carrito."""
        if not self.pos.venta_actual:
            return
        
        if messagebox.askyesno("Confirmar", "¿Vaciar todo el carrito?"):
            self.pos.venta_actual.vaciar_carrito()
            self.actualizar_carrito()
            self.actualizar_status("✓ Carrito vaciado")
    
    # ============================================================
    # FUNCIONES DE VENTA
    # ============================================================
    
    def nueva_venta(self):
        """Inicia una nueva venta."""
        if self.pos.venta_actual and self.pos.venta_actual.get_items():
            if not messagebox.askyesno("Confirmar",
                                      "Hay una venta en progreso.\n¿Cancelarla e iniciar nueva?"):
                return
        
        self.pos.nueva_venta()
        self.actualizar_carrito()
        self.actualizar_status(f"✓ Nueva venta iniciada - Ticket #{self.pos.venta_actual.get_numero_venta()}")
    
    def cobrar_venta(self):
        """Finaliza y cobra la venta."""
        if not self.pos.venta_actual or not self.pos.venta_actual.get_items():
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        # Ventana de pago
        VentanaPago(self.root, self.pos, self.actualizar_despues_venta)
    
    def actualizar_despues_venta(self):
        """Actualiza la interfaz después de completar una venta."""
        self.actualizar_carrito()
        self.cargar_productos()
        self.lbl_ventas.config(text=f"Ventas hoy: {len(self.pos.historial.ventas)}")
        self.actualizar_status("✓ Venta completada exitosamente")
    
    # ============================================================
    # FUNCIONES DE REPORTES
    # ============================================================
    
    def ver_historial(self):
        """Muestra el historial de ventas."""
        VentanaHistorial(self.root, self.pos.historial)
    
    def reporte_diario(self):
        """Muestra el reporte diario."""
        VentanaReporte(self.root, self.pos.historial, 'diario')
    
    def ver_stock_bajo(self):
        """Muestra productos con stock bajo."""
        VentanaStockBajo(self.root, self.gestor)
    
    def ver_top_productos(self):
        """Muestra los productos más vendidos."""
        VentanaTopProductos(self.root, self.pos.historial)
    
    def ver_inventario(self):
        """Muestra el inventario completo."""
        VentanaInventario(self.root, self.gestor)
    
    def agregar_stock(self):
        """Abre ventana para agregar stock."""
        VentanaAgregarStock(self.root, self.gestor, self.cargar_productos)
    
    # ============================================================
    # FUNCIONES AUXILIARES
    # ============================================================
    
    def pedir_cantidad(self):
        """Pide la cantidad al usuario."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Cantidad")
        ventana.geometry("300x150")
        ventana.configure(bg=COLORES['fondo'])
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana,
                text="Ingresa la cantidad:",
                font=('Arial', 12),
                bg=COLORES['fondo']).pack(pady=20)
        
        entry = tk.Entry(ventana, font=('Arial', 14), width=10, justify='center')
        entry.pack(pady=10)
        entry.focus()
        
        resultado = [None]
        
        def aceptar():
            try:
                cantidad = int(entry.get())
                if cantidad > 0:
                    resultado[0] = cantidad
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
            except ValueError:
                messagebox.showerror("Error", "Ingresa un número válido")
        
        def cancelar():
            ventana.destroy()
        
        btn_frame = tk.Frame(ventana, bg=COLORES['fondo'])
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Aceptar", style='Primary.TButton',
                  command=aceptar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", style='Secondary.TButton',
                  command=cancelar).pack(side='left', padx=5)
        
        entry.bind('<Return>', lambda e: aceptar())
        
        ventana.wait_window()
        return resultado[0]
    
    def mostrar_dialogo_cajero(self):
        """Muestra diálogo para ingresar el nombre del cajero."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Bienvenido")
        ventana.geometry("400x200")
        ventana.configure(bg=COLORES['fondo'])
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana,
                text="☕ Bienvenido al Sistema",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        tk.Label(ventana,
                text="Ingresa tu nombre:",
                font=('Arial', 12),
                bg=COLORES['fondo']).pack(pady=10)
        
        entry = tk.Entry(ventana, font=('Arial', 12), width=25)
        entry.pack(pady=10)
        entry.focus()
        
        def aceptar():
            nombre = entry.get().strip()
            if nombre:
                self.cajero = nombre
                self.pos.cajero = nombre
                self.lbl_cajero.config(text=f"Cajero: {self.cajero}")
                ventana.destroy()
            else:
                ventana.destroy()
        
        ttk.Button(ventana, text="Iniciar Sesión", style='Primary.TButton',
                  command=aceptar).pack(pady=10)
        
        entry.bind('<Return>', lambda e: aceptar())
        
        ventana.wait_window()
    
    def actualizar_hora(self):
        """Actualiza la hora en el header."""
        self.lbl_fecha.config(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.root.after(1000, self.actualizar_hora)
    
    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de la barra de estado."""
        self.lbl_status.config(text=mensaje)
        self.root.after(3000, lambda: self.lbl_status.config(text="✓ Sistema listo"))
    
    def guardar_datos(self):
        """Guarda inventario y ventas."""
        self.gestor.guardar_csv()
        self.pos.historial.guardar_csv()
        messagebox.showinfo("Éxito", "Datos guardados correctamente")
        self.actualizar_status("✓ Datos guardados")
    
    def salir(self):
        """Cierra la aplicación."""
        if self.pos.venta_actual and self.pos.venta_actual.get_items():
            if not messagebox.askyesno("Confirmar",
                                      "Hay una venta en progreso.\n¿Salir de todas formas?"):
                return
        
        if messagebox.askyesno("Salir", "¿Guardar datos antes de salir?"):
            self.guardar_datos()
        
        self.root.destroy()


# ============================================================
# VENTANAS SECUNDARIAS
# ============================================================

class VentanaPago:
    """Ventana para procesar el pago."""
    
    def __init__(self, parent, pos, callback):
        self.pos = pos
        self.callback = callback
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("💰 Procesar Pago")
        self.ventana.geometry("500x600")
        self.ventana.configure(bg=COLORES['fondo'])
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de pago."""
        # Título
        tk.Label(self.ventana,
                text="💰 PROCESAR PAGO",
                font=('Arial', 18, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        # Resumen
        frame_resumen = tk.LabelFrame(self.ventana,
                                     text="Resumen de la Venta",
                                     font=('Arial', 12, 'bold'),
                                     bg=COLORES['fondo'],
                                     padx=20, pady=20)
        frame_resumen.pack(fill='x', padx=20, pady=10)
        
        items = len(self.pos.venta_actual.get_items())
        subtotal = self.pos.venta_actual.get_total()
        
        tk.Label(frame_resumen,
                text=f"Productos: {items}",
                font=('Arial', 11),
                bg=COLORES['fondo']).pack(anchor='w')
        
        tk.Label(frame_resumen,
                text=f"Subtotal: ${subtotal:.2f}",
                font=('Arial', 11),
                bg=COLORES['fondo']).pack(anchor='w')
        
        # Descuento
        frame_descuento = tk.LabelFrame(self.ventana,
                                       text="Descuento (Opcional)",
                                       font=('Arial', 11),
                                       bg=COLORES['fondo'],
                                       padx=20, pady=15)
        frame_descuento.pack(fill='x', padx=20, pady=10)
        
        tk.Label(frame_descuento,
                text="Porcentaje:",
                bg=COLORES['fondo']).pack(side='left')
        
        self.entry_descuento = tk.Entry(frame_descuento, font=('Arial', 12), width=10)
        self.entry_descuento.pack(side='left', padx=10)
        self.entry_descuento.insert(0, "0")
        
        tk.Label(frame_descuento,
                text="%",
                bg=COLORES['fondo']).pack(side='left')
        
        ttk.Button(frame_descuento,
                  text="Aplicar",
                  style='Secondary.TButton',
                  command=self.aplicar_descuento).pack(side='left', padx=10)
        
        # Total final
        frame_total = tk.Frame(self.ventana, bg=COLORES['primario'], pady=20)
        frame_total.pack(fill='x', padx=20, pady=20)
        
        tk.Label(frame_total,
                text="TOTAL A PAGAR:",
                font=('Arial', 14, 'bold'),
                bg=COLORES['primario'],
                fg=COLORES['blanco']).pack()
        
        self.lbl_total = tk.Label(frame_total,
                                 text=f"${subtotal:.2f}",
                                 font=('Arial', 28, 'bold'),
                                 bg=COLORES['primario'],
                                 fg=COLORES['acento'])
        self.lbl_total.pack()
        
        # Botones
        btn_frame = tk.Frame(self.ventana, bg=COLORES['fondo'])
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame,
                  text="✅ CONFIRMAR PAGO",
                  style='Success.TButton',
                  command=self.confirmar_pago).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="❌ Cancelar",
                  style='Danger.TButton',
                  command=self.ventana.destroy).pack(side='left', padx=5)
    
    def aplicar_descuento(self):
        """Aplica el descuento."""
        try:
            porcentaje = float(self.entry_descuento.get())
            if 0 <= porcentaje <= 100:
                # Crear copia del total original
                venta = self.pos.venta_actual
                total_original = sum(item['subtotal'] for item in venta.get_items())
                descuento = (total_original * porcentaje) / 100
                total_final = total_original - descuento
                
                self.lbl_total.config(text=f"${total_final:.2f}")
                messagebox.showinfo("Descuento", f"Descuento de ${descuento:.2f} aplicado")
            else:
                messagebox.showerror("Error", "El descuento debe estar entre 0 y 100%")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un porcentaje válido")
    
    def confirmar_pago(self):
        """Confirma el pago y completa la venta."""
        try:
            porcentaje = float(self.entry_descuento.get())
            if porcentaje > 0:
                self.pos.venta_actual.aplicar_descuento(porcentaje)
        except:
            pass
        
        if self.pos.venta_actual.completar_venta():
            # Mostrar ticket
            ticket = self.pos.venta_actual.generar_ticket()
            
            # Guardar ticket
            self.pos.venta_actual.guardar_ticket()
            
            # Agregar al historial
            self.pos.historial.agregar_venta(self.pos.venta_actual)
            
            # Limpiar venta actual
            self.pos.venta_actual = None
            
            messagebox.showinfo("Éxito", "✅ Venta completada exitosamente\n\nTicket guardado en la carpeta 'tickets/'")
            
            self.ventana.destroy()
            self.callback()
        else:
            messagebox.showerror("Error", "No se pudo completar la venta")


class VentanaHistorial:
    """Ventana para ver el historial de ventas."""
    
    def __init__(self, parent, historial):
        self.historial = historial
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("📋 Historial de Ventas")
        self.ventana.geometry("900x600")
        self.ventana.configure(bg=COLORES['fondo'])
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del historial."""
        # Título
        tk.Label(self.ventana,
                text="📋 HISTORIAL DE VENTAS",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        # TreeView
        tree = ttk.Treeview(self.ventana,
                           columns=('#Venta', 'Fecha', 'Hora', 'Cajero', 'Items', 'Total', 'Ganancia'),
                           show='headings',
                           height=20)
        
        tree.heading('#Venta', text='#Venta')
        tree.heading('Fecha', text='Fecha')
        tree.heading('Hora', text='Hora')
        tree.heading('Cajero', text='Cajero')
        tree.heading('Items', text='Items')
        tree.heading('Total', text='Total')
        tree.heading('Ganancia', text='Ganancia')
        
        tree.column('#Venta', width=80)
        tree.column('Fecha', width=100)
        tree.column('Hora', width=80)
        tree.column('Cajero', width=150)
        tree.column('Items', width=60)
        tree.column('Total', width=100)
        tree.column('Ganancia', width=100)
        
        scrollbar = ttk.Scrollbar(self.ventana, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Cargar ventas
        for venta in self.historial.ventas:
            tree.insert('', 'end', values=(
                venta.get_numero_venta(),
                venta.get_fecha().strftime('%d/%m/%Y'),
                venta.get_fecha().strftime('%H:%M:%S'),
                venta.get_cajero(),
                len(venta.get_items()),
                f"${venta.get_total():.2f}",
                f"${venta.get_ganancia_total():.2f}"
            ))
        
        # Botón cerrar
        ttk.Button(self.ventana,
                  text="Cerrar",
                  style='Secondary.TButton',
                  command=self.ventana.destroy).pack(pady=10)


class VentanaReporte:
    """Ventana para mostrar reportes."""
    
    def __init__(self, parent, historial, tipo):
        self.historial = historial
        self.tipo = tipo
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("📈 Reporte")
        self.ventana.geometry("500x400")
        self.ventana.configure(bg=COLORES['fondo'])
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del reporte."""
        tk.Label(self.ventana,
                text="📈 REPORTE DIARIO",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        if not self.historial.ventas:
            tk.Label(self.ventana,
                    text="No hay ventas registradas",
                    font=('Arial', 12),
                    bg=COLORES['fondo']).pack(pady=50)
            return
        
        # Calcular estadísticas
        total_ventas = len(self.historial.ventas)
        monto_total = sum(v.get_total() for v in self.historial.ventas)
        ganancia_total = sum(v.get_ganancia_total() for v in self.historial.ventas)
        promedio = monto_total / total_ventas if total_ventas > 0 else 0
        
        # Frame de datos
        frame = tk.Frame(self.ventana, bg=COLORES['fondo'])
        frame.pack(pady=20)
        
        datos = [
            ("Total de ventas:", str(total_ventas)),
            ("Monto total vendido:", f"${monto_total:,.2f}"),
            ("Ganancia total:", f"${ganancia_total:,.2f}"),
            ("Promedio por venta:", f"${promedio:.2f}")
        ]
        
        for etiqueta, valor in datos:
            row = tk.Frame(frame, bg=COLORES['fondo'])
            row.pack(fill='x', pady=5)
            
            tk.Label(row,
                    text=etiqueta,
                    font=('Arial', 11),
                    bg=COLORES['fondo'],
                    width=20,
                    anchor='w').pack(side='left')
            
            tk.Label(row,
                    text=valor,
                    font=('Arial', 11, 'bold'),
                    bg=COLORES['fondo'],
                    fg=COLORES['primario'],
                    anchor='e').pack(side='right')
        
        ttk.Button(self.ventana,
                  text="Cerrar",
                  style='Primary.TButton',
                  command=self.ventana.destroy).pack(pady=20)


class VentanaStockBajo:
    """Ventana para mostrar productos con stock bajo."""
    
    def __init__(self, parent, gestor):
        self.gestor = gestor
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("⚠️ Stock Bajo")
        self.ventana.geometry("700x500")
        self.ventana.configure(bg=COLORES['fondo'])
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz."""
        tk.Label(self.ventana,
                text="⚠️ PRODUCTOS CON STOCK BAJO",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['advertencia']).pack(pady=20)
        
        tree = ttk.Treeview(self.ventana,
                           columns=('Código', 'Producto', 'Categoría', 'Stock'),
                           show='headings',
                           height=15)
        
        tree.heading('Código', text='Código')
        tree.heading('Producto', text='Producto')
        tree.heading('Categoría', text='Categoría')
        tree.heading('Stock', text='Stock')
        
        tree.column('Código', width=100)
        tree.column('Producto', width=250)
        tree.column('Categoría', width=150)
        tree.column('Stock', width=80)
        
        scrollbar = ttk.Scrollbar(self.ventana, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Cargar productos con stock bajo
        productos_bajos = [p for p in self.gestor.productos if p.get_stock() <= 10]
        
        for producto in productos_bajos:
            tree.insert('', 'end', values=(
                producto.get_codigo(),
                producto.get_nombre(),
                producto.get_categoria(),
                producto.get_stock()
            ))
        
        ttk.Button(self.ventana,
                  text="Cerrar",
                  style='Secondary.TButton',
                  command=self.ventana.destroy).pack(pady=10)


class VentanaTopProductos:
    """Ventana para mostrar top productos vendidos."""
    
    def __init__(self, parent, historial):
        self.historial = historial
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🏆 Top Productos")
        self.ventana.geometry("700x500")
        self.ventana.configure(bg=COLORES['fondo'])
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz."""
        tk.Label(self.ventana,
                text="🏆 TOP PRODUCTOS MÁS VENDIDOS",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        if not self.historial.ventas:
            tk.Label(self.ventana,
                    text="No hay ventas registradas",
                    font=('Arial', 12),
                    bg=COLORES['fondo']).pack(pady=50)
            return
        
        # Calcular productos vendidos
        productos_vendidos = {}
        
        for venta in self.historial.ventas:
            for item in venta.get_items():
                codigo = item['codigo']
                if codigo not in productos_vendidos:
                    productos_vendidos[codigo] = {
                        'nombre': item['nombre'],
                        'cantidad': 0,
                        'monto': 0
                    }
                productos_vendidos[codigo]['cantidad'] += item['cantidad']
                productos_vendidos[codigo]['monto'] += item['subtotal']
        
        # Ordenar
        productos_ordenados = sorted(productos_vendidos.items(),
                                    key=lambda x: x[1]['cantidad'],
                                    reverse=True)
        
        tree = ttk.Treeview(self.ventana,
                           columns=('#', 'Código', 'Producto', 'Cantidad', 'Monto'),
                           show='headings',
                           height=15)
        
        tree.heading('#', text='#')
        tree.heading('Código', text='Código')
        tree.heading('Producto', text='Producto')
        tree.heading('Cantidad', text='Cantidad')
        tree.heading('Monto', text='Monto')
        
        tree.column('#', width=50)
        tree.column('Código', width=100)
        tree.column('Producto', width=250)
        tree.column('Cantidad', width=100)
        tree.column('Monto', width=100)
        
        scrollbar = ttk.Scrollbar(self.ventana, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Cargar top 10
        for i, (codigo, datos) in enumerate(productos_ordenados[:10], 1):
            tree.insert('', 'end', values=(
                i,
                codigo,
                datos['nombre'],
                datos['cantidad'],
                f"${datos['monto']:.2f}"
            ))
        
        ttk.Button(self.ventana,
                  text="Cerrar",
                  style='Secondary.TButton',
                  command=self.ventana.destroy).pack(pady=10)


class VentanaInventario:
    """Ventana para ver inventario completo."""
    
    def __init__(self, parent, gestor):
        self.gestor = gestor
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("📦 Inventario")
        self.ventana.geometry("900x600")
        self.ventana.configure(bg=COLORES['fondo'])
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz."""
        tk.Label(self.ventana,
                text="📦 INVENTARIO COMPLETO",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        tree = ttk.Treeview(self.ventana,
                           columns=('Código', 'Producto', 'Categoría', 'Costo', 'Precio', 'Stock', 'Valor'),
                           show='headings',
                           height=20)
        
        tree.heading('Código', text='Código')
        tree.heading('Producto', text='Producto')
        tree.heading('Categoría', text='Categoría')
        tree.heading('Costo', text='Costo')
        tree.heading('Precio', text='Precio')
        tree.heading('Stock', text='Stock')
        tree.heading('Valor', text='Valor Inv.')
        
        tree.column('Código', width=80)
        tree.column('Producto', width=200)
        tree.column('Categoría', width=120)
        tree.column('Costo', width=80)
        tree.column('Precio', width=80)
        tree.column('Stock', width=60)
        tree.column('Valor', width=100)
        
        scrollbar = ttk.Scrollbar(self.ventana, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Cargar productos
        for producto in self.gestor.productos:
            tree.insert('', 'end', values=(
                producto.get_codigo(),
                producto.get_nombre(),
                producto.get_categoria(),
                f"${producto.get_costo():.2f}",
                f"${producto.get_precio_venta():.2f}",
                producto.get_stock(),
                f"${producto.calcular_valor_inventario():.2f}"
            ))
        
        # Total
        valor_total = sum(p.calcular_valor_inventario() for p in self.gestor.productos)
        
        tk.Label(self.ventana,
                text=f"Valor Total del Inventario: ${valor_total:,.2f}",
                font=('Arial', 12, 'bold'),
                bg=COLORES['primario'],
                fg=COLORES['blanco'],
                pady=15).pack(fill='x', padx=20)
        
        ttk.Button(self.ventana,
                  text="Cerrar",
                  style='Secondary.TButton',
                  command=self.ventana.destroy).pack(pady=10)


class VentanaAgregarStock:
    """Ventana para agregar stock a productos."""
    
    def __init__(self, parent, gestor, callback):
        self.gestor = gestor
        self.callback = callback
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("➕ Agregar Stock")
        self.ventana.geometry("400x300")
        self.ventana.configure(bg=COLORES['fondo'])
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz."""
        tk.Label(self.ventana,
                text="➕ AGREGAR STOCK",
                font=('Arial', 16, 'bold'),
                bg=COLORES['fondo'],
                fg=COLORES['primario']).pack(pady=20)
        
        # Código
        frame1 = tk.Frame(self.ventana, bg=COLORES['fondo'])
        frame1.pack(pady=10)
        
        tk.Label(frame1,
                text="Código del Producto:",
                bg=COLORES['fondo'],
                font=('Arial', 11)).pack(side='left')
        
        self.entry_codigo = tk.Entry(frame1, font=('Arial', 11), width=15)
        self.entry_codigo.pack(side='left', padx=10)
        
        # Cantidad
        frame2 = tk.Frame(self.ventana, bg=COLORES['fondo'])
        frame2.pack(pady=10)
        
        tk.Label(frame2,
                text="Cantidad a Agregar:",
                bg=COLORES['fondo'],
                font=('Arial', 11)).pack(side='left')
        
        self.entry_cantidad = tk.Entry(frame2, font=('Arial', 11), width=15)
        self.entry_cantidad.pack(side='left', padx=10)
        
        # Botones
        btn_frame = tk.Frame(self.ventana, bg=COLORES['fondo'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame,
                  text="✅ Agregar",
                  style='Success.TButton',
                  command=self.agregar).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="❌ Cancelar",
                  style='Danger.TButton',
                  command=self.ventana.destroy).pack(side='left', padx=5)
    
    def agregar(self):
        """Agrega el stock."""
        codigo = self.entry_codigo.get().strip()
        
        try:
            cantidad = int(self.entry_cantidad.get())
            
            producto = self.gestor.buscar_por_codigo(codigo)
            
            if producto:
                if producto.agregar_stock(cantidad):
                    messagebox.showinfo("Éxito", f"Stock agregado correctamente\nNuevo stock: {producto.get_stock()}")
                    self.callback()
                    self.ventana.destroy()
            else:
                messagebox.showerror("Error", "Producto no encontrado")
        except ValueError:
            messagebox.showerror("Error", "Ingresa una cantidad válida")


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """Función principal para iniciar la aplicación."""
    root = tk.Tk()
    app = CafeteriaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()