import os
import re
import csv

# --- CONFIGURACIÓN ---
DIR_INGLES = 'ingles'
DIR_TEXTO = 'texto'
ARCHIVO_CSV = os.path.join(DIR_TEXTO, 'traducciones.csv')
ARCHIVO_REFERENCIAS = os.path.join(DIR_TEXTO, 'referencias.txt')

# Regex para encontrar el bloque completo de "English", escapado o no, y capturar el contenido interior.
# Grupo 1: Bloque completo (p.ej., "English":"texto" o \"English\":\"texto\")
# Grupo 2: Contenido interior de la parte escapada (si coincide)
# Grupo 3: Contenido interior de la parte no escapada (si coincide)
REGEX_EXTRACCION_GENERAL = re.compile(r'(\\"English\\":\\"(.*?)\\"|(?:"English":"(.*?)"))')

# Regex para dividir el texto por marcadores de formato y variables.
MARCADORES = [
    r'<color=#[a-fA-F0-9]{6}>', r'</color>',
    r'</?(?:T|A|R|B|P|R2|i|W|G|Y)>',
    r'\{/?i\}',
    r'\{[a-zA-Z0-9_]+\}'
]
REGEX_DIVISION_MARCADORES = re.compile(f"({'|'.join(MARCADORES)})")

# Regex para excluir textos que son solo una variable.
REGEX_EXCLUSION_VARIABLE = re.compile(r'^\s*\{[a-zA-Z0-9_]+\}\s*$')
# --- FIN DE CONFIGURACIÓN ---

def procesar_texto_interior(id_base, texto_interior):
    """Procesa el contenido de un campo "English", lo divide y genera partes/plantilla."""
    # Nueva regla: si el contenido está envuelto en \\", se eliminan.
    # Se buscan dos barras invertidas literales seguidas de una comilla.
    match_escaped = re.match(r'^\\\\"(.*)\\\\"$', texto_interior, re.DOTALL)
    if match_escaped:
        texto_interior = match_escaped.group(1)

    if REGEX_EXCLUSION_VARIABLE.match(texto_interior):
        return [], None

    partes = REGEX_DIVISION_MARCADORES.split(texto_interior)
    partes = [p for p in partes if p]

    partes_csv = []
    sub_plantilla_partes = []
    contador_partes_traducibles = 0

    for parte in partes:
        if REGEX_DIVISION_MARCADORES.match(parte):
            sub_plantilla_partes.append(parte)
        else:
            sub_id = f"{id_base}_{contador_partes_traducibles + 1}"
            partes_csv.append([sub_id, parte])
            sub_plantilla_partes.append(f"##{contador_partes_traducibles}##")
            contador_partes_traducibles += 1

    if not partes_csv:
        return [], None

    sub_plantilla_final = "".join(sub_plantilla_partes)
    return partes_csv, sub_plantilla_final

def main():
    if not os.path.exists(DIR_TEXTO):
        os.makedirs(DIR_TEXTO)

    extracciones_csv = []
    referencias_plantillas = []

    for filename in os.listdir(DIR_INGLES):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(DIR_INGLES, filename)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            for i, match in enumerate(REGEX_EXTRACCION_GENERAL.finditer(content)):
                bloque_completo = match.group(1)
                texto_interior = match.group(2) if match.group(2) is not None else match.group(3)

                id_base = f"{os.path.splitext(filename)[0]}_{i+1}"

                partes_csv, sub_plantilla = procesar_texto_interior(id_base, texto_interior)

                if sub_plantilla is not None:
                    plantilla_final = bloque_completo.replace(texto_interior, sub_plantilla, 1)
                    extracciones_csv.extend(partes_csv)
                    referencias_plantillas.append(f"{id_base}|{filepath}|{plantilla_final}")
                else:
                    referencias_plantillas.append(f"{id_base}|{filepath}|{bloque_completo}")

        except Exception as e:
            print(f"Error procesando el archivo {filepath}: {e}")

    # Escribir archivos de salida
    try:
        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Texto Original'])
            writer.writerows(extracciones_csv)
        print(f"Archivo CSV '{ARCHIVO_CSV}' creado con éxito con {len(extracciones_csv)} entradas.")
    except Exception as e:
        print(f"Error escribiendo el archivo CSV: {e}")

    try:
        with open(ARCHIVO_REFERENCIAS, 'w', encoding='utf-8') as f:
            for ref in referencias_plantillas:
                f.write(ref + '\n')
        print(f"Archivo de referencias '{ARCHIVO_REFERENCIAS}' creado con éxito.")
    except Exception as e:
        print(f"Error escribiendo el archivo de referencias: {e}")

if __name__ == '__main__':
    main()
