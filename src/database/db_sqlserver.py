import pyodbc
import pandas as pd

server ='CHFNB239\SQLEXPRESS'
db = 'inventarioTI'
user =  'sa'
password = 'Chilefilms23'

try:
    conexion = pyodbc.connect(
        '  DRIVER={ODBC DRIVER 17 FOR SQL server};SERVER='+server+';DATABASE='+db+';UID='+user+';PWD='+password
    )
    print('Conexion exitosa')
except:
    print ('Error al intentar conectarse')

