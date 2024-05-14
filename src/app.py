
import pyodbc
from flask import Flask, flash, redirect, render_template, request, url_for
import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'chf24'

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
#---------------------------------------------------------

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
    try:
        cursor = conexion.cursor()
        cursor.execute('''SELECT persona.id, persona.nombres, persona.correo, area.nombre AS area_nombre
                  FROM persona
                  INNER JOIN area ON persona.area_id = area.id ''')

        personas = cursor.fetchall()
        cursor.close()
        return render_template('index.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)
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
@app.route('/equipos/disponibles')
def mostrar_equipos_disponibles():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM Equipo WHERE estado_id = 1")
        equipos = cursor.fetchall()
        cursor.close()
        return render_template('equipos_disponibles.html', equipos=equipos)
    except pyodbc.Error as ex:
        print(f'Error al obtener los equipos disponibles: {ex}')
        flash('Error al obtener los equipos disponibles', 'error')
        return redirect(url_for('index'))

#----------------------------------------------------------
#Asignar equipo

@app.route('/asignar_equipo/<int:equipo_id>', methods=['GET', 'POST'])
def asignar_equipo(equipo_id):
    if request.method == 'POST':
        persona_id = request.form['persona_id']
        fecha_asignacion = request.form['fecha_asignacion']
        estado_equipo_id = request.form['estado_equipo_id']

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO Movimiento (equipo_id, persona_id, estado_id, tipo_mov, fecha_mov) VALUES (?, ?, ?, ?, ?)",
                           (equipo_id, persona_id, estado_equipo_id, 'Asignación', fecha_asignacion))
            
            cursor.execute("UPDATE Equipo SET persona_id = ?, id_estado = ? WHERE id = ?", (persona_id, estado_equipo_id, equipo_id))
            
            conexion.commit()
            cursor.close()
            flash('Equipo asignado correctamente', 'success')
            return redirect(url_for('mostrar_equipos_disponibles'))
        except pyodbc.Error as ex:
            print(f'Error al asignar el equipo: {ex}')
            flash('Error al asignar el equipo', 'error')
            return redirect(url_for('mostrar_equipos_disponibles'))
    else:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM equipo WHERE id = ?", (equipo_id,))
            equipo = cursor.fetchone()

            cursor.execute("SELECT id, nombres FROM persona")  # Obtener lista de personas
            personas = cursor.fetchall()

            cursor.execute("SELECT id, nombre FROM estadoequipo")  # Obtener lista de estados de equipo
            estados_equipo = cursor.fetchall()

            cursor.close()
            return render_template('asignar_equipo.html', equipo_id=equipo_id, equipo=equipo, personas=personas, estados_equipo=estados_equipo)
        except Exception as ex:
            print(f'Error al obtener equipo: {ex}')
            flash('Error al cargar la página de asignación', 'error')
            return redirect(url_for('mostrar_equipos_disponibles'))
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
@app.route('/detalle_equipo/<int:equipo_id>/<int:tipo_equipo_id>')
def detalle_equipo(equipo_id, tipo_equipo_id):
    try:
        cursor = conexion.cursor()

        # Obtener información básica del equipo
        cursor.execute("SELECT equipo.*, tipoequipo.nombre AS tipo_equipo FROM equipo INNER JOIN tipoequipo ON equipo.tipoequipo_id=tipo_equipo_id WHERE equipo.id = ?", (equipo_id,))
        equipo = cursor.fetchone()

        if tipo_equipo_id == 1:  # tipo 1 es para notebook
            cursor.execute("SELECT * FROM Notebook WHERE id = ?", (equipo_id,))
            tipo_equipo = cursor.fetchone()
        elif tipo_equipo_id == 2:  # tipo 2 es para celular
            cursor.execute("SELECT * FROM Celular WHERE id = ?", (equipo_id,))
            tipo_equipo = cursor.fetchone()

        cursor.close()

        return render_template('detalle_equipo.html', equipo=equipo, tipo_equipo=tipo_equipo)
    except pyodbc.Error as ex:
        print(f'Error al obtener los detalles del equipo: {ex}')
        flash('Error al obtener los detalles del equipo', 'error')
        return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)



