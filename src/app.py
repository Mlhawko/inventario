
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
        cursor.execute('''SELECT persona.id, persona.nombres, persona.correo, area.nombre AS area_nombre
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
        nombre = request.form['nombre']
        correo = request.form['correo']
        area_id = request.form['area']

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO persona (nombres, correo, area_id) VALUES (?, ?, ?)", (nombre, correo, area_id))
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
        return redirect(url_for('index'))

@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
def editar_persona(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        area_id = request.form['area']  # Cambio aquí: obtener el ID del área seleccionada
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE persona SET nombres=?, correo=?, area_id=? WHERE id=?", (nombre, correo, area_id, id))  # Cambio aquí: usar area_id en lugar de area
            conexion.commit()
            cursor.close()
            flash('Persona actualizada correctamente', 'success')
            return redirect(url_for('listar_personas'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Error al actualizar la persona', 'error')
            return redirect(url_for('editar_persona', id=id))
    else:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM persona WHERE id=?", (id,))
            persona = cursor.fetchone()
            
            # Obtener la lista de áreas
            cursor.execute("SELECT * FROM area")
            areas = cursor.fetchall()
            
            cursor.close()
            return render_template('editar_persona.html', persona=persona, areas=areas)  # Pasar las áreas a la plantilla
        except pyodbc.Error as ex:
            print(ex)
            return 'Error al obtener la persona'


# Ruta para eliminar una persona
@app.route('/eliminar_persona/<int:id>', methods=['POST'])
def eliminar_persona(id):
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM persona WHERE id=?", (id,))
        conexion.commit()
        cursor.close()
        flash('Persona eliminada correctamente', 'success')
        return redirect(url_for('index'))
    except pyodbc.Error as ex:
        print(ex)
        flash('Error al eliminar la persona', 'error')
        return redirect(url_for('index'))
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
        cursor.execute("SELECT equipo.id, tipoequipo.nombre AS tipo_nombre, unidad.nombre_e AS unidad_nombre FROM equipo INNER JOIN tipoequipo ON equipo.tipoequipo_id = tipoequipo.id LEFT JOIN unidad ON equipo.id = unidad.id")
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
@app.route('/agregar_equipo', methods=['GET', 'POST'])
def agregar_equipo():
    
    if request.method == 'POST':
        seccion = request.form['seccion']
    
        if seccion == '1' :
            nombre_e = request.form['nombre']
            marca = request.form['marca']
            modelo = request.form['modelo']
            ram = request.form['ram']
            procesador = request.form['procesador']
            almc = request.form['almc']
            perif = request.form['perif']
            numsello = request.form['numsello']
            serial = request.form['serial']
            numproducto = request.form['numproducto']
            tipoimpresion = request.form['tipoimpresion']
            tipo_equipo_id = request.form['tipoequipo']
            estado_equipo_id = request.form['estadoequipo_id']
            observaciones = request.form['observaciones']

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO unidad (nombre_e, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (nombre_e, marca, modelo, ram, procesador, almc, perif, numsello, serial, numproducto, tipoimpresion))
            conexion.commit()

            cursor.execute("SELECT @@IDENTITY")
            unidad_id = cursor.fetchone()[0]
            
            # Insertar en la tabla equipo
            cursor.execute("INSERT INTO equipo (estadoequipo_id, unidad_id, fcreacion, tipoequipo_id, observaciones) VALUES (?, ?, ?, ?, ?)",
                           (estado_equipo_id, unidad_id, datetime.datetime.now(), tipo_equipo_id, observaciones))
            
            conexion.commit()
            cursor.close()
            flash('El equipo ha sido agregado correctamente', 'success')
            return redirect(url_for('mostrar_equipos'))
        except pyodbc.Error as ex:
            print(ex)
            flash('Ocurrió un error al agregar el equipo', 'error')
            return redirect(url_for('agregar_equipo'))

    tipos_equipos = obtener_tipos_equipo()

    return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos)



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



