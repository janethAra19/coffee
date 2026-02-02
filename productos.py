"""
SISTEMA DE GESTIÓN DE PRODUCTOS - CAFETERÍA
Incluye: Clase Producto + Gestor + Catálogo completo de cafetería
Autor: Sistema de Ventas
Fecha: Enero 2026
"""

import csv
import os
from datetime import datetime

# ============================================================
# CLASE PRODUCTO
# ============================================================

class Producto:
    """Representa un producto de la cafetería."""
    
    def __init__(self, codigo, nombre, costo, precio_venta, stock=0, categoria="General"):
        """Inicializa un nuevo producto con validaciones."""
        self.__codigo = codigo
        self.__nombre = nombre
        self.__costo = float(costo)
        self.__precio_venta = float(precio_venta)
        self.__stock = int(stock)
        self.__categoria = categoria
        
        # Validaciones
        if self.__costo < 0:
            raise ValueError("El costo no puede ser negativo")
        if self.__precio_venta < 0:
            raise ValueError("El precio de venta no puede ser negativo")
        if self.__stock < 0:
            raise ValueError("El stock no puede ser negativo")
    
    # --- GETTERS ---
    def get_codigo(self):
        return self.__codigo
    
    def get_nombre(self):
        return self.__nombre
    
    def get_costo(self):
        return self.__costo
    
    def get_precio_venta(self):
        return self.__precio_venta
    
    def get_stock(self):
        return self.__stock
    
    def get_categoria(self):
        return self.__categoria
    
    # --- SETTERS ---
    def set_precio_venta(self, nuevo_precio):
        nuevo_precio = float(nuevo_precio)
        if nuevo_precio < 0:
            raise ValueError("El precio de venta no puede ser negativo")
        self.__precio_venta = nuevo_precio
        print(f"✓ Precio actualizado a: ${nuevo_precio:.2f}")
    
    def set_costo(self, nuevo_costo):
        nuevo_costo = float(nuevo_costo)
        if nuevo_costo < 0:
            raise ValueError("El costo no puede ser negativo")
        self.__costo = nuevo_costo
        print(f"✓ Costo actualizado a: ${nuevo_costo:.2f}")
    
    def set_stock(self, nuevo_stock):
        nuevo_stock = int(nuevo_stock)
        if nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        self.__stock = nuevo_stock
    
    # --- MÉTODOS DE CÁLCULO ---
    def calcular_ganancia(self):
        return round(self.__precio_venta - self.__costo, 2)
    
    def calcular_margen(self):
        if self.__costo == 0:
            return 0
        return round(((self.__precio_venta - self.__costo) / self.__costo) * 100, 2)
    
    def calcular_valor_inventario(self):
        return round(self.__stock * self.__costo, 2)
    
    # --- MÉTODOS LÓGICOS ---
    def agregar_stock(self, cantidad):
        cantidad = int(cantidad)
        if cantidad <= 0:
            print("✗ Error: La cantidad debe ser mayor a cero")
            return False
        self.__stock += cantidad
        print(f"✓ Stock agregado: +{cantidad} | Total: {self.__stock}")
        return True
    
    def vender(self, cantidad):
        cantidad = int(cantidad)
        if cantidad <= 0:
            print("✗ Error: La cantidad debe ser mayor a cero")
            return None
        if cantidad > self.__stock:
            print(f"✗ Stock insuficiente (disponible: {self.__stock})")
            return None
        
        self.__stock -= cantidad
        total = self.__precio_venta * cantidad
        ganancia = self.calcular_ganancia() * cantidad
        
        return {
            'producto': self.__nombre,
            'cantidad': cantidad,
            'precio_unitario': self.__precio_venta,
            'total': round(total, 2),
            'ganancia': round(ganancia, 2),
            'stock_restante': self.__stock
        }
    
    def verificar_stock_minimo(self, minimo=10):
        if self.__stock <= minimo:
            print(f"⚠️  ALERTA: '{self.__nombre}' - Stock: {self.__stock} (Mínimo: {minimo})")
            return True
        return False
    
    def aplicar_descuento(self, porcentaje):
        if porcentaje < 0 or porcentaje > 100:
            raise ValueError("El descuento debe estar entre 0 y 100%")
        descuento = (self.__precio_venta * porcentaje) / 100
        return round(self.__precio_venta - descuento, 2)
    
    # --- VISUALIZACIÓN ---
    def mostrar_informacion(self):
        print("\n" + "="*70)
        print(f"PRODUCTO: {self.__codigo} - {self.__categoria}")
        print("="*70)
        print(f"Nombre:           {self.__nombre}")
        print(f"Costo:            ${self.__costo:.2f}")
        print(f"Precio venta:     ${self.__precio_venta:.2f}")
        print(f"Ganancia/unidad:  ${self.calcular_ganancia():.2f}")
        print(f"Margen:           {self.calcular_margen():.1f}%")
        print(f"Stock:            {self.__stock} unidades")
        print(f"Valor inventario: ${self.calcular_valor_inventario():.2f}")
        print("="*70 + "\n")
    
    def __str__(self):
        return f"[{self.__codigo}] {self.__nombre} | ${self.__precio_venta:.2f} | Stock: {self.__stock}"


# ============================================================
# GESTOR DE PRODUCTOS
# ============================================================

class GestorProductos:
    """Administra el catálogo completo de productos."""
    
    def __init__(self):
        self.productos = []
    
    def agregar_producto(self, producto):
        """Agrega un producto al catálogo."""
        self.productos.append(producto)
    
    def listar_productos(self):
        """Muestra todos los productos."""
        if not self.productos:
            print("No hay productos registrados")
            return
        
        print("\n" + "="*80)
        print("CATÁLOGO DE PRODUCTOS - CAFETERÍA")
        print("="*80)
        for i, producto in enumerate(self.productos, 1):
            print(f"{i:2d}. {producto}")
        print("="*80 + "\n")
    
    def listar_por_categoria(self, categoria):
        """Filtra productos por categoría."""
        filtrados = [p for p in self.productos if p.get_categoria() == categoria]
        
        if not filtrados:
            print(f"No hay productos en la categoría '{categoria}'")
            return
        
        print(f"\n{'='*80}")
        print(f"CATEGORÍA: {categoria.upper()}")
        print("="*80)
        for producto in filtrados:
            print(f"  {producto}")
        print("="*80 + "\n")
    
    def buscar_por_codigo(self, codigo):
        """Busca un producto por código."""
        for producto in self.productos:
            if producto.get_codigo() == codigo:
                return producto
        print(f"✗ No se encontró producto con código '{codigo}'")
        return None
    
    def buscar_por_nombre(self, nombre):
        """Busca productos por nombre (búsqueda parcial)."""
        nombre_lower = nombre.lower()
        encontrados = [p for p in self.productos if nombre_lower in p.get_nombre().lower()]
        
        if not encontrados:
            print(f"No se encontraron productos con '{nombre}'")
            return []
        
        print(f"\nProductos encontrados ({len(encontrados)}):")
        for producto in encontrados:
            print(f"  {producto}")
        return encontrados
    
    def productos_stock_bajo(self, minimo=10):
        """Lista productos con stock bajo."""
        print(f"\n{'='*80}")
        print(f"PRODUCTOS CON STOCK BAJO (Mínimo: {minimo})")
        print("="*80)
        
        productos_bajos = [p for p in self.productos if p.get_stock() <= minimo]
        
        if not productos_bajos:
            print("✓ Todos los productos tienen stock suficiente")
        else:
            for producto in productos_bajos:
                print(f"  {producto.get_nombre():30s} | Stock: {producto.get_stock():3d}")
        print("="*80 + "\n")
    
    def calcular_valor_total_inventario(self):
        """Calcula el valor total del inventario."""
        total = sum(p.calcular_valor_inventario() for p in self.productos)
        print(f"\n{'='*80}")
        print(f"VALOR TOTAL DEL INVENTARIO: ${total:,.2f}")
        print("="*80 + "\n")
        return total
    
    def productos_mas_rentables(self, top=5):
        """Muestra los productos más rentables por margen."""
        productos_ordenados = sorted(self.productos, 
                                    key=lambda p: p.calcular_margen(), 
                                    reverse=True)
        
        print(f"\n{'='*80}")
        print(f"TOP {top} PRODUCTOS MÁS RENTABLES")
        print("="*80)
        for i, producto in enumerate(productos_ordenados[:top], 1):
            print(f"{i}. {producto.get_nombre():30s} | Margen: {producto.calcular_margen():6.1f}%")
        print("="*80 + "\n")
    
    def guardar_csv(self, archivo="inventario_cafeteria.csv"):
        """Guarda todos los productos en CSV."""
        try:
            with open(archivo, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Codigo', 'Nombre', 'Categoria', 'Costo', 'Precio_Venta', 'Stock'])
                
                for p in self.productos:
                    writer.writerow([
                        p.get_codigo(),
                        p.get_nombre(),
                        p.get_categoria(),
                        p.get_costo(),
                        p.get_precio_venta(),
                        p.get_stock()
                    ])
            print(f"✓ Inventario guardado en '{archivo}'")
        except Exception as e:
            print(f"✗ Error al guardar: {e}")
    
    def cargar_csv(self, archivo="inventario_cafeteria.csv"):
        """Carga productos desde CSV."""
        if not os.path.exists(archivo):
            print(f"✗ Archivo '{archivo}' no existe")
            return
        
        try:
            with open(archivo, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    producto = Producto(
                        row['Codigo'],
                        row['Nombre'],
                        row['Costo'],
                        row['Precio_Venta'],
                        row['Stock'],
                        row['Categoria']
                    )
                    self.productos.append(producto)
            print(f"✓ {len(self.productos)} productos cargados desde '{archivo}'")
        except Exception as e:
            print(f"✗ Error al cargar: {e}")


# ============================================================
# CATÁLOGO DE PRODUCTOS DE CAFETERÍA
# ============================================================

def crear_catalogo_cafeteria():
    """Crea el catálogo completo de productos de la cafetería."""
    
    gestor = GestorProductos()
    
    # --- BEBIDAS CALIENTES ---
    gestor.agregar_producto(Producto("CAF001", "Café Americano", 5.00, 25.00, 80, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF002", "Café Espresso", 5.00, 30.00, 80, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF003", "Café Latte", 8.00, 35.00, 60, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF004", "Cappuccino", 8.00, 35.00, 60, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF005", "Café Moka", 10.00, 40.00, 50, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF006", "Café Caramelo", 10.00, 40.00, 50, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF007", "Chocolate Caliente", 12.00, 35.00, 70, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF008", "Té Chai Latte", 9.00, 38.00, 45, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF009", "Té Verde", 4.00, 20.00, 100, "Bebidas Calientes"))
    gestor.agregar_producto(Producto("CAF010", "Té Negro", 4.00, 20.00, 100, "Bebidas Calientes"))
    
    # --- BEBIDAS FRÍAS ---
    gestor.agregar_producto(Producto("FRI001", "Café Frappé", 12.00, 45.00, 50, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI002", "Smoothie de Fresa", 15.00, 50.00, 40, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI003", "Smoothie de Mango", 15.00, 50.00, 40, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI004", "Limonada Natural", 8.00, 30.00, 60, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI005", "Limonada de Fresa", 10.00, 35.00, 50, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI006", "Malteada de Chocolate", 18.00, 55.00, 35, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI007", "Malteada de Vainilla", 18.00, 55.00, 35, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI008", "Frappe de Caramelo", 15.00, 48.00, 45, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI009", "Jugo de Naranja Natural", 10.00, 35.00, 40, "Bebidas Frías"))
    gestor.agregar_producto(Producto("FRI010", "Agua Mineral", 5.00, 15.00, 150, "Bebidas Frías"))
    
    # --- REPOSTERÍA Y PANADERÍA ---
    gestor.agregar_producto(Producto("PAN001", "Croissant Simple", 12.00, 30.00, 40, "Panadería"))
    gestor.agregar_producto(Producto("PAN002", "Croissant de Chocolate", 15.00, 35.00, 35, "Panadería"))
    gestor.agregar_producto(Producto("PAN003", "Pan de Queso", 8.00, 25.00, 50, "Panadería"))
    gestor.agregar_producto(Producto("PAN004", "Muffin de Arándanos", 10.00, 28.00, 45, "Panadería"))
    gestor.agregar_producto(Producto("PAN005", "Muffin de Chocolate", 10.00, 28.00, 45, "Panadería"))
    gestor.agregar_producto(Producto("PAN006", "Dona Glaseada", 8.00, 22.00, 60, "Panadería"))
    gestor.agregar_producto(Producto("PAN007", "Dona de Chocolate", 9.00, 25.00, 55, "Panadería"))
    gestor.agregar_producto(Producto("PAN008", "Pay de Manzana", 18.00, 45.00, 20, "Repostería"))
    gestor.agregar_producto(Producto("PAN009", "Cheesecake", 25.00, 65.00, 15, "Repostería"))
    gestor.agregar_producto(Producto("PAN010", "Brownie", 12.00, 30.00, 40, "Repostería"))
    gestor.agregar_producto(Producto("PAN011", "Cookie de Chispas", 6.00, 18.00, 80, "Repostería"))
    gestor.agregar_producto(Producto("PAN012", "Galleta de Avena", 6.00, 18.00, 70, "Repostería"))
    
    # --- DESAYUNOS Y COMIDAS ---
    gestor.agregar_producto(Producto("DES001", "Sandwich de Jamón y Queso", 20.00, 55.00, 30, "Desayunos"))
    gestor.agregar_producto(Producto("DES002", "Sandwich de Pavo", 22.00, 60.00, 25, "Desayunos"))
    gestor.agregar_producto(Producto("DES003", "Bagel con Queso Crema", 15.00, 40.00, 35, "Desayunos"))
    gestor.agregar_producto(Producto("DES004", "Avena con Frutas", 18.00, 45.00, 30, "Desayunos"))
    gestor.agregar_producto(Producto("DES005", "Yogurt con Granola", 16.00, 42.00, 40, "Desayunos"))
    gestor.agregar_producto(Producto("DES006", "Ensalada César", 25.00, 70.00, 20, "Comidas"))
    gestor.agregar_producto(Producto("DES007", "Ensalada Griega", 28.00, 75.00, 18, "Comidas"))
    gestor.agregar_producto(Producto("DES008", "Wrap de Pollo", 30.00, 80.00, 25, "Comidas"))
    gestor.agregar_producto(Producto("DES009", "Panini Vegetariano", 28.00, 75.00, 22, "Comidas"))
    gestor.agregar_producto(Producto("DES010", "Sopa del Día", 20.00, 50.00, 30, "Comidas"))
    
    # --- EXTRAS Y ADICIONALES ---
    gestor.agregar_producto(Producto("EXT001", "Shot de Espresso Extra", 3.00, 10.00, 100, "Extras"))
    gestor.agregar_producto(Producto("EXT002", "Leche de Almendra", 5.00, 15.00, 50, "Extras"))
    gestor.agregar_producto(Producto("EXT003", "Leche de Soya", 5.00, 15.00, 50, "Extras"))
    gestor.agregar_producto(Producto("EXT004", "Jarabe de Vainilla", 4.00, 12.00, 60, "Extras"))
    gestor.agregar_producto(Producto("EXT005", "Jarabe de Caramelo", 4.00, 12.00, 60, "Extras"))
    gestor.agregar_producto(Producto("EXT006", "Crema Batida", 3.00, 10.00, 80, "Extras"))
    gestor.agregar_producto(Producto("EXT007", "Azúcar Mascabado", 2.00, 8.00, 100, "Extras"))
    gestor.agregar_producto(Producto("EXT008", "Miel de Abeja", 6.00, 18.00, 40, "Extras"))
    
    return gestor


# ============================================================
# MENÚ INTERACTIVO
# ============================================================

def menu_principal():
    """Menú interactivo para gestionar la cafetería."""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     SISTEMA DE GESTIÓN - CAFETERÍA                        ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    print("Cargando catálogo de productos...")
    
    gestor = crear_catalogo_cafeteria()
    print(f"✓ {len(gestor.productos)} productos cargados\n")
    
    while True:
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL")
        print("="*60)
        print("1.  Ver catálogo completo")
        print("2.  Ver productos por categoría")
        print("3.  Buscar producto por código")
        print("4.  Buscar producto por nombre")
        print("5.  Ver productos con stock bajo")
        print("6.  Ver productos más rentables")
        print("7.  Realizar venta")
        print("8.  Agregar stock a producto")
        print("9.  Actualizar precio de venta")
        print("10. Ver valor total del inventario")
        print("11. Ver detalles de un producto")
        print("12. Guardar inventario en CSV")
        print("13. Salir")
        print("="*60)
        
        opcion = input("\nElige una opción: ")
        
        if opcion == "1":
            gestor.listar_productos()
        
        elif opcion == "2":
            print("\nCategorías disponibles:")
            print("  - Bebidas Calientes")
            print("  - Bebidas Frías")
            print("  - Panadería")
            print("  - Repostería")
            print("  - Desayunos")
            print("  - Comidas")
            print("  - Extras")
            categoria = input("\nIngresa la categoría: ")
            gestor.listar_por_categoria(categoria)
        
        elif opcion == "3":
            codigo = input("Código del producto: ")
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                producto.mostrar_informacion()
        
        elif opcion == "4":
            nombre = input("Nombre del producto: ")
            gestor.buscar_por_nombre(nombre)
        
        elif opcion == "5":
            try:
                minimo = int(input("Stock mínimo (default 10): ") or "10")
                gestor.productos_stock_bajo(minimo)
            except ValueError:
                print("✗ Ingresa un número válido")
        
        elif opcion == "6":
            try:
                top = int(input("¿Cuántos productos mostrar? (default 5): ") or "5")
                gestor.productos_mas_rentables(top)
            except ValueError:
                print("✗ Ingresa un número válido")
        
        elif opcion == "7":
            codigo = input("Código del producto: ")
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                try:
                    cantidad = int(input("Cantidad a vender: "))
                    venta = producto.vender(cantidad)
                    if venta:
                        print(f"\n{'='*60}")
                        print("VENTA REALIZADA")
                        print("="*60)
                        print(f"Producto:     {venta['producto']}")
                        print(f"Cantidad:     {venta['cantidad']}")
                        print(f"Precio unit.: ${venta['precio_unitario']:.2f}")
                        print(f"Total:        ${venta['total']:.2f}")
                        print(f"Ganancia:     ${venta['ganancia']:.2f}")
                        print(f"Stock rest.:  {venta['stock_restante']}")
                        print("="*60)
                except ValueError:
                    print("✗ Ingresa un número válido")
        
        elif opcion == "8":
            codigo = input("Código del producto: ")
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                try:
                    cantidad = int(input("Cantidad a agregar: "))
                    producto.agregar_stock(cantidad)
                except ValueError:
                    print("✗ Ingresa un número válido")
        
        elif opcion == "9":
            codigo = input("Código del producto: ")
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                try:
                    nuevo_precio = float(input("Nuevo precio de venta: $"))
                    producto.set_precio_venta(nuevo_precio)
                except ValueError:
                    print("✗ Ingresa un número válido")
        
        elif opcion == "10":
            gestor.calcular_valor_total_inventario()
        
        elif opcion == "11":
            codigo = input("Código del producto: ")
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                producto.mostrar_informacion()
        
        elif opcion == "12":
            gestor.guardar_csv()
        
        elif opcion == "13":
            print("\n¡Gracias por usar el sistema!")
            print("Hasta luego ☕\n")
            break
        
        else:
            print("✗ Opción no válida")


# ============================================================
# EJEMPLOS DE USO RÁPIDO
# ============================================================

def ejemplos_rapidos():
    """Demuestra funcionalidades principales."""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     EJEMPLOS DE USO - CAFETERÍA                           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    gestor = crear_catalogo_cafeteria()
    
    # Ejemplo 1: Ver bebidas calientes
    print("\n--- EJEMPLO 1: Bebidas Calientes ---")
    gestor.listar_por_categoria("Bebidas Calientes")
    
    # Ejemplo 2: Productos más rentables
    print("\n--- EJEMPLO 2: Top 5 Más Rentables ---")
    gestor.productos_mas_rentables(5)
    
    # Ejemplo 3: Simular ventas
    print("\n--- EJEMPLO 3: Simular Ventas ---")
    cafe = gestor.buscar_por_codigo("CAF001")
    if cafe:
        print(f"\nVendiendo 10 {cafe.get_nombre()}...")
        venta = cafe.vender(10)
        if venta:
            print(f"Total: ${venta['total']:.2f} | Ganancia: ${venta['ganancia']:.2f}")
    
    # Ejemplo 4: Productos con stock bajo
    print("\n--- EJEMPLO 4: Stock Bajo ---")
    gestor.productos_stock_bajo(30)
    
    # Ejemplo 5: Valor total del inventario
    print("\n--- EJEMPLO 5: Valor Total ---")
    gestor.calcular_valor_total_inventario()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    # Descomentar la opción que desees:
    
    # Opción 1: Menú interactivo completo
    menu_principal()
    
    # Opción 2: Ver ejemplos rápidos
    # ejemplos_rapidos()