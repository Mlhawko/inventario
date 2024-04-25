from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Configuración de la conexión a la base de datos
server = 'CHFNB239\SQLEXPRESS'
db = 'inventarioTI'
user =  'sa'
password = 'Chilefilms23'

conexion = pyodbc.connect(
    'DRIVER={ODBC DRIVER 17 FOR SQL server};SERVER='+server+';DATABASE='+db+';UID='+user+';PWD='+password
)

# CRUD de personas
@app.route('/')
def listar_personas():
    try:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM Persona')
        personas = cursor.fetchall()
        cursor.close()
        return render_template('listar_personas.html', personas=personas)
    except pyodbc.Error as ex:
        print(ex)

@app.route('/personas/agregar', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombres = request.form['nombres']
        correo = request.form['correo']
        area = request.form['area']
        try:
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO Persona (nombres, correo, area) VALUES (?, ?, ?)', (nombres, correo, area))
            conexion.commit()
            cursor.close()
            return redirect(url_for('listar_personas'))
        except pyodbc.Error as ex:
            print(ex)
    return render_template('agregar_persona.html')

@app.route('/personas/<int:id>/editar', methods=['GET', 'POST'])
def editar_persona(id):
    try:
        cursor = conexion.cursor()
        if request.method == 'POST':
            nombres = request.form['nombres']
            correo = request.form['correo']
            area = request.form['area']
            cursor.execute('UPDATE Persona SET nombres=?, correo=?, area=? WHERE id=?', (nombres, correo, area, id))
            conexion.commit()
            cursor.close()
            return redirect(url_for('listar_personas'))
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
        return redirect(url_for('listar_personas'))
    except pyodbc.Error as ex:
        print(ex)

if __name__ == '__main__':
    app.run(debug=True)
