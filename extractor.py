"""
Extractor de Datos de Productos Web
Extrae información de productos de páginas de e-commerce
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import os
from datetime import datetime


class ProductExtractor:
    """Clase para extraer datos de productos de páginas web"""
    
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.product_data = {}
    
    def fetch_page(self):
        """Obtiene el contenido HTML de la página"""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error al obtener la página: {e}")
            return None
    
    def extract_title(self, soup):
        """Extrae el título del producto"""
        # Múltiples selectores comunes para títulos
        selectors = [
            'h1.product-title',
            'h1[itemprop="name"]',
            'h1.product-name',
            'h1',
            '.product-title',
            '[data-product-title]'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)
        
        return "Título no encontrado"
    
    def extract_price(self, soup):
        """Extrae el precio del producto"""
        # Múltiples selectores para precios
        selectors = [
            '.product-price',
            '[itemprop="price"]',
            '.price',
            '.product-price-value',
            '[data-price]'
        ]
        
        for selector in selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Extraer números y símbolos de moneda
                price_clean = re.sub(r'[^\d.,€$]', '', price_text)
                return price_text if price_clean else None
        
        return None
    
    def extract_images(self, soup):
        """Extrae todas las imágenes del producto"""
        images = []
        base_url = f"{urlparse(self.url).scheme}://{urlparse(self.url).netloc}"
        
        # Buscar imágenes en galerías de productos
        image_selectors = [
            '.product-image img',
            '.product-gallery img',
            '.product-images img',
            '[data-product-image]',
            '.carousel img',
            'img[itemprop="image"]'
        ]
        
        for selector in image_selectors:
            img_elements = soup.select(selector)
            if img_elements:
                for img in img_elements:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        # Convertir URL relativa a absoluta
                        full_url = urljoin(base_url, src)
                        if full_url not in images:
                            images.append(full_url)
        
        # Si no se encontraron imágenes específicas, buscar todas las imágenes grandes
        if not images:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = img.get('src') or img.get('data-src')
                if src and any(keyword in src.lower() for keyword in ['product', 'item', 'image']):
                    full_url = urljoin(base_url, src)
                    if full_url not in images:
                        images.append(full_url)
        
        return images[:10]  # Limitar a 10 imágenes
    
    def extract_description(self, soup):
        """Extrae la descripción del producto"""
        # Selectores comunes para descripciones
        selectors = [
            '.product-description',
            '[itemprop="description"]',
            '.product-details',
            '.product-info',
            '#product-description',
            # Selectores específicos de Odoo
            '.o_product_description',
            '.oe_product_description',
            'div[itemprop="description"]',
            '.product_detail_description',
            '.product-description-full',
            # Selectores genéricos
            '.description',
            '#description',
            'div.description',
            'p.description'
        ]
        
        for selector in selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                text = desc_elem.get_text(separator='\n', strip=True)
                if text and len(text) > 20:  # Asegurar que hay contenido significativo
                    return text
        
        # Buscar párrafos con texto descriptivo largo (común en Odoo)
        paragraphs = soup.find_all('p')
        description_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filtrar párrafos que parecen descripciones (más de 50 caracteres)
            if len(text) > 50 and not any(keyword in text.lower() for keyword in ['cookie', 'privacy', 'términos', 'copyright']):
                description_parts.append(text)
        
        if description_parts:
            return '\n\n'.join(description_parts)
        
        # Buscar divs con contenido de texto descriptivo
        divs = soup.find_all('div', class_=lambda x: x and ('description' in x.lower() or 'detail' in x.lower() or 'info' in x.lower()))
        for div in divs:
            text = div.get_text(separator='\n', strip=True)
            if text and len(text) > 50:
                return text
        
        # Buscar en secciones y artículos
        for tag in ['section', 'article', 'div']:
            elements = soup.find_all(tag, class_=lambda x: x and 'product' in x.lower())
            for elem in elements:
                # Buscar párrafos dentro de estos elementos
                inner_ps = elem.find_all('p')
                if inner_ps:
                    texts = [p.get_text(strip=True) for p in inner_ps if len(p.get_text(strip=True)) > 30]
                    if texts:
                        return '\n\n'.join(texts)
        
        # Buscar meta description como alternativa
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if content and len(content) > 20:
                return content
        
        # Último recurso: buscar cualquier párrafo largo cerca del título
        h1 = soup.find('h1')
        if h1:
            parent = h1.find_parent()
            if parent:
                all_text = parent.get_text(separator='\n', strip=True)
                # Extraer texto después del título
                lines = all_text.split('\n')
                desc_lines = []
                found_title = False
                for line in lines:
                    if found_title and len(line.strip()) > 30:
                        desc_lines.append(line.strip())
                    if h1.get_text(strip=True) in line:
                        found_title = True
                
                if desc_lines:
                    return '\n\n'.join(desc_lines[:5])  # Limitar a primeros 5 párrafos
        
        return "Descripción no encontrada"
    
    def extract_specifications(self, soup):
        """Extrae especificaciones y detalles adicionales del producto"""
        specs = {}
        
        # Buscar secciones de especificaciones
        spec_keywords = ['especificaciones', 'especificación', 'características', 'detalles', 'modo de uso']
        
        # Buscar por títulos/encabezados que contengan estas palabras
        for keyword in spec_keywords:
            # Buscar en h2, h3, h4, strong, b
            for tag in ['h2', 'h3', 'h4', 'strong', 'b', 'span']:
                elements = soup.find_all(tag, string=lambda text: text and keyword.lower() in text.lower())
                for elem in elements:
                    # Buscar el siguiente elemento hermano o padre que contenga la información
                    parent = elem.find_parent()
                    if parent:
                        # Buscar listas (ul, ol) dentro del padre
                        lists = parent.find_all(['ul', 'ol'])
                        if lists:
                            for ul in lists:
                                items = ul.find_all('li')
                                if items:
                                    spec_list = [li.get_text(strip=True) for li in items if li.get_text(strip=True)]
                                    if spec_list:
                                        specs[keyword.capitalize()] = spec_list
                        
                        # Buscar párrafos después del título
                        next_siblings = elem.find_next_siblings(['p', 'div'])
                        spec_texts = []
                        for sibling in next_siblings[:5]:  # Limitar a 5 elementos
                            text = sibling.get_text(strip=True)
                            if text and len(text) > 20:
                                spec_texts.append(text)
                        if spec_texts:
                            specs[keyword.capitalize()] = '\n'.join(spec_texts)
        
        # Buscar listas con viñetas que puedan ser especificaciones
        all_lists = soup.find_all(['ul', 'ol'])
        for ul in all_lists:
            items = ul.find_all('li')
            if items and len(items) >= 2:  # Al menos 2 items para considerar como especificaciones
                # Verificar si los items parecen especificaciones (contienen palabras clave)
                spec_keywords_in_items = ['material', 'batería', 'compatibilidad', 'uso', 'instalación']
                item_texts = [li.get_text(strip=True) for li in items]
                if any(keyword in ' '.join(item_texts).lower() for keyword in spec_keywords_in_items):
                    if 'Especificaciones' not in specs:
                        specs['Especificaciones'] = item_texts
        
        return specs
    
    def extract_attributes(self, soup):
        """Extrae atributos adicionales del producto (SKU, categoría, etc.)"""
        attributes = {}
        
        # SKU
        sku_selectors = [
            '[itemprop="sku"]',
            '.product-sku',
            '[data-sku]'
        ]
        for selector in sku_selectors:
            sku_elem = soup.select_one(selector)
            if sku_elem:
                attributes['SKU'] = sku_elem.get_text(strip=True)
                break
        
        # Categoría
        category_selectors = [
            '[itemprop="category"]',
            '.product-category',
            '.breadcrumb a'
        ]
        categories = []
        for selector in category_selectors:
            cat_elems = soup.select(selector)
            if cat_elems:
                categories = [cat.get_text(strip=True) for cat in cat_elems if cat.get_text(strip=True)]
                if categories:
                    attributes['Categorías'] = categories
                    break
        
        # Disponibilidad
        availability_selectors = [
            '[itemprop="availability"]',
            '.product-availability',
            '.stock-status'
        ]
        for selector in availability_selectors:
            avail_elem = soup.select_one(selector)
            if avail_elem:
                attributes['Disponibilidad'] = avail_elem.get_text(strip=True)
                break
        
        # Agregar especificaciones a los atributos
        specs = self.extract_specifications(soup)
        if specs:
            attributes['Especificaciones'] = specs
        
        return attributes
    
    def extract_all_data(self):
        """Extrae todos los datos del producto"""
        html_content = self.fetch_page()
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        self.product_data = {
            'URL': self.url,
            'Título': self.extract_title(soup),
            'Precio': self.extract_price(soup),
            'Descripción': self.extract_description(soup),
            'Imágenes': self.extract_images(soup),
            'Atributos': self.extract_attributes(soup),
            'Fecha de extracción': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.product_data
    
    def save_to_json(self, filename=None):
        """Guarda los datos extraídos en un archivo JSON"""
        if not self.product_data:
            print("No hay datos para guardar. Ejecuta extract_all_data() primero.")
            return
        
        if not filename:
            # Generar nombre de archivo basado en el título
            safe_title = re.sub(r'[^\w\s-]', '', self.product_data['Título'])[:50]
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"producto_{safe_title}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.product_data, f, ensure_ascii=False, indent=2)
        
        print(f"Datos guardados en: {filename}")
        return filename
    
    def print_data(self):
        """Imprime los datos extraídos de forma legible"""
        if not self.product_data:
            print("No hay datos para mostrar.")
            return
        
        print("\n" + "="*60)
        print("DATOS DEL PRODUCTO EXTRAÍDOS")
        print("="*60)
        print(f"URL: {self.product_data['URL']}")
        print(f"Título: {self.product_data['Título']}")
        print(f"Precio: {self.product_data['Precio'] or 'No disponible'}")
        
        # Mostrar descripción completa
        desc = self.product_data['Descripción']
        if desc and desc != "Descripción no encontrada":
            print(f"\nDescripción:")
            # Mostrar descripción completa o truncada si es muy larga
            if len(desc) > 500:
                print(desc[:500] + "...")
                print(f"\n(Descripción completa tiene {len(desc)} caracteres)")
            else:
                print(desc)
        else:
            print(f"\nDescripción: {desc}")
        
        print(f"\nImágenes encontradas: {len(self.product_data['Imágenes'])}")
        for i, img in enumerate(self.product_data['Imágenes'][:3], 1):
            print(f"  {i}. {img}")
        if len(self.product_data['Imágenes']) > 3:
            print(f"  ... y {len(self.product_data['Imágenes']) - 3} más")
        
        if self.product_data['Atributos']:
            print("\nAtributos adicionales:")
            for key, value in self.product_data['Atributos'].items():
                if key == 'Especificaciones' and isinstance(value, dict):
                    print(f"  {key}:")
                    for spec_key, spec_value in value.items():
                        if isinstance(spec_value, list):
                            print(f"    {spec_key}:")
                            for item in spec_value:
                                print(f"      - {item}")
                        else:
                            print(f"    {spec_key}: {spec_value}")
                elif isinstance(value, list):
                    print(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"  {key}: {value}")
        print("="*60 + "\n")


def main():
    """Función principal"""
    print("="*60)
    print("EXTRACTOR DE DATOS DE PRODUCTOS WEB")
    print("="*60)
    
    # URL de ejemplo basada en la imagen proporcionada
    default_url = "https://imporhouse.odoo.com/shop/dispensador-de-agua-para-botellon-60"
    
    url = input(f"\nIngresa la URL del producto (Enter para usar ejemplo): ").strip()
    if not url:
        url = default_url
        print(f"Usando URL de ejemplo: {url}")
    
    print("\nExtrayendo datos...")
    extractor = ProductExtractor(url)
    data = extractor.extract_all_data()
    
    if data:
        extractor.print_data()
        
        save = input("\n¿Guardar datos en JSON? (s/n): ").strip().lower()
        if save == 's':
            extractor.save_to_json()
    else:
        print("No se pudieron extraer los datos.")


if __name__ == "__main__":
    main()

