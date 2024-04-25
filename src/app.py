from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

server = 'CHFNB239\\SQLEXPRESS'
db = 'inventarioTI'
user = 'sa'
password = 'Chilefilms23'

try:
    conexion = pyodbc.connect(
        'DRIVER={ODBC DRIVER 17 FOR SQL server};SERVER=' + server + ';DATABASE=' + db + ';UID=' + user + ';PWD=' + password
    )
    print('Conexión exitosa')
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(sqlstate)
    print ('Error al intentar conectarse')

@app.route('/')
def index():
    try:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM Persona')
        personas = cursor.fetchall()
        cursor.close()
        return render_template('index.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)

@app.route('/adjuntos')
def equipos():
    equipos = []
    try:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM Equipos')
        rows = cursor.fetchall()
        for row in rows:
            equipos.append({"id": row.id, "nombre": row.nombre, "tipo": row.tipo, "cantidad": row.cantidad})
        cursor.close()
    except pyodbc.Error as ex:
        print(ex)
    return render_template('detalle.html', equipos=equipos)

@app.route('/agregar_personas', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        area = request.form['area']
        try:
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO Persona (nombre, correo, area) VALUES (?, ?, ?)', (nombre, correo, area))
            conexion.commit()
            cursor.close()
            return redirect(url_for('index'))
        except pyodbc.Error as ex:
            print(ex)
    return render_template('agregar_persona.html')

@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
def editar_persona(id):
    try:
        cursor = conexion.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            area = request.form['area']
            cursor.execute('UPDATE Persona SET nombre=?, correo=?, area=? WHERE id=?', (nombre, correo, area, id))
            conexion.commit()
            cursor.close()
            return redirect(url_for('index'))
        else:
            cursor.execute('SELECT * FROM Persona WHERE id=?', (id,))
            persona = cursor.fetchone()
            cursor.close()
            return render_template('editar_persona.html', persona=persona)
    except pyodbc.Error as ex:
        print(ex)

@app.route('/personas/<int:id>/eliminar', methods=['POST'])
def eliminar_persona(id):
    try:
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM Persona WHERE id=?', (id,))
        conexion.commit()
        cursor.close()
        return redirect(url_for('index'))
    except pyodbc.Error as ex:
        print(ex)

@app.route('/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_equipo(id):
    if request.method == 'GET':
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM Equipos WHERE id = ?', (id,))
            equipo = cursor.fetchone()
            cursor.close()
            return render_template('modificar.html', equipo=equipo)
        except pyodbc.Error as ex:
            print(ex)
            return redirect(url_for('index'))
    elif request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        cantidad = request.form['cantidad']
        try:
            cursor = conexion.cursor()
            if id == -1:  # Agregar nuevo equipo
                cursor.execute('INSERT INTO Equipos (nombre, tipo, cantidad) VALUES (?, ?, ?)', (nombre, tipo, cantidad))
            else:  # Modificar equipo existente
                cursor.execute('UPDATE Equipos SET nombre = ?, tipo = ?, cantidad = ? WHERE id = ?', (nombre, tipo, cantidad, id))
            conexion.commit()
            cursor.close()
            return redirect(url_for('index'))
        except pyodbc.Error as ex:
            print(ex)
            return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar_equipo(id):
    try:
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM Equipos WHERE id = ?', (id,))
        conexion.commit()
        cursor.close()
    except pyodbc.Error as ex:
        print(ex)
    return redirect(url_for('index'))

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_equipo():
    if request.method == 'GET':
        return render_template('agregar.html')
    elif request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        cantidad = request.form['cantidad']
        try:
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO Equipos (nombre, tipo, cantidad) VALUES (?, ?, ?)', (nombre, tipo, cantidad))
            conexion.commit()
            cursor.close()
            return redirect(url_for('index'))
        except pyodbc.Error as ex:
            print(ex)
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
