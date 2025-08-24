import os
import csv
from collections import defaultdict

# --- CONFIGURACIÓN ---
DIR_TEXTO = 'texto'
DIR_TRADUCIDO = 'traducido'
ARCHIVO_CSV_TRADUCIDO = os.path.join(DIR_TEXTO, 'traducciones.csv')
ARCHIVO_REFERENCIAS = os.path.join(DIR_TEXTO, 'referencias.txt')
# --- FIN DE CONFIGURACIÓN ---

def cargar_traducciones(archivo_csv):
    """Carga las traducciones del CSV y las agrupa por ID base."""
    traducciones_agrupadas = defaultdict(lambda: {'original': [], 'traducido': []})
    try:
        with open(archivo_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Omitir cabecera
            for row in reader:
                if not row: continue
                id_completo, texto_original = row[0], row[1]
                texto_traducido = texto_original
                if len(row) > 2 and row[2]:
                    texto_traducido = row[2]
                id_base = "_".join(id_completo.split('_')[:-1])
                traducciones_agrupadas[id_base]['original'].append(texto_original)
                traducciones_agrupadas[id_base]['traducido'].append(texto_traducido)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de traducciones '{archivo_csv}'.")
        return None
    except Exception as e:
        print(f"Error leyendo el archivo CSV: {e}")
        return None
    return traducciones_agrupadas

def reconstruir_bloque(plantilla, partes):
    """Reconstruye el bloque completo reemplazando los marcadores ##n## con las partes de texto."""
    bloque_reconstruido = plantilla
    for i, parte in enumerate(partes):
        placeholder = f"##{i}##"
        bloque_reconstruido = bloque_reconstruido.replace(placeholder, parte)
    return bloque_reconstruido

def main():
    if not os.path.exists(DIR_TRADUCIDO):
        os.makedirs(DIR_TRADUCIDO)

    traducciones = cargar_traducciones(ARCHIVO_CSV_TRADUCIDO)
    if traducciones is None:
        return

    try:
        with open(ARCHIVO_REFERENCIAS, 'r', encoding='utf-8') as f:
            referencias = f.readlines()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de referencias '{ARCHIVO_REFERENCIAS}'.")
        return

    contenidos_archivos = {}

    for ref in referencias:
        try:
            id_base, filepath, plantilla_bloque = ref.strip().split('|', 2)

            if filepath not in contenidos_archivos:
                with open(filepath, 'r', encoding='utf-8-sig') as f_orig:
                    contenidos_archivos[filepath] = f_orig.read()

            datos_traduccion = traducciones.get(id_base)

            if not datos_traduccion or not datos_traduccion['original']:
                continue

            # La plantilla ahora es el bloque completo (ej: "English":"##0##")
            # Reconstruimos el bloque original y el traducido
            bloque_original = reconstruir_bloque(plantilla_bloque, datos_traduccion['original'])
            bloque_traducido = reconstruir_bloque(plantilla_bloque, datos_traduccion['traducido'])

            # El reemplazo es ahora directo, del bloque original al bloque traducido
            if bloque_original in contenidos_archivos[filepath]:
                 contenidos_archivos[filepath] = contenidos_archivos[filepath].replace(bloque_original, bloque_traducido, 1)
            else:
                print(f"Advertencia: No se encontró el bloque de texto original para '{id_base}' en el archivo '{filepath}'.")

        except ValueError:
            print(f"Advertencia: Omitiendo línea mal formada en referencias: {ref.strip()}")
        except Exception as e:
            print(f"Error procesando la referencia '{ref.strip()}': {e}")

    for filepath, content in contenidos_archivos.items():
        try:
            output_filename = os.path.basename(filepath)
            output_path = os.path.join(DIR_TRADUCIDO, output_filename)
            with open(output_path, 'w', encoding='utf-8-sig') as f_out:
                f_out.write(content)
            print(f"Archivo traducido '{output_path}' creado con éxito.")
        except Exception as e:
            print(f"Error escribiendo el archivo traducido para '{filepath}': {e}")

if __name__ == '__main__':
    main()
