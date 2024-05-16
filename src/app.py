
import os
import pyodbc
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename



app = Flask(__name__)

app.config['SECRET_KEY'] = 'chf24'
#---------------------------------------------------------

server = 'CHFNB239\\SQLEXPRESS'
db = 'TestDB'
user = 'sa'
password = 'Chilefilms23'
#Conexion a base de datos
try:
    conexion = pyodbc.connect(
        'DRIVER={ODBC DRIVER 17 FOR SQL server};SERVER=' + server + ';DATABASE=' + db + ';UID=' + user + ';PWD=' + password
    )
    print('Conexión exitosa')
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(sqlstate)
    print ('Error al intentar conectarse')



def obtener_tipos_equipos():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM tipoequipo")
        tipos_equipos = cursor.fetchall()
        cursor.close()
        return tipos_equipos
    except pyodbc.Error as ex:
        print(ex)
        return None
#---------------------------------------------------------
# Index mostrar personas
@app.route('/')
def index():
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            SELECT DISTINCT 
    persona.id, 
    persona.nombres, 
    persona.apellidos, 
    persona.correo, 
    persona.rut, 
    persona.dv, 
    area.nombre AS area_nombre,
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
WHERE 
    equipo.estadoequipo_id = 2

        ''')

        rows = cursor.fetchall()
        cursor.close()

        # Organize data in a dictionary
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
                'nombre': row.nombre_unidad if row.nombre_unidad else row.nombre_celular
            }
            if equipo['nombre']:  
                personas[persona_id]['equipos_asignados'].append(equipo)

        return render_template('index.html', personas=list(personas.values()))
    except pyodbc.Error as ex:
        print(f'Error al obtener los datos: {ex}')
        flash('Error al cargar la página de asignación', 'error')
        return redirect(url_for('index'))




#--------------------------------------------------------
# CRUD Persona
@app.route('/listar_personas')
def listar_personas():
    try:
        cursor = conexion.cursor()
        cursor.execute('''SELECT persona.id, persona.nombres, persona.apellidos, persona.correo, area.nombre AS area_nombre
            FROM persona
            INNER JOIN area ON persona.area_id = area.id ''')
        personas = cursor.fetchall()
        cursor.close()
        return render_template('listar_personas.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)

@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        rut = request.form['rut']
        dv= request.form['dv']
        area_id = request.form['area']

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO persona (nombres, apellidos, correo, rut, dv, area_id) VALUES (?, ?, ?, ?, ?, ?)",
                            (nombres, apellidos, correo, rut, dv, area_id))
            conexion.commit()
            cursor.close()
            flash('La persona ha sido agregada correctamente', 'success')
            return redirect(url_for('index'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al agregar la persona', 'error')
            return redirect(url_for('agregar_persona'))

    # Obtener las áreas disponibles para mostrar en el formulario
    areas = obtener_areas()
    if areas:
        return render_template('agregar_persona.html', areas=areas)
    else:
        flash('Ocurrió un error al obtener las áreas', 'error')
        return redirect(url_for('listar_personas'))

from flask import redirect, render_template, request, url_for

@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
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
            flash('Los cambios han sido guardados correctamente', 'success')
            return redirect(url_for('listar_personas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al guardar los cambios', 'error')
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
def eliminar_persona(id):
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM persona WHERE id = ?", (id,))
        conexion.commit()
        cursor.close()
        flash('La persona ha sido eliminada correctamente', 'success')
    except pyodbc.Error as ex:
        print(ex)
        flash('Ocurrió un error al eliminar la persona', 'error')
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
def mostrar_equipos():
    try:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT
        equipo.id,
        tipoequipo.nombre AS tipo_nombre,
        COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
        FROM equipo
        LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
        LEFT JOIN unidad ON equipo.unidad_id = unidad.id
        LEFT JOIN celular ON equipo.celular_id = celular.id
        """)

        equipos = cursor.fetchall()
        cursor.close()
        return render_template('mostrar_equipos.html', equipos=equipos)
    except pyodbc.Error as ex:
        print(f'Error al obtener los equipos: {ex}')
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
def agregar_equipo():
    
    if request.method == 'POST':
        seccion = request.form['seccion']
        nombre = request.form['nombre']
        marca = request.form['marca']
        modelo = request.form['modelo']
        serial = request.form['serial']
        observaciones = request.form['observaciones']

        if seccion == '1':
            # Para equipo
            tipo_equipo_id = request.form['tipo_equipo']
            ram = request.form['ram']
            procesador = request.form['procesador']
            almc = request.form['almc']
            perif = request.form['perif']
            numsello = request.form['numsello']
            numproducto = request.form['numproducto']
            tipoimpresion = request.form['tipoimpresion']
            

            try:
                cursor = conexion.cursor()
                cursor.execute("INSERT INTO unidad (nombre_e, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (nombre, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion))
                conexion.commit()
                cursor.execute("SELECT @@IDENTITY")
                unidad_id = cursor.fetchone()[0]
                
                cursor.execute("INSERT INTO equipo (estadoequipo_id, unidad_id, fcreacion, tipoequipo_id, observaciones) VALUES (?, ?, ?, ?, ?)",
                               (1, unidad_id, datetime.datetime.now(), tipo_equipo_id, observaciones))
                conexion.commit()
                cursor.close()
                flash('El equipo ha sido agregado correctamente', 'success')
                return redirect(url_for('mostrar_equipos'))
            except pyodbc.Error as ex:
                print(ex)
                flash('Ocurrió un error al agregar el equipo', 'error')
                return redirect(url_for('agregar_equipo'))

        elif seccion == '2':
            # Para celular
            imei1 = request.form['imei1']
            imei2 = request.form['imei2']
            SIMcard = request.form['SIMcard']

            try:
                cursor = conexion.cursor()
                cursor.execute("INSERT INTO celular (nombre, marca, modelo, imei1, imei2, SIMcard, serial) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (nombre, marca, modelo, imei1, imei2, SIMcard, serial))
                conexion.commit()
                cursor.execute("SELECT @@IDENTITY")
                celular_id = cursor.fetchone()[0]

                cursor.execute("INSERT INTO equipo (estadoequipo_id, celular_id, fcreacion, tipoequipo_id, observaciones) VALUES (?, ?, ?, ?, ?)",
                               (1, celular_id, datetime.datetime.now(), 4, observaciones))
                conexion.commit()
                cursor.close()
                flash('El celular ha sido agregado correctamente', 'success')
                return redirect(url_for('mostrar_equipos'))
            except pyodbc.Error as ex:
                print(ex)
                flash('Ocurrió un error al agregar el celular', 'error')
                return redirect(url_for('agregar_equipo'))

    tipos_equipos = obtener_tipos_equipo()
    

    return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos)
#---------------------------------------------------
#Editar equipo:
@app.route('/editar_equipo/<int:id>', methods=['GET', 'POST'])
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
                
                return render_template('editar_equipo.html', equipo=equipo_dict, detalle_equipo=detalle_equipo, estados=estados, tipo_equipo=tipo_equipo)
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
                # Convertir la fila del equipo a un diccionario
                equipo_dict = dict(zip((column[0] for column in cursor.description), equipo))

                nombre = request.form['nombre']
                marca = request.form['marca']
                modelo = request.form['modelo']
                serial = request.form['serial']
                estado_equipo_id = request.form['estado_equipo']
                observaciones = request.form['observaciones']

                print("Datos recibidos del formulario:", nombre, marca, modelo, serial, estado_equipo_id, observaciones)

                # Actualizar el detalle del equipo en la tabla correspondiente
                if 'unidad_id' in equipo_dict and equipo_dict['unidad_id'] is not None:
                    cursor.execute("UPDATE unidad SET nombre_e = ?, marca = ?, modelo = ?, serial = ? WHERE id = ?",
                               (nombre, marca, modelo, serial, equipo_dict['unidad_id']))
                    print("Filas afectadas por la actualización en la tabla unidad:", cursor.rowcount)
                elif 'celular_id' in equipo_dict and equipo_dict['celular_id'] is not None:
                    cursor.execute("UPDATE celular SET nombre = ?, marca = ?, modelo = ?, serial = ? WHERE id = ?",
                               (nombre, marca, modelo, serial, equipo_dict['celular_id']))
                    print("Filas afectadas por la actualización en la tabla celular:", cursor.rowcount)

                cursor.execute("UPDATE equipo SET estadoequipo_id = ?, observaciones = ? WHERE id = ?",
                               (estado_equipo_id, observaciones, id))
                print("Filas afectadas por la actualización en la tabla equipo:", cursor.rowcount)

                conexion.commit()
                cursor.close()

                flash('La información del equipo ha sido actualizada correctamente', 'success')
                return redirect(url_for('mostrar_equipos'))
            else:
                flash('No se encontró ningún equipo con el ID proporcionado', 'error')
                return redirect(url_for('mostrar_equipos'))
        
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al intentar actualizar la información del equipo', 'error')
            return redirect(url_for('mostrar_equipos'))



    elif request.method == 'GET':
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM equipo WHERE id = ?", (id,))
            equipo = cursor.fetchone()

            if equipo:
                equipo_dict = dict(zip((column[0] for column in cursor.description), equipo))  
                detalle_equipo = None
                if equipo_dict['unidad_id'] is not None:
                    cursor.execute("SELECT * FROM unidad WHERE id = ?", (equipo_dict['unidad_id'],))
                    detalle_equipo = cursor.fetchone()
                elif equipo_dict['celular_id'] is not None:
                    cursor.execute("SELECT * FROM celular WHERE id = ?", (equipo_dict['celular_id'],))
                    detalle_equipo = cursor.fetchone()

                estados = obtener_estados_equipo()
                
                cursor.close()
                return render_template('editar_equipo.html', equipo=equipo_dict, detalle_equipo=detalle_equipo, estados=estados)
            else:
                flash('No se encontró ningún equipo con el ID proporcionado', 'error')
                return redirect(url_for('mostrar_equipos'))

        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al cargar la información del equipo', 'error')
            return redirect(url_for('mostrar_equipos'))

    else:
        flash('Método HTTP no permitido', 'error')
        return redirect(url_for('mostrar_equipos'))
#-------------------------------------------------------
#Funcion Eliminar equipo
@app.route('/eliminar_equipo/<int:id>', methods=['POST'])
def eliminar_equipo(id):
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM equipo WHERE id = ?", (id,))
        conexion.commit()
        cursor.close()
        flash('El equipo ha sido eliminado correctamente', 'success')
    except pyodbc.Error as ex:
        print(ex)
        flash('Ocurrió un error al eliminar el equipo', 'error')
    
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
# Función para listar todas las áreas y permitir la edición en la misma página
@app.route('/listar_areas', methods=['GET', 'POST'])
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
            # Eliminar un tipo de equipo
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
            # Editar un tipo de equipo
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

    # Obtener la lista de tipos de equipo
    tipos_equipos = obtener_tipos_equipos()

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
#----------------------------------
# Mostrar equipos disponibles


#----------------------------------------------------------
#Asignar equipo

@app.route('/asignar_equipo', methods=['GET', 'POST'])
def asignar_equipo():
    cursor = conexion.cursor()

    if request.method == 'POST':
        equipo_id = request.form['equipo_id']
        persona_id = request.form['persona_id']
        fecha_asignacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        observaciones = request.form['observaciones']
        archivo_pdf = request.files['archivo_pdf']

        if archivo_pdf and archivo_pdf.filename.endswith('.pdf'):
            filename = f"{persona_id}_{equipo_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo_pdf.save(filepath)

            try:
                cursor.execute("""
                    INSERT INTO asignacion_equipo (equipo_id, persona_id, fecha_asignacion, observaciones, archivo_pdf)
                    VALUES (?, ?, ?, ?, ?)
                """, (equipo_id, persona_id, fecha_asignacion, observaciones, filename))
                conexion.commit()

                cursor.execute("UPDATE equipo SET estadoequipo_id = 2 WHERE id = ?", (equipo_id,))
                conexion.commit()

                flash('Equipo asignado correctamente', 'success')
                return redirect(url_for('index'))
            except pyodbc.Error as ex:
                print(f'Error al asignar el equipo: {ex}')
                flash('Error al asignar el equipo', 'error')
                return redirect(url_for('index'))
            finally:
                cursor.close()
        else:
            flash('El archivo debe ser un PDF', 'error')
            return redirect(url_for('asignar_equipo'))

    else:
        try:
            cursor.execute("""
                SELECT
                    equipo.id,
                    tipoequipo.nombre AS tipo_nombre,
                    COALESCE(unidad.nombre_e, celular.nombre) AS nombre_equipo
                FROM equipo
                LEFT JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id
                LEFT JOIN unidad ON equipo.unidad_id = unidad.id
                LEFT JOIN celular ON equipo.celular_id = celular.id
                WHERE equipo.estadoequipo_id = 1
            """)
            equipos = cursor.fetchall()

            cursor.execute("SELECT id, nombres FROM persona")
            personas = cursor.fetchall()

            return render_template('asignar_equipo.html', personas=personas, equipos=equipos)
        except pyodbc.Error as ex:
            print(f'Error al obtener los datos: {ex}')
            flash('Error al cargar la página de asignación', 'error')
            return redirect(url_for('index'))
        finally:
            cursor.close()
#--------------------------------------------------------------------------
# devolucion:
@app.route('/devolver_equipo/<int:equipo_id>', methods=['GET', 'POST'])
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
            filename = f"{equipo_id}_devolucion_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            fecha_devolucion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

                flash('Equipo devuelto correctamente', 'success')
                return redirect(url_for('index'))
            except pyodbc.Error as ex:
                print(f'Error al devolver el equipo: {ex}')
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
                    ae.archivo_pdf_devolucion
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
                return redirect(url_for('index'))

            return render_template('devolver_equipo.html', asignacion=asignacion)
        except pyodbc.Error as ex:
            print(f'Error al obtener los datos: {ex}')
            flash('Error al cargar la página de devolución', 'error')
            return redirect(url_for('index'))
        finally:
            cursor.close()



#---------------------------------------------------------------------------
#Detalle persona
@app.route('/detalle_persona/<int:persona_id>')
def detalle_persona(persona_id):
    try:
        cursor = conexion.cursor()

        # Obtener información de la persona
        cursor.execute("SELECT persona.*, area.nombre AS area_nombre FROM persona INNER JOIN area ON persona.area_id = area.id WHERE persona.id = ?", (persona_id,))
        persona = cursor.fetchone()

        # Obtener equipos asignados a la persona
        cursor.execute("SELECT * FROM equipo WHERE persona_id = ?", (persona_id,))
        equipos = cursor.fetchall()
        
        cursor.close()

        return render_template('detalle_persona.html', persona=persona, equipos=equipos)
    except pyodbc.Error as ex:
        print(f'Error al obtener los detalles de la persona: {ex}')
        flash('Error al obtener los detalles de la persona', 'error')
        return redirect(url_for('index'))
#----------------------------------------------------
# Detalle equipo

@app.route('/detalle_equipo/<int:equipo_id>')
def detalle_equipo(equipo_id):
    try:
        cursor = conexion.cursor()

        # Obtener detalles del equipo
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
                equipo.celular_id,
                celular.nombre AS nombre_celular,
                celular.marca AS marca_celular,
                celular.modelo AS modelo_celular,
                celular.serial AS serial_celular,
                celular.imei1,
                celular.imei2,
                celular.SIMcard
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

        # Obtener historial de asignaciones y devoluciones
        cursor.execute("""
            SELECT
                asignacion_equipo.fecha_asignacion,
                asignacion_equipo.fecha_devolucion,
                asignacion_equipo.observaciones,
                asignacion_equipo.archivo_pdf,
                asignacion_equipo.archivo_pdf_devolucion,
                persona.nombres AS persona_nombre,
                persona.apellidos AS persona_apellidos
            FROM asignacion_equipo
            JOIN persona ON asignacion_equipo.persona_id = persona.id
            WHERE asignacion_equipo.equipo_id = ?
            ORDER BY asignacion_equipo.fecha_asignacion DESC
        """, (equipo_id,))
        historial = cursor.fetchall()

        cursor.close()

        return render_template('detalle_equipo.html', equipo=[equipo_detalle], historial=historial)
    
    except pyodbc.Error as ex:
        print(f'Error al obtener los detalles del equipo: {ex}')
        flash('Error al obtener los detalles del equipo', 'error')
        return redirect(url_for('index'))
#-----------------------------------------------------------------------
@app.route('/equipos')
def lista_equipos():
    try:
        cursor = conexion.cursor()

        cursor.execute("""
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
        """)
        equipos = cursor.fetchall()
        cursor.close()

        return render_template('lista_equipos.html', equipos=equipos)
    
    except pyodbc.Error as ex:
        print(f'Error al obtener la lista de equipos: {ex}')
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





###############################
###############################
###############################

if __name__ == '__main__':
    app.run(debug=True)



