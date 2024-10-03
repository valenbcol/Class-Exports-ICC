# Importamos los paquetes a utilizar

import numpy as np
import pandas as pd
import os
os.getcwd()
"""
    Esta clase toma el archivo enviado de exportaciones y subasigna funciones segun
    se desea agregando por pais o por rubro generando un respectivo metodo para cada uno.
    Se debe insertar dos parametros al iniciar la clase, la ubicacion del archivo en el servidor
    con un "r" antepuesto al string; y como segundo parametro se debe poner el nombre de la columna que
    se quiere agregar a la base, definido como "mes - año" por ejemplo: "Junio - 2022".

"""


os.getcwd()
os.chdir(fr"C:\\Documents\\DEP\\Comercio")
os.getcwd()

# Creamos una clase llamada Export para englobar el entorno donde se realizan las transformaciones de la base

class Exports:
    
    # Importamos el excel con los meses previos agrupados por pais
    dbpais = pd.read_excel(os.getcwd() + fr"\\Exportpais.xlsx")
    # Asignamos el type de datos a la columna codigo como 'Category' en pandas
    dbpais['Cód.'] = dbpais['Cód.'].astype('category')
    # Importamos el excel con los meses previos agrupados por rubro
    dbrubro = pd.read_excel(os.getcwd() + fr"\\Exportrubros.xlsx")
    dbrubro['Producto'] = dbrubro['Producto'].astype('category')
    # Definimos la funcion init necesaria para cada clase, ES NECESARIA para definir las variables dentro del entorno
    # Por un lado la variable db, el cual sera un objeto string con la ubicacion de la base que nos envian de
    # Comercio internacional. Por otro lado, el mes que asignamos, definiendo como string tambien para definir
    # el nombre de la columna
    def __init__(self, db, mes):
        # Se utiliza self (creo) para indicarle a Python que busque la clase Exports (por eso self) y definamos
        # un atributo de la clase
        self.db = db
        self.mes = mes
        # Definimos la funcion que agrupa por pais
    def Pais(self, exportar=0):
        # Importamos la base de datos bruta con los datos de comercio
        tempdb = pd.read_csv(self.db, sep=";", encoding='latin-1')
        print(tempdb.head())
        # Agrupamos por rubro
        tempdb = tempdb.groupby('Pais').sum()
        # Extraemos solo la columna de los valores por pais
        valor = tempdb['FOB_Dolar']
        # La nombramos como el mes insertado "self.mes"
        valor.rename(self.mes, inplace=True)
        # Definimos una fila con el codigo 100 que sea la suma total de las exports
        valor.loc[100] = valor.sum()
        print(valor.head())
        # Unimos merge esta Panda.Series a la Panda.Dataframe
        output = pd.merge(self.dbpais, valor, how='left',
                          left_on='Cód.', right_index=True)
        print(output)
        # Rellenamos codigos sin match con NA
        output[self.mes]=output[self.mes].fillna(0)
        # Exportamos si le damos el parametro previo
        if exportar == 1:
               output.to_excel(os.getcwd() + fr'\\Exportpais.xlsx', sheet_name='Datos', index=False)
        else: 
            return output
    

    def Rubro(self, exportar=0):
        tempdb=pd.read_csv(self.db, sep=";", encoding='latin-1')
        print(tempdb.head())
        tempdb=tempdb.groupby('Rubro').sum()
        valor=tempdb['FOB_Dolar']
        valor.rename(self.mes, inplace=True)
        valor.loc['1']=valor.sum()
        print(valor.head())
        output=pd.merge(self.dbrubro, valor, how='left',
        left_on='Codigo', right_index=True)
        print(output)
        output[self.mes]=output[self.mes].fillna(0)
        print("Listo!")
        if exportar == 1:
            output.to_excel(os.getcwd() + fr'\\Exportrubros.xlsx', sheet_name='Datos', index=False)
        else:
            return output
    

# Definimos la ubicacion de la base de datos bruta
dbase=os.getcwd() + fr"\Datos\Datos_Conf-TN-2304.csv"
# Creamos la clase con el archivo y el mes que queremos añadir
Exports1=Exports(dbase, 'Abril - 2023')
# Elegimos la agrupacion
PorRubro=Exports1.Rubro(1)
Exports1.Pais(1)




