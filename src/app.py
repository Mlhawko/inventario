from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)

app.config['SECRET_KEY'] = 'chf24'

server = 'CHFNB239\\SQLEXPRESS'
db = 'inventarioTI'
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
# Index mostrar personas
@app.route('/')
def index():
    try:
        cursor = conexion.cursor()
        cursor.execute('''SELECT Persona.nombres, Persona.correo, Area.nombre AS area_nombre
            FROM Persona
            INNER JOIN Area ON Persona.area_id = Area.id ''')
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
        cursor.execute('''SELECT Persona.id, Persona.nombres, Persona.correo, Area.nombre AS area_nombre
            FROM Persona
            INNER JOIN Area ON Persona.area_id = Area.id ''')
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
            cursor.execute("INSERT INTO Persona (nombres, correo, area_id) VALUES (?, ?, ?)", (nombre, correo, area_id))
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
            cursor.execute("UPDATE Persona SET nombres=?, correo=?, area_id=? WHERE id=?", (nombre, correo, area_id, id))  # Cambio aquí: usar area_id en lugar de area
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
            cursor.execute("SELECT * FROM Persona WHERE id=?", (id,))
            persona = cursor.fetchone()
            
            # Obtener la lista de áreas
            cursor.execute("SELECT * FROM Area")
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
        cursor.execute("DELETE FROM Persona WHERE id=?", (id,))
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
# Mostrar equipos disponibles
@app.route('/equipos/disponibles')
def mostrar_equipos_disponibles():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM Equipo WHERE id_estado = 1")  # Suponiendo que 1 es el ID del estado "disponible"
        equipos = cursor.fetchall()
        cursor.close()
        return render_template('equipos_disponibles.html', equipos=equipos)
    except pyodbc.Error as ex:
        print(f'Error al obtener los equipos disponibles: {ex}')
        flash('Error al obtener los equipos disponibles', 'error')
        return redirect(url_for('index'))

#----------------------------------------------------------
# CRUD de equipos:
@app.route('/mostrar_equipos')
def mostrar_equipos():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT Equipo.id, Equipo.nombre, TipoEquipo.nombre AS tipo_nombre FROM Equipo INNER JOIN TipoEquipo ON Equipo.tipo_equipo_id = TipoEquipo.id")
        equipos = cursor.fetchall()
        cursor.close()
        return render_template('mostrar_equipos.html', equipos=equipos)
    except pyodbc.Error as ex:
        print(f'Error al obtener los equipos: {ex}')
        flash('Error al obtener los equipos', 'error')
        return redirect(url_for('index'))


@app.route('/equipos/agregar', methods=['GET', 'POST'])
def agregar_equipo():
    if request.method == 'POST':
        nombre = request.form['nombre_equipo']
        tipo_equipo_id = request.form['tipo_equipo'] 

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO Equipo (nombre, tipo_equipo_id, id_estado) VALUES (?, ?, ?)", (nombre, tipo_equipo_id, 1))
            conexion.commit()

            # Obtener el ID del equipo recién insertado
            equipo_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            if tipo_equipo_id == '1':  # ID del tipo de equipo Notebook
                memoria_ram = request.form['memoria_ram']
                capacidad_disco = request.form['capacidad_disco']
                cursor.execute("INSERT INTO Notebook (tipo_equipo_id, nombre, memoria_ram, capacidad_disco) VALUES (?, ?, ?, ?)", (tipo_equipo_id, nombre, memoria_ram, capacidad_disco))
            elif tipo_equipo_id == '2':  # ID del tipo de equipo Celular
                modelo = request.form['modelo']
                sistema_operativo = request.form['sistema_operativo']
                cursor.execute("INSERT INTO Celular (tipo_equipo_id, nombre, modelo, sistema_operativo) VALUES (?, ?, ?, ?)", (tipo_equipo_id, nombre, modelo, sistema_operativo))

            conexion.commit()
            cursor.close()
            flash('Equipo agregado correctamente', 'success')
            return redirect(url_for('mostrar_equipos'))
        except pyodbc.Error as ex:
            print(f'Error al agregar el equipo: {ex}')
            flash('Error al agregar el equipo', 'error')
            return redirect(url_for('agregar_equipo'))
    else:
        tipos_equipos = obtener_tipos_equipos()
        return render_template('agregar_equipo.html', tipos_equipos=tipos_equipos)





from flask import render_template

@app.route('/equipos/<int:id>/editar', methods=['GET', 'POST'])
def editar_equipo(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE Equipo SET nombre = ?, tipo = ? WHERE id = ?", (nombre, tipo, id))
            conexion.commit()
            cursor.close()
            flash('Equipo editado correctamente', 'success')
            return redirect(url_for('mostrar_equipos'))
        except pyodbc.Error as ex:
            print(f'Error al editar el equipo: {ex}')
            flash('Error al editar el equipo', 'error')
            return redirect(url_for('editar_equipo', id=id))
    else:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Equipo WHERE id = ?", (id,))
            equipo = cursor.fetchone()

            # Obtener lista de tipos de equipo desde la base de datos
            tipos_equipos = obtener_tipos_equipos()

            cursor.close()
            return render_template('editar_equipo.html', equipo=equipo, tipos_equipos=tipos_equipos)
        except pyodbc.Error as ex:
            print(f'Error al obtener el equipo: {ex}')
            flash('Error al obtener el equipo', 'error')
            return redirect(url_for('mostrar_equipos'))



@app.route('/equipos/<int:id>/eliminar', methods=['POST'])
def eliminar_equipo(id):
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM Equipo WHERE id = ?", (id,))
        conexion.commit()
        cursor.close()
        flash('Equipo eliminado correctamente', 'success')
        return redirect(url_for('mostrar_equipos'))
    except pyodbc.Error as ex:
        print(f'Error al eliminar el equipo: {ex}')
        flash('Error al eliminar el equipo', 'error')
        return redirect(url_for('mostrar_equipos'))
#---------------------------------------------------
#CRUD Area
# Función para listar todas las áreas y permitir la edición en la misma página
@app.route('/listar_areas', methods=['GET', 'POST'])
def listar_areas():
    if request.method == 'GET':
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM Area')
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
            cursor.execute("UPDATE Area SET nombre = ? WHERE id = ?", (nombre, id_area))
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
            cursor.execute("INSERT INTO Area (nombre) VALUES (?)", (nombre,))
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
            cursor.execute("DELETE FROM Area WHERE id = ?", (id,))
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
                    cursor.execute("INSERT INTO TipoEquipo (nombre) VALUES (?)", (nombre,))
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
                cursor.execute("DELETE FROM TipoEquipo WHERE id = ?", (tipo_equipo_id,))
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
                    cursor.execute("UPDATE TipoEquipo SET nombre = ? WHERE id = ?", (nuevo_nombre, tipo_equipo_id))
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

def obtener_tipos_equipos():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM TipoEquipo")
        tipos_equipos = cursor.fetchall()
        cursor.close()
        return tipos_equipos
    except pyodbc.Error as ex:
        print(ex)
        return None


#--------------------------------------------------------------------------------
# Obtener areas
def obtener_areas():
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM Area")
        areas = cursor.fetchall()
        cursor.close()
        return areas
    except pyodbc.Error as ex:
        print(ex)
        return None

if __name__ == '__main__':
    app.run(debug=True)


