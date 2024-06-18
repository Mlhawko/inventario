
from functools import wraps
import io
import os
import pyodbc
from flask import Flask, flash, make_response, redirect, render_template, request, send_file, session, url_for, send_from_directory, jsonify
import datetime
from werkzeug.utils import secure_filename
from waitress import serve
from fpdf import FPDF
from openpyxl import Workbook
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet






app = Flask(__name__)

app.config['SECRET_KEY'] = 'chf24'
app.config['DEBUG'] = True




#---------------------------------------------------------

server = 'CHFNB239\\SQLEXPRESS'
db = 'TestDB'
user = 'sa'
password = 'Chilefilms23'

###
#Conexion a base de datos-------------------------------
try:
    conexion = pyodbc.connect(
        'DRIVER={ODBC DRIVER 17 FOR SQL server};SERVER=' + server + ';DATABASE=' + db + 
        ';UID=' + user + ';PWD=' + password
    )
    print('Conexión exitosa')
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(sqlstate)
    print ('Error al intentar conectarse')

#------------------------------
def obtener_conexion():

    try:
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={db};'
            f'UID={user};'
            f'PWD={password}'
        )
        return conexion
    except pyodbc.Error as ex:
        print(f"Error al intentar conectarse: {ex}")
        return None
############################################################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Por favor, inicie sesión para acceder a esta página.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(email, password):
    hashed_password = hash_password(password)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE usuarios_correo = ? AND usuarios_contraseña = ?", (email, hashed_password))
    user = cursor.fetchone()
    conexion.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        user = validate_user(correo, contraseña)


        if user:
            session['user_email'] = user.usuarios_correo
            session['user_nombre'] = user.usuarios_nombre
            session['user_ap_paterno'] = user.usuarios_ap_paterno
            session['user_ap_materno'] = user.usuarios_ap_materno
            session['login_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            flash(f'Bienvenido {user.usuarios_nombre} {user.usuarios_ap_paterno} {user.usuarios_ap_materno}')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index', welcome_message=f'Bienvenido {user.usuarios_nombre} {user.usuarios_ap_paterno} {user.usuarios_ap_materno}'))
        else:
            flash('Correo electrónico o contraseña incorrectos.')
    return render_template('login.html', current_date=session.get('current_date'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))




#################################################


def verificar_duplicado(tabla, columnas_valores):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            raise Exception("No se pudo conectar a la base de datos")

        cursor = conexion.cursor()
        
        # Crear la parte de la consulta que compara las columnas y valores
        condiciones = " AND ".join([f"{columna} = ?" for columna in columnas_valores.keys()])
        query = f"SELECT COUNT(1) FROM {tabla} WHERE {condiciones}"
        
        cursor.execute(query, tuple(columnas_valores.values()))
        resultado = cursor.fetchone()
        
        return resultado[0] > 0
    except Exception as e:
        print(f"Error al verificar duplicado: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def verificar_duplicado_persona(nombres, apellidos, correo, id=None):
    cursor = conexion.cursor()
    query_comb = "SELECT COUNT(*) FROM persona WHERE nombres = ? AND apellidos = ? AND correo = ?"
    params_comb = [nombres, apellidos, correo]
    if id:
        query_comb += " AND id != ?"
        params_comb.append(id)
    
    cursor.execute(query_comb, params_comb)
    count_comb = cursor.fetchone()[0]
    
    query_email = "SELECT COUNT(*) FROM persona WHERE correo = ?"
    params_email = [correo]
    if id:
        query_email += " AND id != ?"
        params_email.append(id)
    
    cursor.execute(query_email, params_email)
    count_email = cursor.fetchone()[0]

    cursor.close()
    
    return count_comb > 0, count_email > 0

#---------------------------------------------------------
# Index mostrar personas
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    welcome_message = request.args.get('welcome_message', '')

    cursor = conexion.cursor()
    try:
        search_term = request.form.get('search_term', '')

        query ='''
            SELECT DISTINCT
                persona.id,
                persona.nombres,
                persona.apellidos,
                persona.correo,
                persona.rut,
                persona.dv,
                area.nombre AS area_nombre,
                tipoequipo.nombre AS tipo_nombre,
                ISNULL(unidad.nombre_e, '') AS nombre_unidad,
                ISNULL(celular.nombre, '') AS nombre_celular,
                equipo.id AS equipo_id
            FROM
                persona
            INNER JOIN
                area ON persona.area_id = area.id
            LEFT JOIN
                asignacion_equipo ON persona.id = asignacion_equipo.persona_id
            LEFT JOIN
                equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN
                unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN
                celular ON equipo.celular_id = celular.id
            LEFT JOIN
                tipoequipo ON equipo.tipoequipo_id = tipoequipo.id

            WHERE
                equipo.estadoequipo_id = 2 AND asignacion_equipo.fecha_devolucion IS NULL
                    AND (
                                persona.nombres LIKE ? OR
                                persona.apellidos LIKE ? OR
                                persona.correo LIKE ? OR
                                persona.rut LIKE ? OR
                                area.nombre LIKE ? OR
                                tipoequipo.nombre LIKE ? OR
                                unidad.nombre_e LIKE ? OR
                                celular.nombre LIKE ?
                            )
                '''

        cursor.execute(query, ('%' + search_term + '%',) * 8)  # Aplicar el término de búsqueda a cada campo


        rows = cursor.fetchall()
        cursor.close()

        personas = {}
        for row in rows:
            persona_id = row.id
            if persona_id not in personas:
                personas[persona_id] = {
                    'id': row.id,
                    'nombres': row.nombres,
                    'apellidos': row.apellidos,
                    'correo': row.correo,
                    'rut': row.rut,
                    'dv': row.dv,
                    'area_nombre': row.area_nombre,
                    'equipos_asignados': []
                }
            equipo_id = row.equipo_id
            equipo = {
                'equipo_id': row.equipo_id,
                'nombre': row.nombre_unidad if row.nombre_unidad else row.nombre_celular,
                'tipoequipo': row.tipo_nombre
            }
            if equipo['nombre']:
                personas[persona_id]['equipos_asignados'].append(equipo)

        return render_template('index.html', personas=list(personas.values()), search_term=search_term, welcome_message=welcome_message, login_time=session.get('login_time'),persona_id=persona_id, equipo_id=equipo_id)
    except pyodbc.Error as ex:
        print('Error al obtener los datos: {ex}')
        flash('Error al cargar la página de asignación', 'error')
        return redirect(url_for('index'))
#--------------------------------------------------------
# CRUD Persona
@app.route('/listar_personas', methods=['GET', 'POST'])
@login_required
def listar_personas():
    search_term = request.args.get('search_term', '')
    try:
        cursor = conexion.cursor()
        query = '''
            SELECT persona.id, persona.nombres, persona.apellidos, persona.correo, area.nombre AS area_nombre
            FROM persona
            INNER JOIN area ON persona.area_id = area.id
            WHERE persona.nombres LIKE ? OR persona.apellidos LIKE ? OR persona.correo LIKE ? OR area.nombre LIKE ?
        '''
        search_term_wildcard = '%' + search_term + '%'
        cursor.execute(query, (search_term_wildcard, search_term_wildcard, search_term_wildcard, search_term_wildcard))
        personas = cursor.fetchall()
        cursor.close()
        return render_template('listar_personas.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)
        return "Error en la consulta de la base de datos"


@app.route('/agregar_persona', methods=['GET', 'POST'])
@login_required
def agregar_persona():
    areas = obtener_areas()

    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        rut = request.form['rut']
        dv = request.form['dv']
        area_id = request.form['area']

        try:
            is_duplicate_comb, is_duplicate_email = verificar_duplicado_persona(nombres, apellidos, correo)
            
            if is_duplicate_comb:
                flash('La combinación de nombre, apellido y correo ya existe en la base de datos', 'error')
                return render_template('agregar_persona.html', nombres=nombres, apellidos=apellidos, correo=correo, rut=rut, dv=dv, area_id=area_id, areas=areas)
            
            if is_duplicate_email:
                flash('El correo ya existe en la base de datos', 'error')
                return render_template('agregar_persona.html', nombres=nombres, apellidos=apellidos, correo=correo, rut=rut, dv=dv, area_id=area_id, areas=areas)

            cursor = conexion.cursor()
            cursor.execute("INSERT INTO persona (nombres, apellidos, correo, rut, dv, area_id) VALUES (?, ?, ?, ?, ?, ?)",
                           (nombres, apellidos, correo, rut, dv, area_id))
            conexion.commit()
            cursor.close()
            return redirect(url_for('listar_personas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al agregar la persona', 'error')
            return render_template('agregar_persona.html', nombres=nombres, apellidos=apellidos, correo=correo, rut=rut, dv=dv, area_id=area_id, areas=areas)

    return render_template('agregar_persona.html', areas=areas)


@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_persona(id):
    if request.method == 'POST':
        # Obtener datos del formulario
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        rut = request.form['rut']
        dv = request.form['dv']
        area_id = request.form['area']

        try:

            cursor = conexion.cursor()
            cursor.execute("UPDATE persona SET nombres=?, apellidos=?, correo=?, rut=?, dv=?, area_id=? WHERE id=?",
                           (nombres, apellidos, correo, rut, dv, area_id, id))
            conexion.commit()
            cursor.close()
            return redirect(url_for('listar_personas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al actualizar los datos de la persona', 'error')
            return redirect(url_for('editar_persona', id=id))

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM persona WHERE id=?", (id,))
        persona = cursor.fetchone()
        areas = obtener_areas()
        cursor.close()
        return render_template('editar_persona.html', persona=persona, areas=areas)
    except pyodbc.Error as ex:
        print(ex)
        flash('Ocurrió un error al obtener los datos de la persona', 'error')
        return redirect(url_for('listar_personas'))





@app.route('/eliminar_persona/<int:id>', methods=['POST'])
@login_required
def eliminar_persona(id):
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM persona WHERE id = ?", (id,))
        conexion.commit()
        cursor.close()
    except pyodbc.Error as ex:
        print(ex)
    return redirect(url_for('listar_personas'))

#--------------------------------------------------------
#Barra de busqueda
@app.route('/buscar_personas')
def buscar_personas():
    q = request.args.get('q', '')
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT * FROM Persona
            WHERE nombres LIKE ? OR correo LIKE ? OR area LIKE ?
        ''', ('%' + q + '%', '%' + q + '%', '%' + q + '%'))
        personas = cursor.fetchall()
        cursor.close()
        return render_template('index.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)
        return 'Error al buscar personas'
#----------------------------------------
# CRUD de equipos:
@app.route('/mostrar_equipos')
@login_required
def mostrar_equipos():
    search_term = request.args.get('search_term', '')
    try:
        cursor = conexion.cursor()
        query = """
        SELECT
            equipo.id,
            estadoequipo.nombre AS estado_nombre,
            tipoequipo.nombre AS tipo_nombre,
            COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
        FROM equipo
        LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
        LEFT JOIN unidad ON equipo.unidad_id = unidad.id
        LEFT JOIN celular ON equipo.celular_id = celular.id
        LEFT JOIN estadoequipo ON equipo.estadoequipo_id = estadoequipo.id
        WHERE
            estadoequipo.nombre LIKE ? OR
            tipoequipo.nombre LIKE ? OR
            unidad.nombre_e LIKE ? OR
            celular.nombre LIKE ?
        """
        search_term_wildcard = '%' + search_term + '%'
        cursor.execute(query, (search_term_wildcard, search_term_wildcard, search_term_wildcard, search_term_wildcard))
        equipos = cursor.fetchall()
        cursor.close()
        return render_template('mostrar_equipos.html', equipos=equipos)
    except pyodbc.Error as ex:
        print('Error al obtener los equipos: {ex}')
        flash('Error al obtener los equipos', 'error')
        return redirect(url_for('index'))

#------------------------------------------------------------
#Obtener tipos de equipo
def obtener_tipos_equipo():
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM tipoequipo')
    tipos_equipo = cursor.fetchall()
    return tipos_equipo
#------------------------------------------------------------
#Obtener estados
def obtener_estado():
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM estadoequipo')
    estado_equipo = cursor.fetchall()
    return estado_equipo
#------------------------------------------------------------

@app.route('/agregar_equipo', methods=['GET', 'POST'])
@login_required
def agregar_equipo():
    tipos_equipos = obtener_tipos_equipo()

    if request.method == 'POST':
        tipo_equipo = request.form.get('tipo_equipo')
        tipo_equipo_id, tipo_equipo_nombre = tipo_equipo.split('_')
        observaciones = request.form.get('observaciones', '')

        nombre = request.form.get('nombre', '').upper()
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        serial = request.form.get('serial', '')

        try:
            # Verificar si el nombre del equipo ya existe en la tabla 'Unidad'
            if verificar_duplicado('Unidad', {'nombre_e': nombre}):
                flash('El nombre del equipo ya existe en la base de datos', 'error')
                return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos, form_data=request.form)

            # Verificar si el nombre del equipo ya existe en la tabla 'Celular'
            if verificar_duplicado('Celular', {'nombre': nombre}):
                flash('El nombre del equipo ya existe en la base de datos', 'error')
                return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos, form_data=request.form)

            if tipo_equipo_nombre in ['notebook', 'pc', 'mac']:
                ram = request.form.get('ram', '')
                procesador = request.form.get('procesador', '')
                almc = request.form.get('almc', '')
                perif = request.form.get('perif', '')
                numsello = request.form.get('numsello', '')
                numproducto = request.form.get('numproducto', '')
                insertar_equipo(nombre, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, None, None, observaciones, tipo_equipo_id)

            elif tipo_equipo_nombre == 'monitor':
                numproducto = request.form.get('numproducto', '')
                insertar_equipo(nombre, marca, modelo, None, None, None, None, None, serial, numproducto, None, None, observaciones, tipo_equipo_id)

            elif tipo_equipo_nombre == 'impresora':
                tipoimpresion = request.form.get('tipoimpresion', '')
                insertar_equipo(nombre, marca, modelo, None, None, None, None, None, serial, None, tipoimpresion, None, observaciones, tipo_equipo_id)

            elif tipo_equipo_nombre == 'celular':
                imei1 = request.form.get('imei1', '')
                imei2 = request.form.get('imei2', '')
                insertar_celular(nombre, marca, modelo, imei1, imei2, serial, None, observaciones, tipo_equipo_id)

            elif tipo_equipo_nombre == 'accesorios':
                cantidad = request.form.get('cantidad', '')
                insertar_equipo(nombre, marca, modelo, None, None, None, None, None, serial, None, None, cantidad, observaciones, tipo_equipo_id)

            elif tipo_equipo_nombre == 'simcard':
                imei1 = request.form.get('imei1', '')
                ntelefono = request.form.get('ntelefono', '')
                insertar_celular(imei1, None, None, imei1, None, None, ntelefono, observaciones, tipo_equipo_id)
            
            else:
                insertar_equipo(nombre, marca, modelo, None, None, None, None, None, serial, None, None, None, observaciones, tipo_equipo_id)

            return redirect(url_for('mostrar_equipos'))

        except Exception as e:
            flash('Ocurrió un error al agregar el equipo: {str(e)}', 'error', 'agregar_equipo_error')
            print(e)
            return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos, form_data=request.form)

    return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos)





def insertar_equipo(nombre, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion, cantidad, observaciones, tipo_equipo_id):
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO unidad (nombre_e, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion, cantidad) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nombre, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion, cantidad))
        conexion.commit()
        cursor.execute("SELECT @@IDENTITY")
        unidad_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO equipo (estadoequipo_id, unidad_id, fcreacion, tipoequipo_id, observaciones) VALUES (?, ?, ?, ?, ?)",
                       (1, unidad_id, datetime.datetime.now(), tipo_equipo_id, observaciones))
        conexion.commit()
        cursor.close()
    except Exception as e:
        print("Error al insertar equipo:", e)

def insertar_celular(nombre, marca, modelo, imei1, imei2, serial, ntelefono, observaciones, tipo_equipo_id):
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO celular (nombre, marca, modelo, imei1, imei2, serial, ntelefono) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (nombre, marca, modelo, imei1, imei2, serial, ntelefono))
    conexion.commit()
    cursor.execute("SELECT @@IDENTITY")
    celular_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO equipo (estadoequipo_id, celular_id, fcreacion, tipoequipo_id, observaciones) VALUES (?, ?, ?, ?, ?)",
                   (1, celular_id, datetime.datetime.now(), tipo_equipo_id, observaciones))
    conexion.commit()
    cursor.close()

#---------------------------------------------------
#Editar equipo:
@app.route('/editar_equipo/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_equipo(id):
    detalle_equipo = None

    if request.method == 'GET':
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM equipo WHERE id = ?", (id,))
            equipo = cursor.fetchone()

            if equipo:
                equipo_dict = dict(zip((column[0] for column in cursor.description), equipo))
                detalle_equipo = None
                if equipo_dict['unidad_id'] is not None:
                    cursor.execute("SELECT equipo.*, unidad.* FROM equipo INNER JOIN unidad ON equipo.unidad_id = unidad.id WHERE equipo.id = ?", (id,))
                    detalle_equipo = cursor.fetchone()
                    tipo_equipo = 'unidad'
                elif equipo_dict['celular_id'] is not None:
                    cursor.execute("SELECT equipo.*, celular.* FROM equipo INNER JOIN celular ON equipo.celular_id = celular.id WHERE equipo.id = ?", (id,))
                    detalle_equipo = cursor.fetchone()
                    tipo_equipo = 'celular'

                estados = obtener_estados_equipo()

                return render_template('editar_equipo.html', equipo=equipo_dict, detalle_equipo=detalle_equipo,
                                       estados=estados, tipo_equipo=tipo_equipo)
            else:
                flash('No se encontró ningún equipo con el ID proporcionado', 'error')
                return redirect(url_for('mostrar_equipos'))

        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al cargar la información del equipo', 'error')
            return redirect(url_for('mostrar_equipos'))

        finally:
            cursor.close()

    elif request.method == 'POST':
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM equipo WHERE id = ?", (id,))
            equipo = cursor.fetchone()

            if equipo:
                
                equipo_dict = dict(zip((column[0] for column in cursor.description), equipo))

                nombre = request.form.get('nombre', equipo_dict.get('nombre', ''))
                marca = request.form.get('marca', equipo_dict.get('marca', ''))
                modelo = request.form.get('modelo', equipo_dict.get('modelo', ''))
                serial = request.form.get('serial', equipo_dict.get('serial', ''))
                observaciones = request.form['observaciones']

                
                if 'unidad_id' in equipo_dict and equipo_dict['unidad_id'] is not None:
                    cursor.execute(
                        "UPDATE unidad SET nombre_e = ?, marca = ?, modelo = ?, serial = ?, ram = ?, procesador = ?, almc = ?, perif = ?, numsello = ?, numproducto = ?, tipoimpresion = ?, cantidad = ? WHERE id = ?",
                        (nombre, marca, modelo, serial, request.form.get('ram', ''), request.form.get('procesador', ''),
                         request.form.get('almc', ''), request.form.get('perif', ''), request.form.get('numsello', ''),
                         request.form.get('numproducto', ''), request.form.get('tipoimpresion', ''),
                         request.form.get('cantidad', ''), equipo_dict['unidad_id']))
                elif 'celular_id' in equipo_dict and equipo_dict['celular_id'] is not None:
                    cursor.execute(
                        "UPDATE celular SET nombre = ?, marca = ?, modelo = ?, serial = ?, imei1 = ?, imei2 = ?, ntelefono = ? WHERE id = ?",
                        (nombre, marca, modelo, serial, request.form.get('imei1', ''), request.form.get('imei2', ''),
                         request.form.get('ntelefono', ''), equipo_dict['celular_id']))

                cursor.execute("UPDATE equipo SET observaciones = ? WHERE id = ?",
                               (observaciones, id))

                conexion.commit()
                cursor.close()

                
                return redirect(url_for('mostrar_equipos'))
            else:
                
                return redirect(url_for('mostrar_equipos'))

        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al intentar actualizar la información del equipo', 'error')
            return redirect(url_for('mostrar_equipos'))

    else:
        flash('Método HTTP no permitido', 'error')
        return redirect(url_for('mostrar_equipos'))

#-------------------------------------------------------
#Funcion Eliminar equipo
@app.route('/eliminar_equipo/<int:id>', methods=['POST'])
@login_required
def eliminar_equipo(id):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conexion.cursor()
        print(f"Conexión obtenida, eliminando equipo con ID: {id}")

        # Primero, obtenemos los IDs relacionados en unidad y celular
        cursor.execute("SELECT unidad_id, celular_id FROM equipo WHERE id = ?", (id,))
        equipo = cursor.fetchone()
        
        if equipo:
            unidad_id, celular_id = equipo

            # Eliminamos los registros relacionados en unidad y celular si existen
            if unidad_id:
                cursor.execute("DELETE FROM unidad WHERE id = ?", (unidad_id,))
            if celular_id:
                cursor.execute("DELETE FROM celular WHERE id = ?", (celular_id,))

            # Luego, eliminamos el registro de la tabla equipo
            cursor.execute("DELETE FROM equipo WHERE id = ?", (id,))
            conexion.commit()

            print(f"Equipo con ID: {id} eliminado correctamente")
            flash('El equipo ha sido eliminado correctamente', 'success')
        else:
            print(f"No se encontró el equipo con ID: {id}")
            flash('No se encontró el equipo a eliminar', 'error')

    except pyodbc.Error as ex:
        if conexion:
            conexion.rollback()  # Revertir los cambios en caso de error
        print(f"Error al eliminar el equipo: {ex}")
        flash('Ocurrió un error al eliminar el equipo', 'error')
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
    
    return redirect(url_for('mostrar_equipos'))


#--------------------------------------------------
# Obtener estados
def obtener_estados_equipo():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM estadoequipo")
        estequipos = cursor.fetchall()
        cursor.close()
        return estequipos
    except pyodbc.Error as ex:
        print(ex)
        return None
#---------------------------------------------------
#CRUD Area

@app.route('/listar_areas', methods=['GET', 'POST'])
@login_required
def listar_areas():
    if request.method == 'GET':
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM area')
            areas = cursor.fetchall()
            cursor.close()
            return render_template('listar_areas.html', areas=areas)
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al listar las áreas', 'error')
            return redirect(url_for('index'))
    elif request.method == 'POST':
        id_area = request.form.get('id_area')
        nombre = request.form.get('nombre')
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE area SET nombre = ? WHERE id = ?", (nombre, id_area))
            conexion.commit()
            cursor.close()
            flash('Área actualizada correctamente', 'success')
        except pyodbc.Error as ex:
            print(ex)
            flash('Error al actualizar el área', 'error')
        return redirect(url_for('listar_areas'))

@app.route('/crear_area', methods=['GET', 'POST'])
@login_required
def crear_area():
    if request.method == 'POST':
        nombre = request.form['nombre']
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO area (nombre) VALUES (?)", (nombre,))
            conexion.commit()
            cursor.close()
            flash('Área creada correctamente', 'success')
            return redirect(url_for('listar_areas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Error al crear el área', 'error')
            return redirect(url_for('listar_areas'))
    return render_template('listar_areas.html')


@app.route('/eliminar_area/<int:id>', methods=['POST'])
@login_required
def eliminar_area(id):
    if request.method == 'POST':
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM area WHERE id = ?", (id,))
            conexion.commit()
            cursor.close()
            flash('Área eliminada correctamente', 'success')
            return redirect(url_for('listar_areas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Error al eliminar el área', 'error')
            return redirect(url_for('listar_areas'))
    return 'Método no permitido'
#-----------------------------------------------------------------
#CRUD TIPOS
@app.route('/crud_tipos_equipos', methods=['GET', 'POST'])
@login_required
def crud_tipos_equipos():
    if request.method == 'POST':
        if 'agregar' in request.form:
            # Agregar un nuevo tipo de equipo
            nombre = request.form['nombre']
            if nombre:
                try:
                    cursor = conexion.cursor()
                    cursor.execute("INSERT INTO tipoequipo (nombre) VALUES (?)", (nombre,))
                    conexion.commit()
                    cursor.close()
                    flash('El tipo de equipo ha sido agregado correctamente', 'success')
                except pyodbc.Error as ex:
                    print(ex)
                    flash('Ocurrió un error al agregar el tipo de equipo', 'error')
            else:
                flash('Por favor, ingrese un nombre para el tipo de equipo', 'error')
        elif 'eliminar' in request.form:
            tipo_equipo_id = request.form.get('eliminar')
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM tipoequipo WHERE id = ?", (tipo_equipo_id,))
                conexion.commit()
                cursor.close()
                flash('El tipo de equipo ha sido eliminado correctamente', 'success')
            except pyodbc.Error as ex:
                print(ex)
                flash('Ocurrió un error al eliminar el tipo de equipo', 'error')
        elif 'editar' in request.form:
            tipo_equipo_id = request.form['editar']
            nuevo_nombre = request.form['nombre_editado']
            if nuevo_nombre:
                try:
                    cursor = conexion.cursor()
                    cursor.execute("UPDATE tipoequipo SET nombre = ? WHERE id = ?", (nuevo_nombre, tipo_equipo_id))
                    conexion.commit()
                    cursor.close()
                    flash('El tipo de equipo ha sido actualizado correctamente', 'success')
                except pyodbc.Error as ex:
                    print(ex)
                    flash('Ocurrió un error al actualizar el tipo de equipo', 'error')
            else:
                flash('Por favor, ingrese un nuevo nombre para el tipo de equipo', 'error')

    tipos_equipos = obtener_tipos_equipo()

    return render_template('crud_tipos_equipos.html', tipos_equipos=tipos_equipos)

#--------------------------------------------------------------------------------
# Obtener areas
def obtener_areas():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM area")
        areas = cursor.fetchall()
        cursor.close()
        return areas
    except pyodbc.Error as ex:
        print(ex)
        return None

#----------------------------------------------------------
#Asignar equipo

@app.route('/asignar_equipo', methods=['GET', 'POST'])
@login_required
def asignar_equipo():
    cursor = conexion.cursor()

    if request.method == 'POST':
        equipo_ids = request.form.getlist('equipo_id[]')
        persona_id = request.form['persona_id']
        fecha_asignacion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        observaciones = request.form['observaciones']
        archivo_pdf = request.files['archivo_pdf']

        print("Equipo IDs recibidos:", equipo_ids)  # Depuración

        # Verificación de duplicados en el backend
        if len(equipo_ids) != len(set(equipo_ids)):
            flash('No se pueden asignar equipos duplicados.', 'error')
            return redirect(url_for('asignar_equipo', persona_id=persona_id))

        # Verificar que el archivo es un PDF
        if archivo_pdf and archivo_pdf.filename.endswith('.pdf'):
            filename = f"{persona_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo_pdf.save(filepath)

            try:
                for equipo_id in equipo_ids:
                    if not equipo_id:  # Verificar que equipo_id no esté vacío
                        flash('Todos los campos de equipo deben estar seleccionados.', 'error')
                        return redirect(url_for('asignar_equipo', persona_id=persona_id))

                    # Verificar que el equipo_id existe en la tabla equipo
                    cursor.execute("SELECT COUNT(*) FROM equipo WHERE id = ?", (equipo_id,))
                    equipo_existe = cursor.fetchone()[0]
                    
                    if equipo_existe == 0:
                        flash(f'El equipo con ID {equipo_id} no existe.', 'error')
                        return redirect(url_for('asignar_equipo', persona_id=persona_id))

                    # Inserción en asignacion_equipo
                    cursor.execute("""
                        INSERT INTO asignacion_equipo (equipo_id, persona_id, fecha_asignacion, observaciones, archivo_pdf)
                        VALUES (?, ?, ?, ?, ?)
                    """, (equipo_id, persona_id, fecha_asignacion, observaciones, filename))
                    conexion.commit()

                    # Actualización del estado del equipo
                    cursor.execute("UPDATE equipo SET estadoequipo_id = 2 WHERE id = ?", (equipo_id,))
                    conexion.commit()

                flash('Equipos asignados correctamente', 'success')
                return redirect(url_for('index'))
            except pyodbc.Error as ex:
                print(f'Error al asignar el equipo: {ex}')
                flash('Error al asignar los equipos', 'error')
                return redirect(url_for('index'))
            finally:
                cursor.close()
        else:
            flash('El archivo debe ser un PDF', 'error')
            return redirect(url_for('asignar_equipo', persona_id=persona_id))

    else:
        try:
            cursor.execute("""
            SELECT
                equipo.id AS equipo_id,
                tipoequipo.nombre AS tipo_nombre,
                COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
            FROM equipo
            LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            LEFT JOIN unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN celular ON equipo.celular_id = celular.id
            WHERE equipo.estadoequipo_id = 1
        """)
            equipos = cursor.fetchall()

            # Obtener el ID de la persona de la URL
            persona_id = request.args.get('persona_id')

            cursor.execute("SELECT nombres, apellidos FROM persona WHERE id = ?", (persona_id,))
            persona_info = cursor.fetchone()
            nombres_persona = persona_info[0] if persona_info else ""
            apellidos_persona = persona_info[1] if persona_info else ""

            return render_template('asignar_equipo.html', persona_id=persona_id, nombres=nombres_persona, apellidos=apellidos_persona, equipos=equipos)
        except pyodbc.Error as ex:
            print(f'Error al obtener los datos: {ex}')
            flash('Error al cargar la página de asignación', 'error')
            return redirect(url_for('index'))
        finally:
            cursor.close()






#--------------------------------------------------------------------------
# Devolucion:
@app.route('/devolver_equipo/<int:equipo_id>', methods=['GET', 'POST'])
@login_required
def devolver_equipo(equipo_id):
    cursor = conexion.cursor()

    if request.method == 'POST':
        if 'archivo_pdf' not in request.files:
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        file = request.files['archivo_pdf']

        if file.filename == '':
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = f"{equipo_id}_devolucion_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            fecha_devolucion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            observaciones = request.form['observaciones']

            try:
                cursor.execute("""
                    UPDATE asignacion_equipo
                    SET fecha_devolucion = ?, observaciones = ?, archivo_pdf_devolucion = ?
                    WHERE equipo_id = ? AND fecha_devolucion IS NULL
                """, (fecha_devolucion, observaciones, filename, equipo_id))
                conexion.commit()

                cursor.execute("UPDATE equipo SET estadoequipo_id = 1 WHERE id = ?", (equipo_id,))
                conexion.commit()

                persona_id = obtener_persona_id_asociada(equipo_id)


                flash('Equipo devuelto correctamente', 'success')
                return redirect(url_for('detalle_persona', persona_id=persona_id))
            except pyodbc.Error as ex:
                print('Error al devolver el equipo: {ex}')
                flash('Error al devolver el equipo', 'error')
                return redirect(url_for('devolver_equipo', equipo_id=equipo_id))
            finally:
                cursor.close()

    else:
        try:
            cursor.execute("""
                SELECT
                    ae.id,
                    e.id AS equipo_id,
                    te.nombre AS tipo_nombre,
                    COALESCE(u.nombre_e, c.nombre) AS nombre_equipo,
                    p.nombres,
                    ae.fecha_asignacion,
                    ae.fecha_devolucion,
                    ae.observaciones,
                    ae.archivo_pdf_devolucion,
                    ae.persona_id
                FROM asignacion_equipo AS ae
                JOIN equipo AS e ON ae.equipo_id = e.id
                JOIN tipoequipo AS te ON e.tipoequipo_id = te.id
                LEFT JOIN unidad AS u ON e.unidad_id = u.id
                LEFT JOIN celular AS c ON e.celular_id = c.id
                JOIN persona AS p ON ae.persona_id = p.id
                WHERE ae.fecha_devolucion IS NULL AND ae.equipo_id = ?
            """, (equipo_id,))
            asignacion = cursor.fetchone()

            if not asignacion:
                flash('No se encontró una asignación activa para este equipo', 'error')
                return redirect(url_for('detalle_equipo', equipo_id=equipo_id))

            persona_id = asignacion[-1]

            return render_template('devolver_equipo.html', asignacion=asignacion, equipo_id=equipo_id, persona_id=persona_id)
        except pyodbc.Error as ex:
            print('Error al obtener los datos: {ex}')
            flash('Error al cargar la página de devolución', 'error')
            return redirect(url_for('detalle_equipo', equipo_id=equipo_id))
        finally:
            cursor.close()


#---
def obtener_persona_id_asociada(equipo_id):
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT persona_id FROM asignacion_equipo WHERE equipo_id = ?", (equipo_id,))
        persona_id = cursor.fetchone()[0]
        return persona_id
    except pyodbc.Error as ex:
        print(f'Error al obtener el ID de la persona asociada al equipo: {ex}')
        # Manejo del error: puedes retornar un valor predeterminado, lanzar una excepción, o retornar None
        return None

#---------------------------------------------------------------------------
#Detalle persona
@app.route('/detalle_persona/<int:persona_id>')
@login_required
def detalle_persona(persona_id):
    try:
        cursor = conexion.cursor()
        
        # Obtener los detalles de la persona
        cursor.execute("""
            SELECT
                id,
                nombres,
                apellidos,
                correo,
                rut,
                dv
            FROM persona
            WHERE id = ?
        """, (persona_id,))
        persona = cursor.fetchone()

        if not persona:
            flash('No se encontró la persona', 'error')
            return redirect(url_for('index'))

        # Obtener el historial completo de asignaciones y devoluciones de la persona
        cursor.execute("""
            SELECT
                asignacion_equipo.fecha_asignacion,
                asignacion_equipo.fecha_devolucion,
                asignacion_equipo.observaciones,
                asignacion_equipo.archivo_pdf,
                asignacion_equipo.archivo_pdf_devolucion,
                equipo.id AS equipo_id,
                tipoequipo.nombre AS tipo_equipo,
                COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
            FROM asignacion_equipo
            JOIN equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN celular ON equipo.celular_id = celular.id
            LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE asignacion_equipo.persona_id = ?
            ORDER BY asignacion_equipo.fecha_asignacion DESC
        """, (persona_id,))
        historial_completo = cursor.fetchall()

        # Obtener la lista de equipos mantenidos por la persona
        cursor.execute("""
            SELECT
                equipo.id,
                tipoequipo.nombre AS tipo_equipo,
                COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo,
                COALESCE(unidad.modelo, celular.modelo) AS modelo_equipo
            FROM equipo
            JOIN asignacion_equipo ON equipo.id = asignacion_equipo.equipo_id
            LEFT JOIN unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN celular ON equipo.celular_id = celular.id
            LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE asignacion_equipo.persona_id = ?
        """, (persona_id,))
        equipos_mantenidos = cursor.fetchall()

        cursor.close()

        return render_template('detalle_persona.html', persona=persona, historial_completo=historial_completo, equipos_mantenidos=equipos_mantenidos)
    
    except pyodbc.Error as ex:
        print('Error al obtener los detalles de la persona: {ex}')
        flash('Error al obtener los detalles de la persona', 'error')
        return redirect(url_for('index'))




#----------------------------------------------------
# Detalle equipo

@app.route('/detalle_equipo/<int:equipo_id>')
@login_required
def detalle_equipo(equipo_id):
    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                equipo.id,
                estadoequipo.nombre AS estado_nombre,
                equipo.fcreacion AS fecha_creacion,
                equipo.observaciones,
                equipo.unidad_id,
                unidad.nombre_e,
                unidad.marca,
                unidad.modelo,
                unidad.ram,
                unidad.procesador,
                unidad.almc,
                unidad.perif,
                unidad.numsello,
                unidad.serial,
                unidad.numproducto,
                unidad.tipoimpresion,
                unidad.cantidad,
                equipo.celular_id,
                celular.nombre AS nombre_celular,
                celular.marca AS marca_celular,
                celular.modelo AS modelo_celular,
                celular.serial AS serial_celular,
                celular.imei1,
                celular.imei2,
                celular.ntelefono
            FROM equipo
            LEFT JOIN estadoequipo ON equipo.estadoequipo_id = estadoequipo.id
            LEFT JOIN unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN celular ON equipo.celular_id = celular.id
            WHERE equipo.id = ?
        """, (equipo_id,))
        equipo_detalle = cursor.fetchone()

        if not equipo_detalle:
            flash('No se encontró el equipo', 'error')
            return redirect(url_for('index'))

        cursor.execute("""
            SELECT TOP 3
                asignacion_equipo.fecha_asignacion,
                asignacion_equipo.fecha_devolucion,
                asignacion_equipo.observaciones,
                asignacion_equipo.archivo_pdf,
                asignacion_equipo.archivo_pdf_devolucion,
                persona.id AS persona_id,
                persona.nombres AS persona_nombre,
                persona.apellidos AS persona_apellidos
            FROM asignacion_equipo
            JOIN persona ON asignacion_equipo.persona_id = persona.id
            WHERE asignacion_equipo.equipo_id = ?
            ORDER BY asignacion_equipo.fecha_asignacion DESC
        """, (equipo_id,))
        historial = cursor.fetchall()

        persona_id = None
        if historial:
            persona_id = historial[0].persona_id

        otros_equipos = []
        if persona_id:
            cursor.execute("""
                SELECT
                    equipo.id,
                    equipo.fcreacion,
                    equipo.observaciones,
                    estadoequipo.nombre AS estado_nombre,
                    COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
                FROM asignacion_equipo
                JOIN equipo ON asignacion_equipo.equipo_id = equipo.id
                JOIN estadoequipo ON equipo.estadoequipo_id = estadoequipo.id
                LEFT JOIN unidad ON equipo.unidad_id = unidad.id
                LEFT JOIN celular ON equipo.celular_id = celular.id
                WHERE asignacion_equipo.persona_id = ? AND equipo.id != ?
            """, (persona_id, equipo_id))
            otros_equipos = cursor.fetchall()

        cursor.close()

        return render_template('detalle_equipo.html', equipo=[equipo_detalle], historial=historial, otros_equipos=otros_equipos)
    
    except pyodbc.Error as ex:
        print('Error al obtener los detalles del equipo: {ex}')
        flash('Error al obtener los detalles del equipo', 'error')
        return redirect(url_for('index'))


#-----------------------------------------------------------------------
@app.route('/equipos')
@login_required
def lista_equipos():
    buscar = request.args.get('buscar', '')
    tipo_equipo = request.args.get('tipo_equipo', '')
    estado = request.args.get('estado', '')

    try:
        cursor = conexion.cursor()

        query = """
            SELECT
                equipo.id,
                tipoequipo.nombre AS tipo_equipo_nombre,
                COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo,
                estadoequipo.nombre AS estado_nombre,
                equipo.observaciones
            FROM equipo
            LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            LEFT JOIN estadoequipo ON equipo.estadoequipo_id = estadoequipo.id
            LEFT JOIN unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN celular ON equipo.celular_id = celular.id
            WHERE 1=1
        """
        
        params = []
        
        if buscar:
            query += " AND (unidad.nombre_e LIKE ? OR celular.nombre LIKE ?)"
            params.append(f'%{buscar}%')
            params.append(f'%{buscar}%')
        
        if tipo_equipo:
            query += " AND equipo.tipoequipo_id = ?"
            params.append(tipo_equipo)
        
        if estado:
            query += " AND equipo.estadoequipo_id = ?"
            params.append(estado)
        
        cursor.execute(query, params)
        equipos = cursor.fetchall()
        
        cursor.execute("SELECT id, nombre FROM tipoequipo")
        tipos_equipo = cursor.fetchall()
        
        cursor.execute("SELECT id, nombre FROM estadoequipo")
        estados = cursor.fetchall()
        
        cursor.close()

        return render_template('lista_equipos.html', equipos=equipos, tipos_equipo=tipos_equipo, estados=estados)
    
    except pyodbc.Error as ex:
        print('Error al obtener la lista de equipos: {ex}')
        flash('Error al obtener la lista de equipos', 'error')
        return redirect(url_for('index'))

#-----------------------------------------------------------------------
#descargar:
UPLOAD_FOLDER = 'C:/descarga/'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/descargar_pdf/<pdf_filename>')
def descargar_pdf(pdf_filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], pdf_filename, as_attachment=True)
    except FileNotFoundError:
        flash('El archivo PDF no se encontró', 'error')
        return redirect(url_for('index'))
#-----------------------------------------

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)
#------------------------------------------


def fetch_data(equipo_id):
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            equipo.id,
            estadoequipo.nombre AS estado_nombre,
            equipo.fcreacion AS fecha_creacion,
            equipo.observaciones,
            equipo.unidad_id,
            unidad.nombre_e,
            unidad.marca,
            unidad.modelo,
            unidad.ram,
            unidad.procesador,
            unidad.almc,
            unidad.perif,
            unidad.numsello,
            unidad.serial,
            unidad.numproducto,
            unidad.tipoimpresion,
            unidad.cantidad,
            equipo.celular_id,
            celular.nombre AS nombre_celular,
            celular.marca AS marca_celular,
            celular.modelo AS modelo_celular,
            celular.serial AS serial_celular,
            celular.imei1,
            celular.imei2,
            celular.ntelefono,
            persona.nombres AS persona_nombre,
            persona.apellidos AS persona_apellidos,
            persona.area AS persona_area
        FROM equipo
        LEFT JOIN estadoequipo ON equipo.estadoequipo_id = estadoequipo.id
        LEFT JOIN unidad ON equipo.unidad_id = unidad.id
        LEFT JOIN celular ON equipo.celular_id = celular.id
        LEFT JOIN asignacion_equipo ON equipo.id = asignacion_equipo.equipo_id
        LEFT JOIN persona ON asignacion_equipo.persona_id = persona.id
        WHERE equipo.id = ?
    """, (equipo_id,))
    equipo_detalle = cursor.fetchone()
    cursor.close()
    conexion.close()

    return equipo_detalle


@app.route('/generate_pdf/<int:persona_id>', methods=['POST'])
@login_required
def generate_pdf(persona_id):
    print(f"Recibido persona_id: {persona_id}")
    print(f"Datos recibidos: {request.form}")

    # Consultar la información de la persona en la base de datos
    cursor = conexion.cursor()
    cursor.execute("SELECT nombres, apellidos FROM persona WHERE id = ?", (persona_id,))
    persona = cursor.fetchone()
    cursor.close()

    if not persona:
        return "Persona no encontrada", 404

    nombres = persona[0]
    apellidos = persona[1]

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Acta de Entrega de Equipos', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Persona: {nombres} {apellidos}', 0, 1)
    pdf.cell(0, 10, 'Equipos: No se incluyeron equipos en esta prueba', 0, 1)

    # Guardar el PDF en un objeto BytesIO
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    # Devolver el archivo PDF como respuesta para descargar
    return send_file(pdf_output, download_name='acta_entrega.pdf', as_attachment=True)

#-------------------------------------


#---------------------------------------

#---------------------------------------
def validar_credenciales(username, password):
    try:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM Usuarios WHERE username = ? AND password = ?', (username, password))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario is not None
    except Exception as e:
        print("Error de base de datos:", e)
        return False
#----------------------------------------

#----------------------------------------
@app.route('/exportar_excel', methods=['GET'])
def exportar_excel():
    try:
        search_term = request.args.get('search_term', '')
        

        # Crear la consulta SQL con el término de búsqueda
        query = '''
            SELECT DISTINCT 
                persona.id, 
                persona.nombres, 
                persona.apellidos, 
                persona.correo, 
                persona.rut, 
                persona.dv, 
                area.nombre AS area_nombre,
                tipoequipo.nombre AS tipo_nombre,
                ISNULL(unidad.nombre_e, '') AS nombre_unidad, 
                ISNULL(celular.nombre, '') AS nombre_celular, 
                equipo.id AS equipo_id
            FROM 
                persona
            INNER JOIN 
                area ON persona.area_id = area.id
            LEFT JOIN 
                asignacion_equipo ON persona.id = asignacion_equipo.persona_id
            LEFT JOIN 
                equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN 
                unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN 
                celular ON equipo.celular_id = celular.id
            LEFT JOIN 
                tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE
                equipo.estadoequipo_id = 2 AND asignacion_equipo.fecha_devolucion IS NULL
                AND (
                    persona.nombres LIKE ? OR
                    persona.apellidos LIKE ? OR
                    persona.correo LIKE ? OR
                    persona.rut LIKE ? OR
                    area.nombre LIKE ? OR
                    tipoequipo.nombre LIKE ? OR
                    unidad.nombre_e LIKE ? OR
                    celular.nombre LIKE ?
                )
        '''

        cursor = conexion.cursor()
        cursor.execute(query, ('%' + search_term + '%',) * 8)  # Aplicar el término de búsqueda a cada campo
        rows = cursor.fetchall()
        cursor.close()

        # Crear un diccionario para almacenar los datos de las personas
        personas_dict = {}

        # Recorrer las filas seleccionadas y agrupar los equipos por persona
        for row in rows:
            persona_id = row.id
            if persona_id not in personas_dict:
                personas_dict[persona_id] = {
                    'id': row.id,
                    'nombres': row.nombres,
                    'apellidos': row.apellidos,
                    'correo': row.correo,
                    'rut': row.rut,
                    'dv': row.dv,
                    'area_nombre': row.area_nombre,
                    'equipos_asignados': []
                }
            equipo = {
                'nombre': row.nombre_unidad if row.nombre_unidad else row.nombre_celular,
                'tipoequipo': row.tipo_nombre
            }
            if equipo not in personas_dict[persona_id]['equipos_asignados']:
                personas_dict[persona_id]['equipos_asignados'].append(equipo)

        # Crear el libro de Excel y seleccionar la primera hoja
        wb = Workbook()
        ws = wb.active

        # Añadir encabezados a la primera fila
        ws.append(['Rut', 'Nombre', 'Apellido', 'Correo', 'Área', 'Equipos Asignados'])

        # Añadir filas de datos desde el diccionario de personas
        for persona in personas_dict.values():
            equipos_asignados = ', '.join([f"{equipo['nombre']} - {equipo['tipoequipo']}" for equipo in persona['equipos_asignados']])
            ws.append([persona['rut'], persona['nombres'], persona['apellidos'], persona['correo'], persona['area_nombre'], equipos_asignados])

        # Ajustar el ancho de las columnas
        for col in ws.columns:
            max_length = 0
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[col[0].column_letter].width = adjusted_width

        # Crear una respuesta con el archivo Excel adjunto
        filename = "index.xlsx"
        wb.save(filename)
        with open(filename, 'rb') as file:
            response = make_response(file.read())
        response.headers['Content-Disposition'] = 'attachment; filename=index.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response
    except Exception as ex:
        print('Error al exportar a Excel:', ex)
        flash('Error al exportar a Excel', 'error')
        return redirect(url_for('index'))





def obtener_personas():
    cursor = conexion.cursor()
    try:
        search_term = ''  # Puedes ajustar este valor según sea necesario

        query = '''
            SELECT DISTINCT 
                persona.id, 
                persona.nombres, 
                persona.apellidos, 
                persona.correo, 
                persona.rut, 
                persona.dv, 
                area.nombre AS area_nombre,
                tipoequipo.nombre AS tipo_nombre,
                ISNULL(unidad.nombre_e, '') AS nombre_unidad, 
                ISNULL(celular.nombre, '') AS nombre_celular, 
                equipo.id AS equipo_id
            FROM 
                persona
            INNER JOIN 
                area ON persona.area_id = area.id
            LEFT JOIN 
                asignacion_equipo ON persona.id = asignacion_equipo.persona_id
            LEFT JOIN 
                equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN 
                unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN 
                celular ON equipo.celular_id = celular.id
            LEFT JOIN 
                tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE
                equipo.estadoequipo_id = 2 AND asignacion_equipo.fecha_devolucion IS NULL
                AND (
                    persona.nombres LIKE ? OR
                    persona.apellidos LIKE ? OR
                    persona.correo LIKE ? OR
                    persona.rut LIKE ? OR
                    area.nombre LIKE ? OR
                    tipoequipo.nombre LIKE ? OR
                    unidad.nombre_e LIKE ? OR
                    celular.nombre LIKE ?
                )
        '''

        cursor.execute(query, ('%' + search_term + '%',) * 8)  # Aplicar el término de búsqueda a cada campo

        rows = cursor.fetchall()
        cursor.close()

        personas = {}
        for row in rows:
            persona_id = row.id
            if persona_id not in personas:
                personas[persona_id] = {
                    'id': row.id,
                    'nombres': row.nombres,
                    'apellidos': row.apellidos,
                    'correo': row.correo,
                    'rut': row.rut,
                    'dv': row.dv,
                    'area_nombre': row.area_nombre,
                    'equipos_asignados': []
                }
            equipo = {
                'equipo_id': row.equipo_id,
                'nombre': row.nombre_unidad if row.nombre_unidad else row.nombre_celular,
                'tipoequipo': row.tipo_nombre
            }
            if equipo['nombre']:
                personas[persona_id]['equipos_asignados'].append(equipo)

        return list(personas.values())
    except pyodbc.Error as ex:
        print('Error al obtener los datos:', ex)
        flash('Error al cargar la página de asignación', 'error')
        return []

@app.route('/exportar_reporte_individual/<int:persona_id>', methods=['GET'])
@login_required
def exportar_reporte_individual(persona_id):
    try:
        # Obtener los datos de la persona por su ID
        persona = obtener_persona_por_id(persona_id)
        
        if persona:
            # Crear un nuevo libro de Excel y seleccionar la primera hoja
            wb = Workbook()
            ws = wb.active

            # Añadir encabezados a la primera fila
            ws.append(['Rut', 'Nombre', 'Apellido', 'Correo', 'Área', 'Equipos Asignados'])

            # Concatenar los nombres de los equipos asignados en una sola cadena
            equipos_asignados = ', '.join([f"{equipo['nombre']} - {equipo['tipoequipo']}" for equipo in persona['equipos_asignados']])

            # Agregar los datos de la persona y los equipos asignados en una fila
            ws.append([persona['rut'], persona['nombres'], persona['apellidos'], persona['correo'], persona['area_nombre'], equipos_asignados])

            # Ajustar el ancho de las columnas
            for col in ws.columns:
                max_length = 0
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = (max_length + 2) * 1.2
                ws.column_dimensions[col[0].column_letter].width = adjusted_width

            # Crear una respuesta con el archivo Excel adjunto
            filename = f"reporte_{persona_id}.xlsx"
            wb.save(filename)
            with open(filename, 'rb') as file:
                response = make_response(file.read())
            response.headers['Content-Disposition'] = f'attachment; filename=reporte_{persona_id}.xlsx'
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

            return response
        else:
            flash('Persona no encontrada', 'error')
            return redirect(url_for('index'))
    except Exception as ex:
        print('Error al exportar el reporte individual a Excel:', ex)
        flash('Error al exportar el reporte individual a Excel', 'error')
        return redirect(url_for('index'))


#---------------------------------------------

def obtener_persona_por_id(persona_id):
    cursor = conexion.cursor()
    try:
        query = '''
            SELECT DISTINCT 
                persona.id, 
                persona.nombres, 
                persona.apellidos, 
                persona.correo, 
                persona.rut, 
                persona.dv, 
                area.nombre AS area_nombre
            FROM 
                persona
            INNER JOIN 
                area ON persona.area_id = area.id
            WHERE
                persona.id = ?
        '''

        cursor.execute(query, (persona_id,))
        row = cursor.fetchone()

        if row:
            persona = {
                'id': row.id,
                'nombres': row.nombres,
                'apellidos': row.apellidos,
                'correo': row.correo,
                'rut': row.rut,
                'dv': row.dv,
                'area_nombre': row.area_nombre,
                'equipos_asignados': obtener_equipos_por_persona(persona_id)
            }
            return persona
        else:
            return None
    except pyodbc.Error as ex:
        print('Error al obtener la persona por ID:', ex)
        return None
    finally:
        cursor.close()

def obtener_equipos_por_persona(persona_id):
    cursor = conexion.cursor()
    try:
        query = '''
            SELECT 
                equipo.id AS equipo_id,
                ISNULL(unidad.nombre_e, '') AS nombre_unidad, 
                ISNULL(celular.nombre, '') AS nombre_celular,
                tipoequipo.nombre AS tipo_nombre
            FROM 
                asignacion_equipo
            INNER JOIN 
                equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN 
                unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN 
                celular ON equipo.celular_id = celular.id
            LEFT JOIN 
                tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE 
                asignacion_equipo.persona_id = ?
        '''

        cursor.execute(query, (persona_id,))
        rows = cursor.fetchall()

        equipos_asignados = []
        for row in rows:
            equipo = {
                'equipo_id': row.equipo_id,
                'nombre': row.nombre_unidad if row.nombre_unidad else row.nombre_celular,
                'tipoequipo': row.tipo_nombre
            }
            equipos_asignados.append(equipo)

        return equipos_asignados
    except pyodbc.Error as ex:
        print('Error al obtener los equipos por persona:', ex)
        return []
    finally:
        cursor.close()

##############################

@app.route('/exportar_pdf', methods=['GET'])
def exportar_pdf():
    try:
        search_term = request.args.get('search_term', '')

        # Crear la consulta SQL con el término de búsqueda
        query = '''
            SELECT DISTINCT 
                persona.id, 
                persona.nombres, 
                persona.apellidos, 
                persona.correo, 
                persona.rut, 
                persona.dv, 
                area.nombre AS area_nombre,
                tipoequipo.nombre AS tipo_nombre,
                ISNULL(unidad.nombre_e, '') AS nombre_unidad, 
                ISNULL(celular.nombre, '') AS nombre_celular, 
                equipo.id AS equipo_id
            FROM 
                persona
            INNER JOIN 
                area ON persona.area_id = area.id
            LEFT JOIN 
                asignacion_equipo ON persona.id = asignacion_equipo.persona_id
            LEFT JOIN 
                equipo ON asignacion_equipo.equipo_id = equipo.id
            LEFT JOIN 
                unidad ON equipo.unidad_id = unidad.id
            LEFT JOIN 
                celular ON equipo.celular_id = celular.id
            LEFT JOIN 
                tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
            WHERE
                equipo.estadoequipo_id = 2 AND asignacion_equipo.fecha_devolucion IS NULL
                AND (
                    persona.nombres LIKE ? OR
                    persona.apellidos LIKE ? OR
                    persona.correo LIKE ? OR
                    persona.rut LIKE ? OR
                    area.nombre LIKE ? OR
                    tipoequipo.nombre LIKE ? OR
                    unidad.nombre_e LIKE ? OR
                    celular.nombre LIKE ?
                )
        '''

        cursor = conexion.cursor()
        cursor.execute(query, ('%' + search_term + '%',) * 8)  # Aplicar el término de búsqueda a cada campo
        rows = cursor.fetchall()
        cursor.close()

        # Crear un buffer de memoria para almacenar el PDF
        buffer = io.BytesIO()

        # Crear un documento PDF
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Datos para la tabla PDF
        data = [['Rut', 'Nombre', 'Apellido', 'Correo', 'Área', 'Equipos Asignados']]

        # Recorrer las filas seleccionadas y agregar los datos a la tabla
        for row in rows:
            equipos_asignados = ', '.join([f"{row.nombre_unidad if row.nombre_unidad else row.nombre_celular} - {row.tipo_nombre}"])
            data.append([row.rut, row.nombres, row.apellidos, row.correo, row.area_nombre, equipos_asignados])

        # Crear la tabla PDF
        table = Table(data)

        # Estilo de la tabla
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)
        elements.append(table)

        # Construir el PDF
        pdf.build(elements)

        # Devolver el PDF como una respuesta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=exportacion.pdf'
        response.headers['Content-Type'] = 'application/pdf'

        return response
    except Exception as ex:
        print('Error al exportar a PDF:', ex)
        flash('Error al exportar a PDF', 'error')
        return redirect(url_for('index'))


class PDF(FPDF):
    def header(self):

        left_margin = 20
        self.set_left_margin(left_margin)
        self.set_x(left_margin)
        self.image('C:/ProyectosPython/Inventario/src/static/logochf.png', x=150, y=12, w=40)
        self.set_font('Arial', 'B', 25)
        self.cell(0, 40, 'Carta de Responsabilidad', ln=True, align='L')

    def footer(self):
        self.set_y(-50)
    
        # Ancho total de la página
        page_width = self.w - 2 * self.l_margin

        # Ancho de cada celda de firma
        cell_width = page_width / 3


        self.cell(cell_width, 8, '____________________', 0, 0, 'C')
        self.cell(cell_width, 8, '____________________', 0, 0, 'C')
        self.cell(cell_width, 8, '____________________', 0, 1, 'C')

        self.set_font('Arial', 'B', 8)
        self.cell(cell_width, 5, 'FIRMA DEL USUARIO', 0, 0, 'C')
        self.cell(cell_width, 5, 'GASTON MARILEO', 0, 0, 'C')
        self.cell(cell_width, 5, 'CARLOS AHUMADA', 0, 1, 'C')

        self.set_font('Arial', 'B', 6)
        self.cell(cell_width, 5, 'RESPONSABLE', 0, 0, 'C')
        self.cell(cell_width, 5, 'JEFE SISTEMA TI', 0, 0, 'C')
        self.cell(cell_width, 5, 'ENCARGADO SOPORTE TI', 0, 1, 'C')

        # Línea de firma
        

@app.route('/exportar_pdf/<int:persona_id>', methods=['GET', 'POST'])
def exportar_pdf_persona(persona_id):
    try:
        query = '''
            SELECT DISTINCT 
    persona.id, 
    persona.nombres, 
    persona.apellidos, 
    persona.correo, 
    persona.rut, 
    persona.dv, 
    area.nombre AS area_nombre,
    tipoequipo.nombre AS tipo_nombre,
    ISNULL(unidad.nombre_e, '') AS nombre_unidad, 
    ISNULL(celular.nombre, '') AS nombre_celular, 
    equipo.id AS equipo_id,
    unidad.id AS unidad_id, 
    unidad.marca AS marca,
    unidad.modelo AS modelo,
    unidad.ram AS ram,
    unidad.procesador AS procesador,
    unidad.almc AS almc,
    unidad.perif AS perif,
    unidad.numsello AS numsello,
    unidad.serial AS serial,
    unidad.numproducto AS numproducto,
    unidad.tipoimpresion AS tipoimpresion,
    unidad.cantidad AS cantidad,
    celular.id AS celular_id,
    celular.marca AS marca_celular,
    celular.modelo AS modelo_celular,
    celular.serial AS serial_celular,
    celular.imei1 AS imei1,
    celular.imei2 AS imei2,
    celular.ntelefono AS ntelefono
FROM 
    persona
INNER JOIN 
    area ON persona.area_id = area.id
LEFT JOIN 
    asignacion_equipo ON persona.id = asignacion_equipo.persona_id
LEFT JOIN 
    equipo ON asignacion_equipo.equipo_id = equipo.id
LEFT JOIN 
    unidad ON equipo.unidad_id = unidad.id
LEFT JOIN 
    celular ON equipo.celular_id = celular.id
LEFT JOIN 
    tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
WHERE
    persona.id = ? 

        '''

        cursor = conexion.cursor()
        cursor.execute(query, (persona_id,))
        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            flash('No se encontraron datos para la persona seleccionada', 'error')
            return redirect(url_for('index'))

        buffer = io.BytesIO()

        # Crear un documento PDF
        pdf = PDF()
        pdf.add_page()

        # Agregar borde cuadrado
        pdf.set_line_width(0.5)
        pdf.rect(10, 10, 190, 270)

        left_margin = 20  


        nombre = f"{rows[0].nombres} {rows[0].apellidos}"
        area = rows[0].area_nombre
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_x(left_margin)
        pdf.cell(0, 10, f'Se entrega a Sr/a: {nombre}', ln=True, align='L')
        pdf.set_x(left_margin)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(0, 2, f'{area}', ln=True, align='L')

        # Espacio
        pdf.cell(0, 10, '', ln=True)
        pdf.set_font('Helvetica', '', 12)

        # Agregar datos de los equipos
        for row in rows:
            equipo_nombre = row.nombre_unidad if row.nombre_unidad else row.nombre_celular
            tipo_nombre = row.tipo_nombre
            if equipo_nombre:
                pdf.cell(0, 5, f"Nombre del equipo: {equipo_nombre}", ln=True, align='L')
            if tipo_nombre:
                pdf.cell(0, 5, f"Tipo de equipo: {tipo_nombre}", ln=True, align='L')

            # Agregar otros atributos del equipo si están presentes
            if row.unidad_id:
                if row.marca:
                    pdf.cell(0, 5, f"Marca: {row.marca}", ln=True, align='L')
                if row.modelo:
                    pdf.cell(0, 5, f"Modelo: {row.modelo}", ln=True, align='L')
                if row.ram:
                    pdf.cell(0, 5, f"RAM: {row.ram}", ln=True, align='L')
                if row.procesador:
                    pdf.cell(0, 5, f"Procesador: {row.procesador}", ln=True, align='L')
                if row.almc:
                    pdf.cell(0, 5, f"Almacenamiento: {row.almc}", ln=True, align='L')
                if row.perif:
                    pdf.cell(0, 5, f"Periféricos: {row.perif}", ln=True, align='L')
                if row.numsello:
                    pdf.cell(0, 5, f"Número de Sello: {row.numsello}", ln=True, align='L')
                if row.serial:
                    pdf.cell(0, 5, f"Serial: {row.serial}", ln=True, align='L')
                if row.numproducto:
                    pdf.cell(0, 5, f"Número de Producto: {row.numproducto}", ln=True, align='L')
                if row.tipoimpresion:
                    pdf.cell(0, 5, f"Tipo de Impresión: {row.tipoimpresion}", ln=True, align='L')
                if row.cantidad:
                    pdf.cell(0, 5, f"Cantidad: {row.cantidad}", ln=True, align='L')
            if row.celular_id:
                if row.marca_celular:
                    pdf.cell(0, 5, f"Marca del Celular: {row.marca_celular}", ln=True, align='L')
                if row.modelo_celular:
                    pdf.cell(0, 5, f"Modelo del Celular: {row.modelo_celular}", ln=True, align='L')
                if row.serial_celular:
                    pdf.cell(0, 5, f"Serial del Celular: {row.serial_celular}", ln=True, align='L')
                if row.imei1:
                    pdf.cell(0, 5, f"IMEI 1: {row.imei1}", ln=True, align='L')
                if row.imei2:
                    pdf.cell(0, 5, f"IMEI 2: {row.imei2}", ln=True, align='L')
                if row.ntelefono:
                    pdf.cell(0, 5, f"Número de Teléfono: {row.ntelefono}", ln=True, align='L')
            pdf.cell(0, 8, '', ln=True)  # Espacio entre equipos

        # Guardar el PDF en el buffer
        pdf.output(buffer)

        # Devolver el PDF como una respuesta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=carta_responsabilidad.pdf'
        response.headers['Content-Type'] = 'application/pdf'

        return response
    except Exception as ex:
        print(f'Error al exportar a PDF: {ex}')
        flash('Error al exportar a PDF', 'error')
        return redirect(url_for('index'))











###############################
###############################
###############################

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

