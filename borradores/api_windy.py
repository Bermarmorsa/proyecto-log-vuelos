import requests

# Configuración de la URL y los datos
url = "https://api.windy.com/api/point-forecast/v2"

payload = {
    "lat": 49.809,
    "lon": 16.787,
    "model": "gfs",
    "parameters": ["wind", "dewpoint", "rh", "pressure"],
    "levels": ["surface", "800h", "300h"],
    "key": "zTkNFBUPHrEEbSSZ7ZQcjjuuHsur0UXn"  # Reemplaza con tu API Key real
}

try:
    # Realizamos la petición POST
    response = requests.post(url, json=payload)

    # Verificamos si la petición fue exitosa (código 200)
    response.raise_for_status()

    # Convertimos la respuesta a un diccionario de Python
    data = response.json()
    print("Datos recibidos con éxito:")
    print(data)

except requests.exceptions.HTTPError as err:
    print(f"Error en la petición: {err}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")