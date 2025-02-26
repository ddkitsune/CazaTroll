# Importación de módulos necesarios
import psycopg2  # Para la conexión con PostgreSQL
from psycopg2 import Error  # Para manejar errores de PostgreSQL
import hashlib  # Para funciones de hash de contraseñas
import os  # Para generación de valores aleatorios
from datetime import datetime  # Para manejo de fechas
from dotenv import load_dotenv  # Para cargar variables de entorno
from flask import redirect, url_for, render_template

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class DatabaseAuth:
    """
    Clase para manejar la autenticación y gestión de usuarios en la base de datos.
    Proporciona métodos para registro, login, y gestión de usuarios.
    """
    
    def __init__(self):
        """
        Inicializa la clase con los parámetros de conexión a la base de datos.
        """
        self.connection_params = {
            "host": "localhost",  # Host de la base de datos
            "database": "CazaTroll",  # Nombre de la base de datos
            "user": "postgres",  # Usuario de la base de datos
            "password": "PanchoLaika4445.@",  # Contraseña del usuario
            "port": "5423"  # Puerto de conexión
        }

    def get_connection(self):
        """
        Establece y retorna una conexión con la base de datos.
        
        Returns:
            psycopg2.connection: Objeto de conexión a PostgreSQL
            None: Si ocurre un error al conectar
        """
        try:
            return psycopg2.connect(**self.connection_params)
        except Error as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            return None

    def hash_password(self, password):
        """
        Genera un hash seguro de la contraseña usando PBKDF2 con SHA-256.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña en formato hexadecimal
        """
        salt = os.urandom(32)  # Genera una sal aleatoria
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Algoritmo de hash
            password.encode('utf-8'),  # Contraseña codificada
            salt,  # Sal generada
            100000  # Número de iteraciones
        )
        return salt.hex() + key.hex()  # Combina sal y hash en un solo string

    def verify_password(self, stored_password, provided_password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        
        Args:
            stored_password (str): Hash almacenado de la contraseña
            provided_password (str): Contraseña proporcionada por el usuario
            
        Returns:
            bool: True si las contraseñas coinciden, False si no
        """
        stored_bytes = bytes.fromhex(stored_password)  # Convierte el hash a bytes
        salt = stored_bytes[:32]  # Extrae la sal (primeros 32 bytes)
        key = stored_bytes[32:]  # Extrae el hash (resto de los bytes)

        # Calcula el hash de la contraseña proporcionada
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            100000
        )
        return new_key == key  # Compara los hashes

    def register_user(self, username, password, email, role_id=2):
        """
        Registra un nuevo usuario en la base de datos.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña en texto plano
            email (str): Correo electrónico
            role_id (int, optional): ID del rol del usuario. Default es 2
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            
            # Verifica si el usuario ya existe
            cursor.execute("SELECT username FROM users WHERE username = %s OR email = %s", 
                         (username, email))
            if cursor.fetchone():
                return False, "El usuario o email ya existe"

            # Genera el hash de la contraseña
            password_hash = self.hash_password(password)

            # Inserta el nuevo usuario
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, email, role_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (username, password_hash, email, role_id)
            )
            
            user_id = cursor.fetchone()[0]
            connection.commit()
            return True, f"Usuario registrado exitosamente con ID: {user_id}"

        except Error as e:
            return False, f"Error al registrar usuario: {e}"
        finally:
            connection.close()

    def login_user(self, username, password):
        """
        Autentica a un usuario verificando sus credenciales.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña en texto plano
            
        Returns:
            tuple: (success: bool, message: str/dict)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            
            # Obtiene la información del usuario
            cursor.execute(
                "SELECT id, password_hash, role_id FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()

            if not result:
                return False, "Usuario no encontrado"

            user_id, stored_password, role_id = result

            # Verifica la contraseña
            if not self.verify_password(stored_password, password):
                return False, "Contraseña incorrecta"

            # Actualiza la fecha del último login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(), user_id)
            )
            
            connection.commit()
            return True, {'user_id': user_id, 'role_id': role_id}

        except Error as e:
            return False, f"Error durante el login: {e}"
        finally:
            connection.close()

    def get_all_users(self):
        """
        Obtiene todos los usuarios registrados en la base de datos.
        
        Returns:
            tuple: (success: bool, message: list/str)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, username, email, role_id FROM users"
            )
            users = cursor.fetchall()
            # Convertimos el resultado en una lista de diccionarios
            users_list = [
                {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'role_id': user[3]
                }
                for user in users
            ]
            return True, users_list
        except Error as e:
            return False, f"Error al obtener usuarios: {e}"
        finally:
            connection.close()

    def update_user_role(self, user_id, role_id):
        """
        Actualiza el rol de un usuario específico.
        
        Args:
            user_id (int): ID del usuario
            role_id (int): Nuevo ID de rol
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET role_id = %s WHERE id = %s",
                (role_id, user_id)
            )
            connection.commit()
            return True, "Rol actualizado correctamente"
        except Error as e:
            return False, f"Error al actualizar el rol: {e}"
        finally:
            connection.close()

    def delete_user(self, user_id):
        """
        Elimina un usuario de la base de datos.
        
        Args:
            user_id (int): ID del usuario a eliminar
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            connection.commit()
            return True, "Usuario eliminado correctamente"
        except Error as e:
            return False, f"Error al eliminar el usuario: {e}"
        finally:
            connection.close()

    def update_user(self, user_id, username=None, email=None, role_id=None):
        """
        Actualiza la información de un usuario específico.
        
        Args:
            user_id (int): ID del usuario
            username (str, optional): Nuevo nombre de usuario
            email (str, optional): Nuevo correo electrónico
            role_id (int, optional): Nuevo ID de rol
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self.get_connection()
        if not connection:
            return False, "Error de conexión a la base de datos"

        try:
            cursor = connection.cursor()
            updates = []
            params = []
            
            if username:
                updates.append("username = %s")
                params.append(username)
            if email:
                updates.append("email = %s")
                params.append(email)
            if role_id:
                updates.append("role_id = %s")
                params.append(role_id)
                
            if not updates:
                return False, "No se proporcionaron datos para actualizar"
                
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            connection.commit()
            return True, "Usuario actualizado correctamente"
        except Error as e:
            return False, f"Error al actualizar el usuario: {e}"
        finally:
            connection.close()

# Ejemplo de uso
if __name__ == "__main__":
    auth = DatabaseAuth()

    # Ejemplo de registro
    success, message = auth.register_user(
        username="usuario_prueba",
        password="contraseña123",
        email="usuario@ejemplo.com"
    )
    print(f"Registro: {message}")

    # Ejemplo de login
    success, message = auth.login_user(
        username="usuario_prueba",
        password="contraseña123"
    )
    print(f"Login: {message}")

    