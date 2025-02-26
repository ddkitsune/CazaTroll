# Importación de módulos necesarios
import secrets  # Módulo para generar números y cadenas aleatorias criptográficamente seguras
import string   # Módulo que contiene constantes de cadenas útiles (letras, dígitos, etc.)

# Creación de un alfabeto completo para la clave secreta:
# - string.ascii_letters: Todas las letras ASCII (a-z, A-Z)
# - string.digits: Dígitos del 0 al 9
# - string.punctuation: Caracteres de puntuación y símbolos especiales
alphabet = string.ascii_letters + string.digits + string.punctuation

# Generación de una clave secreta segura:
# - secrets.choice(alphabet): Selecciona un carácter aleatorio del alfabeto
# - for i in range(50): Repite el proceso 50 veces para crear una clave de 50 caracteres
# - ''.join(): Une todos los caracteres seleccionados en una sola cadena
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))

# Imprime la clave secreta generada en la consola
# Nota: En un entorno de producción, no se debe imprimir la clave secreta
# sino almacenarla de manera segura (por ejemplo, en variables de entorno)
print(secret_key)