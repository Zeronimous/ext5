import os
import re
import csv

# Directorios de entrada y salida
dir_ingles = 'ingles'
dir_texto = 'texto'

# Crear el directorio de salida si no existe
if not os.path.exists(dir_texto):
    os.makedirs(dir_texto)

# Archivos de salida
archivo_csv = os.path.join(dir_texto, 'traducciones.csv')
archivo_referencias = os.path.join(dir_texto, 'referencias.txt')

# Almacenar las extracciones
extracciones = []
referencias = []
id_counter = 1

# Expresión regular para buscar \"English\":\"...\"
# Captura el contenido entre las comillas escapadas
regex = re.compile(r'\\"English\\":\\"(.*?)\\"')

# Procesar cada archivo en el directorio 'ingles'
for filename in os.listdir(dir_ingles):
    if filename.endswith('.txt'):
        filepath = os.path.join(dir_ingles, filename)

        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()

                # Encontrar todas las coincidencias
                matches = regex.findall(content)

                for i, match in enumerate(matches):
                    # Generar un ID único
                    unique_id = f"{os.path.splitext(filename)[0]}_{i+1}"

                    # Guardar la extracción para el CSV
                    extracciones.append([unique_id, match])

                    # Guardar la referencia para el reemplazo posterior
                    # Formato: id|ruta_archivo|texto_original
                    referencias.append(f"{unique_id}|{filepath}|{match}")

        except Exception as e:
            print(f"Error procesando el archivo {filepath}: {e}")

# Escribir el archivo CSV
try:
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Texto Original'])
        writer.writerows(extracciones)
    print(f"Archivo CSV '{archivo_csv}' creado con éxito.")
except Exception as e:
    print(f"Error escribiendo el archivo CSV: {e}")

# Escribir el archivo de referencias
try:
    with open(archivo_referencias, 'w', encoding='utf-8') as f:
        for ref in referencias:
            f.write(ref + '\n')
    print(f"Archivo de referencias '{archivo_referencias}' creado con éxito.")
except Exception as e:
    print(f"Error escribiendo el archivo de referencias: {e}")
