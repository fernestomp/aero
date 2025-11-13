import warnings
import matplotlib as mpl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import seaborn as sns
sns.set()
plt.style.use('seaborn-white')
sns.set_style("whitegrid")

# para evitar warning
#https://github.com/pandas-dev/pandas/issues/18301
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import itertools

import warnings
import re #expresiones regulares
from pylatex import Document, Section, Command, Subsection, Figure
from pylatex.utils import italic, NoEscape


class analisisWT():
    """
        Clase que lee datos de densidad de potencia de 16 aerogeneradores y velociades de viento a partir de un
        archivo de excel y ofrece diferentes fuciones como el ploteo de las series de tiempo y un resumen de
        produccion de potencia y energía.
    """
    def __init__(self, rutaxls,numaerog =16):

        """
        Parameters
        ----------
        rutaxls : str
            Ruta del archivo excel.
        numaerog : str
            Numero de aerogeneradores del archivo excel.
        dataWindRaw : dataframe
            Datos de viento directos del archivo de excel.
        dataPotActRaw: DataFrame
            Datos de potencia activa directos del archivo de excel.
        dataPotIns: DataFrame
            Datos de potencia instantenea calculados a partir de la
            densidad de potencia.
        mintreshold: int
            Potencia minima aceptable, si es menor, se toma como outlier.
        maxtreshold: int
            Potencia maxima aceptable, si es mayor, se toma como outlier.
        potinsmin: float
            Potencia instantena minimina calculada de todos los aerognereadores.
        potinsmax: float
            Potencia instanta maxima calculada de todos los aerogeneradores.
        velmin: float
            Velocidad minima registrada de todos los aerogeneradores.
        velmax: float
            Velocidad maxima registrada de todos los aerogeneradores.
        totalregistros: int
            Total de registros de datos.
        """

        self.rutaxls=rutaxls
        self.numaerog=numaerog
        self.dataWindRaw=[]#datos de viento directo del excel
        self.dataPotActRaw=[]#datos de potencia activa acumulada directo del excel
        self.dataPotIns=[] #datos de potencia instantenea calculada a partir de potencia activa
        self.mintreshold = -6e4#potencia minima aceptable (clipping)
        self.maxtreshold =  3e6#potencia maxima aceptable (clipping)
        self.potinsmin = np.nan #potencia instantanea minima
        self.potinsmax = np.nan
        self.velmin = np.nan
        self.velmax = np.nan
        self.totalregistros =None
        self.__cargar_xls(rutaxls)

    def __cargar_xls(self,rutaxls):

        """
        Carga los datos del archivo excel.

        Parameters
        ----------
        rutaxls: str
            Ruta del archivo excel.
        """

        print('Abriendo archivo excel:' + rutaxls+'...')
        if 'xls' not in locals(): #revisar si ya se cargo el archivo excel para no cargarlo de nuevo
            xls = pd.ExcelFile(rutaxls)
        print('Archivo abierto.')
#        print('Nombre de las hojas:')
#         for n,sn in enumerate(xls.sheet_names): #nombre de las hojas del archivo
#             print(' %i: %s'%(n+1,sn))


        self.__cargar_datos(xls,self.numaerog)
    #-----------------------------------------------------------------------------------
    def __cargar_datos(self,xls,numaerog):
        """
        Crea los Dataframes con los que se van a trabajar.

        Parameters
        ----------
        xls: pandas ExcelFile
            Archivo que contiene los datos del excel pero en formato pandas ExcelFile.

        numaerog: int
            'Numero de aerogeneradores presentes en los datos'
        """
        #nombre de las columnas (PAC= potencia acumulada, AWS = ambient wind speed)
        headagtap =['PCTimeStamp']#lista con los headers del dataframe de los aerogeneradores
        headws =['PCTimeStamp']
        headagpi =[]#no necesita el pctimestamp por que es copia de un df con index timestamp

        for i in range(numaerog):
            headagtap.append('WTG{:02d}_PAC'.format(i+1))#de esta forma incluye 2 ceros a la izquierda
            headagpi.append('WTG{:02d}_PI'.format(i+1))#de esta forma incluye 2 ceros a la izquierda
            headws.append('WTG{:02d}_AWS'.format(i+1))#de esta forma incluye 2 ceros a la izquierda

        #crear dataframe temporal de las potencias (hoja 1)
        #es parse() porque ya cargue el archivo con pd.ExcelFile()
        dfWTG_TAP_raw = xls.parse(sheet_name='Tot_act_pow',index_col=0,names=headagtap)
        dfWTG_AWS_raw = xls.parse(sheet_name='Wind_speed_av',index_col=0,names=headws)
        print('Comprobando si faltan fechas...')
        #revisar que el indice de las fechas este completo, si no esta completo hace un desastre
        #en los datos de 16wt en la velocidad de viento faltan dos pctimestamp al final
        if dfWTG_TAP_raw.index.isnull().any():
            print('Warning, faltan fechas en las potencias,completando automaticamente')
            warnings.warn("Faltan fechas en las potencias,completando automaticamente")
            newidx  =pd.date_range(dfWTG_TAP_raw.index.min(),freq='10min',periods=len(dfWTG_TAP_raw))
            dfWTG_TAP_raw.reset_index(drop=True,inplace=True)
            dfWTG_TAP_raw.set_index(newidx,inplace=True)

        if dfWTG_AWS_raw.index.isnull().any():
            newidx =pd.date_range(dfWTG_AWS_raw.index.min(),freq='10min',periods=len(dfWTG_AWS_raw))
            #comparar indices, podria cambiar la condicion de isnull a una secuencia de fechas logica
            #se podria comparar la secuencia de fechas reales con una secuencia de fechas creadas automaticamente
            #asi se podria saber si faltan fechas o no estan en orden,aunque el reindex te detecta duplicados
            #a = list(dfWTG_AWS_raw.index)
            #b = list(newidx)
            #regresa una lista que no esta vacia
            #[i for i, j in zip(a, b) if not i == j]
            print('Warning, faltan fechas en las velocidades,completando automaticamente')
            warnings.warn("Faltan fechas en las velocidades,completando automaticamente")
            dfWTG_AWS_raw.reset_index(drop=True,inplace=True)
            dfWTG_AWS_raw.set_index(newidx,inplace=True)

        self.velmin = dfWTG_AWS_raw.min().min()
        self.velmax = dfWTG_AWS_raw.max().max()
        self.dataPotActRaw =dfWTG_TAP_raw
        self.dataWindRaw=dfWTG_AWS_raw
        #datos perdidos
        self.listpotperd =self.dataPotActRaw.loc[self.dataPotActRaw.isnull().any(axis=1), :].isnull().sum().to_list()
        self.listvelperd =self.dataWindRaw.loc[self.dataWindRaw.isnull().any(axis=1), :].isnull().sum().to_list()
        self.totalrowspot = len(self.dataPotActRaw)
        self.totalrowsvel = len(self.dataWindRaw)
        #totaldatpot = totalrowspot*nag #total de datos de potencia incluidos NA
        #mas elegante
        self.totaldatpot = sum(self.dataPotActRaw.count().to_list()) +sum(self.listpotperd)
        #totaldatvel = totalrowsvel*nag
        #mas elegante
        self.totaldatvel = sum(self.dataWindRaw.count().to_list()) +sum(self.listvelperd)
        #dataframe de datos perdidos
        self.dfperd =pd.DataFrame({'pot':self.listpotperd,'vel':self.listvelperd},index=range(1,self.numaerog+1))

        print('Procesando datos...')

        self.__procesar_datos(dfWTG_TAP_raw,dfWTG_AWS_raw,self.numaerog,headagpi)
    #-------------------------------------------------------------------------------------
    def __procesar_datos(self,dataPotRaw,dataWind,numaerog,headagpi):

        """
        Se procesan los datos, quitando datos en blanco, revisando fechas, calculando potencias, etc.
        Si la estructura del archivo excel cambia, este metodo debe cambiar.

        Parameters
        ----------
        dataPotRaw: DataFrame
            Datos de potencia directos del excel.

        dataWind: DataFrame
            Datos de viento directos del excel.

        numaerog: int
            Numero de aerogeneradores contenidos en los datos.

        headagpi: list
            Lista de headers.
        """
        #calculo de la potencia instantanea
        dfWTG_PI=dataPotRaw.copy()
        dfWTG_PI.columns=headagpi
        for i in range(numaerog):
           #calculo de la potencia instananea
            arrpotins = (dataPotRaw.iloc[1:,i].values-dataPotRaw.iloc[0:-1,i].values)* np.pi*45**2
            #repetir el ultimo valor de los datos para agregarlos directamente al df
            arrpotins =np.append(arrpotins,arrpotins[-1])
            dfWTG_PI[dfWTG_PI.columns[i]]=arrpotins


        ########################################################################################
        print('Comprobando consistencia en las fechas...')
        #para la grafica viento-potencia, comparar fechas registro por registro
        #si para el mismo numero de fila la fecha difiere mandar un error avisando esto
        #revisar si las fechas difieren al final, si es el caso, solo rellenar con None's
        #[1] si el numero de registros es igual en viento y potencia
        FLAG_IGUAL_NUM_REGISTROS = True
        if len(dataWind)  > len(dfWTG_PI):
            print('Warning, el numero de registros en las velocidades de viento es mayor que las potencias')
            warnings.warn("El numero de registros en las velocidades de viento es mayor que las potencias")
            #crear una lista con tres columnas: numero de registro, fecha1, fecha 2
            listavpZip = itertools.zip_longest(range(1,len(dataWind)+1),dataWind.index.values,
                                              dfWTG_PI.index.values)
            ultimafecha = dataWind.index.values[-1]
            FLAG_IGUAL_NUM_REGISTROS = False

        elif  len(dfWTG_PI) > len(dataWind):
            print('Warning, el numero de registros de las potencias es mayor que las velociades de viento')
            warnings.warn("El numero de registros de las potencias es mayor que las velociades de viento")
            #crear una lista con tres columnas: numero de registro, fecha1, fecha 2
            listavpZip = itertools.zip_longest(range(1,len(dfWTG_PI.index.values)+1),dfWTG_PI.index.values,
                                              dataWind.index.values)
            ultimafecha = dfWTG_PI.index.values[-1]
            FLAG_IGUAL_NUM_REGISTROS = False

        FLAG_DIFERENCIA_FECHAS = False
        if not FLAG_IGUAL_NUM_REGISTROS:
            #i: numero de registro, f1:fecha1, f2:fecha2
            listafechfalt = [[i,f1,f2] for i,f1,f2 in listavpZip if not f1 == f2]
            #hay discrepancias en las fechas
            FLAG_DIFERENCIA_FECHAS = False # de fechas diferentes
            if len(listafechfalt) >1:
                FLAG_DIFERENCIA_FECHAS=True

        #hay discrepancias en las fechas
        if FLAG_DIFERENCIA_FECHAS:
            #se supone que la segunda columna siempre van a ser fechas y la tercera None
            listafechaschec = [i[1] for  i in listafechfalt]
            #revisar si las fechas estan a final, comparando la fecha final con la ultima fecha que no concuerda
            if ultimafecha == listafechaschec[-1]:
                print('La ultima fecha de los datos corresponde con la fecha faltante, revisando si son consecutivas.')
            else:
                print('Las fechas faltantes no estan al final de los datos, terminando ejecucion.')
                raise ValueError('Las fechas faltantes no estan al final de los datos, terminando ejecucion.')
            #revisar si las fechas son consecutivas en intervalos de 10min
            FLAG_FECHAS_CONSECUTIVAS = True# las fechas son consecutivas
            for i in range(1,len(listafechaschec)):
                if  (listafechaschec[i]-listafechaschec[i-1]).astype('timedelta64[m]') == np.timedelta64(10,'m'):
                    FLAG_FECHAS_CONSECUTIVAS = True
                else:
                    FLAG_FECHAS_CONSECUTIVAS = False

            if FLAG_FECHAS_CONSECUTIVAS:
                    print('Las fechas son consecutivas, rellenando al final')
                    if len(dataWind)  > len(dfWTG_PI):
                        for i in range(len(listafechaschec)):
                            #irse a la ultima fila (mediante index) y agregar diez minutos
                            #esto crea una nueva fila al final con nans
                            dfWTG_PI.loc[dfWTG_PI.index.max() + np.timedelta64(10,'m')]= np.nan

                    else:
                        #crear una copia de las velociades de viento raw y llamarlas pro(cesadas)
                        for i in range(len(listafechaschec)):
                            #irse a la ultima fila (mediante index) y agregar diez minutos
                            #esto crea una nueva fila al final con nans
                            dataWind.loc[dataWind.index.max() + np.timedelta64(10,'m')]= np.nan

            else:
                #fechas no consecutivas
                print('Las fechas no son consecutivas, revisar')
                raise ValueError('Las fechas no son consecutivas, revisar')

        #######################################
        #reemplazando los valores de mintreshold y mastreshold de potencias por nan
        dfWTG_PI= dfWTG_PI.apply(lambda x: [y if y <= self.maxtreshold else np.nan for y in x])
        dfWTG_PI= dfWTG_PI.apply(lambda x: [y if y >= self.mintreshold else np.nan for y in x])
        self.potinsmin = dfWTG_PI.min().min()
        self.potinsmax = dfWTG_PI.max().max()
        self.dataPotIns = dfWTG_PI
        self.dataWindProc = dataWind

        ########################################################################################
        #energias producidas al año
        dictenergprodxWT={}
        for c in dfWTG_PI.columns:
            dictenergprodxWT[c] = (dfWTG_PI[c].sum()*1/6) #10 minutos es 1/6 de hora
        #energia producida por cada wt sumando la energía de todos los años
        self.energiaporWT=dictenergprodxWT
        #energia producida por todos los anios de todas las wt's
        self.energiaProdTotal =sum(self.energiaporWT.values())
        ########################################################################################
        #diccionario con las caracteristicas individuales de la wt (vel min, max, pot min, max,etc)
        dictcaractwt={}
        colnames = ['WTG{:02d}'.format(i) for i in range(1,self.numaerog+1)]
        yearnames =dataWind.index.strftime("%Y").unique().tolist()
        for i in range(16):
            dictcaractwt[colnames[i]] = {
                'velMin':dataWind[dataWind.columns[i]].min(),
                'velMax':dataWind[dataWind.columns[i]].max(),
                'potInstMin':dfWTG_PI[dfWTG_PI.columns[i]].min(),
                'potInstMax':dfWTG_PI[dfWTG_PI.columns[i]].max(),
                'EnerTotProd':dfWTG_PI[dfWTG_PI.columns[i]].sum()*1/6 #10 minutos es 1/6 de hora
            }
            #incluyendo energía por anio
            for y in yearnames:
                #obtener serie de tiempo de potencias instanteas y filtrar por año
                PIS = dfWTG_PI[dfWTG_PI.columns[i]]
                dictcaractwt[colnames[i]].update(
                    {'energia{}'.format(y):PIS[PIS.index.year ==int(y)].sum()*1/6}
                )
        #diccionario con datos caracteristicos de cada WT
        self.dictCaractWT = dictcaractwt
        ######################################################################################
        print('Procesamiento finalizado.')

    #-----------------------------------------------------------------------------------------
    def imprimir_reporte(self):

        '''
            Imprime un reporte de los datos en consola.
        '''

        print('Numero de aerogeneradores: {:d}'.format(self.numaerog))
        print('Minima velocidad de viento:{:0.2f}[m/s]'.format(self.velmin))
        print('Maxima velocidad de viento:{:0.2f}[m/s]'.format(self.velmax))
        print('Potencia instantanea minima:{:0.4E}W'.format(self.potinsmin))
        print('Potencia instantanea maxima:{:0.4E}W'.format(self.potinsmax))
        print('Minimo de potencia aceptable (clipping): {:,.2E}W'.format(self.mintreshold))
        print('Maximo de potencia aceptable (clipping): {:,.2E}W'.format(self.maxtreshold))
        print('----------------------')
        print('Numero total de filas potencia:{:,}'.format(self.totalrowspot))
        print('Numero total de filas viento:{:,}'.format(self.totalrowsvel))
        print('Numero total de datos potencia: {:,}'.format(self.totaldatpot))
        print('Numero total de datos viento: {:,}'.format(self.totaldatvel))
        print('-------------------------')
        #filas sin datos
        print('Datos perdidos:')
        print(self.dfperd)
        print('Total de potencias perdidas {:,} - {:,.3f}%'.format(
            sum(self.listpotperd),sum(self.listpotperd)*100/self.totaldatpot ))
        print('Total de velocidades perdidas{:,} - {:,.3f}%'.format(
        sum(self.listvelperd),sum(self.listvelperd)*100/self.totaldatvel ))
        print('------------------------')
        print('Energia producida por anio:')
        #energia producida por aerognerador por año
        l=[]
        for w in self.dictCaractWT:
            for st in list(self.dictCaractWT[w].keys()):
                x = re.findall("^energia2\d\d\d", st)
                if x:
                    l.append(x)
            print('{}:'.format(w))
            for j in l:
                print('    {}: {:,.2f}GWh'.format(j[0],self.dictCaractWT[w][j[0]]))
            print('------------')
            l.clear()
        print('--------------------------')
        print('Energia producida por aerogenerador (todos los anios):')
        for key in self.energiaporWT:
            print('{}: {:,.3f} GWh'.format(key[0:5],self.energiaporWT[key]/1e9))
        print('Energia total ({:d} WT) (todos los anios): {:,.4f} GWh'.format(self.numaerog,self.energiaProdTotal/1e9))
#-----------------------------------------------------------------------------
    def plot_ts_pot_ac(self,select_ts='all',mostrar=True):
        '''
        Muestra las gráficas de las series de tiempo de la potencia acumulada.

        Parameters
        ----------
        select_ts: lista
            Lista que contiene los numeros de los aerogeneradores que se van a graficar.

        mostrar: Bool
            Define si se muestran las gráficas o solo se guardan.

        '''

        self.__plot_timeseries(self.dataPotActRaw,'potac',select_ts,mostrar=mostrar)

    def plot_ts_pot_ins(self,select_ts='all',mostrar=True):

        '''
        Muestra las gráficas de las series de tiempo de la potencia instananea.

        Parameters
        ----------
        select_ts: lista
            Lista que contiene los numeros de los aerogeneradores que se van a graficar.

        mostrar: Bool
            Define si se muestran las gráficas o solo se guardan.

        '''
        self.__plot_timeseries(self.dataPotIns,'potins',select_ts,mostrar=mostrar)

    def plot_ts_viento(self,select_ts='all',mostrar=True):
        '''
        Muestra las gráficas de las series de tiempo de velociad de viento.

        Parameters
        ----------
        select_ts: lista
            Lista que contiene los numeros de los aerogeneradores que se van a graficar.

        mostrar: Bool
            Define si se muestran las gráficas o solo se guardan.

        '''
        mostrar=False
        self.__plot_timeseries(self.dataWindRaw,'wind',select_ts,mostrar=mostrar)


    def __plot_timeseries(self,df,serType, select_ts='all', width=20,height=10,dpi=80,mostrar=True):
        '''
        Método para crear las gráficas. Este método es usado por los otros que crean gráficas.

        Parameters
        ----------

        df: DataFrame
            Contiene los datos que se van a gráficar.

        serType: str
            Define que tipo de serie de tiempo se va a graficar (viento, potencia, etc.)

        width: int
            Ancho de la gráfica.

        height: int
            Alto de la gráfica.

        dpi: int
            dpi de la gráfica.

        select_ts: lista
            Lista que contiene los numeros de los aerogeneradores que se van a graficar.

        mostrar: Bool
            Define si se muestran las gráficas o solo se guardan.
        '''

        if serType=='potac' or serType =='potins':
            maxpot= df.max().max()
            minpot = df.min().min()
            #calcular el yticks del plot averiguando si esta en miles, millones,etc
            #revisar para exponentes mayores a 1e9
            pottemp =df.max().max()
            nzeros = 0
            while pottemp != 0:
                pottemp = pottemp // 10
                nzeros=nzeros+1
            expo = np.power(10,nzeros-1) #para el range del ylim

        elif serType=='wind':
            maxviento= df.max().max()
            minviento = df.min().min()

        if select_ts=='all':#seleccionar que columnas plotear
            ntotplots=len(df.columns)
            select_ts=range(1,ntotplots+1)
        else:
            ntotplots = len(select_ts)

        #convertir a array para restar un 1, pues el indice empieza en cero y no uno
        select_ts = np.subtract(select_ts,1)
        cols = 3
        rows =int(np.ceil(ntotplots/3))

        #como tienen que ser maximo tres columnas, uso diferentes coordenadas si son mas de 3 plots
        if ntotplots >3:
            #crear un sistema de coordenadas para usar un solo valor de i en el loop
            coord = [(j, i) for j in range(rows) for i in range(cols)]
        else:
            #incluye los plots que no existen para eliminarlos, pues se crean subplots de mas
            coord=range(cols*rows)

        #si le pongo el fisize da error (muy reciente) bug https://github.com/matplotlib/jupyter-matplotlib/issues/127
        fig, axs = plt.subplots(rows,cols, figsize=(width,height), facecolor='w', edgecolor='k',dpi=dpi)
        #fig, axs = plt.subplots(rows,cols, facecolor='w', edgecolor='k',dpi=dpi)
        for i, c in enumerate(df.columns[select_ts]):
            axs[coord[i]].scatter(df[c].index,df[c],s=1)
            axs[coord[i]].set_title(c)
            #dando formato al plot
            if serType=='potac' or serType =='potins':
                axs[coord[i]].ticklabel_format(
                    style='sci', axis='y', scilimits=(0, 0), useMathText=True)
                axs[coord[i]].set_ylim([minpot,maxpot])
                axs[coord[i]].set_yticks(np.arange(np.round(minpot,-(nzeros-2)), np.round(maxpot,-(nzeros-2))+0.5*expo,0.5*expo))
                axs[coord[i]].set(ylabel='Pot [W]')
            elif serType=='wind':
                axs[coord[i]].set_ylim([minviento,maxviento])
                axs[coord[i]].set_yticks(np.arange(0, np.ceil(maxviento) ,5))
                axs[coord[i]].set(ylabel='Vel [m/s]')


        #eliminar ejes sin datos, mas ineficiente? que add_subplot pero mas facil de entender
        for a in coord[i+1:]:
            plt.delaxes(axs[a])
        plt.tight_layout()
        print('guardando{}.png'.format(serType))
        plt.savefig('.\imagenes\{}.png'.format(serType))
        if mostrar:
            plt.ion()
            plt.show()
        else:
            plt.close(fig)

    def plot_vp(self,select_wt='all', width=20,height=10,dpi=80,mostrar=True):
        '''
        Método para crear la gráfica viento-potencia.

        Parameters
        ----------

        width: int
            Ancho de la gráfica.

        height: int
            Alto de la gráfica.

        dpi: int
            dpi de la gráfica.

        select_ts: lista
            Lista que contiene los numeros de los aerogeneradores que se van a graficar.

        mostrar: Bool
            Define si se muestran las gráficas o solo se guardan.

        '''

        df = self.dataPotIns.copy()
        maxpot= df.max().max()
        minpot = df.min().min()
        #calcular el yticks del plot averiguando si esta en miles, millones,etc
        pottemp =df.max().max()
        nzeros = 0
        while pottemp != 0:
            pottemp = pottemp // 10
            nzeros=nzeros+1
        expo = np.power(10,nzeros-1) #para el range del ylim

        if select_wt=='all':#seleccionar que columnas plotear
            ntotplots=len(df.columns)
            select_wt=range(1,ntotplots+1)
        else:
            ntotplots = len(select_wt)

        #convertir a array para restar un 1, pues el indice empieza en cero y no uno
        select_wt = np.subtract(select_wt,1)
        cols = 3
        rows =int(np.ceil(ntotplots/3))

        #como tienen que ser maximo tres columnas, uso diferentes coordenadas si son mas de 3 plots
        if ntotplots >3:
            #crear un sistema de coordenadas para usar un solo valor de i en el loop
            coord = [(j, i) for j in range(rows) for i in range(cols)]
        else:
            #incluye los plots que no existen para eliminarlos, pues se crean subplots de mas
            coord=range(cols*rows)

        fig, axs = plt.subplots(rows,cols, figsize=(width, height), facecolor='w', edgecolor='k',dpi=dpi)
        for i, c in enumerate(df.columns[select_wt]):
            #del nombre de las columnas me quedo con el WTGXX y le añado viento _AWS o potencia _PI
            axs[coord[i]].scatter(self.dataWindProc[c[0:5] + '_AWS'],self.dataPotIns[c[0:5] + '_PI'],s=1)
            axs[coord[i]].set_title(c)
            #dando formato al plot
            axs[coord[i]].ticklabel_format(
                style='sci', axis='y', scilimits=(0, 0), useMathText=True)
            axs[coord[i]].set_ylim([minpot,maxpot])
            axs[coord[i]].set_yticks(np.arange(np.round(minpot,-(nzeros-2)), np.round(maxpot,-(nzeros-2))+0.5*expo,0.5*expo))
            axs[coord[i]].set(ylabel='Pot [W]')

        #eliminar ejes sin datos, mas ineficiente? que add_subplot pero mas facil de entender
        for a in coord[i+1:]:
            plt.delaxes(axs[a])
        plt.tight_layout()
        print('Guardando plot vp')
        plt.savefig('.\imagenes\plotvp.png')
        if mostrar:
            plt.ion()
            plt.show()
        else:
            plt.close(fig)
    def generar_reporte_pdf(self):

        '''
        Genera un reporte en formato pdf.

        '''

        #creando imagenes
        self.plot_vp(mostrar=False)
        self.plot_ts_pot_ac(mostrar=False)
        self.plot_ts_viento(mostrar=False)
        self.plot_ts_pot_ins(mostrar=False)
        doc = Document()
        doc.preamble.append(Command('title', 'Reporte'))
        doc.preamble.append(Command('author', 'Ernesto Munguía'))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        doc.append(NoEscape(r'\maketitle'))

        # creating a pdf with title "the simple stuff"
        with doc.create(Section('Datos generales')):
            doc.append('Numero de aerogeneradores: {:d}\n'.format(self.numaerog))
            doc.append('Minima velocidad de viento:{:0.2f}[m/s]\n'.format(self.velmin))
            doc.append('Maxima velocidad de viento:{:0.2f}[m/s]\n'.format(self.velmax))
            doc.append('Potencia instantanea minima:{:0.4E}W\n'.format(self.potinsmin))
            doc.append('Potencia instantanea maxima:{:0.4E}W\n'.format(self.potinsmax))
            doc.append('Minimo de potencia aceptable (clipping): {:,.2E}W\n'.format(self.mintreshold))
            doc.append('Maximo de potencia aceptable (clipping): {:,.2E}W\n'.format(self.maxtreshold))
            doc.append('Energia total ({:d} WT) (todos los años): {:,.4f} GWh\n'.format(self.numaerog,self.energiaProdTotal/1e9))
            doc.append('\n')
            doc.append('Numero total de filas potencia:{:,}\n'.format(self.totalrowspot))
            doc.append('Numero total de filas viento:{:,}\n'.format(self.totalrowsvel))
            doc.append('Numero total de datos potencia: {:,}\n'.format(self.totaldatpot))
            doc.append('Numero total de datos viento: {:,}\n'.format(self.totaldatvel))
        with doc.create(Section('Datos perdidos')):
            for i in range(len(self.dfperd)):
                doc.append('WT{:d}: pot: {:d} vel: {:d}\n'.format(
                    i,int(self.dfperd.iloc[[i]].pot),int(self.dfperd.iloc[[i]].vel))
                    )
            doc.append('Total de potencias perdidas {:,} - {:,.3f}%\n'.format(
                sum(self.listpotperd),sum(self.listpotperd)*100/self.totaldatpot ))
            doc.append('Total de velocidades perdidas {:,} - {:,.3f}%\n'.format(
                sum(self.listvelperd),sum(self.listvelperd)*100/self.totaldatvel ))
        with doc.create(Section('Energía producida por año')):
            #energia producida por aerognerador por año
            l=[]
            for w in self.dictCaractWT:
                for st in list(self.dictCaractWT[w].keys()):
                    x = re.findall("^energia2\d\d\d", st)
                    if x:
                        l.append(x)
                doc.append('{}:\n'.format(w))
                for j in l:
                    doc.append('    {}: {:,.2f}GWh\n'.format(j[0],self.dictCaractWT[w][j[0]]/1e9))
                doc.append('------------\n')
                l.clear()

        with doc.create(Section('Energia producida por aerogenerador (todos los años):')):
            for key in self.energiaporWT:
                doc.append('{}: {:,.3f} GWh\n'.format(key[0:5],self.energiaporWT[key]/1e9))
        #como el reporte.pdf esta dentro de la carpeta reporte, la ruta tiene ../
        with doc.create(Section('Gráficas')):
            with doc.create(Subsection('Serie de tiempo del viento')):
                with doc.create(Figure(position='h!')) as imgvv:
                    imgvv.add_image('..\imagenes\wind.png', width='200px')
                    imgvv.add_caption('Serie de tiempo del viento')
            with doc.create(Subsection('Serie de tiempo de la potencia acumulada')):
                with doc.create(Figure(position='h!')) as imgpac:
                    imgpac.add_image('..\imagenes\potac.png', width='200px')
                    imgpac.add_caption('Serie de tiempo la potencia acumulada')
            with doc.create(Subsection('Serie de tiempo de la potencia instantanea')):
                with doc.create(Figure(position='h!')) as imgpotins:
                    imgpotins.add_image('..\imagenes\potins.png', width='200px')
                    imgpotins.add_caption('Serie de tiempo de la potencia instantanea')
            with doc.create(Subsection('Gráfica VP')):
                with doc.create(Figure(position='h!')) as imgvp:
                    imgvp.add_image('..\imagenes\plotvp.png', width='200px')
                    imgvp.add_caption('Gráfica viento-potencia')

        doc.generate_pdf('.\\reporte\\Reporte',compiler='pdflatex')
        #abrir pdf en el visor de pdf's
        os.system('.\\reporte\Reporte.pdf')
