"""
Generador de Vista HTML para Productos
Genera automáticamente una vista HTML con todos los productos JSON encontrados
"""

import json
import os
import glob
from datetime import datetime


def format_price(price):
    """Formatea el precio"""
    if not price:
        return 'No disponible'
    try:
        num_price = float(price)
        return f"{num_price:,.0f}".replace(',', '.')
    except:
        return str(price)


def get_main_image(images):
    """Obtiene la imagen principal"""
    if not images or len(images) == 0:
        return ''
    # Buscar imagen de alta resolución
    for img in images:
        if 'image_1024' in img:
            return img
    return images[0] if images else ''


def get_gallery_images(images):
    """Obtiene imágenes para la galería"""
    if not images:
        return []
    # Filtrar imágenes de alta resolución y limitar a 4
    gallery = [img for img in images if 'image_1024' in img][:4]
    return gallery if gallery else images[:4]


def generate_attributes_html(attributes):
    """Genera HTML para los atributos del producto"""
    if not attributes:
        return ''
    
    html = ''
    
    if attributes.get('Categorías'):
        html += f'''
                        <div class="product-attributes">
                            <h4>Categorías</h4>
                            <ul>
                                {''.join([f'<li>{cat}</li>' for cat in attributes['Categorías']])}
                            </ul>
                        </div>
                    '''
    
    if attributes.get('Especificaciones'):
        specs = attributes['Especificaciones']
        html += '<div class="specifications">'
        for key, value in specs.items():
            if isinstance(value, list):
                html += f'''
                                <h5>{key}</h5>
                                <ul>
                                    {''.join([f'<li>{item}</li>' for item in value])}
                                </ul>
                            '''
            else:
                html += f'''
                                <h5>{key}</h5>
                                <p style="color: #666; font-size: 0.9em; margin-top: 5px;">{value}</p>
                            '''
        html += '</div>'
    
    if attributes.get('SKU'):
        html += f'''
                        <div class="product-attributes">
                            <h4>SKU</h4>
                            <p style="color: #666; font-size: 0.9em;">{attributes['SKU']}</p>
                        </div>
                    '''
    
    if attributes.get('Disponibilidad'):
        html += f'''
                        <div class="product-attributes">
                            <h4>Disponibilidad</h4>
                            <p style="color: #666; font-size: 0.9em;">{attributes['Disponibilidad']}</p>
                        </div>
                    '''
    
    return html


def generate_product_card(product):
    """Genera el HTML de una tarjeta de producto"""
    main_image = get_main_image(product.get('Imágenes', []))
    gallery_images = get_gallery_images(product.get('Imágenes', []))
    title = product.get('Título', 'Sin título')
    price = format_price(product.get('Precio'))
    description = product.get('Descripción', '')
    url = product.get('URL', '#')
    fecha = product.get('Fecha de extracción', 'Fecha no disponible')
    attributes_html = generate_attributes_html(product.get('Atributos', {}))
    
    # Procesar descripción
    if description and description != 'Descripción no encontrada':
        description_html = description.replace('\n', '<br>')
    else:
        description_html = '<em style="color: #999;">Descripción no disponible</em>'
    
    # Generar galería de imágenes
    gallery_html = ''
    if len(gallery_images) > 1:
        gallery_items = []
        for img in gallery_images:
            onclick_attr = f"changeMainImage(this, '{main_image}')"
            gallery_items.append(f'<img src="{img}" alt="Vista adicional" onclick="{onclick_attr}">')
        gallery_html = f'''
                    <div class="product-image-gallery">
                        {''.join(gallery_items)}
                    </div>
                '''
    
    # Generar imagen principal
    main_img_html = ''
    if main_image:
        error_img = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'300\'%3E%3Crect fill=\'%23ddd\' width=\'400\' height=\'300\'/%3E%3Ctext fill=\'%23999\' font-family=\'sans-serif\' font-size=\'20\' dy=\'10.5\' font-weight=\'bold\' x=\'50%25\' y=\'50%25\' text-anchor=\'middle\'%3EImagen no disponible%3C/text%3E%3C/svg%3E'
        main_img_html = f'<img src="{main_image}" alt="{title}" class="product-image" onerror="this.src=\'{error_img}\'">'
    
    return f'''
                <div class="product-card">
                    <div class="product-image-container">
                        {main_img_html}
                    </div>
                    {gallery_html}
                    <div class="product-info">
                        <h2 class="product-title">{title}</h2>
                        <div class="product-price">${price}</div>
                        <div class="product-description">
                            {description_html}
                        </div>
                        {attributes_html}
                        <a href="{url}" target="_blank" class="product-link">
                            Ver producto original →
                        </a>
                        <div class="product-meta">
                            Extraído el: {fecha}
                        </div>
                    </div>
                </div>
            '''


def generate_html(products):
    """Genera el HTML completo"""
    products_html = ''.join([generate_product_card(product) for product in products])
    
    html_template = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Productos - Extractor</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 30px 0;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .product-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .product-image-container {{
            position: relative;
            width: 100%;
            height: 300px;
            overflow: hidden;
            background: #f5f5f5;
        }}

        .product-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}

        .product-card:hover .product-image {{
            transform: scale(1.05);
        }}

        .product-image-gallery {{
            display: flex;
            gap: 5px;
            padding: 10px;
            background: #f9f9f9;
            overflow-x: auto;
        }}

        .product-image-gallery img {{
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 5px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: border-color 0.3s ease;
        }}

        .product-image-gallery img:hover {{
            border-color: #667eea;
        }}

        .product-info {{
            padding: 25px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}

        .product-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.3;
        }}

        .product-price {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
        }}

        .product-description {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
            flex-grow: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
        }}

        .product-attributes {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}

        .product-attributes h4 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .product-attributes ul {{
            list-style: none;
            padding-left: 0;
        }}

        .product-attributes li {{
            color: #666;
            padding: 5px 0;
            font-size: 0.9em;
        }}

        .product-attributes li::before {{
            content: "✓ ";
            color: #667eea;
            font-weight: bold;
        }}

        .product-link {{
            display: inline-block;
            margin-top: 15px;
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            text-align: center;
            transition: opacity 0.3s ease;
            font-weight: 600;
        }}

        .product-link:hover {{
            opacity: 0.9;
        }}

        .product-meta {{
            font-size: 0.85em;
            color: #999;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}

        .specifications {{
            margin-top: 15px;
        }}

        .specifications h5 {{
            color: #333;
            margin-bottom: 8px;
            font-size: 0.95em;
        }}

        .specifications ul {{
            list-style: none;
            padding-left: 0;
        }}

        .specifications li {{
            color: #666;
            padding: 3px 0;
            font-size: 0.85em;
            padding-left: 15px;
            position: relative;
        }}

        .specifications li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #667eea;
        }}

        @media (max-width: 768px) {{
            .products-grid {{
                grid-template-columns: 1fr;
            }}

            header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛍️ Catálogo de Productos</h1>
            <p>Productos extraídos de páginas web - {len(products)} producto(s) encontrado(s)</p>
        </header>

        <div class="products-grid">
            {products_html}
        </div>
    </div>

    <script>
        function changeMainImage(clickedImg, originalMain) {{
            const card = clickedImg.closest('.product-card');
            const mainImg = card.querySelector('.product-image');
            if (mainImg) {{
                mainImg.src = clickedImg.src.replace('image_128', 'image_1024').replace('image_512', 'image_1024');
            }}
        }}
    </script>
</body>
</html>'''
    
    return html_template


def main():
    """Función principal"""
    print("="*60)
    print("GENERADOR DE VISTA HTML DE PRODUCTOS")
    print("="*60)
    
    # Buscar todos los archivos JSON de productos
    json_files = glob.glob('producto_*.json')
    
    if not json_files:
        print("\n❌ No se encontraron archivos JSON de productos.")
        print("   Asegúrate de tener archivos con el formato: producto_*.json")
        return
    
    print(f"\nEncontrados {len(json_files)} archivo(s) JSON:")
    products = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                product = json.load(f)
                products.append(product)
                print(f"   [OK] {json_file} - {product.get('Título', 'Sin título')}")
        except Exception as e:
            print(f"   [ERROR] Error al leer {json_file}: {e}")
    
    if not products:
        print("\nNo se pudieron cargar productos.")
        return
    
    # Generar HTML
    html_content = generate_html(products)
    
    # Guardar archivo HTML
    output_file = 'vista_productos.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nVista HTML generada exitosamente: {output_file}")
    print(f"   Total de productos: {len(products)}")
    print(f"\nAbre {output_file} en tu navegador para ver el catalogo.")


if __name__ == "__main__":
    main()

