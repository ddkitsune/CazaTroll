# Importación de módulos necesarios
import psycopg2  # Módulo para conectarse a PostgreSQL
from psycopg2 import Error  # Para manejar errores específicos de PostgreSQL

def test_database_connection():
    """
    Función para probar la conexión a la base de datos PostgreSQL.
    Realiza las siguientes acciones:
    1. Intenta conectarse a la base de datos
    2. Obtiene y muestra la versión de PostgreSQL
    3. Cuenta y muestra el número de usuarios en la tabla 'users'
    4. Maneja posibles errores durante la conexión
    5. Cierra la conexión de manera segura
    """
    try:
        # Establecer conexión con la base de datos
        connection = psycopg2.connect(
            host="localhost",  # Host donde está alojada la base de datos
            database="CazaTroll",  # Nombre de la base de datos
            user="postgres",  # Usuario de la base de datos
            password="PanchoLaika4445.@",  # Contraseña del usuario
            port="5423"  # Puerto de conexión
        )
        
        # Crear un cursor para ejecutar consultas SQL
        cursor = connection.cursor()
        
        # Obtener y mostrar la versión de PostgreSQL
        cursor.execute("SELECT version();")  # Ejecuta consulta SQL
        db_version = cursor.fetchone()  # Obtiene la primera fila del resultado
        print("Conectado a PostgreSQL. Versión:", db_version)

        # Contar y mostrar el número de usuarios en la tabla 'users'
        cursor.execute("SELECT COUNT(*) FROM users;")  # Ejecuta consulta de conteo
        user_count = cursor.fetchone()  # Obtiene el resultado del conteo
        print(f"Número de usuarios en la base de datos: {user_count[0]}")

    except (Exception, Error) as error:
        # Manejo de errores durante la conexión o ejecución de consultas
        print("Error mientras se conectaba a PostgreSQL:", error)
    finally:
        # Bloque que siempre se ejecuta, asegurando el cierre de la conexión
        if connection:
            cursor.close()  # Cierra el cursor
            connection.close()  # Cierra la conexión
            print("Conexión a PostgreSQL cerrada.")

# Punto de entrada principal del script
if __name__ == "__main__":
    test_database_connection()  # Ejecuta la función de prueba de conexión