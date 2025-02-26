# Importación de módulos necesarios
from flask import Flask, request, jsonify, render_template, session, redirect, url_for  # Flask para la aplicación web, request para manejar peticiones, jsonify para respuestas JSON, render_template para renderizar HTML, session para manejar sesiones, redirect para redirigir, url_for para generar URLs
from functools import wraps  # Para crear decoradores
from auth_service import DatabaseAuth  # Módulo personalizado para autenticación
from dotenv import load_dotenv  # Para cargar variables de entorno
import os  # Para interactuar con el sistema operativo

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Configura la clave secreta para las sesiones desde las variables de entorno
app.secret_key = os.getenv('SECRET_KEY')
# Instancia del servicio de autenticación
auth = DatabaseAuth()

# Decorador para proteger rutas que requieren autenticación
def login_required(f):
    @wraps(f)  # Preserva los metadatos de la función original
    def decorated_function(*args, **kwargs):
        # Verifica si el usuario está autenticado (user_id en sesión)
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401  # Respuesta 401 si no está autenticado
        return f(*args, **kwargs)  # Ejecuta la función original si está autenticado
    return decorated_function

# Ruta principal de la aplicación
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Aquí va la lógica para manejar el POST
        # ... procesar el formulario ...
        return redirect(url_for('index'))  # O redirige a donde necesites
    return render_template('index.html')

# Ruta para la página de login
@app.route('/login')
def login_page():
    return render_template('login.html')  # Renderiza la plantilla login.html

# Ruta para la página de registro
@app.route('/register')
def register_page():
    return render_template('register.html')  # Renderiza la plantilla register.html

# Ruta para la página de la tienda
@app.route('/store')
def store():
    return render_template('store.html')

# Ruta API para cerrar sesión
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Limpia todos los datos de la sesión
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})  # Respuesta JSON de éxito

# Ruta API para registro de usuarios
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    role_id = 2  # Todos los nuevos usuarios serán usuarios normales por defecto
    success, message = auth.register_user(
        username=data.get('username'),
        password=data.get('password'),
        email=data.get('email'),
        role_id=role_id
    )
    
    if success:
        session['role_id'] = role_id
        return jsonify({'success': True, 'message': message})
    
    return jsonify({'success': False, 'message': message})

# Ruta API para inicio de sesión
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    success, message = auth.login_user(
        username=data.get('username'),
        password=data.get('password')
    )
    
    if success:
        session['user_id'] = message['user_id']  # 'user_id' es el valor de 'id' de la base de datos
        session['role_id'] = message['role_id']
        print("Sesión después del login:", session)  # Imprime la sesión para depuración
        return jsonify({'success': True, 'message': 'Login exitoso'})
    
    return jsonify({'success': False, 'message': message})

# Ruta API para obtener todos los usuarios con más detalles (solo admin)
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if session.get('role_id') != 1:
        return jsonify({'error': 'No autorizado'}), 403
    success, message = auth.get_all_users()
    if success:
        return jsonify({'success': True, 'users': message})
    return jsonify({'success': False, 'message': message}), 400

# Ruta API para actualizar un usuario (solo admin)
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if session.get('role_id') != 1:
        return jsonify({'error': 'No autorizado'}), 403
    data = request.json
    success, message = auth.update_user(
        user_id=user_id,
        username=data.get('username'),
        email=data.get('email'),
        role_id=data.get('role_id')
    )
    return jsonify({'success': success, 'message': message})

# Ruta API para eliminar un usuario (solo admin)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if session.get('role_id') != 1:
        return jsonify({'error': 'No autorizado'}), 403
    success, message = auth.delete_user(user_id)
    return jsonify({'success': success, 'message': message})

# Ruta para la página de administración (solo admin)
@app.route('/admin')
@login_required
def admin_page():
    if session.get('role_id') != 1:  # Verifica si el usuario es admin
        return jsonify({'error': 'No autorizado'}), 403
    return render_template('admin.html')  # Renderiza la plantilla admin.html

# Ruta API para hacer admin a un usuario (solo admin)
@app.route('/api/users/<int:user_id>/make_admin', methods=['POST'])
@login_required
def make_admin(user_id):
    if session.get('role_id') != 1:  # Verifica si el usuario es admin
        return jsonify({'error': 'No autorizado'}), 403
    # Actualiza el rol del usuario a admin (role_id = 1)
    success, message = auth.update_user_role(user_id, 1)
    return jsonify({'success': success, 'message': message})  # Retorna el resultado

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# Punto de entrada de la aplicación
if __name__ == '__main__':
    app.run(debug=True)  # Inicia la aplicación en modo debug