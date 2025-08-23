import os
import csv

# Directorios
dir_texto = 'texto'
dir_traducido = 'traducido'

# Archivos de entrada
# El usuario deberá renombrar su archivo traducido a 'traducciones.csv'
# o modificar este nombre de archivo.
archivo_csv_traducido = os.path.join(dir_texto, 'traducciones.csv')
archivo_referencias = os.path.join(dir_texto, 'referencias.txt')

# Crear el directorio de salida si no existe
if not os.path.exists(dir_traducido):
    os.makedirs(dir_traducido)

# 1. Cargar las traducciones desde el CSV
traducciones = {}
try:
    with open(archivo_csv_traducido, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Omitir la cabecera
        # Asumimos que el formato es ID,Texto Original,Texto Traducido
        # Si el usuario solo edita la segunda columna, ajustamos aquí
        for row in reader:
            if len(row) >= 2:
                id_tr, texto_traducido = row[0], row[1]
                traducciones[id_tr] = texto_traducido
            # Si el usuario añade una tercera columna con la traducción
            if len(row) >= 3 and row[2]:
                 id_tr, texto_traducido = row[0], row[2]
                 traducciones[id_tr] = texto_traducido

except FileNotFoundError:
    print(f"Error: No se encontró el archivo de traducciones '{archivo_csv_traducido}'.")
    print("Asegúrese de haber guardado sus traducciones en ese archivo.")
    exit()
except Exception as e:
    print(f"Error leyendo el archivo CSV: {e}")
    exit()


# 2. Leer las referencias y procesar los archivos
try:
    with open(archivo_referencias, 'r', encoding='utf-8') as f:
        referencias = f.readlines()
except FileNotFoundError:
    print(f"Error: No se encontró el archivo de referencias '{archivo_referencias}'.")
    print("Asegúrese de haber ejecutado primero 'extractor.py'.")
    exit()
except Exception as e:
    print(f"Error leyendo el archivo de referencias: {e}")
    exit()

# Almacenar el contenido de los archivos para no leerlos múltiples veces
file_contents = {}

for ref in referencias:
    try:
        id_ref, filepath, texto_original = ref.strip().split('|', 2)

        # Si el contenido del archivo aún no se ha leído
        if filepath not in file_contents:
            with open(filepath, 'r', encoding='utf-8-sig') as f_orig:
                file_contents[filepath] = f_orig.read()

        # Obtener la traducción, si no existe, usar el original
        texto_traducido = traducciones.get(id_ref, texto_original)

        # Construir los patrones de búsqueda y reemplazo
        # "English":"Original" -> "English":"Traducido"
        patron_busqueda = f'"English":"{texto_original}"'
        patron_reemplazo = f'"English":"{texto_traducido}"'

        # Realizar el reemplazo en el contenido del archivo
        file_contents[filepath] = file_contents[filepath].replace(patron_busqueda, patron_reemplazo)

    except ValueError:
        print(f"Advertencia: Omitiendo línea mal formada en referencias: {ref.strip()}")
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo original '{filepath}' mencionado en las referencias.")
    except Exception as e:
        print(f"Error procesando la referencia '{ref.strip()}': {e}")


# 3. Escribir los nuevos archivos traducidos
for filepath, content in file_contents.items():
    try:
        # Crear el subdirectorio si es necesario (aunque en este caso no lo es)
        output_filename = os.path.basename(filepath)
        output_path = os.path.join(dir_traducido, output_filename)

        with open(output_path, 'w', encoding='utf-8-sig') as f_out:
            f_out.write(content)
        print(f"Archivo traducido '{output_path}' creado con éxito.")
    except Exception as e:
        print(f"Error escribiendo el archivo traducido para '{filepath}': {e}")
