import logging


# 1. Creamos el logge
# r
logger = logging.getLogger("mi_app")
logger.setLevel(logging.DEBUG)

# 2. Definimos el formato que me pediste
formato = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 3. Handler para la CONSOLA (Pantalla)
consola = logging.StreamHandler()
consola.setFormatter(formato)

# 4. Handler para el ARCHIVO
archivo = logging.FileHandler('registro_programa.log')
archivo.setFormatter(formato)

# 5. Agregamos los manejadores al logger
logger.addHandler(consola)
logger.addHandler(archivo)
