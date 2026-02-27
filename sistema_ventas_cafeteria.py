"""
SISTEMA DE VENTAS - CAFETERÍA
Integrado con el Sistema de Gestión de Productos
Incluye: Carrito, Tickets, Historial, Reportes
Autor: Sistema de Ventas
Fecha: Febrero 2026
"""

import csv
import os
from datetime import datetime
from sistema_gestion_productos import Producto, GestorProductos, crear_catalogo_cafeteria

# ============================================================
# CLASE VENTA
# ============================================================

class Venta:
    """Representa una venta individual con todos sus detalles."""
    
    contador_ventas = 1000  # Empezar desde 1000
    
    def __init__(self, cajero="Cajero General"):
        """Inicializa una nueva venta."""
        Venta.contador_ventas += 1
        self.__numero_venta = Venta.contador_ventas
        self.__fecha = datetime.now()
        self.__items = []
        self.__cajero = cajero
        self.__total = 0.0
        self.__ganancia_total = 0.0
        self.__estado = "Pendiente"  # Pendiente, Completada, Cancelada
    
    # --- GETTERS ---
    def get_numero_venta(self):
        return self.__numero_venta
    
    def get_fecha(self):
        return self.__fecha
    
    def get_items(self):
        return self.__items.copy()
    
    def get_cajero(self):
        return self.__cajero
    
    def get_total(self):
        return self.__total
    
    def get_ganancia_total(self):
        return self.__ganancia_total
    
    def get_estado(self):
        return self.__estado
    
    # --- MÉTODOS DE CARRITO ---
    def agregar_item(self, producto, cantidad):
        """Agrega un producto al carrito de la venta."""
        cantidad = int(cantidad)
        
        if cantidad <= 0:
            print("✗ La cantidad debe ser mayor a cero")
            return False
        
        if cantidad > producto.get_stock():
            print(f"✗ Stock insuficiente. Disponible: {producto.get_stock()}")
            return False
        
        # Verificar si el producto ya está en el carrito
        for item in self.__items:
            if item['codigo'] == producto.get_codigo():
                # Actualizar cantidad
                nueva_cantidad = item['cantidad'] + cantidad
                if nueva_cantidad > producto.get_stock():
                    print(f"✗ Stock insuficiente para agregar más unidades")
                    return False
                item['cantidad'] = nueva_cantidad
                item['subtotal'] = round(item['cantidad'] * item['precio_unitario'], 2)
                item['ganancia_item'] = round(item['cantidad'] * item['ganancia_unitaria'], 2)
                print(f"✓ Cantidad actualizada a {nueva_cantidad}")
                self.__calcular_totales()
                return True
        
        # Agregar nuevo item
        subtotal = producto.get_precio_venta() * cantidad
        ganancia_unitaria = producto.calcular_ganancia()
        ganancia_item = ganancia_unitaria * cantidad
        
        item = {
            'codigo': producto.get_codigo(),
            'nombre': producto.get_nombre(),
            'precio_unitario': producto.get_precio_venta(),
            'cantidad': cantidad,
            'subtotal': round(subtotal, 2),
            'ganancia_unitaria': ganancia_unitaria,
            'ganancia_item': round(ganancia_item, 2),
            'producto_obj': producto  # Referencia al objeto producto
        }
        
        self.__items.append(item)
        self.__calcular_totales()
        print(f"✓ Agregado: {cantidad}x {producto.get_nombre()} - ${subtotal:.2f}")
        return True
    
    def eliminar_item(self, codigo):
        """Elimina un producto del carrito."""
        for i, item in enumerate(self.__items):
            if item['codigo'] == codigo:
                nombre = item['nombre']
                self.__items.pop(i)
                self.__calcular_totales()
                print(f"✓ Eliminado: {nombre}")
                return True
        print(f"✗ Producto '{codigo}' no encontrado en el carrito")
        return False
    
    def modificar_cantidad_item(self, codigo, nueva_cantidad):
        """Modifica la cantidad de un producto en el carrito."""
        nueva_cantidad = int(nueva_cantidad)
        
        if nueva_cantidad <= 0:
            return self.eliminar_item(codigo)
        
        for item in self.__items:
            if item['codigo'] == codigo:
                producto = item['producto_obj']
                if nueva_cantidad > producto.get_stock():
                    print(f"✗ Stock insuficiente. Disponible: {producto.get_stock()}")
                    return False
                
                item['cantidad'] = nueva_cantidad
                item['subtotal'] = round(nueva_cantidad * item['precio_unitario'], 2)
                item['ganancia_item'] = round(nueva_cantidad * item['ganancia_unitaria'], 2)
                self.__calcular_totales()
                print(f"✓ Cantidad actualizada a {nueva_cantidad}")
                return True
        
        print(f"✗ Producto '{codigo}' no encontrado en el carrito")
        return False
    
    def vaciar_carrito(self):
        """Vacía todo el carrito."""
        self.__items.clear()
        self.__calcular_totales()
        print("✓ Carrito vaciado")
    
    def __calcular_totales(self):
        """Recalcula los totales de la venta."""
        self.__total = sum(item['subtotal'] for item in self.__items)
        self.__ganancia_total = sum(item['ganancia_item'] for item in self.__items)
    
    # --- MÉTODOS DE FINALIZACIÓN ---
    def aplicar_descuento(self, porcentaje):
        """Aplica un descuento porcentual al total."""
        if porcentaje < 0 or porcentaje > 100:
            print("✗ El descuento debe estar entre 0 y 100%")
            return False
        
        descuento = (self.__total * porcentaje) / 100
        self.__total = round(self.__total - descuento, 2)
        print(f"✓ Descuento del {porcentaje}% aplicado: -${descuento:.2f}")
        return True
    
    def completar_venta(self):
        """Finaliza la venta y actualiza el inventario."""
        if not self.__items:
            print("✗ No hay productos en el carrito")
            return False
        
        if self.__estado == "Completada":
            print("✗ Esta venta ya fue completada")
            return False
        
        # Actualizar stock de todos los productos
        for item in self.__items:
            producto = item['producto_obj']
            producto.vender(item['cantidad'])
        
        self.__estado = "Completada"
        print("✓ Venta completada exitosamente")
        return True
    
    def cancelar_venta(self):
        """Cancela la venta."""
        if self.__estado == "Completada":
            print("✗ No se puede cancelar una venta completada")
            return False
        
        self.__estado = "Cancelada"
        self.vaciar_carrito()
        print("✓ Venta cancelada")
        return True
    
    # --- VISUALIZACIÓN ---
    def mostrar_carrito(self):
        """Muestra el contenido actual del carrito."""
        if not self.__items:
            print("\n🛒 Carrito vacío\n")
            return
        
        print("\n" + "="*90)
        print("🛒 CARRITO DE COMPRAS")
        print("="*90)
        print(f"{'#':<3} {'Código':<8} {'Producto':<30} {'Cant.':<6} {'P.Unit':<10} {'Subtotal':<10}")
        print("-"*90)
        
        for i, item in enumerate(self.__items, 1):
            print(f"{i:<3} {item['codigo']:<8} {item['nombre']:<30} "
                  f"{item['cantidad']:<6} ${item['precio_unitario']:<9.2f} ${item['subtotal']:<9.2f}")
        
        print("-"*90)
        print(f"{'TOTAL:':<58} ${self.__total:.2f}")
        print("="*90 + "\n")
    
    def generar_ticket(self):
        """Genera el ticket de venta."""
        if not self.__items:
            print("✗ No hay items para generar ticket")
            return ""
        
        ticket = []
        ticket.append("\n" + "="*60)
        ticket.append("             ☕ CAFETERÍA - TICKET DE VENTA ☕")
        ticket.append("="*60)
        ticket.append(f"Ticket #:     {self.__numero_venta}")
        ticket.append(f"Fecha:        {self.__fecha.strftime('%d/%m/%Y %H:%M:%S')}")
        ticket.append(f"Cajero:       {self.__cajero}")
        ticket.append("="*60)
        ticket.append(f"{'Producto':<35} {'Cant':<5} {'P.Unit':<10} {'Total':<10}")
        ticket.append("-"*60)
        
        for item in self.__items:
            ticket.append(f"{item['nombre']:<35} {item['cantidad']:<5} "
                         f"${item['precio_unitario']:<9.2f} ${item['subtotal']:<9.2f}")
        
        ticket.append("-"*60)
        ticket.append(f"{'SUBTOTAL:':<52} ${self.__total:.2f}")
        ticket.append(f"{'TOTAL A PAGAR:':<52} ${self.__total:.2f}")
        ticket.append("="*60)
        ticket.append("         ¡Gracias por su compra! Vuelva pronto")
        ticket.append("="*60 + "\n")
        
        ticket_texto = "\n".join(ticket)
        print(ticket_texto)
        return ticket_texto
    
    def guardar_ticket(self, carpeta="tickets"):
        """Guarda el ticket en un archivo."""
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        
        nombre_archivo = f"{carpeta}/ticket_{self.__numero_venta}_{self.__fecha.strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as file:
                file.write(self.generar_ticket())
            print(f"✓ Ticket guardado en '{nombre_archivo}'")
            return nombre_archivo
        except Exception as e:
            print(f"✗ Error al guardar ticket: {e}")
            return None


# ============================================================
# CLASE HISTORIAL DE VENTAS
# ============================================================

class HistorialVentas:
    """Administra el historial completo de ventas."""
    
    def __init__(self):
        self.ventas = []
    
    def agregar_venta(self, venta):
        """Registra una venta en el historial."""
        if venta.get_estado() == "Completada":
            self.ventas.append(venta)
    
    def listar_ventas(self, limite=None):
        """Lista todas las ventas registradas."""
        if not self.ventas:
            print("No hay ventas registradas")
            return
        
        ventas_mostrar = self.ventas[-limite:] if limite else self.ventas
        
        print("\n" + "="*90)
        print("HISTORIAL DE VENTAS")
        print("="*90)
        print(f"{'#Venta':<8} {'Fecha':<20} {'Cajero':<20} {'Items':<6} {'Total':<12} {'Ganancia':<12}")
        print("-"*90)
        
        for venta in ventas_mostrar:
            fecha_str = venta.get_fecha().strftime('%d/%m/%Y %H:%M')
            print(f"{venta.get_numero_venta():<8} {fecha_str:<20} {venta.get_cajero():<20} "
                  f"{len(venta.get_items()):<6} ${venta.get_total():<11.2f} ${venta.get_ganancia_total():<11.2f}")
        
        print("="*90 + "\n")
    
    def buscar_venta(self, numero_venta):
        """Busca una venta por número."""
        for venta in self.ventas:
            if venta.get_numero_venta() == numero_venta:
                return venta
        print(f"✗ Venta #{numero_venta} no encontrada")
        return None
    
    def ventas_por_fecha(self, fecha):
        """Filtra ventas por fecha específica."""
        ventas_fecha = [v for v in self.ventas 
                       if v.get_fecha().date() == fecha.date()]
        
        if not ventas_fecha:
            print(f"No hay ventas para la fecha {fecha.strftime('%d/%m/%Y')}")
            return []
        
        print(f"\nVentas del {fecha.strftime('%d/%m/%Y')}:")
        for venta in ventas_fecha:
            print(f"  Ticket #{venta.get_numero_venta()} - ${venta.get_total():.2f}")
        
        return ventas_fecha
    
    def ventas_por_cajero(self, cajero):
        """Filtra ventas por cajero."""
        ventas_cajero = [v for v in self.ventas if v.get_cajero() == cajero]
        
        if not ventas_cajero:
            print(f"No hay ventas del cajero '{cajero}'")
            return []
        
        total = sum(v.get_total() for v in ventas_cajero)
        print(f"\nVentas de {cajero}:")
        print(f"  Total ventas: {len(ventas_cajero)}")
        print(f"  Monto total: ${total:.2f}")
        
        return ventas_cajero
    
    # --- REPORTES ---
    def reporte_diario(self, fecha=None):
        """Genera reporte de ventas del día."""
        if fecha is None:
            fecha = datetime.now()
        
        ventas_dia = [v for v in self.ventas 
                     if v.get_fecha().date() == fecha.date()]
        
        if not ventas_dia:
            print(f"\n✗ No hay ventas para el {fecha.strftime('%d/%m/%Y')}")
            return
        
        total_ventas = sum(v.get_total() for v in ventas_dia)
        total_ganancias = sum(v.get_ganancia_total() for v in ventas_dia)
        
        print("\n" + "="*70)
        print(f"REPORTE DIARIO - {fecha.strftime('%d/%m/%Y')}")
        print("="*70)
        print(f"Total de ventas:        {len(ventas_dia)}")
        print(f"Monto total vendido:    ${total_ventas:,.2f}")
        print(f"Ganancia total:         ${total_ganancias:,.2f}")
        print(f"Promedio por venta:     ${total_ventas/len(ventas_dia):,.2f}")
        print("="*70 + "\n")
    
    def reporte_general(self):
        """Genera reporte general de todas las ventas."""
        if not self.ventas:
            print("No hay ventas registradas")
            return
        
        total_ventas = sum(v.get_total() for v in self.ventas)
        total_ganancias = sum(v.get_ganancia_total() for v in self.ventas)
        
        print("\n" + "="*70)
        print("REPORTE GENERAL DE VENTAS")
        print("="*70)
        print(f"Total de ventas:        {len(self.ventas)}")
        print(f"Monto total vendido:    ${total_ventas:,.2f}")
        print(f"Ganancia total:         ${total_ganancias:,.2f}")
        print(f"Promedio por venta:     ${total_ventas/len(self.ventas):,.2f}")
        print(f"Ticket más alto:        ${max(v.get_total() for v in self.ventas):,.2f}")
        print(f"Ticket más bajo:        ${min(v.get_total() for v in self.ventas):,.2f}")
        print("="*70 + "\n")
    
    def productos_mas_vendidos(self, top=10):
        """Muestra los productos más vendidos."""
        productos_vendidos = {}
        
        for venta in self.ventas:
            for item in venta.get_items():
                codigo = item['codigo']
                nombre = item['nombre']
                cantidad = item['cantidad']
                
                if codigo not in productos_vendidos:
                    productos_vendidos[codigo] = {
                        'nombre': nombre,
                        'cantidad': 0,
                        'monto': 0
                    }
                
                productos_vendidos[codigo]['cantidad'] += cantidad
                productos_vendidos[codigo]['monto'] += item['subtotal']
        
        # Ordenar por cantidad
        productos_ordenados = sorted(productos_vendidos.items(), 
                                    key=lambda x: x[1]['cantidad'], 
                                    reverse=True)
        
        print("\n" + "="*80)
        print(f"TOP {top} PRODUCTOS MÁS VENDIDOS")
        print("="*80)
        print(f"{'#':<4} {'Código':<10} {'Producto':<35} {'Cantidad':<10} {'Monto':<12}")
        print("-"*80)
        
        for i, (codigo, datos) in enumerate(productos_ordenados[:top], 1):
            print(f"{i:<4} {codigo:<10} {datos['nombre']:<35} "
                  f"{datos['cantidad']:<10} ${datos['monto']:<11.2f}")
        
        print("="*80 + "\n")
    
    def guardar_csv(self, archivo="historial_ventas.csv"):
        """Guarda el historial en CSV."""
        if not self.ventas:
            print("No hay ventas para guardar")
            return
        
        try:
            with open(archivo, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Numero_Venta', 'Fecha', 'Hora', 'Cajero', 
                               'Items', 'Total', 'Ganancia', 'Estado'])
                
                for venta in self.ventas:
                    writer.writerow([
                        venta.get_numero_venta(),
                        venta.get_fecha().strftime('%d/%m/%Y'),
                        venta.get_fecha().strftime('%H:%M:%S'),
                        venta.get_cajero(),
                        len(venta.get_items()),
                        venta.get_total(),
                        venta.get_ganancia_total(),
                        venta.get_estado()
                    ])
            
            print(f"✓ Historial guardado en '{archivo}'")
        except Exception as e:
            print(f"✗ Error al guardar: {e}")


# ============================================================
# SISTEMA DE PUNTO DE VENTA (POS)
# ============================================================

class SistemaPOS:
    """Sistema de Punto de Venta completo."""
    
    def __init__(self, gestor_productos):
        self.gestor_productos = gestor_productos
        self.historial = HistorialVentas()
        self.venta_actual = None
        self.cajero = "Cajero Principal"
    
    def nueva_venta(self):
        """Inicia una nueva venta."""
        if self.venta_actual and self.venta_actual.get_items():
            respuesta = input("¿Hay una venta en progreso. ¿Cancelarla? (s/n): ")
            if respuesta.lower() != 's':
                return
        
        self.venta_actual = Venta(self.cajero)
        print(f"\n✓ Nueva venta iniciada - Ticket #{self.venta_actual.get_numero_venta()}")
    
    def agregar_producto(self):
        """Agrega un producto a la venta actual."""
        if not self.venta_actual:
            self.nueva_venta()
        
        codigo = input("Código del producto: ").strip()
        producto = self.gestor_productos.buscar_por_codigo(codigo)
        
        if producto:
            try:
                cantidad = int(input("Cantidad: "))
                self.venta_actual.agregar_item(producto, cantidad)
            except ValueError:
                print("✗ Cantidad inválida")
    
    def eliminar_producto(self):
        """Elimina un producto de la venta actual."""
        if not self.venta_actual or not self.venta_actual.get_items():
            print("✗ No hay productos en el carrito")
            return
        
        self.venta_actual.mostrar_carrito()
        codigo = input("Código del producto a eliminar: ").strip()
        self.venta_actual.eliminar_item(codigo)
    
    def modificar_cantidad(self):
        """Modifica la cantidad de un producto."""
        if not self.venta_actual or not self.venta_actual.get_items():
            print("✗ No hay productos en el carrito")
            return
        
        self.venta_actual.mostrar_carrito()
        codigo = input("Código del producto: ").strip()
        try:
            nueva_cantidad = int(input("Nueva cantidad: "))
            self.venta_actual.modificar_cantidad_item(codigo, nueva_cantidad)
        except ValueError:
            print("✗ Cantidad inválida")
    
    def finalizar_venta(self):
        """Finaliza y registra la venta."""
        if not self.venta_actual:
            print("✗ No hay venta activa")
            return
        
        if not self.venta_actual.get_items():
            print("✗ No hay productos en el carrito")
            return
        
        self.venta_actual.mostrar_carrito()
        
        # Opción de aplicar descuento
        descuento = input("\n¿Aplicar descuento? (s/n): ")
        if descuento.lower() == 's':
            try:
                porcentaje = float(input("Porcentaje de descuento: "))
                self.venta_actual.aplicar_descuento(porcentaje)
            except ValueError:
                print("✗ Porcentaje inválido")
        
        # Confirmar venta
        print(f"\nTotal a cobrar: ${self.venta_actual.get_total():.2f}")
        confirmar = input("¿Confirmar venta? (s/n): ")
        
        if confirmar.lower() == 's':
            if self.venta_actual.completar_venta():
                self.venta_actual.generar_ticket()
                
                # Preguntar si guardar ticket
                guardar = input("\n¿Guardar ticket en archivo? (s/n): ")
                if guardar.lower() == 's':
                    self.venta_actual.guardar_ticket()
                
                # Agregar al historial
                self.historial.agregar_venta(self.venta_actual)

                             # ── GUARDAR EN SQLITE ─────────────────────────── NUEVO
                if hasattr(self, 'db') and self.db:
                    self.db.guardar_venta(self.venta_actual)
                # ─────────────────────────────────────────────────────

                self.venta_actual = None
        else:
            print("Venta no confirmada")


# ============================================================
# MENÚ INTERACTIVO DEL SISTEMA DE VENTAS
# ============================================================

def menu_ventas():
    """Menú principal del sistema de ventas."""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     SISTEMA DE VENTAS - CAFETERÍA                         ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    print("Inicializando sistema...")
    
    # Cargar catálogo de productos
    gestor = crear_catalogo_cafeteria()
    pos = SistemaPOS(gestor)
    
    print(f"✓ Sistema listo - {len(gestor.productos)} productos disponibles\n")
    
    # Configurar cajero
    nombre_cajero = input("Nombre del cajero: ").strip()
    if nombre_cajero:
        pos.cajero = nombre_cajero
    
    while True:
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL - PUNTO DE VENTA")
        print("="*60)
        print("VENTAS:")
        print("  1.  Nueva venta")
        print("  2.  Agregar producto al carrito")
        print("  3.  Ver carrito actual")
        print("  4.  Eliminar producto del carrito")
        print("  5.  Modificar cantidad")
        print("  6.  Finalizar y cobrar venta")
        print("  7.  Cancelar venta actual")
        print("\nCONSULTAS:")
        print("  8.  Buscar producto")
        print("  9.  Ver catálogo por categoría")
        print("  10. Ver productos disponibles")
        print("\nHISTORIAL Y REPORTES:")
        print("  11. Ver historial de ventas")
        print("  12. Buscar venta específica")
        print("  13. Reporte diario")
        print("  14. Reporte general")
        print("  15. Productos más vendidos")
        print("  16. Guardar historial en CSV")
        print("\nOTROS:")
        print("  17. Ver stock bajo")
        print("  18. Salir")
        print("="*60)
        
        opcion = input("\nElige una opción: ").strip()
        
        # --- OPCIONES DE VENTA ---
        if opcion == "1":
            pos.nueva_venta()
        
        elif opcion == "2":
            pos.agregar_producto()
        
        elif opcion == "3":
            if pos.venta_actual:
                pos.venta_actual.mostrar_carrito()
            else:
                print("✗ No hay venta activa")
        
        elif opcion == "4":
            pos.eliminar_producto()
        
        elif opcion == "5":
            pos.modificar_cantidad()
        
        elif opcion == "6":
            pos.finalizar_venta()
        
        elif opcion == "7":
            if pos.venta_actual:
                confirmar = input("¿Cancelar venta actual? (s/n): ")
                if confirmar.lower() == 's':
                    pos.venta_actual.cancelar_venta()
                    pos.venta_actual = None
            else:
                print("✗ No hay venta activa")
        
        # --- OPCIONES DE CONSULTA ---
        elif opcion == "8":
            codigo = input("Código del producto: ").strip()
            producto = gestor.buscar_por_codigo(codigo)
            if producto:
                producto.mostrar_informacion()
        
        elif opcion == "9":
            print("\nCategorías disponibles:")
            print("  - Bebidas Calientes")
            print("  - Bebidas Frías")
            print("  - Panadería")
            print("  - Repostería")
            print("  - Desayunos")
            print("  - Comidas")
            print("  - Extras")
            categoria = input("\nIngresa la categoría: ").strip()
            gestor.listar_por_categoria(categoria)
        
        elif opcion == "10":
            gestor.listar_productos()
        
        # --- OPCIONES DE HISTORIAL ---
        elif opcion == "11":
            try:
                limite = input("¿Cuántas ventas mostrar? (Enter = todas): ").strip()
                limite = int(limite) if limite else None
                pos.historial.listar_ventas(limite)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "12":
            try:
                numero = int(input("Número de venta: "))
                venta = pos.historial.buscar_venta(numero)
                if venta:
                    venta.generar_ticket()
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "13":
            pos.historial.reporte_diario()
        
        elif opcion == "14":
            pos.historial.reporte_general()
        
        elif opcion == "15":
            try:
                top = int(input("¿Cuántos productos mostrar? (default 10): ") or "10")
                pos.historial.productos_mas_vendidos(top)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "16":
            pos.historial.guardar_csv()
        
        # --- OTRAS OPCIONES ---
        elif opcion == "17":
            try:
                minimo = int(input("Stock mínimo (default 10): ") or "10")
                gestor.productos_stock_bajo(minimo)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "18":
            # Advertir si hay venta en progreso
            if pos.venta_actual and pos.venta_actual.get_items():
                print("\n⚠️  Hay una venta en progreso")
                confirmar = input("¿Salir de todas formas? (s/n): ")
                if confirmar.lower() != 's':
                    continue
            
            print("\n╔════════════════════════════════════════════════════════════╗")
            print("║   ¡Gracias por usar el Sistema de Ventas!                ║")
            print("║   Hasta luego ☕                                           ║")
            print("╚════════════════════════════════════════════════════════════╝\n")
            break
        
        else:
            print("✗ Opción no válida")


# ============================================================
# DEMOSTRACIÓN CON VENTAS DE PRUEBA
# ============================================================

def demo_ventas():
    """Demostración del sistema con ventas simuladas."""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     DEMOSTRACIÓN - SISTEMA DE VENTAS                      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Inicializar sistema
    gestor = crear_catalogo_cafeteria()
    pos = SistemaPOS(gestor)
    pos.cajero = "Demo - Sistema"
    
    print("="*60)
    print("SIMULANDO VENTAS...")
    print("="*60 + "\n")
    
    # Venta 1: Desayuno
    print("--- Venta 1: Desayuno Completo ---")
    venta1 = Venta("María González")
    venta1.agregar_item(gestor.buscar_por_codigo("CAF001"), 2)  # 2 Cafés
    venta1.agregar_item(gestor.buscar_por_codigo("PAN001"), 2)  # 2 Croissants
    venta1.agregar_item(gestor.buscar_por_codigo("FRI009"), 1)  # 1 Jugo
    venta1.mostrar_carrito()
    venta1.completar_venta()
    venta1.generar_ticket()
    pos.historial.agregar_venta(venta1)
    
    # Venta 2: Café de la tarde
    print("\n--- Venta 2: Café de la Tarde ---")
    venta2 = Venta("Carlos Ruiz")
    venta2.agregar_item(gestor.buscar_por_codigo("CAF003"), 1)  # Latte
    venta2.agregar_item(gestor.buscar_por_codigo("PAN010"), 1)  # Brownie
    venta2.agregar_item(gestor.buscar_por_codigo("EXT002"), 1)  # Leche de almendra
    venta2.mostrar_carrito()
    venta2.completar_venta()
    venta2.generar_ticket()
    pos.historial.agregar_venta(venta2)
    
    # Venta 3: Pedido grande
    print("\n--- Venta 3: Pedido de Oficina ---")
    venta3 = Venta("Ana Martínez")
    venta3.agregar_item(gestor.buscar_por_codigo("CAF001"), 5)  # 5 Cafés
    venta3.agregar_item(gestor.buscar_por_codigo("PAN006"), 10) # 10 Donas
    venta3.agregar_item(gestor.buscar_por_codigo("PAN011"), 12) # 12 Cookies
    venta3.mostrar_carrito()
    venta3.aplicar_descuento(10)  # 10% de descuento
    venta3.completar_venta()
    venta3.generar_ticket()
    pos.historial.agregar_venta(venta3)
    
    # Mostrar reportes
    print("\n" + "="*60)
    print("REPORTES DE DEMOSTRACIÓN")
    print("="*60 + "\n")
    
    pos.historial.reporte_general()
    pos.historial.productos_mas_vendidos(5)
    
    print("\n✓ Demostración completada")
    print("="*60 + "\n")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    # Descomentar la opción deseada:
    
    # Opción 1: Sistema completo de ventas
    menu_ventas()
    
    # Opción 2: Ver demostración
    # demo_ventas()
