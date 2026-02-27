"""
BASE DE DATOS SQLITE - CAFETERÍA EL AROMA
Módulo de vinculación SQLite para el Sistema de Gestión y Ventas
Autor: Sistema de Ventas
Versión: 1.0.0
"""

import sqlite3
import os
from datetime import datetime


# ============================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================

DB_PATH = "cafeteria.db"  # Archivo de base de datos (se crea automáticamente)


# ============================================================
# CLASE PRINCIPAL DE BASE DE DATOS
# ============================================================

class BaseDatos:
    """Maneja todas las operaciones con la base de datos SQLite."""

    def __init__(self, ruta_db=DB_PATH):
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Abre la conexión a la base de datos."""
        self.conexion = sqlite3.connect(self.ruta_db)
        self.conexion.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
        self.cursor = self.conexion.cursor()
        print(f"✓ Conectado a la base de datos: {self.ruta_db}")

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.conexion:
            self.conexion.close()
            self.conexion = None
            self.cursor = None
            print("✓ Conexión cerrada")

    def __enter__(self):
        """Soporte para uso con 'with'."""
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente al salir del bloque 'with'."""
        if exc_type:
            self.conexion.rollback()
        else:
            self.conexion.commit()
        self.cerrar()

    # ============================================================
    # CREACIÓN DE TABLAS
    # ============================================================

    def crear_tablas(self):
        """Crea todas las tablas necesarias si no existen."""
        
        # Tabla de Productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                codigo       TEXT PRIMARY KEY,
                nombre       TEXT NOT NULL,
                costo        REAL NOT NULL DEFAULT 0,
                precio_venta REAL NOT NULL DEFAULT 0,
                stock        INTEGER NOT NULL DEFAULT 0,
                categoria    TEXT NOT NULL DEFAULT 'General',
                activo       INTEGER NOT NULL DEFAULT 1,
                fecha_alta   TEXT NOT NULL
            )
        """)

        # Tabla de Ventas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_venta INTEGER UNIQUE NOT NULL,
                fecha        TEXT NOT NULL,
                cajero       TEXT NOT NULL,
                total        REAL NOT NULL DEFAULT 0,
                ganancia     REAL NOT NULL DEFAULT 0,
                descuento    REAL NOT NULL DEFAULT 0,
                estado       TEXT NOT NULL DEFAULT 'Completada'
            )
        """)

        # Tabla de Detalle de Ventas (items del carrito)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_venta     INTEGER NOT NULL,
                codigo_producto  TEXT NOT NULL,
                nombre_producto  TEXT NOT NULL,
                cantidad         INTEGER NOT NULL,
                precio_unitario  REAL NOT NULL,
                subtotal         REAL NOT NULL,
                ganancia_item    REAL NOT NULL,
                FOREIGN KEY (numero_venta) REFERENCES ventas(numero_venta),
                FOREIGN KEY (codigo_producto) REFERENCES productos(codigo)
            )
        """)

        # Tabla de Log de Actividades
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_actividades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha       TEXT NOT NULL,
                tipo        TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                usuario     TEXT DEFAULT 'Sistema'
            )
        """)

        self.conexion.commit()
        print("✓ Tablas creadas / verificadas correctamente")

    # ============================================================
    # OPERACIONES CON PRODUCTOS
    # ============================================================

    def insertar_producto(self, producto):
        """Inserta un nuevo producto en la base de datos."""
        try:
            self.cursor.execute("""
                INSERT INTO productos (codigo, nombre, costo, precio_venta, stock, categoria, fecha_alta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                producto.get_codigo(),
                producto.get_nombre(),
                producto.get_costo(),
                producto.get_precio_venta(),
                producto.get_stock(),
                producto.get_categoria(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️  El producto '{producto.get_codigo()}' ya existe en la base de datos")
            return False
        except Exception as e:
            print(f"✗ Error al insertar producto: {e}")
            return False

    def actualizar_stock(self, codigo, nuevo_stock):
        """Actualiza el stock de un producto."""
        self.cursor.execute(
            "UPDATE productos SET stock = ? WHERE codigo = ?",
            (nuevo_stock, codigo)
        )
        self.conexion.commit()

    def actualizar_precio(self, codigo, nuevo_precio):
        """Actualiza el precio de venta de un producto."""
        self.cursor.execute(
            "UPDATE productos SET precio_venta = ? WHERE codigo = ?",
            (nuevo_precio, codigo)
        )
        self.conexion.commit()

    def obtener_producto(self, codigo):
        """Obtiene un producto por su código."""
        self.cursor.execute(
            "SELECT * FROM productos WHERE codigo = ? AND activo = 1",
            (codigo,)
        )
        return self.cursor.fetchone()

    def obtener_todos_productos(self):
        """Obtiene todos los productos activos."""
        self.cursor.execute(
            "SELECT * FROM productos WHERE activo = 1 ORDER BY categoria, nombre"
        )
        return self.cursor.fetchall()

    def obtener_productos_por_categoria(self, categoria):
        """Obtiene productos filtrados por categoría."""
        self.cursor.execute(
            "SELECT * FROM productos WHERE categoria = ? AND activo = 1 ORDER BY nombre",
            (categoria,)
        )
        return self.cursor.fetchall()

    def obtener_productos_stock_bajo(self, minimo=10):
        """Obtiene productos con stock por debajo del mínimo."""
        self.cursor.execute(
            "SELECT * FROM productos WHERE stock <= ? AND activo = 1 ORDER BY stock ASC",
            (minimo,)
        )
        return self.cursor.fetchall()

    def sincronizar_productos_desde_gestor(self, gestor_productos):
        """
        Sincroniza todos los productos del GestorProductos a la base de datos.
        Si ya existen, actualiza stock y precio. Si no, los inserta.
        """
        insertados = 0
        actualizados = 0

        for producto in gestor_productos.productos:
            existente = self.obtener_producto(producto.get_codigo())
            if existente:
                # Actualizar stock y precio
                self.cursor.execute("""
                    UPDATE productos SET stock = ?, precio_venta = ?, costo = ? WHERE codigo = ?
                """, (
                    producto.get_stock(),
                    producto.get_precio_venta(),
                    producto.get_costo(),
                    producto.get_codigo()
                ))
                actualizados += 1
            else:
                self.insertar_producto(producto)
                insertados += 1

        self.conexion.commit()
        print(f"✓ Sincronización: {insertados} insertados, {actualizados} actualizados")

    def sincronizar_stock_a_gestor(self, gestor_productos):
        """
        Carga el stock guardado en la BD hacia los objetos Producto en memoria.
        Útil para restaurar el stock al iniciar el sistema.
        """
        for producto in gestor_productos.productos:
            fila = self.obtener_producto(producto.get_codigo())
            if fila:
                producto.set_stock(fila["stock"])
                producto.set_precio_venta(fila["precio_venta"])
        print("✓ Stock y precios restaurados desde la base de datos")

    # ============================================================
    # OPERACIONES CON VENTAS
    # ============================================================

    def guardar_venta(self, venta):
        """
        Guarda una venta completada en la base de datos.
        Inserta en ventas y en detalle_ventas.
        """
        try:
            # Insertar cabecera de venta
            self.cursor.execute("""
                INSERT INTO ventas (numero_venta, fecha, cajero, total, ganancia, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venta.get_numero_venta(),
                venta.get_fecha().strftime("%Y-%m-%d %H:%M:%S"),
                venta.get_cajero(),
                venta.get_total(),
                venta.get_ganancia_total(),
                venta.get_estado()
            ))

            # Insertar detalle (items del carrito)
            for item in venta.get_items():
                self.cursor.execute("""
                    INSERT INTO detalle_ventas
                        (numero_venta, codigo_producto, nombre_producto, cantidad,
                         precio_unitario, subtotal, ganancia_item)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    venta.get_numero_venta(),
                    item["codigo"],
                    item["nombre"],
                    item["cantidad"],
                    item["precio_unitario"],
                    item["subtotal"],
                    item["ganancia_item"]
                ))

                # Actualizar stock del producto en la BD
                self.cursor.execute("""
                    UPDATE productos SET stock = stock - ? WHERE codigo = ?
                """, (item["cantidad"], item["codigo"]))

            self.conexion.commit()
            print(f"✓ Venta #{venta.get_numero_venta()} guardada en la base de datos")
            return True

        except sqlite3.IntegrityError:
            print(f"⚠️  La venta #{venta.get_numero_venta()} ya existe en la base de datos")
            self.conexion.rollback()
            return False
        except Exception as e:
            print(f"✗ Error al guardar venta: {e}")
            self.conexion.rollback()
            return False

    def obtener_ventas_del_dia(self, fecha=None):
        """Obtiene todas las ventas de un día específico (hoy por default)."""
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("""
            SELECT * FROM ventas
            WHERE fecha LIKE ? AND estado = 'Completada'
            ORDER BY fecha DESC
        """, (f"{fecha}%",))
        return self.cursor.fetchall()

    def obtener_todas_ventas(self, limite=None):
        """Obtiene todas las ventas registradas."""
        query = "SELECT * FROM ventas WHERE estado = 'Completada' ORDER BY fecha DESC"
        if limite:
            query += f" LIMIT {limite}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def obtener_detalle_venta(self, numero_venta):
        """Obtiene el detalle completo de una venta."""
        self.cursor.execute(
            "SELECT * FROM detalle_ventas WHERE numero_venta = ?",
            (numero_venta,)
        )
        return self.cursor.fetchall()

    def reporte_productos_mas_vendidos(self, top=10):
        """Genera un reporte de productos más vendidos."""
        self.cursor.execute("""
            SELECT
                codigo_producto,
                nombre_producto,
                SUM(cantidad)  AS total_vendido,
                SUM(subtotal)  AS total_ingresos,
                SUM(ganancia_item) AS total_ganancia
            FROM detalle_ventas
            GROUP BY codigo_producto, nombre_producto
            ORDER BY total_vendido DESC
            LIMIT ?
        """, (top,))
        return self.cursor.fetchall()

    def reporte_ventas_por_cajero(self):
        """Genera un reporte de ventas agrupado por cajero."""
        self.cursor.execute("""
            SELECT
                cajero,
                COUNT(*) AS num_ventas,
                SUM(total) AS total_vendido,
                SUM(ganancia) AS total_ganancia
            FROM ventas
            WHERE estado = 'Completada'
            GROUP BY cajero
            ORDER BY total_vendido DESC
        """)
        return self.cursor.fetchall()

    def total_vendido_hoy(self):
        """Calcula el total vendido en el día de hoy."""
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("""
            SELECT
                COUNT(*) AS num_ventas,
                COALESCE(SUM(total), 0) AS total,
                COALESCE(SUM(ganancia), 0) AS ganancia
            FROM ventas
            WHERE fecha LIKE ? AND estado = 'Completada'
        """, (f"{fecha_hoy}%",))
        return self.cursor.fetchone()

    # ============================================================
    # LOG DE ACTIVIDADES
    # ============================================================

    def registrar_log(self, tipo, descripcion, usuario="Sistema"):
        """Registra una actividad en el log."""
        self.cursor.execute("""
            INSERT INTO log_actividades (fecha, tipo, descripcion, usuario)
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tipo,
            descripcion,
            usuario
        ))
        self.conexion.commit()

    # ============================================================
    # UTILIDADES
    # ============================================================

    def mostrar_resumen_bd(self):
        """Muestra un resumen del estado de la base de datos."""
        self.cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        num_productos = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE estado = 'Completada'")
        num_ventas = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE estado = 'Completada'")
        total_acumulado = self.cursor.fetchone()[0]

        print("\n" + "="*60)
        print("RESUMEN - BASE DE DATOS CAFETERÍA")
        print("="*60)
        print(f"Archivo BD:       {self.ruta_db}")
        print(f"Productos:        {num_productos}")
        print(f"Ventas guardadas: {num_ventas}")
        print(f"Total acumulado:  ${total_acumulado:,.2f}")
        print("="*60 + "\n")


# ============================================================
# FUNCIÓN DE INICIALIZACIÓN RÁPIDA
# ============================================================

def inicializar_base_de_datos(gestor_productos=None):
    """
    Inicializa la base de datos: crea el archivo, las tablas
    y opcionalmente carga el catálogo de productos.
    
    Uso:
        db = inicializar_base_de_datos(gestor_productos)
    """
    db = BaseDatos()
    db.conectar()
    db.crear_tablas()

    if gestor_productos:
        db.sincronizar_productos_desde_gestor(gestor_productos)

    print("✓ Base de datos lista")
    return db


# ============================================================
# INTEGRACIÓN CON main.py  -  EJEMPLO DE USO COMPLETO
# ============================================================

"""
CÓMO INTEGRAR database.py EN TU PROYECTO
-----------------------------------------

1. En main.py, importa el módulo al inicio:

    from database import BaseDatos, inicializar_base_de_datos

2. En SistemaIntegrado.inicializar(), añade estas líneas
   después de crear el catálogo:

    self.db = inicializar_base_de_datos(self.gestor_productos)
    self.db.sincronizar_stock_a_gestor(self.gestor_productos)

3. En sistema_ventas_cafeteria.py, después de completar cada venta
   en el método finalizar_venta() de SistemaPOS, añade:

    if hasattr(self, 'db') and self.db:
        self.db.guardar_venta(venta)

4. Al cerrar el sistema (opción 26 de main.py), sincroniza el stock:

    sistema.db.sincronizar_productos_desde_gestor(
        sistema.gestor_productos
    )
    sistema.db.cerrar()
"""


# ============================================================
# DEMO / PRUEBA INDEPENDIENTE
# ============================================================

if __name__ == "__main__":
    # Importar el gestor de productos
    try:
        from sistema_gestion_productos import crear_catalogo_cafeteria
        from sistema_ventas_cafeteria import Venta
    except ImportError:
        print("Ejecuta este archivo desde la carpeta del proyecto.")
        exit(1)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PRUEBA DE BASE DE DATOS SQLite - CAFETERÍA            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # 1. Cargar catálogo
    print("1. Cargando catálogo de productos...")
    gestor = crear_catalogo_cafeteria()

    # 2. Inicializar BD
    print("\n2. Inicializando base de datos...")
    db = inicializar_base_de_datos(gestor)

    # 3. Mostrar resumen
    print("\n3. Resumen inicial:")
    db.mostrar_resumen_bd()

    # 4. Simular una venta
    print("4. Simulando una venta de prueba...")
    venta_prueba = Venta("Cajero Principal")
    cafe = gestor.buscar_por_codigo("CAF001")
    pan = gestor.buscar_por_codigo("PAN001")
    if cafe and pan:
        venta_prueba.agregar_item(cafe, 2)
        venta_prueba.agregar_item(pan, 1)
        venta_prueba.completar_venta()
        db.guardar_venta(venta_prueba)

    # 5. Resumen final
    print("\n5. Resumen final:")
    db.mostrar_resumen_bd()

    # 6. Consultar ventas del día
    print("6. Ventas de hoy:")
    ventas_hoy = db.obtener_ventas_del_dia()
    for v in ventas_hoy:
        print(f"   Venta #{v['numero_venta']} | Cajero: {v['cajero']} | Total: ${v['total']:.2f}")

    # 7. Cerrar
    db.cerrar()
    print("\n✓ Prueba completada. Revisa el archivo 'cafeteria.db'")
