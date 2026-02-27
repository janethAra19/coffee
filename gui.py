"""
SISTEMA DE VENTAS - CAFETERÍA EL AROMA (GUI)
Interfaz gráfica completa con Tkinter + SQLite
Versión: 2.0.0  |  Fecha: 2026-02-26
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CARGAR CONFIGURACIÓN
# ─────────────────────────────────────────────
CONFIG_PATH = "gui.json"

def cargar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CONFIG = cargar_config()

COLORES = CONFIG.get("colores", {
    "primario": "#4A90D9", "secundario": "#F5A623",
    "fondo": "#F0F0F0", "exito": "#27AE60",
    "error": "#E74C3C", "advertencia": "#F39C12",
    "texto_oscuro": "#2C3E50", "blanco": "#FFFFFF"
})

DB_PATH = CONFIG.get("app", {}).get("db_path", "gui.db")
CAJEROS = CONFIG.get("cajeros", ["Cajero Principal"])
CATEGORIAS = CONFIG.get("categorias", ["General"])
MONEDA = CONFIG.get("negocio", {}).get("moneda", "$")
STOCK_MIN = CONFIG.get("inventario", {}).get("stock_minimo_alerta", 10)
CONT_INICIAL = CONFIG.get("ventas", {}).get("contador_inicial", 2000)
DESC_MAX = CONFIG.get("ventas", {}).get("descuento_maximo", 30)

# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────
class DB:
    def __init__(self):
        self.path = DB_PATH
        self._init_db()

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init_db(self):
        with self._conn() as con:
            cur = con.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS productos (
                    codigo       TEXT PRIMARY KEY,
                    nombre       TEXT NOT NULL,
                    costo        REAL DEFAULT 0,
                    precio_venta REAL DEFAULT 0,
                    stock        INTEGER DEFAULT 0,
                    categoria    TEXT DEFAULT 'General',
                    activo       INTEGER DEFAULT 1,
                    fecha_alta   TEXT
                );
                CREATE TABLE IF NOT EXISTS ventas (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_venta INTEGER UNIQUE,
                    fecha        TEXT,
                    cajero       TEXT,
                    total        REAL DEFAULT 0,
                    ganancia     REAL DEFAULT 0,
                    descuento    REAL DEFAULT 0,
                    estado       TEXT DEFAULT 'Completada'
                );
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_venta    INTEGER,
                    codigo_producto TEXT,
                    nombre_producto TEXT,
                    cantidad        INTEGER,
                    precio_unitario REAL,
                    subtotal        REAL,
                    ganancia_item   REAL
                );
                CREATE TABLE IF NOT EXISTS config_contador (
                    clave TEXT PRIMARY KEY,
                    valor INTEGER
                );
                INSERT OR IGNORE INTO config_contador (clave, valor)
                VALUES ('ultimo_numero', 2000);
            """)
            # Poblar catálogo si está vacío
            cur.execute("SELECT COUNT(*) FROM productos")
            if cur.fetchone()[0] == 0:
                self._insertar_catalogo(cur)
            con.commit()

    def _insertar_catalogo(self, cur):
        productos = [
            ("CAF001","Café Americano",8,25,50,"Bebidas Calientes"),
            ("CAF002","Café Cappuccino",12,35,40,"Bebidas Calientes"),
            ("CAF003","Café Latte",14,40,40,"Bebidas Calientes"),
            ("CAF004","Té Negro",5,18,60,"Bebidas Calientes"),
            ("CAF005","Chocolate Caliente",10,30,45,"Bebidas Calientes"),
            ("BEF001","Jugo Natural Naranja",15,35,30,"Bebidas Frías"),
            ("BEF002","Agua de Jamaica",8,20,40,"Bebidas Frías"),
            ("BEF003","Limonada",10,25,35,"Bebidas Frías"),
            ("BEF004","Frappé Café",18,50,25,"Bebidas Frías"),
            ("PAN001","Croissant",10,25,40,"Panadería"),
            ("PAN002","Dona Glaseada",8,18,50,"Panadería"),
            ("PAN003","Muffin Arándanos",12,28,35,"Panadería"),
            ("PAN004","Cuerno Mantequilla",6,15,60,"Panadería"),
            ("REP001","Pastel Chocolate",25,65,20,"Repostería"),
            ("REP002","Cheesecake Fresa",22,55,18,"Repostería"),
            ("DES001","Huevos Rancheros",35,75,15,"Desayunos"),
            ("DES002","Molletes",25,55,20,"Desayunos"),
            ("COM001","Ensalada César",40,90,12,"Comidas"),
            ("COM002","Sandwich Club",38,85,15,"Comidas"),
            ("EXT001","Azúcar Extra",1,3,100,"Extras"),
            ("EXT002","Shot Espresso",5,15,50,"Extras"),
        ]
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for p in productos:
            cur.execute(
                "INSERT OR IGNORE INTO productos VALUES (?,?,?,?,?,?,1,?)",
                (*p, ahora)
            )

    # --- Productos ---
    def get_productos(self, categoria=None):
        with self._conn() as con:
            cur = con.cursor()
            if categoria and categoria != "Todas":
                cur.execute("SELECT * FROM productos WHERE activo=1 AND categoria=? ORDER BY nombre", (categoria,))
            else:
                cur.execute("SELECT * FROM productos WHERE activo=1 ORDER BY categoria,nombre")
            return cur.fetchall()

    def get_producto(self, codigo):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM productos WHERE codigo=? AND activo=1", (codigo,))
            return cur.fetchone()

    def agregar_producto(self, codigo, nombre, costo, precio, stock, categoria):
        with self._conn() as con:
            cur = con.cursor()
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO productos VALUES (?,?,?,?,?,?,1,?)",
                (codigo, nombre, costo, precio, stock, categoria, ahora)
            )
            con.commit()

    def actualizar_producto(self, codigo, nombre, costo, precio, stock, categoria):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE productos SET nombre=?,costo=?,precio_venta=?,stock=?,categoria=? WHERE codigo=?",
                (nombre, costo, precio, stock, categoria, codigo)
            )
            con.commit()

    def eliminar_producto(self, codigo):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("UPDATE productos SET activo=0 WHERE codigo=?", (codigo,))
            con.commit()

    def actualizar_stock(self, codigo, nuevo_stock):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("UPDATE productos SET stock=? WHERE codigo=?", (nuevo_stock, codigo))
            con.commit()

    # --- Contador ventas ---
    def siguiente_numero(self):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("UPDATE config_contador SET valor=valor+1 WHERE clave='ultimo_numero'")
            cur.execute("SELECT valor FROM config_contador WHERE clave='ultimo_numero'")
            return cur.fetchone()[0]

    # --- Ventas ---
    def guardar_venta(self, cajero, items, total, ganancia, descuento):
        num = self.siguiente_numero()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO ventas (numero_venta,fecha,cajero,total,ganancia,descuento) VALUES (?,?,?,?,?,?)",
                (num, fecha, cajero, total, ganancia, descuento)
            )
            for it in items:
                cur.execute(
                    "INSERT INTO detalle_ventas (numero_venta,codigo_producto,nombre_producto,cantidad,precio_unitario,subtotal,ganancia_item) VALUES (?,?,?,?,?,?,?)",
                    (num, it["codigo"], it["nombre"], it["cantidad"], it["precio"], it["subtotal"], it["ganancia"])
                )
                cur.execute("UPDATE productos SET stock=stock-? WHERE codigo=?", (it["cantidad"], it["codigo"]))
            con.commit()
        return num

    def get_ventas(self, fecha=None):
        with self._conn() as con:
            cur = con.cursor()
            if fecha:
                cur.execute("SELECT * FROM ventas WHERE fecha LIKE ? ORDER BY fecha DESC", (f"{fecha}%",))
            else:
                cur.execute("SELECT * FROM ventas ORDER BY fecha DESC LIMIT 200")
            return cur.fetchall()

    def get_detalle(self, num):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM detalle_ventas WHERE numero_venta=?", (num,))
            return cur.fetchall()

    def resumen_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*),COALESCE(SUM(total),0),COALESCE(SUM(ganancia),0) FROM ventas WHERE fecha LIKE ?",
                (f"{hoy}%",)
            )
            return cur.fetchone()

    def top_productos(self, n=5):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT nombre_producto, SUM(cantidad) AS total
                FROM detalle_ventas GROUP BY nombre_producto
                ORDER BY total DESC LIMIT ?
            """, (n,))
            return cur.fetchall()

    def stock_bajo(self):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("SELECT nombre, stock FROM productos WHERE activo=1 AND stock<=? ORDER BY stock", (STOCK_MIN,))
            return cur.fetchall()


# ─────────────────────────────────────────────
# APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.carrito = []
        self.cajero_var = tk.StringVar(value=CAJEROS[0])
        self.descuento_var = tk.DoubleVar(value=0.0)

        cfg_v = CONFIG.get("ventana", {})
        self.title(cfg_v.get("titulo", "☕ Cafetería El Aroma"))
        self.geometry(f"{cfg_v.get('ancho',1100)}x{cfg_v.get('alto',700)}")
        self.resizable(True, True)
        self.configure(bg=COLORES["fondo"])

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[12, 6])
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background=COLORES["primario"], foreground="white")
        style.configure("Treeview", font=("Arial", 10), rowheight=26)
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("Green.TButton", background=COLORES["exito"])
        style.configure("Red.TButton", background=COLORES["error"])

        self._build_header()
        self._build_notebook()
        self._refresh_dashboard()

    # ── HEADER ──────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORES["primario"], height=55)
        hdr.pack(fill="x")
        tk.Label(hdr, text="☕  Cafetería El Aroma", font=("Arial", 18, "bold"),
                 bg=COLORES["primario"], fg="white").pack(side="left", padx=20, pady=8)
        tk.Label(hdr, text="Sistema de Gestión y Ventas v2.0",
                 font=("Arial", 10), bg=COLORES["primario"], fg="#D6EAF8").pack(side="left", padx=5)
        self.lbl_hora = tk.Label(hdr, text="", font=("Arial", 10),
                                  bg=COLORES["primario"], fg="white")
        self.lbl_hora.pack(side="right", padx=20)
        self._tick()

    def _tick(self):
        self.lbl_hora.config(text=datetime.now().strftime("🕐 %d/%m/%Y  %H:%M:%S"))
        self.after(1000, self._tick)

    # ── NOTEBOOK ────────────────────────────────
    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_venta    = ttk.Frame(self.nb)
        self.tab_productos = ttk.Frame(self.nb)
        self.tab_historial = ttk.Frame(self.nb)
        self.tab_dashboard = ttk.Frame(self.nb)

        self.nb.add(self.tab_venta,    text="🛒  Nueva Venta")
        self.nb.add(self.tab_productos, text="📦  Productos")
        self.nb.add(self.tab_historial, text="📋  Historial")
        self.nb.add(self.tab_dashboard, text="📊  Dashboard")

        self._build_tab_venta()
        self._build_tab_productos()
        self._build_tab_historial()
        self._build_tab_dashboard()

        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, e):
        tab = self.nb.index(self.nb.select())
        if tab == 2:
            self._refresh_historial()
        elif tab == 3:
            self._refresh_dashboard()

    # ════════════════════════════════════════════
    # TAB NUEVA VENTA
    # ════════════════════════════════════════════
    def _build_tab_venta(self):
        f = self.tab_venta
        f.columnconfigure(0, weight=2)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(0, weight=1)

        # ── Panel izquierdo (catálogo) ──
        left = ttk.LabelFrame(f, text="  Catálogo de Productos", padding=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(8,4), pady=8)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        # Filtros
        fbar = tk.Frame(left, bg=COLORES["fondo"])
        fbar.grid(row=0, column=0, sticky="ew", pady=(0,6))
        tk.Label(fbar, text="Categoría:", font=("Arial",10), bg=COLORES["fondo"]).pack(side="left")
        cats = ["Todas"] + CATEGORIAS
        self.cat_var = tk.StringVar(value="Todas")
        cb_cat = ttk.Combobox(fbar, textvariable=self.cat_var, values=cats, width=18, state="readonly")
        cb_cat.pack(side="left", padx=6)
        cb_cat.bind("<<ComboboxSelected>>", lambda e: self._refresh_catalogo())
        tk.Label(fbar, text="Buscar:", font=("Arial",10), bg=COLORES["fondo"]).pack(side="left", padx=(10,0))
        self.buscar_var = tk.StringVar()
        self.buscar_var.trace_add("write", lambda *a: self._refresh_catalogo())
        ttk.Entry(fbar, textvariable=self.buscar_var, width=16).pack(side="left", padx=6)

        # Treeview catálogo
        cols = ("Código","Nombre","Precio","Stock","Categoría")
        self.tree_cat = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c, w in zip(cols, [80,200,80,60,130]):
            self.tree_cat.heading(c, text=c)
            self.tree_cat.column(c, width=w, anchor="center" if c not in ("Nombre","Categoría") else "w")
        self.tree_cat.tag_configure("bajo", foreground=COLORES["error"])
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree_cat.yview)
        self.tree_cat.configure(yscrollcommand=sb.set)
        self.tree_cat.grid(row=1, column=0, sticky="nsew")
        sb.grid(row=1, column=1, sticky="ns")
        self.tree_cat.bind("<Double-1>", self._agregar_al_carrito)
        self._refresh_catalogo()

        # ── Panel derecho (carrito) ──
        right = ttk.LabelFrame(f, text="  Carrito de Compra", padding=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(4,8), pady=8)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # Cajero y descuento
        info = tk.Frame(right, bg=COLORES["fondo"])
        info.grid(row=0, column=0, sticky="ew", pady=(0,6))
        tk.Label(info, text="Cajero:", font=("Arial",9,"bold"), bg=COLORES["fondo"]).grid(row=0, column=0, sticky="w")
        cb_c = ttk.Combobox(info, textvariable=self.cajero_var, values=CAJEROS, width=18, state="readonly")
        cb_c.grid(row=0, column=1, padx=4)
        tk.Label(info, text="Descuento %:", font=("Arial",9,"bold"), bg=COLORES["fondo"]).grid(row=1, column=0, sticky="w", pady=(4,0))
        ttk.Spinbox(info, from_=0, to=DESC_MAX, textvariable=self.descuento_var,
                    width=6, command=self._recalcular).grid(row=1, column=1, padx=4, pady=(4,0))

        # Treeview carrito
        cols_c = ("Nombre","Cant.","P.Unit","Subtotal")
        self.tree_carrito = ttk.Treeview(right, columns=cols_c, show="headings", height=12)
        for c, w in zip(cols_c, [140,50,70,80]):
            self.tree_carrito.heading(c, text=c)
            self.tree_carrito.column(c, width=w, anchor="center" if c != "Nombre" else "w")
        sb2 = ttk.Scrollbar(right, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=sb2.set)
        self.tree_carrito.grid(row=1, column=0, sticky="nsew")
        sb2.grid(row=1, column=1, sticky="ns")

        # Totales
        tot = tk.Frame(right, bg=COLORES["fondo"])
        tot.grid(row=2, column=0, sticky="ew", pady=6)
        self.lbl_subtotal = tk.Label(tot, text="Subtotal:  $0.00", font=("Arial",10), bg=COLORES["fondo"])
        self.lbl_subtotal.pack(anchor="e")
        self.lbl_desc = tk.Label(tot, text="Descuento: $0.00", font=("Arial",10), bg=COLORES["fondo"])
        self.lbl_desc.pack(anchor="e")
        self.lbl_total = tk.Label(tot, text="TOTAL:     $0.00", font=("Arial",13,"bold"),
                                   bg=COLORES["fondo"], fg=COLORES["primario"])
        self.lbl_total.pack(anchor="e")

        # Botones
        btns = tk.Frame(right, bg=COLORES["fondo"])
        btns.grid(row=3, column=0, sticky="ew", pady=(0,4))
        ttk.Button(btns, text="➕ Agregar", command=self._agregar_al_carrito).pack(side="left", padx=2, fill="x", expand=True)
        ttk.Button(btns, text="➖ Quitar", command=self._quitar_del_carrito).pack(side="left", padx=2, fill="x", expand=True)
        ttk.Button(btns, text="🗑 Vaciar", command=self._vaciar_carrito).pack(side="left", padx=2, fill="x", expand=True)
        ttk.Button(btns, text="✅ COBRAR", command=self._cobrar, style="Green.TButton").pack(fill="x", pady=(6,0))

    def _refresh_catalogo(self):
        for row in self.tree_cat.get_children():
            self.tree_cat.delete(row)
        cat = self.cat_var.get() if hasattr(self, "cat_var") else "Todas"
        buscar = self.buscar_var.get().lower() if hasattr(self, "buscar_var") else ""
        prods = self.db.get_productos(cat)
        for p in prods:
            if buscar and buscar not in p["nombre"].lower() and buscar not in p["codigo"].lower():
                continue
            tag = "bajo" if p["stock"] <= STOCK_MIN else ""
            self.tree_cat.insert("", "end", iid=p["codigo"],
                                  values=(p["codigo"], p["nombre"], f"${p['precio_venta']:.2f}",
                                          p["stock"], p["categoria"]), tags=(tag,))

    def _agregar_al_carrito(self, event=None):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto del catálogo.")
            return
        codigo = sel[0]
        prod = self.db.get_producto(codigo)
        if not prod:
            return
        cant = simpledialog.askinteger("Cantidad", f"¿Cuántas unidades de:\n{prod['nombre']}?",
                                       minvalue=1, maxvalue=prod["stock"])
        if not cant:
            return
        # Verificar si ya está en el carrito
        for it in self.carrito:
            if it["codigo"] == codigo:
                nueva = it["cantidad"] + cant
                if nueva > prod["stock"]:
                    messagebox.showerror("Error", f"Stock insuficiente. Disponible: {prod['stock']}")
                    return
                it["cantidad"] = nueva
                it["subtotal"] = round(nueva * it["precio"], 2)
                it["ganancia"] = round(nueva * (it["precio"] - prod["costo"]), 2)
                self._render_carrito()
                return
        self.carrito.append({
            "codigo": codigo,
            "nombre": prod["nombre"],
            "precio": prod["precio_venta"],
            "costo": prod["costo"],
            "cantidad": cant,
            "subtotal": round(prod["precio_venta"] * cant, 2),
            "ganancia": round((prod["precio_venta"] - prod["costo"]) * cant, 2)
        })
        self._render_carrito()

    def _quitar_del_carrito(self):
        sel = self.tree_carrito.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.carrito[idx]
        self._render_carrito()

    def _vaciar_carrito(self):
        if self.carrito and messagebox.askyesno("Confirmar", "¿Vaciar el carrito?"):
            self.carrito.clear()
            self._render_carrito()

    def _render_carrito(self):
        for r in self.tree_carrito.get_children():
            self.tree_carrito.delete(r)
        for i, it in enumerate(self.carrito):
            self.tree_carrito.insert("", "end", iid=str(i),
                                      values=(it["nombre"], it["cantidad"],
                                              f"${it['precio']:.2f}", f"${it['subtotal']:.2f}"))
        self._recalcular()

    def _recalcular(self):
        subtotal = sum(it["subtotal"] for it in self.carrito)
        desc_pct = self.descuento_var.get()
        desc_amt = round(subtotal * desc_pct / 100, 2)
        total = round(subtotal - desc_amt, 2)
        self.lbl_subtotal.config(text=f"Subtotal:  {MONEDA}{subtotal:.2f}")
        self.lbl_desc.config(text=f"Descuento: -{MONEDA}{desc_amt:.2f} ({desc_pct:.0f}%)")
        self.lbl_total.config(text=f"TOTAL:     {MONEDA}{total:.2f}")

    def _cobrar(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agrega productos antes de cobrar.")
            return
        subtotal = sum(it["subtotal"] for it in self.carrito)
        desc_pct = self.descuento_var.get()
        desc_amt = round(subtotal * desc_pct / 100, 2)
        total = round(subtotal - desc_amt, 2)
        ganancia = round(sum(it["ganancia"] for it in self.carrito) - desc_amt, 2)
        cajero = self.cajero_var.get()

        confirmar = messagebox.askyesno(
            "Confirmar cobro",
            f"Cajero: {cajero}\nTotal a cobrar: {MONEDA}{total:.2f}\n\n¿Confirmar venta?"
        )
        if not confirmar:
            return
        try:
            num = self.db.guardar_venta(cajero, self.carrito, total, ganancia, desc_amt)
            messagebox.showinfo("✅ Venta completada",
                                f"Venta #{num} registrada exitosamente.\nTotal cobrado: {MONEDA}{total:.2f}")
            self.carrito.clear()
            self._render_carrito()
            self._refresh_catalogo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la venta:\n{e}")

    # ════════════════════════════════════════════
    # TAB PRODUCTOS
    # ════════════════════════════════════════════
    def _build_tab_productos(self):
        f = self.tab_productos
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        # Barra de herramientas
        bar = tk.Frame(f, bg=COLORES["fondo"])
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Button(bar, text="➕ Nuevo Producto", command=self._dlg_nuevo_prod).pack(side="left", padx=4)
        ttk.Button(bar, text="✏️ Editar", command=self._dlg_editar_prod).pack(side="left", padx=4)
        ttk.Button(bar, text="🗑 Eliminar", command=self._eliminar_prod).pack(side="left", padx=4)
        ttk.Button(bar, text="📦 Actualizar Stock", command=self._dlg_stock).pack(side="left", padx=4)
        ttk.Button(bar, text="🔄 Refrescar", command=self._refresh_prods).pack(side="right", padx=4)
        tk.Label(bar, text="⚠ Rojo = stock bajo", font=("Arial",9), bg=COLORES["fondo"],
                 fg=COLORES["error"]).pack(side="right", padx=8)

        # Treeview
        cols = ("Código","Nombre","Costo","P.Venta","Stock","Categoría","Ganancia","Margen%")
        self.tree_prods = ttk.Treeview(f, columns=cols, show="headings")
        widths = [80,200,80,80,60,130,80,80]
        for c, w in zip(cols, widths):
            self.tree_prods.heading(c, text=c)
            self.tree_prods.column(c, width=w, anchor="center" if c not in ("Nombre","Categoría") else "w")
        self.tree_prods.tag_configure("bajo", foreground=COLORES["error"])
        self.tree_prods.tag_configure("critico", background="#FDEDEC")
        sb = ttk.Scrollbar(f, orient="vertical", command=self.tree_prods.yview)
        self.tree_prods.configure(yscrollcommand=sb.set)
        self.tree_prods.grid(row=1, column=0, sticky="nsew", padx=(8,0), pady=4)
        sb.grid(row=1, column=1, sticky="ns", pady=4)
        self._refresh_prods()

    def _refresh_prods(self):
        for r in self.tree_prods.get_children():
            self.tree_prods.delete(r)
        for p in self.db.get_productos():
            gan = round(p["precio_venta"] - p["costo"], 2)
            margen = round((gan / p["costo"]) * 100, 1) if p["costo"] else 0
            tags = ("critico",) if p["stock"] <= 5 else (("bajo",) if p["stock"] <= STOCK_MIN else ())
            self.tree_prods.insert("", "end", iid=p["codigo"],
                                    values=(p["codigo"], p["nombre"], f"${p['costo']:.2f}",
                                            f"${p['precio_venta']:.2f}", p["stock"],
                                            p["categoria"], f"${gan:.2f}", f"{margen}%"), tags=tags)

    def _dlg_nuevo_prod(self):
        self._formulario_producto()

    def _dlg_editar_prod(self):
        sel = self.tree_prods.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto para editar.")
            return
        prod = self.db.get_producto(sel[0])
        self._formulario_producto(prod)

    def _formulario_producto(self, prod=None):
        dlg = tk.Toplevel(self)
        dlg.title("Nuevo Producto" if not prod else "Editar Producto")
        dlg.grab_set()
        dlg.resizable(False, False)
        dlg.configure(bg=COLORES["fondo"])

        campos = [
            ("Código:", prod["codigo"] if prod else ""),
            ("Nombre:", prod["nombre"] if prod else ""),
            ("Costo ($):", prod["costo"] if prod else ""),
            ("Precio Venta ($):", prod["precio_venta"] if prod else ""),
            ("Stock:", prod["stock"] if prod else ""),
        ]
        entries = []
        for i, (lbl, val) in enumerate(campos):
            tk.Label(dlg, text=lbl, bg=COLORES["fondo"], font=("Arial",10)).grid(row=i, column=0, padx=14, pady=6, sticky="e")
            e = ttk.Entry(dlg, width=25)
            e.insert(0, str(val))
            if prod and lbl == "Código:":
                e.config(state="disabled")
            e.grid(row=i, column=1, padx=14, pady=6)
            entries.append(e)

        tk.Label(dlg, text="Categoría:", bg=COLORES["fondo"], font=("Arial",10)).grid(row=5, column=0, padx=14, pady=6, sticky="e")
        cat_v = tk.StringVar(value=prod["categoria"] if prod else CATEGORIAS[0])
        cb = ttk.Combobox(dlg, textvariable=cat_v, values=CATEGORIAS, state="readonly", width=23)
        cb.grid(row=5, column=1, padx=14, pady=6)

        def guardar():
            try:
                codigo  = entries[0].get().strip()
                nombre  = entries[1].get().strip()
                costo   = float(entries[2].get())
                precio  = float(entries[3].get())
                stock   = int(entries[4].get())
                cat     = cat_v.get()
                if not codigo or not nombre:
                    raise ValueError("Código y nombre son obligatorios.")
                if costo < 0 or precio < 0 or stock < 0:
                    raise ValueError("Los valores no pueden ser negativos.")
                if prod:
                    self.db.actualizar_producto(codigo, nombre, costo, precio, stock, cat)
                    messagebox.showinfo("✅", "Producto actualizado.")
                else:
                    self.db.agregar_producto(codigo, nombre, costo, precio, stock, cat)
                    messagebox.showinfo("✅", "Producto agregado.")
                dlg.destroy()
                self._refresh_prods()
                self._refresh_catalogo()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dlg, text="💾 Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=12)

    def _eliminar_prod(self):
        sel = self.tree_prods.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto {sel[0]}?"):
            self.db.eliminar_producto(sel[0])
            self._refresh_prods()
            self._refresh_catalogo()

    def _dlg_stock(self):
        sel = self.tree_prods.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto.")
            return
        prod = self.db.get_producto(sel[0])
        nuevo = simpledialog.askinteger("Actualizar Stock",
                                        f"Nuevo stock para:\n{prod['nombre']}\nActual: {prod['stock']}",
                                        minvalue=0)
        if nuevo is not None:
            self.db.actualizar_stock(sel[0], nuevo)
            self._refresh_prods()
            self._refresh_catalogo()

    # ════════════════════════════════════════════
    # TAB HISTORIAL
    # ════════════════════════════════════════════
    def _build_tab_historial(self):
        f = self.tab_historial
        f.columnconfigure(0, weight=2)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(1, weight=1)

        # Barra de filtros
        bar = tk.Frame(f, bg=COLORES["fondo"])
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=6)
        tk.Label(bar, text="Filtrar por fecha:", bg=COLORES["fondo"], font=("Arial",10)).pack(side="left")
        self.fecha_hist = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(bar, textvariable=self.fecha_hist, width=12).pack(side="left", padx=6)
        ttk.Button(bar, text="🔍 Buscar", command=self._refresh_historial).pack(side="left")
        ttk.Button(bar, text="📅 Todas", command=lambda: (self.fecha_hist.set(""), self._refresh_historial())).pack(side="left", padx=6)

        # Treeview ventas
        cols = ("#Venta","Fecha","Cajero","Total","Ganancia","Descuento")
        self.tree_hist = ttk.Treeview(f, columns=cols, show="headings", height=20)
        ws = [70,155,150,90,90,80]
        for c, w in zip(cols, ws):
            self.tree_hist.heading(c, text=c)
            self.tree_hist.column(c, width=w, anchor="center" if c not in ("Cajero",) else "w")
        sb = ttk.Scrollbar(f, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sb.set)
        self.tree_hist.grid(row=1, column=0, sticky="nsew", padx=(8,0), pady=4)
        sb.grid(row=1, column=1, sticky="ns", pady=4)
        self.tree_hist.bind("<<TreeviewSelect>>", self._ver_detalle)

        # Detalle
        det = ttk.LabelFrame(f, text="  Detalle de Venta", padding=8)
        det.grid(row=1, column=1, sticky="nsew", padx=(4,8), pady=4)
        det.columnconfigure(0, weight=1)
        det.rowconfigure(0, weight=1)
        cols_d = ("Producto","Cant.","P.Unit","Subtotal")
        self.tree_det = ttk.Treeview(det, columns=cols_d, show="headings", height=20)
        for c, w in zip(cols_d, [150,50,70,80]):
            self.tree_det.heading(c, text=c)
            self.tree_det.column(c, width=w, anchor="center" if c != "Producto" else "w")
        sb3 = ttk.Scrollbar(det, orient="vertical", command=self.tree_det.yview)
        self.tree_det.configure(yscrollcommand=sb3.set)
        self.tree_det.grid(row=0, column=0, sticky="nsew")
        sb3.grid(row=0, column=1, sticky="ns")
        self._refresh_historial()

    def _refresh_historial(self):
        for r in self.tree_hist.get_children():
            self.tree_hist.delete(r)
        fecha = self.fecha_hist.get().strip() if hasattr(self, "fecha_hist") else ""
        ventas = self.db.get_ventas(fecha if fecha else None)
        for v in ventas:
            self.tree_hist.insert("", "end", iid=str(v["numero_venta"]),
                                   values=(v["numero_venta"], v["fecha"], v["cajero"],
                                           f"${v['total']:.2f}", f"${v['ganancia']:.2f}",
                                           f"${v['descuento']:.2f}"))

    def _ver_detalle(self, e):
        sel = self.tree_hist.selection()
        if not sel:
            return
        for r in self.tree_det.get_children():
            self.tree_det.delete(r)
        for it in self.db.get_detalle(int(sel[0])):
            self.tree_det.insert("", "end",
                                  values=(it["nombre_producto"], it["cantidad"],
                                          f"${it['precio_unitario']:.2f}", f"${it['subtotal']:.2f}"))

    # ════════════════════════════════════════════
    # TAB DASHBOARD
    # ════════════════════════════════════════════
    def _build_tab_dashboard(self):
        f = self.tab_dashboard
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

        # Resumen del día
        self.frm_res = ttk.LabelFrame(f, text="  📈 Resumen del Día", padding=12)
        self.frm_res.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.lbl_ventas_hoy = tk.Label(self.frm_res, text="", font=("Arial",12), bg=COLORES["blanco"])
        self.lbl_ventas_hoy.pack(anchor="w", pady=2)
        self.lbl_total_hoy = tk.Label(self.frm_res, text="", font=("Arial",14,"bold"),
                                       fg=COLORES["primario"], bg=COLORES["blanco"])
        self.lbl_total_hoy.pack(anchor="w", pady=2)
        self.lbl_gan_hoy = tk.Label(self.frm_res, text="", font=("Arial",12),
                                     fg=COLORES["exito"], bg=COLORES["blanco"])
        self.lbl_gan_hoy.pack(anchor="w", pady=2)
        ttk.Button(self.frm_res, text="🔄 Actualizar", command=self._refresh_dashboard).pack(pady=8)

        # Stock bajo
        self.frm_stock = ttk.LabelFrame(f, text="  ⚠️ Productos con Stock Bajo", padding=12)
        self.frm_stock.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.frm_stock.columnconfigure(0, weight=1)
        self.frm_stock.rowconfigure(0, weight=1)
        cols_s = ("Producto", "Stock")
        self.tree_stock = ttk.Treeview(self.frm_stock, columns=cols_s, show="headings", height=8)
        self.tree_stock.heading("Producto", text="Producto")
        self.tree_stock.heading("Stock", text="Stock")
        self.tree_stock.column("Producto", width=180)
        self.tree_stock.column("Stock", width=60, anchor="center")
        self.tree_stock.tag_configure("critico", foreground=COLORES["error"])
        self.tree_stock.grid(row=0, column=0, sticky="nsew")

        # Top productos
        self.frm_top = ttk.LabelFrame(f, text="  🏆 Productos Más Vendidos", padding=12)
        self.frm_top.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0,8))
        self.frm_top.columnconfigure(0, weight=1)
        cols_t = ("Posición","Producto","Unidades Vendidas")
        self.tree_top = ttk.Treeview(self.frm_top, columns=cols_t, show="headings", height=6)
        for c, w in zip(cols_t, [80,300,140]):
            self.tree_top.heading(c, text=c)
            self.tree_top.column(c, width=w, anchor="center" if c != "Producto" else "w")
        self.tree_top.grid(row=0, column=0, sticky="nsew")

    def _refresh_dashboard(self):
        res = self.db.resumen_hoy()
        self.lbl_ventas_hoy.config(text=f"Ventas realizadas hoy: {res[0]}")
        self.lbl_total_hoy.config(text=f"Total vendido: {MONEDA}{res[1]:,.2f}")
        self.lbl_gan_hoy.config(text=f"Ganancia estimada: {MONEDA}{res[2]:,.2f}")

        for r in self.tree_stock.get_children():
            self.tree_stock.delete(r)
        for p in self.db.stock_bajo():
            tag = "critico" if p["stock"] <= 5 else ""
            self.tree_stock.insert("", "end", values=(p["nombre"], p["stock"]), tags=(tag,))

        for r in self.tree_top.get_children():
            self.tree_top.delete(r)
        for i, p in enumerate(self.db.top_productos(), 1):
            self.tree_top.insert("", "end", values=(f"#{i}", p["nombre_producto"], p["total"]))


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
