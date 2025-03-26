import os

# La ruta de la base de datos que estás usando en tu código
RUTA = r'C:\Users\Santi\Documents\santi\Gymbot(DEV)\gym.db'

# Imprimir la ruta absoluta para asegurarnos de que estamos apuntando al archivo correcto
print(f"Ruta absoluta de la base de datos: {os.path.abspath(RUTA)}")

# Verifica si el archivo existe
if os.path.exists(RUTA):
    print(f"El archivo {RUTA} existe.")
else:
    print(f"El archivo {RUTA} NO existe.")
