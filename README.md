# Extractor de Datos de Productos Web

Aplicación para extraer información de productos de páginas web de e-commerce.

## Características

- ✅ Extracción automática de títulos de productos
- ✅ Detección de precios
- ✅ Obtención de todas las imágenes del producto
- ✅ Extracción de descripciones y especificaciones
- ✅ Captura de atributos adicionales (SKU, categorías, disponibilidad)
- ✅ Exportación a formato JSON
- ✅ Generación automática de vista HTML con catálogo de productos
- ✅ Soporte para múltiples estructuras de páginas web (incluyendo Odoo)

## Instalación

1. Asegúrate de tener Python 3.7 o superior instalado

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Uso básico desde línea de comandos:

```bash
python extractor.py
```

El programa te pedirá la URL del producto. Puedes presionar Enter para usar una URL de ejemplo.

### Uso programático:

```python
from extractor import ProductExtractor

# Crear instancia del extractor
extractor = ProductExtractor("https://ejemplo.com/producto")

# Extraer todos los datos
data = extractor.extract_all_data()

# Ver los datos
extractor.print_data()

# Guardar en JSON
extractor.save_to_json("mi_producto.json")
```

### Generar vista HTML del catálogo:

```bash
python generar_vista.py
```

Este script busca todos los archivos JSON de productos y genera una vista HTML interactiva con todos ellos.

## Datos Extraídos

La aplicación extrae la siguiente información:

- **URL**: URL del producto
- **Título**: Nombre del producto
- **Precio**: Precio (si está disponible)
- **Descripción**: Descripción del producto
- **Imágenes**: Lista de URLs de imágenes del producto
- **Atributos**: Información adicional (SKU, categorías, disponibilidad)
- **Fecha de extracción**: Timestamp de cuándo se extrajeron los datos

## Formato de Salida JSON

```json
{
  "URL": "https://ejemplo.com/producto",
  "Título": "Nombre del Producto",
  "Precio": "$99.99",
  "Descripción": "Descripción completa...",
  "Imágenes": [
    "https://ejemplo.com/imagen1.jpg",
    "https://ejemplo.com/imagen2.jpg"
  ],
  "Atributos": {
    "SKU": "PROD-123",
    "Categorías": ["Electrónica", "Accesorios"]
  },
  "Fecha de extracción": "2024-01-15 10:30:00"
}
```

## Notas

- La aplicación intenta múltiples selectores CSS comunes para encontrar los datos
- Algunas páginas pueden requerir JavaScript para cargar contenido dinámico
- Para páginas con contenido dinámico, considera usar Selenium en lugar de requests

## Vista HTML

El proyecto incluye un generador de vista HTML que crea un catálogo visual de todos los productos extraídos:

- Diseño responsive y moderno
- Galería de imágenes interactiva
- Visualización completa de descripciones y especificaciones
- Enlaces directos a los productos originales

Ejecuta `python generar_vista.py` para generar o actualizar la vista HTML.

## Mejoras Futuras

- [ ] Soporte para Selenium para páginas con JavaScript
- [ ] Extracción de reviews/calificaciones
- [ ] Exportación a CSV
- [ ] Interfaz gráfica (GUI)
- [ ] Extracción en lote de múltiples productos
- [ ] Filtros y búsqueda en la vista HTML

## Licencia

Este proyecto es de código abierto y está disponible para uso libre.

