"""
Ejemplo de uso del Extractor de Productos
"""

from extractor import ProductExtractor

# Ejemplo 1: Extraer datos de un producto
print("Ejemplo 1: Extracción básica")
print("-" * 60)

url = "https://imporhouse.odoo.com/shop/dispensador-de-agua-para-botellon-60"
extractor = ProductExtractor(url)

# Extraer todos los datos
data = extractor.extract_all_data()

if data:
    # Mostrar los datos
    extractor.print_data()
    
    # Guardar en JSON
    extractor.save_to_json("producto_ejemplo.json")
    print("\n✅ Datos guardados exitosamente!")
else:
    print("❌ No se pudieron extraer los datos")

print("\n" + "=" * 60)
print("\nEjemplo 2: Extracción y acceso a datos específicos")
print("-" * 60)

if data:
    print(f"Título: {data['Título']}")
    print(f"Precio: {data['Precio']}")
    print(f"Número de imágenes: {len(data['Imágenes'])}")
    if data['Imágenes']:
        print(f"Primera imagen: {data['Imágenes'][0]}")

