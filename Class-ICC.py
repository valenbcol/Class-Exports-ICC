import numpy as np
import pandas as pd
import matplotlib as plt

class ICC:
    ''' 
    Esta clase se inicia con dos inputs, los precios del mes anterior y los precios del mes actual. 
    Una de sus funciones es la de "Check" la cual chequea si los precios tiene variaciones anomalas segun los siguientes criterios:
        -La variacion mensual esta por debajo del -9% y mayor al 25%
        -La diferencia absoluta de los precios es mayor a $50
    Una vez que los identifica genera un excel llamado 
    '''
    
    def __init__(self, precios0, precios1):
        self.precios0 = precios0
        self.precios1 = precios1
        
    def Check(self,exportar=0):
        dbprecios0 = pd.read_excel(self.precios0,skiprows=1)                       #Importo los precios de t-1
        dbprecios0['Cod. Insumo']=dbprecios0['Cod. Insumo'].astype('str')          #A la columna correspondiente, se la transforma para que quede como string
        marcadummy0=dbprecios0['Cod. Insumo'].str.contains('_M').fillna(False)     #Creo el objeto de los insumos que tienen marca ("_M")
        iniciacon1=dbprecios0['Cod. Insumo'].str.startswith('1').fillna(False)     #Creo el objeto para reconocer los que empiezan con 0
        largosuf0=dbprecios0['Cod. Insumo'].str.len()>6                            
        cat10dummy0=iniciacon1&largosuf0
        dbprecios0['Cod. Insumo'][(~marcadummy0)&(~cat10dummy0)]='0'+dbprecios0['Cod. Insumo'][(~marcadummy0)&(~cat10dummy0)].str[:] 
        #lo que hace la linea 25 es...primero va a la columna Cod. insumo. Dentro de esa columna, los insumos que NO pertenezcan al objeto
        #marcadummy y que NO pertenezcan al otro grupo (el simbolo "~"), les agrega un 0 previo al codigo ese. Luego, le indica que los
        #codigos sean str. De esta manera, quedan todos los Cod. Insumo con el mismo largo (de dígitos)
        dbprecios0.loc[dbprecios0['Cod. Insumo']=='0101003']
        dbprecios0['Fecha']=dbprecios0['Mes'].astype('string')+'-'+dbprecios0['Año'].astype('string')  #Crea columna fecha
        dbprecios0['Fecha']=pd.to_datetime(dbprecios0['Fecha'],format='%m-%Y')   #Le agrega formato de fecha
        dbprecios1 = pd.read_excel(self.precios1,skiprows=1)                     #Se hace lo mismo con los precio de t 
        dbprecios1['Cod. Insumo']=dbprecios1['Cod. Insumo'].astype('str')
        marcadummy1=dbprecios1['Cod. Insumo'].str.contains('_M').fillna(False)   #Se identifican segun los criterios 
        iniciacon1=dbprecios1['Cod. Insumo'].str.startswith('1').fillna(False)
        largosuf1=dbprecios1['Cod. Insumo'].str.len()>6            #Esta linea nos dice si la longitud en digitos es > 6
        cat10dummy1=iniciacon1&largosuf1
        dbprecios1['Cod. Insumo'][(~marcadummy1)&(~cat10dummy1)]='0'+dbprecios1['Cod. Insumo'][(~marcadummy1)&(~cat10dummy1)].str[:]
        dbprecios1['Fecha']=dbprecios1['Mes'].astype('string')+'-'+dbprecios1['Año'].astype('string')
        dbprecios1['Fecha']=pd.to_datetime(dbprecios1['Fecha'],format='%m-%Y')
        dbprecios=pd.merge(dbprecios1,dbprecios0,how='outer',on=['Cod. Informante','Cod. Insumo'],suffixes=['_t','_t-1'])  #Se mergean ambas bases
        solomes0=dbprecios[dbprecios['Precio_t'].isna()]         #Diferencia los de t-1 y los de t
        solomes1=dbprecios[dbprecios['Precio_t-1'].isna()]       #Idem
        dbprecios_m=dbprecios.dropna(subset=['Precio_t-1','Precio_t'])     #Crea nuevo objeto sin los na en los precios
        #Agregamos los items que sean marca a la lista de item sin importar la marca
        dbprecios_m['Cod. Insumo']=dbprecios_m['Cod. Insumo'].str.replace('_M','')
        dbprecios_m=dbprecios_m.drop_duplicates(keep='first',subset=['Cod. Informante', 'Cod. Insumo', 'Marca_t','Precio_t'])
        #Elimina los duplicados xq algunos estan cargados con marca y sin marca (sin "_M"); entonces para que no se los cuente x2
        dbprecios_m['Variacion']=(dbprecios_m['Precio_t']/dbprecios_m['Precio_t-1'])-1    #Genera la variacion %
        dbprecios_m['Diff']=dbprecios_m['Precio_t']-dbprecios_m['Precio_t-1']             #Genera la variacion abs
        precioraro=dbprecios_m[((dbprecios_m['Variacion']>0.25) | (dbprecios_m['Variacion']<-0.09))&(dbprecios_m['Diff'].abs()>50)]
        #se identifica los precios que tienen variaciones raras, seguramente explicadas por errores en las cargas de datos
        #para enviarlas de nuevo al Encuestador, y chequee a que se pueden deber estos errores y las corrija
        añoactual=dbprecios1['Fecha'][0].year
        mesactual=dbprecios1['Fecha'][0].month
        if exportar==1:
            precioraro.to_excel(fr'C:\\Documents\\DEP\\ICC\\Revision\PreciosRevision{mesactual}_{añoactual}.xlsx', sheet_name='Datos', index=False)
            dbprecios_m.to_excel(fr'C:\\Documents\\DEP\\ICC\\dbprecios{mesactual}_{añoactual}.xlsx', sheet_name='Datos', index=False)
        return dbprecios_m, precioraro
        #Se exportan los precios raros para enviarlos a encuestador

    def VarxCap(self,exportar=0):
        dbprecios_m,precioraro=self.Check()
        oferta=(dbprecios_m['Tipo de Precio_t']=='O') | (dbprecios_m['Tipo de Precio_t-1']=='O')       #Se reconoce los precios que son ofertas
        dbprecios_m=dbprecios_m[~oferta]                             #Se los elimina a los mismos
        capvar=dbprecios_m.groupby('Cod. Insumo').mean()       #Esta linea agarra a todos los insumos que tengan el mismo codigo, y genera
        #la media de todas las columnas correspondientes (Las variaciones estan incluidas, que finalmente es lo que nos importa)
        capvar['Cod. Insumo']= capvar.index      #Aclara que la columna "Cod. ins" sea el indice del df
        capvar['cantp']=dbprecios_m.groupby('Cod. Insumo').count()['Precio_t']     #Genera una nueva columna que nos indica la cantidad de 
        #precios existentes para cada insumo. De nuevo, el groupby junta a todos los que tenga el mismo cod ins, y en vez de sacarle la media
        #como se hizo antes, cuenta la cantidad de precios existentes (xq se le aclara luego con precio_t)
        ICCCrudo = pd.read_excel(r"C:\\Documents\\DEP\\ICC\\ICCseries.xlsx",dtype={'Cod.':str},usecols=['Cod.'])
        ICCVars=pd.merge(ICCCrudo,capvar,how='left', left_on='Cod.', right_index=True)  #mergea los capvar con este nuevo archivo (ver en excel)
        #para entenderlo bien
        Familia=pd.read_excel(r"C:\\Documents\\DEP\\ICC\\Familias.xlsx",dtype={'Cod. Insumo':str,'Familia':str},usecols=['Cod. Insumo','Familia'])
        #se crea el objeto flia para agruparlos. por ej, los cementos (independientemente del tamaño) son una familia
        ICCVars=pd.merge(ICCVars,Familia,how='left',left_on='Cod.', right_on='Cod. Insumo')
        ICCVars.index=ICCVars.index.astype(str)
        #Creo Dummy para Monopolios, genero lista de codigos que son monopolios para subset mas abajo
        MonopolioDummy = ["0301004", "0304006", "0301008", "0403001", "0403002", "0403003", "0403004", "0403005", "0403006",
                "0406001", "0801071", "0801076", "0806012", "0806013", "0301001", "0301005", "0301007",
                "0301008", "0303003", "0303009", "0303013", "0304006",
                "0304008", "0308001", "0308002", "0308003", "0313001", "0313003", "0316006", "0405008",
                "0501001", "0501002", "0501003", "0801072", "0801073", "0801076", "0802008", "0802015",
                "0802017", "0803007", "0805002", "0806009", "0906003", "0906006", "0906007"]
        #La condicion ICCVars['Cod.'].isin(MonopolioDummy) lo que hace es crear una serie de booleans que indica si el codigo esta en la lista MonopolioDummy
        #Entonces si tiene menos de 3 articulos y NO esta (por eso pongo el ~(condicion) ) le asigna un valor #N/A

        ICCVars['Variacion'][ICCVars['cantp']<3 & ~(ICCVars['Cod.'].isin(MonopolioDummy))]=np.nan

        Familiagroup=ICCVars.groupby('Familia').mean()['Variacion']     #Saca variaciones de cada flia 
        Familiagroup=Familiagroup.rename('VarFamilia')

        ICCVars=pd.merge(ICCVars,Familiagroup,how='left', on='Familia',validate='m:1') #Sigue agregando las otras columnas 
        ICCVars['Variacion']=ICCVars['Variacion'].fillna(ICCVars['VarFamilia'])  #agrega las variaciones de las familias
        ICCVars['Variacion'][(ICCVars['cantp']<3) & ~(ICCVars['Cod.'].isin(MonopolioDummy))] = ICCVars['VarFamilia'] 
        #Cuando haya menos de 3 precios y NO sea monop, se le otorga la variacion de la familia
        ICCVars=ICCVars[ICCVars['Cod.'].str.len()==7]
        ICCVars['Categoria']=ICCVars['Cod.'].str[0:2]        #Diferencia categoria
        ICCVars['Subcategoria']=ICCVars['Cod.'].str[0:4]     #Diferencia subcat
        subcat=ICCVars.groupby('Subcategoria').mean()        #Media de subcategorias
        subcat['Cod.']= subcat.index
        subcat['Categoria']=subcat['Cod.'].str[0:2]
        cat=subcat.groupby('Categoria').mean()
        cat['Cod.']= cat.index
        ICCVars=ICCVars.append(subcat)
        ICCVars=ICCVars.append(cat)
        ICCVars['Variacion']=ICCVars['Variacion'].fillna('*')    #Agrega * para los na
        ICCVars=ICCVars.sort_values('Cod.')                      #ordena de acuerdo al codigo
        añoactual=ICCVars['Año_t'][10].astype('int64')
        mesactual=ICCVars['Mes_t'][10].astype('int64')

        ICCVars["Tiene_var_flia"]=np.where((ICCVars['Variacion']==ICCVars['VarFamilia']),2,np.NaN)                #Les doy el valor 2 los que tienen = var que
        ICCVars = ICCVars[['Cod.','Año_t','Mes_t','Cod. Informante','Precio_t','Usuario_t',                       # la flia
        'Año_t-1', 'Mes_t-1', 'Precio_t-1', 'Usuario_t-1', 'Variacion', 'Tiene_var_flia','Diff',                  #Reordeno las columnas para que quede simi-
        'Cod. Insumo_x', 'cantp', 'Familia', 'Cod. Insumo_y', 'VarFamilia',                                       #lar al de Andrea
        'Categoria', 'Subcategoria']]

        if exportar==1:
            ICCVars.to_excel(fr'C:\\Documents\\DEP\\ICC\\Resultados\\CapVar{mesactual}_{añoactual}.xlsx', sheet_name='Datos', index=False)
        return ICCVars




preciost_1=r"C:\\Documents\\DEP\\ICC\\Datos\\Precios2304.xlsx"
preciost=r"C:\\Documents\\DEP\\ICC\\Datos\\Precios2305.xlsx"
ICC= ICC(preciost_1,preciost)
precios, revisar = ICC.Check(1)
Resultados = ICC.VarxCap(0)

listadetablas=precios.groupby('Cod. Insumo').count()[['Precio_t-1','Precio_t']]

insumocod=precios.iloc[:,5:7]
listadetablas=pd.merge(insumocod,listadetablas,how='right',left_on='Cod. Insumo',right_index=True)
listadetablas.to_excel(fr'C:\\Documents\\DEP\\ICC\\Resultados\\cantidadedatos.xlsx', sheet_name='Datos')
