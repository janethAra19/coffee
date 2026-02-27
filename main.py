"""
SISTEMA INTEGRADO DE GESTIÓN Y VENTAS - CAFETERÍA
Archivo Principal (main.py)
Integra: Gestión de Productos + Sistema de Ventas + Configuración
Autor: Sistema de Ventas
Fecha: Febrero 2026
Versión: 1.0.0
"""

import os
import sys
import json
from datetime import datetime
from database import BaseDatos, inicializar_base_de_datos

# Importar módulos del sistema
try:
    from sistema_gestion_productos import (
        Producto, 
        GestorProductos, 
        crear_catalogo_cafeteria,
        menu_principal as menu_gestion
    )
    from sistema_ventas_cafeteria import (
        Venta,
        HistorialVentas,
        SistemaPOS,
        menu_ventas,
        demo_ventas
    )
except ImportError as e:
    print(f"✗ Error al importar módulos: {e}")
    print("Asegúrate de tener los archivos:")
    print("  - sistema_gestion_productos.py")
    print("  - sistema_ventas_cafeteria.py")
    sys.exit(1)


# ============================================================
# CLASE CONFIGURACIÓN
# ============================================================

class ConfiguracionSistema:
    """Maneja la configuración del sistema desde config.json."""
    
    def __init__(self, archivo_config="config.json"):
        self.archivo_config = archivo_config
        self.config = self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON."""
        if not os.path.exists(self.archivo_config):
            print(f"⚠️  Archivo de configuración '{self.archivo_config}' no encontrado")
            print("Usando configuración por defecto...")
            return self.configuracion_default()
        
        try:
            with open(self.archivo_config, 'r', encoding='utf-8') as file:
                config = json.load(file)
            print(f"✓ Configuración cargada desde '{self.archivo_config}'")
            return config
        except Exception as e:
            print(f"✗ Error al cargar configuración: {e}")
            print("Usando configuración por defecto...")
            return self.configuracion_default()
    
    def configuracion_default(self):
        """Retorna configuración por defecto si no existe el archivo."""
        return {
            "sistema": {
                "nombre": "Sistema de Gestión y Ventas - Cafetería",
                "version": "1.0.0"
            },
            "configuracion_general": {
                "nombre_negocio": "Cafetería",
                "direccion": "Sin dirección",
                "telefono": "Sin teléfono"
            },
            "ventas": {
                "contador_inicial": 1000,
                "descuento_maximo_permitido": 30,
                "carpeta_tickets": "tickets"
            },
            "inventario": {
                "stock_minimo_alerta": 10
            }
        }
    
    def obtener(self, seccion, clave=None):
        """Obtiene un valor de la configuración."""
        try:
            if clave:
                return self.config[seccion][clave]
            else:
                return self.config[seccion]
        except KeyError:
            return None
    
    def guardar_configuracion(self):
        """Guarda la configuración actual en el archivo."""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
            print(f"✓ Configuración guardada en '{self.archivo_config}'")
        except Exception as e:
            print(f"✗ Error al guardar configuración: {e}")


# ============================================================
# SISTEMA INTEGRADO
# ============================================================

class SistemaIntegrado:
    """Sistema principal que integra todos los módulos."""
    
    def __init__(self):
        self.config = ConfiguracionSistema()
        self.gestor_productos = None
        self.sistema_pos = None
        self.inicializado = False
    
    def inicializar(self):
        """Inicializa todos los componentes del sistema."""
        print("\n" + "="*70)
        print("INICIALIZANDO SISTEMA...")
        print("="*70)
        
        # Cargar catálogo de productos
        print("\n1. Cargando catálogo de productos...")
        self.gestor_productos = crear_catalogo_cafeteria()
        print(f"   ✓ {len(self.gestor_productos.productos)} productos cargados")
        
        # Inicializar sistema POS
        print("\n2. Inicializando sistema de ventas...")
        self.sistema_pos = SistemaPOS(self.gestor_productos)
        
        # Configurar contador de ventas
        contador_inicial = self.config.obtener("ventas", "contador_inicial")
        if contador_inicial:
            Venta.contador_ventas = contador_inicial
        print(f"   ✓ Sistema POS listo (Contador inicial: {Venta.contador_ventas})")

          # ── BASE DE DATOS SQLITE ──────────────────────────────── NUEVO
        print("\n3. Inicializando base de datos SQLite...")
        self.db = inicializar_base_de_datos(self.gestor_productos)
        self.db.sincronizar_stock_a_gestor(self.gestor_productos)
        self.sistema_pos.db = self.db
        # ─────────────────────────────────────────────────────────────
        
        # Crear directorios necesarios
        print("\n4. Verificando directorios...")
        self.crear_directorios()
        
        self.inicializado = True
        print("\n" + "="*70)
        print("✓ SISTEMA INICIALIZADO CORRECTAMENTE")
        print("="*70 + "\n")
    
    def crear_directorios(self):
        """Crea los directorios necesarios para el sistema."""
        directorios = [
            self.config.obtener("ventas", "carpeta_tickets") or "tickets",
            self.config.obtener("ventas", "carpeta_reportes") or "reportes",
            self.config.obtener("sistema_archivos", "carpeta_datos") or "datos",
            self.config.obtener("sistema_archivos", "carpeta_respaldos") or "respaldos"
        ]
        
        for directorio in directorios:
            if directorio and not os.path.exists(directorio):
                try:
                    os.makedirs(directorio)
                    print(f"   ✓ Directorio creado: {directorio}/")
                except Exception as e:
                    print(f"   ✗ Error creando {directorio}/: {e}")
    
    def mostrar_encabezado(self):
        """Muestra el encabezado del sistema."""
        nombre_sistema = self.config.obtener("sistema", "nombre")
        version = self.config.obtener("sistema", "version")
        nombre_negocio = self.config.obtener("configuracion_general", "nombre_negocio")
        
        print("\n" + "╔" + "="*68 + "╗")
        print(f"║{nombre_sistema:^68}║")
        print(f"║{('Versión ' + version):^68}║")
        print("╠" + "="*68 + "╣")
        print(f"║{nombre_negocio:^68}║")
        print(f"║{datetime.now().strftime('%d de %B de %Y - %H:%M:%S'):^68}║")
        print("╚" + "="*68 + "╝\n")


# ============================================================
# MENÚ PRINCIPAL INTEGRADO
# ============================================================

def menu_principal_integrado():
    """Menú principal que integra todos los sistemas."""
    
    # Inicializar sistema
    sistema = SistemaIntegrado()
    sistema.mostrar_encabezado()
    sistema.inicializar()
    
    # Configurar nombre del cajero
    print("="*70)
    cajeros = sistema.config.obtener("cajeros")
    if cajeros:
        print("Cajeros disponibles:")
        for i, cajero in enumerate(cajeros, 1):
            print(f"  {i}. {cajero}")
        print()
    
    nombre_cajero = input("Ingresa el nombre del cajero (Enter = Cajero Principal): ").strip()
    if nombre_cajero:
        sistema.sistema_pos.cajero = nombre_cajero
    else:
        sistema.sistema_pos.cajero = "Cajero Principal"
    
    print(f"✓ Sesión iniciada como: {sistema.sistema_pos.cajero}\n")
    
    # Menú principal
    while True:
        print("\n" + "="*70)
        print("MENÚ PRINCIPAL - SISTEMA INTEGRADO")
        print("="*70)
        print("\n📦 GESTIÓN DE INVENTARIO:")
        print("  1.  Ver catálogo completo de productos")
        print("  2.  Ver productos por categoría")
        print("  3.  Buscar producto (por código o nombre)")
        print("  4.  Agregar stock a producto")
        print("  5.  Actualizar precio de producto")
        print("  6.  Ver productos con stock bajo")
        print("  7.  Ver productos más rentables")
        print("  8.  Ver valor total del inventario")
        
        print("\n💰 PUNTO DE VENTA:")
        print("  9.  Iniciar nueva venta")
        print("  10. Agregar producto al carrito")
        print("  11. Ver carrito actual")
        print("  12. Modificar carrito (eliminar/cambiar cantidad)")
        print("  13. Finalizar y cobrar venta")
        print("  14. Cancelar venta actual")
        
        print("\n📊 REPORTES Y CONSULTAS:")
        print("  15. Ver historial de ventas")
        print("  16. Buscar venta específica")
        print("  17. Reporte diario de ventas")
        print("  18. Reporte general de ventas")
        print("  19. Top productos más vendidos")
        
        print("\n💾 ARCHIVO Y RESPALDO:")
        print("  20. Guardar inventario en CSV")
        print("  21. Guardar historial de ventas en CSV")
        print("  22. Ver configuración del sistema")
        
        print("\n🎯 ACCESOS RÁPIDOS:")
        print("  23. Modo: Sistema de Ventas completo")
        print("  24. Modo: Gestión de Productos completo")
        print("  25. Ejecutar demostración")
        
        print("\n🚪 SALIR:")
        print("  26. Cerrar sistema")
        
        print("="*70)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        # === GESTIÓN DE INVENTARIO ===
        if opcion == "1":
            sistema.gestor_productos.listar_productos()
        
        elif opcion == "2":
            categorias = sistema.config.obtener("categorias_productos")
            if categorias:
                print("\nCategorías disponibles:")
                for cat in categorias:
                    print(f"  - {cat}")
            categoria = input("\nIngresa la categoría: ").strip()
            sistema.gestor_productos.listar_por_categoria(categoria)
        
        elif opcion == "3":
            print("\n1. Buscar por código")
            print("2. Buscar por nombre")
            tipo = input("Tipo de búsqueda: ").strip()
            
            if tipo == "1":
                codigo = input("Código del producto: ").strip()
                producto = sistema.gestor_productos.buscar_por_codigo(codigo)
                if producto:
                    producto.mostrar_informacion()
            elif tipo == "2":
                nombre = input("Nombre del producto: ").strip()
                sistema.gestor_productos.buscar_por_nombre(nombre)
        
        elif opcion == "4":
            codigo = input("Código del producto: ").strip()
            producto = sistema.gestor_productos.buscar_por_codigo(codigo)
            if producto:
                try:
                    cantidad = int(input("Cantidad a agregar: "))
                    producto.agregar_stock(cantidad)
                except ValueError:
                    print("✗ Cantidad inválida")
        
        elif opcion == "5":
            codigo = input("Código del producto: ").strip()
            producto = sistema.gestor_productos.buscar_por_codigo(codigo)
            if producto:
                try:
                    nuevo_precio = float(input("Nuevo precio de venta: $"))
                    producto.set_precio_venta(nuevo_precio)
                except ValueError:
                    print("✗ Precio inválido")
        
        elif opcion == "6":
            stock_minimo = sistema.config.obtener("inventario", "stock_minimo_alerta") or 10
            try:
                minimo = int(input(f"Stock mínimo (default {stock_minimo}): ") or str(stock_minimo))
                sistema.gestor_productos.productos_stock_bajo(minimo)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "7":
            try:
                top = int(input("¿Cuántos productos mostrar? (default 5): ") or "5")
                sistema.gestor_productos.productos_mas_rentables(top)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "8":
            sistema.gestor_productos.calcular_valor_total_inventario()
        
        # === PUNTO DE VENTA ===
        elif opcion == "9":
            sistema.sistema_pos.nueva_venta()
        
        elif opcion == "10":
            sistema.sistema_pos.agregar_producto()
        
        elif opcion == "11":
            if sistema.sistema_pos.venta_actual:
                sistema.sistema_pos.venta_actual.mostrar_carrito()
            else:
                print("✗ No hay venta activa. Inicia una nueva venta primero (opción 9)")
        
        elif opcion == "12":
            if not sistema.sistema_pos.venta_actual or not sistema.sistema_pos.venta_actual.get_items():
                print("✗ No hay productos en el carrito")
            else:
                sistema.sistema_pos.venta_actual.mostrar_carrito()
                print("\n1. Eliminar producto")
                print("2. Modificar cantidad")
                sub_opcion = input("Elige una opción: ").strip()
                
                if sub_opcion == "1":
                    codigo = input("Código del producto a eliminar: ").strip()
                    sistema.sistema_pos.venta_actual.eliminar_item(codigo)
                elif sub_opcion == "2":
                    codigo = input("Código del producto: ").strip()
                    try:
                        nueva_cantidad = int(input("Nueva cantidad: "))
                        sistema.sistema_pos.venta_actual.modificar_cantidad_item(codigo, nueva_cantidad)
                    except ValueError:
                        print("✗ Cantidad inválida")
        
        elif opcion == "13":
            sistema.sistema_pos.finalizar_venta()
        
        elif opcion == "14":
            if sistema.sistema_pos.venta_actual:
                confirmar = input("¿Cancelar venta actual? (s/n): ")
                if confirmar.lower() == 's':
                    sistema.sistema_pos.venta_actual.cancelar_venta()
                    sistema.sistema_pos.venta_actual = None
            else:
                print("✗ No hay venta activa")
        
        # === REPORTES ===
        elif opcion == "15":
            try:
                limite = input("¿Cuántas ventas mostrar? (Enter = todas): ").strip()
                limite = int(limite) if limite else None
                sistema.sistema_pos.historial.listar_ventas(limite)
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "16":
            try:
                numero = int(input("Número de venta: "))
                venta = sistema.sistema_pos.historial.buscar_venta(numero)
                if venta:
                    venta.generar_ticket()
            except ValueError:
                print("✗ Número inválido")
        
        elif opcion == "17":
            sistema.sistema_pos.historial.reporte_diario()
        
        elif opcion == "18":
            sistema.sistema_pos.historial.reporte_general()
        
        elif opcion == "19":
            try:
                top = int(input("¿Cuántos productos mostrar? (default 10): ") or "10")
                sistema.sistema_pos.historial.productos_mas_vendidos(top)
            except ValueError:
                print("✗ Número inválido")
        
        # === ARCHIVO Y RESPALDO ===
        elif opcion == "20":
            sistema.gestor_productos.guardar_csv()
        
        elif opcion == "21":
            sistema.sistema_pos.historial.guardar_csv()
        
        elif opcion == "22":
            print("\n" + "="*70)
            print("CONFIGURACIÓN DEL SISTEMA")
            print("="*70)
            print(json.dumps(sistema.config.config, indent=2, ensure_ascii=False))
            print("="*70)
        
        # === ACCESOS RÁPIDOS ===
        elif opcion == "23":
            print("\n🔄 Cambiando a modo: Sistema de Ventas completo...")
            input("Presiona Enter para continuar...")
            menu_ventas()
        
        elif opcion == "24":
            print("\n🔄 Cambiando a modo: Gestión de Productos completo...")
            input("Presiona Enter para continuar...")
            menu_gestion()
        
        elif opcion == "25":
            print("\n🎬 Ejecutando demostración del sistema...")
            confirmar = input("¿Continuar? (s/n): ")
            if confirmar.lower() == 's':
                demo_ventas()
        
        # === SALIR ===
        elif opcion == "26":
            # Advertir si hay venta en progreso
            if sistema.sistema_pos.venta_actual and sistema.sistema_pos.venta_actual.get_items():
                print("\n⚠️  Hay una venta en progreso")
                confirmar = input("¿Salir de todas formas? (s/n): ")
                if confirmar.lower() != 's':
                    continue
            
            # Resumen final
            print("\n" + "="*70)
            print("RESUMEN DE LA SESIÓN")
            print("="*70)
            print(f"Cajero:           {sistema.sistema_pos.cajero}")
            print(f"Ventas realizadas: {len(sistema.sistema_pos.historial.ventas)}")
            if sistema.sistema_pos.historial.ventas:
                total_vendido = sum(v.get_total() for v in sistema.sistema_pos.historial.ventas)
                print(f"Total vendido:    ${total_vendido:,.2f}")
            print("="*70)
            
            # Preguntar si guardar datos
            guardar = input("\n¿Guardar inventario y ventas? (s/n): ")
            if guardar.lower() == 's':
                sistema.gestor_productos.guardar_csv()
                sistema.sistema_pos.historial.guardar_csv()

                            # ── GUARDAR STOCK FINAL Y CERRAR BD ──────────────── NUEVO
            sistema.db.sincronizar_productos_desde_gestor(
                sistema.gestor_productos
            )
            sistema.db.cerrar()
            # ─────────────────────────────────────────────────────────
            

            print("\n" + "╔" + "="*68 + "╗")
            print("║" + " "*68 + "║")
            print("║" + "¡Gracias por usar el Sistema Integrado!".center(68) + "║")
            print("║" + "Hasta luego ☕".center(68) + "║")
            print("║" + " "*68 + "║")
            print("╚" + "="*68 + "╝\n")
            break
        
        else:
            print("✗ Opción no válida. Por favor selecciona una opción del 1 al 26.")
        
        # Pausa para que el usuario pueda leer el resultado
        if opcion not in ["23", "24", "26"]:
            input("\nPresiona Enter para continuar...")


# ============================================================
# FUNCIÓN DE AYUDA
# ============================================================

def mostrar_ayuda():
    """Muestra la ayuda del sistema."""
    print("\n" + "="*70)
    print("AYUDA DEL SISTEMA")
    print("="*70)
    print("""
Este es un sistema integrado de gestión y ventas para cafetería.

MÓDULOS PRINCIPALES:
1. Gestión de Productos - Administra el inventario y catálogo
2. Sistema de Ventas - Maneja las ventas y punto de venta (POS)
3. Reportes - Genera estadísticas e informes

ARCHIVOS NECESARIOS:
- sistema_gestion_productos.py (Módulo de productos)
- sistema_ventas_cafeteria.py (Módulo de ventas)
- config.json (Configuración del sistema)
- main.py (Este archivo - punto de entrada)

FLUJO BÁSICO DE USO:
1. Iniciar el sistema
2. Ingresar como cajero
3. Consultar productos disponibles
4. Iniciar nueva venta
5. Agregar productos al carrito
6. Finalizar y cobrar
7. Ver reportes al final del día

Para más información, consulta el archivo README.md
    """)
    print("="*70)


# ============================================================
# FUNCIÓN DE VERIFICACIÓN
# ============================================================

def verificar_sistema():
    """Verifica que todos los componentes necesarios estén presentes."""
    archivos_necesarios = [
        "sistema_gestion_productos.py",
        "sistema_ventas_cafeteria.py"
    ]
    
    archivos_opcionales = [
        "config.json",
        "README.md"
    ]
    
    print("\n" + "="*70)
    print("VERIFICACIÓN DEL SISTEMA")
    print("="*70)
    
    print("\nArchivos necesarios:")
    todos_presentes = True
    for archivo in archivos_necesarios:
        existe = os.path.exists(archivo)
        simbolo = "✓" if existe else "✗"
        print(f"  {simbolo} {archivo}")
        if not existe:
            todos_presentes = False
    
    print("\nArchivos opcionales:")
    for archivo in archivos_opcionales:
        existe = os.path.exists(archivo)
        simbolo = "✓" if existe else "⚠"
        print(f"  {simbolo} {archivo}")
    
    print("\n" + "="*70)
    
    if not todos_presentes:
        print("\n✗ ADVERTENCIA: Faltan archivos necesarios.")
        print("El sistema no podrá funcionar correctamente.\n")
        return False
    else:
        print("\n✓ Todos los archivos necesarios están presentes.\n")
        return True


# ============================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================

def main():
    """Función principal del sistema."""
    
    # Verificar componentes
    if not verificar_sistema():
        respuesta = input("¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("\nSaliendo del sistema...\n")
            sys.exit(1)
    
    # Menú de inicio
    while True:
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + "SISTEMA INTEGRADO - CAFETERÍA".center(68) + "║")
        print("╚" + "="*68 + "╝\n")
        
        print("Selecciona una opción:")
        print("  1. Iniciar sistema completo (RECOMENDADO)")
        print("  2. Modo: Solo gestión de productos")
        print("  3. Modo: Solo sistema de ventas")
        print("  4. Ejecutar demostración")
        print("  5. Ver ayuda")
        print("  6. Salir")
        
        opcion = input("\nOpción: ").strip()
        
        if opcion == "1":
            menu_principal_integrado()
            break
        elif opcion == "2":
            menu_gestion()
            break
        elif opcion == "3":
            menu_ventas()
            break
        elif opcion == "4":
            demo_ventas()
            input("\nPresiona Enter para volver al menú...")
        elif opcion == "5":
            mostrar_ayuda()
            input("\nPresiona Enter para volver al menú...")
        elif opcion == "6":
            print("\n¡Hasta luego! ☕\n")
            break
        else:
            print("✗ Opción no válida")


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Sistema interrumpido por el usuario")
        print("¡Hasta luego! ☕\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error fatal del sistema: {e}")
        print("Por favor contacta al soporte técnico.\n")
        sys.exit(1)
