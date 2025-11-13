# Notebook de funciones que usan los demás notebooks. Este debe contener las fuciones actualizadas
# %% md
# Procesamiento de datos
# %%

# Todo: organize imports
import pandas as pd
import numpy as np
import os
from pathlib import Path

def raw_to_datafr(xlsPath, xlsPathMfgCurve):
    """

    :param xlsPath: path to data file
    :param xlsPathMfgCurve: path to manufacturer power curve file
    :return: processed dataframes
    """
    # imprimir a consola
    os.write(1, b"Inciando procesamiento de datos...\n")

    # xlsPath = 'C:/Users/mungu/Documents/DatosWTG.xlsx'
    # xlsPath = 'C:\\Users\\ernesto\\Dropbox\\Doctorado\\datos\\DatosWTG.xlsx'
    # xlsPathMfgCurve = 'Curva de potencia vestas 90.xlsx'

    # dataVPxls = pd.read_excel(xlsPath,usecols=[0,1,2],index_col=0,names=['vViento','Pacw'])
    dataVPxls = pd.read_excel(xlsPath, usecols=[0, 1, 2], index_col=0)
    dataVPxls.columns = ['vViento', 'Pacw']
    # agrego la columna de potencia instantanea sin filtrar
    # dataVPxls['Pw']= (dataVPxls.iloc[1:,1].values-dataVPxls.iloc[0:-1,1]) * np.pi*45**2
    print('Total de registros: ' + str(len(dataVPxls)))
    # dfMfgCurve = pd.read_excel(xlsPathMfgCurve,usecols=[0,2],index_col=0,names=['pw'])#cambio esto en la nueva version
    dfMfgCurve = pd.read_excel(xlsPathMfgCurve, usecols=[0, 2], index_col=0)
    dfMfgCurve.columns = ['pw']
    # marcando los datos faltantes asignando un nan a la fila completa
    datamk = dataVPxls
    datamk.loc[datamk.isnull().any(axis=1), :] = np.nan
    # numero de filas sin datos
    print('Numero de filas sin datos')
    print(datamk.loc[datamk.isnull().any(axis=1), :].isnull().sum())

    # eliminando filas con NaN. Si busco la fecha anterior debe aparecer error.
    cleanData = datamk.dropna()

    ###calculando la potencia
    # la pontencia del archivo de excel es la densidad de potencia acumulada.
    # Se tiene que hacer la resta de la potencia siguiente a la anterio y multiplicar por pi*r^2
    # el radio es 45m
    # si se hace la resta con un array de numpy (values) si se puede restar
    # pues se hace elemento por elemento
    dataVP = cleanData.drop('Pacw', axis=1)
    dataVP['Pw'] = (cleanData.iloc[1:, 1].values - cleanData.iloc[0:-1, 1]) * np.pi * 45 ** 2

    # eliminar el ultimo valor pues es NaN
    dataVP.drop(dataVP.tail(1).index, inplace=True)

    # Eliminando outliers
    dataVP.drop([pd.to_datetime('2016-03-07 09:50:00')], inplace=True)
    # agregado para el reporte
    dataVP.drop([pd.to_datetime('2016-03-08 09:00:00')], inplace=True)
    dataVP.drop([pd.to_datetime('2016-01-02 06:40:00')], inplace=True)
    dataVP.drop([pd.to_datetime('2016-05-05 07:20:00')], inplace=True)
    dataVP.drop([pd.to_datetime('2016-05-23 23:00:00')], inplace=True)

    # leyendo la direccion del viento
    # dataDirVxls = pd.read_excel(xlsPath,sheet_name=1, usecols=[0,1],index_col=0,names=['Dir'])
    dataDirVxls = pd.read_excel(xlsPath, sheet_name=1, usecols=[0, 1], index_col=0)
    dataDirVxls.columns = ['Dir']
    # limpiando datos
    # marcando los datos faltantes asignando un nan a la fila completa
    datamkdir = dataDirVxls
    datamkdir.loc[datamkdir.isnull().any(axis=1), :] = np.nan
    # eliminando filas con NaN. Si busco la fecha anterior debe aparecer error.
    # tambien elimino el ultimo valor como lo hice en los datos de v y p
    # el copy es para que no me de la copy warning
    dataDir = datamkdir.dropna().copy()
    dataDir.drop(dataDir.tail(1).index, inplace=True)
    # eliminando del outlier de viento misma fecha que el de la pontencia
    dataDir.drop([pd.to_datetime('2016-03-07 09:50:00')], inplace=True)
    # agregado para el reporte
    dataDir.drop([pd.to_datetime('2016-03-08 09:00:00')], inplace=True)
    dataDir.drop([pd.to_datetime('2016-01-02 06:40:00')], inplace=True)
    dataDir.drop([pd.to_datetime('2016-05-05 07:20:00')], inplace=True)
    dataDir.drop([pd.to_datetime('2016-05-23 23:00:00')], inplace=True)

    direcvrad = np.deg2rad(dataDir['Dir'].values)
    velocidades = dataVP.iloc[:]['vViento'].values
    vecVel = [-np.sin(direcvrad) * velocidades, np.cos(direcvrad) * velocidades]
    vecVelnp = np.array(vecVel).transpose()
    # original sin timestamp
    # dfVecVel = pd.DataFrame(data=vecVelnp,columns=['vx','vy']
    # con timestamp
    dfVecVel = pd.DataFrame(data=vecVelnp, columns=['vx', 'vy'], index=dataVP.index)

    # datos direccion velocidad
    # print(len(dataVP))
    # print(len(dataDir))
    # dataDV = pd.concat([dataDir,dataVP.vViento],axis=1)
    dataVDP = pd.concat([dataVP.vViento, dataDir, dataVP.Pw], axis=1)
    # dataVcD =pd.concat([dataDir,dfVecVel],axis=1)
    # Datos en p.u.. Divido todos los datos entre el máximo del conjunto de datos

    # OPERATIONAL DATA
    # Rated power
    # 2,000 kW/2,200 kW
    # Cut-in wind speed	4 m/s
    # Cut-out wind speed	25 m/s
    # Re cut-in wind speed	23 m/s

    os.write(1, b"Fin del procesamiento de datos\n")
    return [dataVDP, dfVecVel, dfMfgCurve]


# %% md
# dataframe to cluster
# %%
# Todo: en el idx_centroids los numeros de los clusters no llevan la C, en el idx_centroids_sc si la (llevan,
# o) cambiar todo a que la lleven o que no la lleven'''

from sklearn import cluster, datasets
from scipy.spatial.distance import cdist


# crear clusters a partir de dataframes
def dataframe_to_cluster(dfvxvy, n_clusters, dfVP=None, n_subclu=0, clusters_data=None, subclusters_data=None,
                         datadir=None):
    """
        Descripcion:
        Esta funcion toma diferentes dataframes de entrada agrupa los datos por cluster.

        :param subclusters_data: data to do subclustering [wind,pow,dir]
        :param clusters_data: data to do clustering [wind,pow,dir]
        :param dfvxvy: dataframe con columnas vx y vy
        :param dfVP: dataframe con columnas de magnitud de viento y potencia
        :param n_clusters: numero de clusters
        :param n_subclu: Número de suclusters a calcular a partir de los n clusters calculados en un principio.
                  Si n_subclu=0 no se calcula ningun subcluster. Por defecto n_sub=0


        :return cl_ord: un array que contiene el número de cluster n ordenado de menor a mayor
            de las magnitudes de la velocidad de viento sin tomar en cuenta la direccion
        :return dfclvv: dataframe donde las componentes de velocidad de viento vx y vy estan
            agrupadas por cluster
        :return dfclpw: dataframe donde la potencia esta agrupada por cluster
        :return dfclvp: dataframe donde la potencia y la magnitud de viento esta agrupada por
            cluster
    """
    # check if dataframe with power values exist
    if dfVP is None:
        dfvp_is_empty = True
    else:
        dfvp_is_empty = False
    # '''- KMEANS -----------------------------------------------------------------------------------------'''
    if clusters_data == 'wind':
        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(dfvxvy)
        # buscar centroides en dataframes
        # https://stackoverflow.com/questions/42583995/get-the-centroid-row-index-from-k-means-clustering-using-sklearn
        min_dist = np.min(cdist(dfvxvy.values, kmeans.cluster_centers_, 'euclidean'),
                          axis=1)  # distancia minima a cada centroide
        Y = pd.DataFrame(min_dist, index=dfvxvy.index, columns=['PCTimeStamp'])
        Z = pd.DataFrame(kmeans.labels_, index=dfvxvy.index, columns=['cluster_ID'])
        # crea el dataframe
        PAP = pd.concat([Y, Z], axis=1)

    if clusters_data == 'pow' and not dfvp_is_empty:

        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(dfVP)
        # buscar centroides en dataframes
        min_dist = np.min(cdist(dfVP.values, kmeans.cluster_centers_, 'euclidean'), axis=1)
        Y = pd.DataFrame(min_dist, index=dfVP.index, columns=['PCTimeStamp'])
        Z = pd.DataFrame(kmeans.labels_, index=dfVP.index, columns=['cluster_ID'])
        PAP = pd.concat([Y, Z], axis=1)

    elif clusters_data == 'pow' and dfvp_is_empty:

        print('Power data is emtpy...')
        return None

    if clusters_data == 'dir' and not dfvp_is_empty:
        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(datadir)
        # buscar centroides en dataframes
        min_dist = np.min(cdist(dfVP.values, kmeans.cluster_centers_, 'euclidean'), axis=1)
        Y = pd.DataFrame(min_dist, index=dfVP.index, columns=['PCTimeStamp'])
        Z = pd.DataFrame(kmeans.labels_, index=dfVP.index, columns=['cluster_ID'])
        PAP = pd.concat([Y, Z], axis=1)

    elif clusters_data == 'dir' and dfvp_is_empty:

        print('Clustering with only direction and no power data not implemented yet.')
        return None

    # ordend e los cluster por magnitud de vv
    cl_magni = np.zeros(n_clusters)

    for i in range(n_clusters):
        vx = dfvxvy.vx.values[kmeans.labels_ == i]
        vy = dfvxvy.vy.values[kmeans.labels_ == i]
        cl_magni[i] = np.mean(np.sqrt(vx ** 2 + vy ** 2))  # magnitud de la vv
    cl_ord = np.argsort(cl_magni.argsort())  # ver https://github.com/numpy/numpy/issues/8757

    grouped = PAP.groupby(['cluster_ID'])  # agrupa por numero de clusters las distancias minimas
    idx_centroids = grouped.idxmin()  # encuentra el indice de la distanciam minima
    # agregando columnas de velocidadd de viento y potencia al dataframe de los centroides
    vxvy = dfvxvy.loc[idx_centroids.PCTimeStamp].values
    if dfvp_is_empty:
        idx_centroids = idx_centroids.assign(vx=vxvy[:, 0], vy=vxvy[:, 1])
    else:
        vvpot = dfVP.loc[idx_centroids.PCTimeStamp].values
        idx_centroids = idx_centroids.assign(vx=vxvy[:, 0], vy=vxvy[:, 1], vwind=vvpot[:, 0], pw=vvpot[:, 1])
        idx_centroids.sort_values(by='vwind', inplace=True)  # ordenar por velocidad de viento

    idx_centroids.reset_index(inplace=True)  # que ya no sea el cluster id el indice
    idx_centroids.index.set_names('cluster_ID_ord', inplace=True)  # ponerle el nombre al indice ordenado
    idx_centroids.index += 1  # paraque el indice empieze en uno y no exista cluster 0
    # agregando columna de magnitud de vv
    idx_centroids['wind_mag'] = cl_magni

    ## CREAR MULTIINDICE ---------------------------------------------------------------'''
    # CLUSTER VX,VY:
    # https://stackoverflow.com/questions/37835508/how-to-do-multi-column-from-tuples
    # nombre de las columnas del dataframe
    if dfvp_is_empty:
        colheadvv = []
        for i in range(n_clusters):
            colheadvv.append(('C' + str(i + 1), 'vx'))
            colheadvv.append(('C' + str(i + 1), 'vy'))
        dfclvv = pd.DataFrame()

        for i in range(n_clusters):
            dfclvv = pd.concat([dfclvv, dfvxvy.vx[kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                dfvxvy.vy[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1, ignore_index=True)
        # crear multiindice
        dfclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

    else:

        colheadvv = []
        colheadpw = []
        for i in range(n_clusters):
            colheadvv.append(('C' + str(i + 1), 'vx'))
            colheadvv.append(('C' + str(i + 1), 'vy'))
            colheadpw.append('C' + str(i + 1))
        dfclvv = pd.DataFrame()

        for i in range(n_clusters):
            dfclvv = pd.concat([dfclvv, dfvxvy.vx[kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                dfvxvy.vy[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1, ignore_index=True)
        # crear multiindice
        dfclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

        # CLUSTER POTENCIA:
        dfclpw = pd.DataFrame()
        for i in range(n_clusters):
            dfclpw = pd.concat([dfclpw, dfVP.Pw[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], ignore_index=True,
                               axis=1)
        dfclpw.columns = colheadpw

        # CLUSTER VIENTO POTENCIA:

        colheadvp = []
        for i in range(n_clusters):
            colheadvp.append(('C' + str(i + 1), 'vViento'))
            colheadvp.append(('C' + str(i + 1), 'Pw'))
        dfclvp = pd.DataFrame()

        for i in range(n_clusters):
            dfclvp = pd.concat([dfclvp, dfVP.vViento[kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                dfVP.Pw[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1, ignore_index=True)
        # crear multiindice
        dfclvp.columns = pd.MultiIndex.from_tuples(colheadvp)

    if clusters_data == 'direccion':
        # CLUSTER direccion viento
        colheadvp = []
        for i in range(n_clusters):
            colheadvp.append(('C' + str(i + 1), 'Dir'))
            colheadvp.append(('C' + str(i + 1), 'vViento'))
        dfcldv = pd.DataFrame()
        for i in range(n_clusters):
            dfcldv = pd.concat([dfcldv, datadir.vViento[kmeans.labels_ == (cl_ord == i)],
                                datadir.Dir[kmeans.labels_ == (cl_ord == i)]], axis=1, ignore_index=True)
        # crear multiindice
        dfcldv.columns = pd.MultiIndex.from_tuples(colheadvp)
    '''- CALCULAR SUBCLUSTERS ------------------------------------------------------------------- '''

    if n_subclu > 0:
        scl_centroids = []
        scl_labels = []
        scl_ncentroids = []
        idx_centroids_sc = pd.DataFrame()  # va almacenar los centroides de los subclusters
        # obtener los resultados del clusterizado
        for i in range(n_clusters):
            if subclusters_data == 'wind':
                dfclvvnoNA = dfclvv['C' + str(i + 1)].dropna()
                # buscando centroides con los subclusters
                kmeans_sc = cluster.KMeans(n_clusters=n_subclu, random_state=0, init='k-means++', n_init='auto').fit(
                    dfclvvnoNA)
                min_dist_sc = np.min(cdist(dfclvvnoNA.values, kmeans_sc.cluster_centers_, 'euclidean'), axis=1)
                Y_sc = pd.DataFrame(min_dist_sc, index=dfclvvnoNA.index, columns=['PCTimeStamp'])
                Z_sc = pd.DataFrame(kmeans_sc.labels_, index=dfclvvnoNA.index, columns=['subcluster_ID'])

            elif subclusters_data == 'pow':
                dfclvpnoNA = dfclvp['C' + str(i + 1)].dropna()
                # buscando centroides con los subclusters
                kmeans_sc = cluster.KMeans(n_clusters=n_subclu, random_state=0, init='k-means++', n_init='auto').fit(
                    dfclvpnoNA)
                min_dist_sc = np.min(cdist(dfclvpnoNA.values, kmeans_sc.cluster_centers_, 'euclidean'), axis=1)
                Y_sc = pd.DataFrame(min_dist_sc, index=dfclvpnoNA.index, columns=['PCTimeStamp'])
                Z_sc = pd.DataFrame(kmeans_sc.labels_, index=dfclvpnoNA.index, columns=['subcluster_ID'])
            else:
                print('Todavía no programado, haciendo subclusters en potencia')
                kmeans_sc = cluster.KMeans(n_clusters=n_subclu, random_state=0, init='k-means++', n_init='auto').fit(
                    dfclvp['C' + str(i + 1)].dropna())

            scl_centroids.append(kmeans_sc.cluster_centers_)
            scl_labels.append(kmeans_sc.labels_)
            scl_ncentroids.append(len(scl_centroids[i]))

            PAP_sc = pd.concat([Y_sc, Z_sc], axis=1)
            # poniendo index a los centroides de los subclusters
            grouped_sc = PAP_sc.groupby(['subcluster_ID'])
            idx_cent_sc = grouped_sc.idxmin()
            idx_cent_sc.index += 1
            # agregando columnas de velocidadd de viento y potencia al dataframe de los centroides
            vxvy_sc = dfvxvy.loc[idx_cent_sc.PCTimeStamp].values
            vvpot_sc = dfVP.loc[idx_cent_sc.PCTimeStamp].values
            idx_centroids_sc = pd.concat([idx_centroids_sc,
                                          idx_cent_sc.assign(vx=vxvy_sc[:, 0], vy=vxvy_sc[:, 1], vwind=vvpot_sc[:, 0],
                                                             pw=vvpot_sc[:, 1], cluster_ID='C' + str(i + 1))])
        # creando el multiindex fuera del ciclo for
        # idx_centroids_sc.set_index(['cluster_ID',idx_centroids_sc.index],inplace=True)

        idx_centroids_sc.reset_index(inplace=True)
        idx_centroids_sc.sort_values(['cluster_ID', 'vwind'], ascending=[1, 1], inplace=True)
        lst_num_sc = list(
            range(1, n_subclu + 1)) * n_clusters  # crea una lista de numeros para el subcluster [1,2,3..1,2,3]
        sc_idx_list = list(
            map(lambda x: 'SC' + str(x), lst_num_sc))  # le pone las letras SC [SC1,SC2,SC3...SC1,SC2,SC3]
        idx_centroids_sc = idx_centroids_sc.assign(subcluster_ID_ord=sc_idx_list)
        idx_centroids_sc.set_index(['cluster_ID', 'subcluster_ID_ord'], inplace=True)

        ############  ORDENAR CENTROIDES:  ordenar el orden de aparicion segun la magnitud de la vv
        scl_magni = np.zeros([n_clusters, n_subclu])
        scl_ord = []

        for i in range(n_clusters):

            for j in range(n_subclu):
                vx = dfclvv['C' + str(i + 1)].vx.dropna().values[scl_labels[i] == j]
                vy = dfclvv['C' + str(i + 1)].vy.dropna().values[scl_labels[i] == j]
                scl_magni[i][j] = np.mean(np.sqrt(vx ** 2 + vy ** 2))  # magnitud de la vv

            scl_ord.append(scl_magni[i].argsort())  # ver https://github.com/numpy/numpy/issues/8757

        # ORDENAR CENTROIDES
        for i in range(len(scl_centroids)):
            scl_centroids[i] = scl_centroids[i][scl_ord[i]]

        # CLUSTER VIENTO POTENCIA:
        colheadvp = []
        for i in range(n_clusters):
            for j in range(n_subclu):
                colheadvp.append(('C' + str(i + 1), 'SC' + str(j + 1), 'vViento'))
                colheadvp.append(('C' + str(i + 1), 'SC' + str(j + 1), 'Pw'))
        dfsclvp = pd.DataFrame()

        for i in range(n_clusters):
            for j in range(n_subclu):
                dfsclvp = pd.concat([dfsclvp, dfclvp['C' + str(i + 1)].dropna().vViento[scl_labels[i] == scl_ord[i][j]],
                                     dfclvp['C' + str(i + 1)].dropna().Pw[scl_labels[i] == scl_ord[i][j]]], axis=1,
                                    ignore_index=True)
        # crear multiindice
        dfsclvp.columns = pd.MultiIndex.from_tuples(colheadvp)

        # CLUSTER VX,VY:####################################################
        colheadvv = []
        for i in range(n_clusters):
            for j in range(n_subclu):
                colheadvv.append(('C' + str(i + 1), 'SC' + str(j + 1), 'vx'))
                colheadvv.append(('C' + str(i + 1), 'SC' + str(j + 1), 'vy'))
        dfsclvv = pd.DataFrame()

        for i in range(n_clusters):
            for j in range(n_subclu):
                dfsclvv = pd.concat([dfsclvv, dfclvv['C' + str(i + 1)].dropna().vx[scl_labels[i] == scl_ord[i][j]],
                                     dfclvv['C' + str(i + 1)].dropna().vy[scl_labels[i] == scl_ord[i][j]]], axis=1,
                                    ignore_index=True)
        # crear multiindice
        dfsclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

        # CLUSTER POTENCIA:
        dfsclpw = pd.DataFrame()
        colheadpw = []
        for i in range(n_clusters):
            for j in range(n_subclu):
                colheadpw.append(('C' + str(i + 1), 'SC' + str(j + 1)))

        for i in range(n_clusters):
            for j in range(n_subclu):
                dfsclpw = pd.concat([dfsclpw, dfclvp['C' + str(i + 1)].Pw.dropna()[scl_labels[i] == scl_ord[i][j]]],
                                    ignore_index=True, axis=1)
        dfsclpw.columns = pd.MultiIndex.from_tuples(colheadpw)

        #### buscar centroides para la grafica vv
        # obtener nombre de niveles
        n_subclu = len(dfsclvv.columns.levels[1])
        # numero total de clusters incluidos los subclusters
        n_tot_clusters = n_subclu * n_clusters
        # solo aplica cuando hay subclusters
        lev0 = dfsclvv.columns.get_level_values(0)
        lev1 = dfsclvv.columns.get_level_values(1)
        namcl = [(lev0[i], lev1[i]) for i in range(len(lev0))]
        colnames = namcl[::2]

        return dfsclvv, dfsclpw, dfsclvp, cl_ord, kmeans.cluster_centers_, idx_centroids, scl_ord, scl_centroids, idx_centroids_sc

    else:  # sin subclusters
        scl_ord = []
        scl_centroids = []
        idx_centroids_sc = []
        if dfvp_is_empty:
            return dfclvv, [], [], cl_ord, kmeans.cluster_centers_, idx_centroids, scl_ord, scl_centroids, idx_centroids_sc
        else:
            return dfclvv, dfclpw, dfclvp, cl_ord, kmeans.cluster_centers_, idx_centroids, scl_ord, scl_centroids, idx_centroids_sc


# %% md
# Eliminar clusters
# %%
''' FUNCION ACTUALIZADA A AGOSTO VER: https://pandas-docs.github.io/pandas-docs-travis/user_guide/advanced.html
La palabra labels cambio a codes
Changed in version 0.24.0: MultiIndex.labels has been renamed to MultiIndex.codes and MultiIndex.set_labels
to MultiIndex.set_codes.
'''


# Todo: POR ALGUNA RAZON NO PUEDO EJECUTAR LA MISMA FUNCION DOS VECES. ES COMO SI AFECTARA MIS VARIABLES ORIGINALES
def del_clusters(data, cltodel, idx_cent, idx_cent_sc=None, scl_ord=None, cl_type='cluster'):
    """
    Elimina clusters, subclusters, centroides de clusters o centroides de subclusters.
        Argumentos:
            dataf: dataframes a los que se eliminaran los clusters o subclusters.
            cltodel: lista o listas de clusters o subclusters a eliminar
            sc_centroids: lista que contiene los centroides. De esta lista se eliminaran los centroides
                            a partir de cltodel.
    """
    dflist = []
    for df in data:
        dflist.append(df.drop(cltodel, axis=1))
    # cambiar nombre por numero de centroides
    n_cl = len(df.columns.levels[0])
    n_subcl = len(df.columns.levels[1])
    # numero total de clusters incluidos los subclusters
    # sn_tot_clusters = (n_subcl*n_cl) -(len(df.columns.labels[0])-len(dflist[0].columns.labels[0]))/2
    # sn_tot_clusters = (n_subcl*n_cl) -(len(df.columns.codes[0])-len(dflist[0].columns.codes[0]))/2
    # eliminar centroides de clusters
    clnames = pd.unique(df.columns.get_level_values(0))
    lev0 = data[0].columns.get_level_values(0)
    lev1 = data[0].columns.get_level_values(1)
    namcl = [(lev0[i], lev1[i]) for i in range(len(lev0))]
    cl_sc_names = namcl[::2]
    # convertir a conjuntos
    a = set(cltodel)  # clusters a eliminar
    b = set(cl_sc_names)  # nombre de todos los clusters
    c = (b - a)  # a b lequito a
    cent_restantes = set(sorted(set(int(item[0][1:]) for item in c)))  # quito la letra C
    idx_cent_reales = set(idx_cent.index.values)
    idx_cent_todel = list(idx_cent_reales - cent_restantes)
    idx_centroids_clean = idx_cent.drop(idx_cent_todel)

    # eliminar centroides de los subclusters
    idx_centroidssc_clean = idx_cent_sc.drop(cltodel)

    return dflist, idx_centroids_clean, idx_centroidssc_clean


# %% md
# clusters a datos

# %%
def clust_to_data(dfv, dfvp):
    """
    Convierte el dataframe de los datos de vx,vy y potencia separados en clusters (C1-SC1-vx,vy) a datos con
    con tres columnas time,vx,vy o time,vv,pw.
    To-do:   Sigue perdiendo miles de registros, ¿porque hay registros na en el original?
    hay filas con solo nan en el original, en una prueba fueron como 4000"""
    dfv = dfv.copy()  # para que no afecte el original, si lo afecta el que esta como argumento
    dfvp = dfvp.copy()
    # Quitar multiindex
    dfv.columns = dfv.columns.map(''.join)
    dfv.reset_index(inplace=True)
    # list comprehension
    lvv = [dfv.iloc[i].dropna().values for i in range(len(dfv))]
    dfvxvy_clean = pd.DataFrame(lvv, columns=['PCTimeStamp', 'vx', 'vy'])
    dfvxvy_clean.dropna(inplace=True)  # hay filas de nan y se pierden miles de datos, revisar

    # Quitar multiindex
    dfvp.columns = dfvp.columns.map(''.join)
    dfvp.reset_index(inplace=True)
    # list comprehension
    lvp = [dfvp.iloc[i].dropna().values for i in range(len(dfvp))]
    dfvp_clean = pd.DataFrame(lvp, columns=['PCTimeStamp', 'vViento', 'Pw'])
    dfvp_clean.dropna(inplace=True)  # hay filas de nan y se pierden miles de datos, revisar

    return dfvxvy_clean, dfvp_clean


# %% md
# daymin2date
# %%
import datetime


def daymin2date(year, day, hour_min):
    """

    :param year: year when data was measured
    :param day: day
    :param hour_min: hour and minute in 24 hour format without separating character, e.g. 16:37 --> 1637
    :return: timestamp in format dd/mm/YYYY HH:MM
    """
    hourmin = hour_min.zfill(4)
    hour = hourmin[:2]
    minute = hourmin[2:]
    res = datetime.datetime.strptime(year + "-" + day + " " + hour + ":" + minute, "%Y-%j %H:%M").strftime(
        "%d/%m/%Y %H:%M")
    return res


# %% md
# Class kmData
# %%

# Todo: en el idx_centroids los numeros de los clusters no llevan la C, en el idx_centroids_sc si
# la llevan, o cambiar todo a que la lleven o que no la lleven
# Todo: Cambiar assign, o ver como puedo poner un variable como nombre, que en lugar de pw
# sea pw_col_name


from sklearn import cluster, datasets
from scipy.spatial.distance import cdist


class KMData:
    """
    Clase para tener un objeto con todos los datos de los clusters.
    """

    def __init__(self):
        self.kmeans_labels = None
        self.dfclvv = None
        self.cl_ord = None
        self.scl_ord = None
        self.scl_centroids = None
        self.idx_centroids = None
        self.idx_centroids_sc = None
        self.cl_centers = None
        self.dfclpw = None
        self.dfclvp = None

    # crear clusters a partir de dataframes
    def dataframe_to_cluster(self, dfvxvy, n_clusters, dfVP=None, n_sub_clusters=0, clusters_data=None,
                             subclusters_data=None, datadir=None, pw_col_name='pw', wind_col_name='vwind'):
        """
            Descripcion:
            Esta funcion toma diferentes dataframes de entrada agrupa los datos por cluster.

            :param wind_col_name: nombre de la columna "viento" del dataframe
            :param pw_col_name: nombre de la columna "potencia" del dataframe
            :param datadir: Datos de direccion
            :param subclusters_data: data to do subclustering [wind,pow,dir]
            :param clusters_data: data to do clustering [wind,pow,dir]
            :param dfvxvy: dataframe con columnas vx y vy
            :param dfVP: dataframe con columnas de magnitud de viento y potencia
            :param n_clusters: numero de clusters
            :param n_sub_clusters: Número de suclusters a calcular a partir de los n clusters calculados en un principio.
                      Si n_sub_clusters=0 no se calcula ningun subcluster. Por defecto n_sub=0


            :return cl_ord: un array que contiene el número de cluster n ordenado de menor a mayor
                de las magnitudes de la velocidad de viento sin tomar en cuenta la direccion
            :return dfclvv: dataframe donde las componentes de velocidad de viento vx y vy estan
                agrupadas por cluster
            :return dfclpw: dataframe donde la potencia esta agrupada por cluster
            :return dfclvp: dataframe donde la potencia y la magnitud de viento esta agrupada por
                cluster
        """

        # inicializacion de variables internas
        dfclpw = None
        dfclvp = None
        scl_ord = None
        scl_centroids = None
        idx_centroids_sc = None

        # check if dataframe with power values exist
        if dfVP is None:
            dfvp_is_empty = True
        else:
            dfvp_is_empty = False

        # '''- KMEANS -----------------------------------------------------------------------------------------'''
        if clusters_data == 'wind':
            kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(dfvxvy)
            # buscar centroides en dataframes
            # https://stackoverflow.com/questions/42583995/get-the-centroid-row-index-from-k-means-clustering-using-sklearn
            min_dist = np.min(cdist(dfvxvy.values, kmeans.cluster_centers_, 'euclidean'),
                              axis=1)  # distancia minima a cada centroide
            Y = pd.DataFrame(min_dist, index=dfvxvy.index, columns=['PCTimeStamp'])
            Z = pd.DataFrame(kmeans.labels_, index=dfvxvy.index, columns=['cluster_ID'])
            # crea el dataframe
            PAP = pd.concat([Y, Z], axis=1)

        if clusters_data == 'pow' and not dfvp_is_empty:

            kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(dfVP)
            # buscar centroides en dataframes
            min_dist = np.min(cdist(dfVP.values, kmeans.cluster_centers_, 'euclidean'), axis=1)
            Y = pd.DataFrame(min_dist, index=dfVP.index, columns=['PCTimeStamp'])
            Z = pd.DataFrame(kmeans.labels_, index=dfVP.index, columns=['cluster_ID'])
            PAP = pd.concat([Y, Z], axis=1)

        elif clusters_data == 'pow' and dfvp_is_empty:

            print('Power data is emtpy...')
            return None

        if clusters_data == 'dir' and not dfvp_is_empty:
            kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0, init='k-means++', n_init='auto').fit(datadir)
            # buscar centroides en dataframes
            min_dist = np.min(cdist(dfVP.values, kmeans.cluster_centers_, 'euclidean'), axis=1)
            Y = pd.DataFrame(min_dist, index=dfVP.index, columns=['PCTimeStamp'])
            Z = pd.DataFrame(kmeans.labels_, index=dfVP.index, columns=['cluster_ID'])
            PAP = pd.concat([Y, Z], axis=1)

        elif clusters_data == 'dir' and dfvp_is_empty:

            print('Clustering with only direction and no power data not implemented yet.')
            return None

        # ordend e los cluster por magnitud de vv
        cl_magni = np.zeros(n_clusters)
        # esta magnitud no esta correcta, funciona para ordenar
        # pero no es la real, revisar porque no sale lo mismo si
        # se hace los centroides. La media no es lo mismo que los
        # centroides de kmeans?, probablemente no
        for i in range(n_clusters):
            # vx = dfvxvy.vx.values[kmeans.labels_ == i]
            # vy = dfvxvy.vy.values[kmeans.labels_ == i]
            # cl_magni[i] = np.mean(np.sqrt(vx**2 + vy**2))  #magnitud de la vv
            cl_magni[i] = np.sqrt(
                dfvxvy[kmeans.labels_ == i].vx.mean() ** 2 + dfvxvy[kmeans.labels_ == i].vy.mean() ** 2)

        cl_ord = np.argsort(cl_magni.argsort())  # ver https://github.com/numpy/numpy/issues/8757

        grouped = PAP.groupby(['cluster_ID'])  # agrupa por numero de clusters las distancias minimas
        idx_centroids = grouped.idxmin()  # encuentra el indice de la distanciam minima
        # agregando columnas de velocidadd de viento y potencia al dataframe de los centroides
        vxvy = dfvxvy.loc[idx_centroids.PCTimeStamp].values
        if dfvp_is_empty:
            idx_centroids = idx_centroids.assign(vx=vxvy[:, 0], vy=vxvy[:, 1])

        else:
            vvpot = dfVP.loc[idx_centroids.PCTimeStamp].values
            idx_centroids = idx_centroids.assign(vx=vxvy[:, 0], vy=vxvy[:, 1], vwind=vvpot[:, 0], pw=vvpot[:,
                                                                                                     1])  # tal vez se necesite si no funciona cuando le meto el plot de potencia  # idx_centroids.sort_values(by='vwind',inplace=True)# ordenar por velocidad de viento  # idx_centroids.reset_index(inplace=True) #que ya no sea el cluster id el indice  # idx_centroids.index.set_names('cluster_ID_ord',inplace=True)  #ponerle el nombre al indice ordenado  # idx_centroids.index+=1 #paraque el indice empieze en uno y no exista cluster 0

        idx_centroids.reset_index(inplace=True)
        idx_centroids['cluster_ID_ord'] = cl_ord + 1
        idx_centroids.set_index('cluster_ID_ord', inplace=True)
        idx_centroids.sort_index(inplace=True)
        # agregar columnas de magnitud de viento
        mag_windv = []
        for i in range(len(idx_centroids)):
            mag_windv.append(np.sqrt(idx_centroids.iloc[i].vx ** 2 + idx_centroids.iloc[i].vy ** 2))
        idx_centroids['mag_windv'] = mag_windv

        ## CREAR MULTIINDICE ---------------------------------------------------------------'''
        # CLUSTER VX,VY:
        # https://stackoverflow.com/questions/37835508/how-to-do-multi-column-from-tuples
        # nombre de las columnas del dataframe
        if dfvp_is_empty:
            colheadvv = []
            for i in range(n_clusters):
                colheadvv.append(('C' + str(i + 1), 'vx'))
                colheadvv.append(('C' + str(i + 1), 'vy'))
            dfclvv = pd.DataFrame()

            for i in range(n_clusters):
                dfclvv = pd.concat([dfclvv, dfvxvy.vx[kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                    dfvxvy.vy[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1,
                                   ignore_index=True)
            # crear multiindice
            dfclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

        else:

            colheadvv = []
            colheadpw = []
            for i in range(n_clusters):
                colheadvv.append(('C' + str(i + 1), 'vx'))
                colheadvv.append(('C' + str(i + 1), 'vy'))
                colheadpw.append('C' + str(i + 1))
            dfclvv = pd.DataFrame()

            for i in range(n_clusters):
                dfclvv = pd.concat([dfclvv, dfvxvy.vx[kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                    dfvxvy.vy[kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1,
                                   ignore_index=True)
            # crear multiindice
            dfclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

            # CLUSTER POTENCIA:
            dfclpw = pd.DataFrame()
            for i in range(n_clusters):
                dfclpw = pd.concat([dfclpw, dfVP[pw_col_name][kmeans.labels_ == np.where(cl_ord == i)[0][0]]],
                                   ignore_index=True, axis=1)
            dfclpw.columns = colheadpw

            # CLUSTER VIENTO POTENCIA:

            colheadvp = []
            for i in range(n_clusters):
                colheadvp.append(('C' + str(i + 1), 'vwind'))
                colheadvp.append(('C' + str(i + 1), 'pw'))
            dfclvp = pd.DataFrame()

            for i in range(n_clusters):
                dfclvp = pd.concat([dfclvp, dfVP[wind_col_name][kmeans.labels_ == np.where(cl_ord == i)[0][0]],
                                    dfVP[pw_col_name][kmeans.labels_ == np.where(cl_ord == i)[0][0]]], axis=1,
                                   ignore_index=True)
            # crear multiindice
            dfclvp.columns = pd.MultiIndex.from_tuples(colheadvp)

        if clusters_data == 'direccion':
            # CLUSTER direccion viento
            colheadvp = []
            for i in range(n_clusters):
                colheadvp.append(('C' + str(i + 1), 'Dir'))
                colheadvp.append(('C' + str(i + 1), pw_col_name))
            dfcldv = pd.DataFrame()
            for i in range(n_clusters):
                dfcldv = pd.concat([dfcldv, datadir[wind_col_name][kmeans.labels_ == (cl_ord == i)],
                                    datadir.Dir[kmeans.labels_ == (cl_ord == i)]], axis=1, ignore_index=True)
            # crear multiindice
            dfcldv.columns = pd.MultiIndex.from_tuples(colheadvp)
        '''- CALCULAR SUBCLUSTERS ------------------------------------------------------------------- '''
        if n_sub_clusters > 0:
            scl_centroids = []
            scl_labels = []
            scl_ncentroids = []
            idx_centroids_sc = pd.DataFrame()  # va almacenar los centroides de los subclusters
            # obtener los resultados del clusterizado
            for i in range(n_clusters):
                if subclusters_data == 'wind':
                    dfclvvnoNA = dfclvv['C' + str(i + 1)].dropna()
                    # buscando centroides con los subclusters
                    kmeans_sc = cluster.KMeans(n_clusters=n_sub_clusters, random_state=0, init='k-means++',
                                               n_init='auto').fit(dfclvvnoNA)
                    min_dist_sc = np.min(cdist(dfclvvnoNA.values, kmeans_sc.cluster_centers_, 'euclidean'), axis=1)
                    Y_sc = pd.DataFrame(min_dist_sc, index=dfclvvnoNA.index, columns=['PCTimeStamp'])
                    Z_sc = pd.DataFrame(kmeans_sc.labels_, index=dfclvvnoNA.index, columns=['subcluster_ID'])

                elif subclusters_data == 'pow':
                    dfclvpnoNA = dfclvp['C' + str(i + 1)].dropna()
                    # buscando centroides con los subclusters
                    kmeans_sc = cluster.KMeans(n_clusters=n_sub_clusters, random_state=0, init='k-means++',
                                               n_init='auto').fit(dfclvpnoNA)
                    min_dist_sc = np.min(cdist(dfclvpnoNA.values, kmeans_sc.cluster_centers_, 'euclidean'), axis=1)
                    Y_sc = pd.DataFrame(min_dist_sc, index=dfclvpnoNA.index, columns=['PCTimeStamp'])
                    Z_sc = pd.DataFrame(kmeans_sc.labels_, index=dfclvpnoNA.index, columns=['subcluster_ID'])
                else:
                    print('Todavía no programado, haciendo subclusters en potencia')
                    kmeans_sc = cluster.KMeans(n_clusters=n_sub_clusters, random_state=0, init='k-means++',
                                               n_init='auto').fit(dfclvp['C' + str(i + 1)].dropna())

                scl_centroids.append(kmeans_sc.cluster_centers_)
                scl_labels.append(kmeans_sc.labels_)
                scl_ncentroids.append(len(scl_centroids[i]))

                PAP_sc = pd.concat([Y_sc, Z_sc], axis=1)
                # poniendo index a los centroides de los subclusters
                grouped_sc = PAP_sc.groupby(['subcluster_ID'])
                idx_cent_sc = grouped_sc.idxmin()
                idx_cent_sc.index += 1
                # agregando columnas de velocidadd de viento y potencia al dataframe de los centroides
                vxvy_sc = dfvxvy.loc[idx_cent_sc.PCTimeStamp].values
                vvpot_sc = dfVP.loc[idx_cent_sc.PCTimeStamp].values
                idx_centroids_sc = pd.concat([idx_centroids_sc, idx_cent_sc.assign(vx=vxvy_sc[:, 0], vy=vxvy_sc[:, 1],
                                                                                   vwind=vvpot_sc[:, 0],
                                                                                   pw=vvpot_sc[:, 1],
                                                                                   cluster_ID='C' + str(i + 1))])
            # creando el multiindex fuera del ciclo for
            # idx_centroids_sc.set_index(['cluster_ID',idx_centroids_sc.index],inplace=True)

            idx_centroids_sc.reset_index(inplace=True)
            idx_centroids_sc.sort_values(['cluster_ID', pw_col_name], ascending=[1, 1], inplace=True)
            lst_num_sc = list(range(1,
                                    n_sub_clusters + 1)) * n_clusters  # crea una lista de numeros para el subcluster [1,2,3..1,2,3]
            sc_idx_list = list(
                map(lambda x: 'SC' + str(x), lst_num_sc))  # le pone las letras SC [SC1,SC2,SC3...SC1,SC2,SC3]
            idx_centroids_sc = idx_centroids_sc.assign(subcluster_ID_ord=sc_idx_list)
            idx_centroids_sc.set_index(['cluster_ID', 'subcluster_ID_ord'], inplace=True)

            ############  ORDENAR CENTROIDES:  ordenar el orden de aparicion segun la magnitud de la vv
            scl_magni = np.zeros([n_clusters, n_sub_clusters])
            scl_ord = []

            for i in range(n_clusters):

                for j in range(n_sub_clusters):
                    vx = dfclvv['C' + str(i + 1)].vx.dropna().values[scl_labels[i] == j]
                    vy = dfclvv['C' + str(i + 1)].vy.dropna().values[scl_labels[i] == j]
                    scl_magni[i][j] = np.mean(np.sqrt(vx ** 2 + vy ** 2))  # magnitud de la vv

                scl_ord.append(scl_magni[i].argsort())  # ver https://github.com/numpy/numpy/issues/8757

            # ORDENAR CENTROIDES
            for i in range(len(scl_centroids)):
                scl_centroids[i] = scl_centroids[i][scl_ord[i]]

            # CLUSTER VIENTO POTENCIA:
            colheadvp = []
            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    colheadvp.append(('C' + str(i + 1), 'SC' + str(j + 1), wind_col_name))
                    colheadvp.append(('C' + str(i + 1), 'SC' + str(j + 1), pw_col_name))
            dfsclvp = pd.DataFrame()

            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    dfsclvp = pd.concat(
                        [dfsclvp, dfclvp['C' + str(i + 1)].dropna()[wind_col_name][scl_labels[i] == scl_ord[i][j]],
                         dfclvp['C' + str(i + 1)].dropna()[pw_col_name][scl_labels[i] == scl_ord[i][j]]], axis=1,
                        ignore_index=True)
            # crear multiindice
            dfsclvp.columns = pd.MultiIndex.from_tuples(colheadvp)

            # CLUSTER VX,VY:####################################################
            colheadvv = []
            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    colheadvv.append(('C' + str(i + 1), 'SC' + str(j + 1), 'vx'))
                    colheadvv.append(('C' + str(i + 1), 'SC' + str(j + 1), 'vy'))
            dfsclvv = pd.DataFrame()

            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    dfsclvv = pd.concat([dfsclvv, dfclvv['C' + str(i + 1)].dropna().vx[scl_labels[i] == scl_ord[i][j]],
                                         dfclvv['C' + str(i + 1)].dropna().vy[scl_labels[i] == scl_ord[i][j]]], axis=1,
                                        ignore_index=True)
            # crear multiindice
            dfsclvv.columns = pd.MultiIndex.from_tuples(colheadvv)

            # CLUSTER POTENCIA:
            dfsclpw = pd.DataFrame()
            colheadpw = []
            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    colheadpw.append(('C' + str(i + 1), 'SC' + str(j + 1)))

            for i in range(n_clusters):
                for j in range(n_sub_clusters):
                    dfsclpw = pd.concat(
                        [dfsclpw, dfclvp['C' + str(i + 1)][pw_col_name].dropna()[scl_labels[i] == scl_ord[i][j]]],
                        ignore_index=True, axis=1)
            dfsclpw.columns = pd.MultiIndex.from_tuples(colheadpw)

            #### buscar centroides para la grafica vv
            # obtener nombre de niveles
            n_sub_clusters = len(dfsclvv.columns.levels[1])
            # numero total de clusters incluidos los subclusters
            n_tot_clusters = n_sub_clusters * n_clusters
            # solo aplica cuando hay subclusters
            lev0 = dfsclvv.columns.get_level_values(0)
            lev1 = dfsclvv.columns.get_level_values(1)
            namcl = [(lev0[i], lev1[i]) for i in range(len(lev0))]
            colnames = namcl[::2]

        # llenado de datos
        self.kmeans_labels = kmeans.labels_
        self.comp_vel = dfclvv
        self.cl_ord = cl_ord
        self.idx_centroids = idx_centroids
        self.cl_centers = kmeans.cluster_centers_
        # self.dfclpw = dfclpw
        self.dfclvp = dfclvp

        self.scl_ord = scl_ord
        self.scl_centroids = scl_centroids
        self.idx_centroids_sc = idx_centroids_sc


# %% md
# Procesar datos de BCS
# %%
'''
Se reemplaza la hora 24:00 por 00:00 y se suma un día, así que la última
toma de datos de un día se cambia por la primera del día siguiente
'''


def proc_dat_bcs(data_path, mf_pow_curve_path=None, mf_vel_colname=None, mf_pw_colname=None, mf_rename_cols=None):
    """
    Procesamiento de datos de BCS, viento y curva del fabricante.
    :param data_path: ruta del archivo de los datos de viento
    :param mf_pow_curve_path: file that contains wind velocity and power of the manufacturer power curve. Can be a
    CSV file or an Excel file
    :param mf_vel_colname: manufacturer power curve wind velocity column name.
    :return: mf_pw_colname: manufacturer power curve power column name.
    """
    ###########################################configuración
    columns_to_use = [0, 1, 3, 6]
    columns_id = ['day', 'hour', 'wdir', 'vwind']
    dir_format = 'deg'
    year = '2005'  # data year
    ########################################################
    # imprimir a consola
    os.write(1, b"Inciando procesamiento de datos...\n")
    print("Inciando procesamiento de datos...\n")
    dataVDxls = pd.read_excel(data_path, usecols=columns_to_use, dtype={'DIA': str, 'HORA': str})
    dataVDxls.columns = columns_id
    # agrego la columna de potencia instantanea sin filtrar
    # dataVPxls['Pw']= (dataVPxls.iloc[1:,1].values-dataVPxls.iloc[0:-1,1]) * np.pi*45**2
    print('Total de registros: ' + str(len(dataVDxls)))

    # marcando los datos faltantes asignando un nan a la fila completa
    datamk = dataVDxls
    datamk.loc[datamk.isnull().any(axis=1), :] = np.nan
    # numero de filas sin datos
    print('Numero de filas sin datos')
    print(datamk.loc[datamk.isnull().any(axis=1), :].isnull().sum())

    # eliminando filas con NaN
    cleanData = datamk.dropna()

    # datos direccion velocidad
    # print(len(dataVP))
    # print(len(dataDir))
    # dataDV = pd.concat([dataDir,dataVP.vViento],axis=1)
    # dataVD = pd.concat([dataVP.vViento,dataDir,axis=1)
    # dataVcD =pd.concat([dataDir,df_comp_vel],axis=1)
    # change hour 24:00 to 00:00
    dataVDxls['hour'] = dataVDxls['hour'].str.replace('2400', '0000')
    dataVDxls['timeStamp'] = dataVDxls.apply(lambda x: daymin2date(year, x.day, x.hour), axis=1)
    # dataVDxls['timeStamp'] =pd.to_datetime(pd.to_datetime(dataVDxls['timeStamp'], format='%d/%m/%Y '
    #                                                                                     '%H:%M').dt.strftime(
    #                                                                                     '%d/%m/%Y %H:%M'))
    dataVDxls['timeStamp'] = pd.to_datetime(dataVDxls['timeStamp'], format='%d/%m/%Y %H:%M')

    # cambiar formato de 24:00 a 00:00 sumando un día a 00:00
    filtro1 = dataVDxls['timeStamp'].dt.hour == 0
    filtro2 = dataVDxls['timeStamp'].dt.minute == 0
    idx = np.where(filtro1.values & filtro2.values)
    ts = dataVDxls['timeStamp'].values
    ts[idx] = ts[idx] + pd.to_timedelta(1, 'd')
    dataVDxls['timeStamp'] = ts

    dataVDxls.set_index('timeStamp', inplace=True, verify_integrity=True)
    dfWD = dataVDxls.drop(columns=['day', 'hour'])
    # eliminar la ultima fila, ya que con el cambio de formato de hora llego
    # al 01/01/2006 y no me interesa esa fecha
    dfWD.drop(dfWD.tail(1).index, inplace=True)  # drop last n rows
    # dfWD.index = pd.to_datetime(pd.to_datetime(dfWD.index).strftime('%d/%m/%Y %H:%M'))

    del dataVDxls
    # CHECK THE DIRECTION OF THE ANEMOMETER
    if dir_format == 'rad':
        direcvrad = np.deg2rad(dfWD['wdir'].values)
        vecVel = [-np.sin(direcvrad) * dfWD['vwind'].values, np.cos(direcvrad) * dfWD['vwind'].values]
    else:
        vecVel = [-np.sin(dfWD['wdir'].values * np.pi / 180) * dfWD['vwind'].values,
                  np.cos(dfWD['wdir'].values * np.pi / 180) * dfWD['vwind'].values]

    vecVelnp = np.array(vecVel).transpose()
    # original sin timestamp
    # df_comp_vel = pd.DataFrame(data=vecVelnp,columns=['vx','vy']
    # con timestamp
    df_comp_vel = pd.DataFrame(data=vecVelnp, columns=['vx', 'vy'], index=dfWD.index)

    # ----------------------------------------------------------
    #               Manufacturer power curve                  -
    # ----------------------------------------------------------
    if mf_pow_curve_path is not None:
        if mf_pow_curve_path[-3:] == 'csv':
            # first column sill be the index
            dfMfgCurve = pd.read_csv(mf_pow_curve_path, index_col=0)
        else:
            dfMfgCurve = pd.read_excel(mf_pow_curve_path, usecols=[0, 2], index_col=0)
        if mf_rename_cols is not None:
            dfMfgCurve.rename(columns={mf_vel_colname: mf_rename_cols[0], mf_pw_colname: mf_rename_cols[1]},
                              inplace=True)
            dfMfgCurve.set_index(mf_rename_cols[0], inplace=True)

        os.write(1, b"Fin del procesamiento de datos\n")
        print('Fin del procesamiento de datos')
        return dfWD, df_comp_vel, dfMfgCurve

    else:
        os.write(1, b"Fin del procesamiento de datos\n")
        print('Fin del procesamiento de datos')
        return dfWD, df_comp_vel


# %% md
# Interpolar curva del fabricante
# %%
import numpy as np


def interp_pow_curve(df_mf_curve, wind_min_max=(0, 25), step=0.1):
    """
    Interpolación de la curva del fabricante.
    :param wind_min_max: min y max de las velocidades de viento
    :param df_mf_curve: dataframe con los datos de vel y pw del fabricante.
    :param step: paso entre una potencia y otra
    :return: curva del fabricante interpolada
    """
    # crear un df con datos de velocidad de viento calculadas con range
    # y una fila pw de nan's para despues llenar esa fila con los datos de potencia
    # aqui solo crea el df sin interpolar
    # para el indice de vv
    wind_range = list(np.round(np.arange(wind_min_max[0], wind_min_max[1], step), decimals=1))
    df_mfcurve_interp = pd.DataFrame(data={'pw': np.nan}, index=wind_range)
    # con el indice de las velocidades de viento que existen, voy a copiar las potencias que existen
    # al dataframe a interpolar
    for i in df_mf_curve.index:
        df_mfcurve_interp[df_mfcurve_interp.index == i] = df_mf_curve.loc[i].pw
    # interpolando
    df_mfcurve_interp.interpolate(method='linear', inplace=True)
    # reemplazando nan con cero (viento bajo,cero potencia)
    df_mfcurve_interp.fillna(0, inplace=True)

    return df_mfcurve_interp


# %% md
# Crear plot de la cadena de Markov
# %%
import subprocess
from matplotlib import image


# Todo: - el NodeFontSize no funciona para versiones antes de MATLAB 2019 tal vez hacer esto: https://la.mathworks.com/matlabcentral/answers/450580-change-font-size-of-node-name-in-a-graph

# def create_mc_plot(trans_matrix,marker_size=10,node_fontsize=14,line_width =1,x_width =20,y_width=10,fig_size=(20,10)):
#     """
#     Crea un plot con la cardena de Markov a partir del dataframe que contiene la matriz de transicion de probabilidades.
#     El dataframe debe contener los nombres de columnas en el header y en el index (es el mismo que se utiliza para
#     crear el heatmap).
#
#     Esta funcion crea un script de matlab con lo necesario para crear el plot de la cadena de Markov
#     y lo ejecuta. Este script crea una imagen en el mismo directorio del script de python llamada graph_mc.jpg
#     y lo carga en el notebook con matplotlib e image show
#
#     :param fig_size: tamaño de la figura que se muestra en el notebook.
#     :param trans_matrix: dataframe que contiene la matriz de transicion de probabilidades.
#     :param marker_size: tamaño del nodo (punto que representa al estado)
#     :param node_fontsize: tamaño de la fuente.
#     :param line_width: tamaño de linea.
#     :param x_width: ancho de la imagen en pulgadas.
#     :param y_width: largo de la imagen en pulgadas.
#     """
#     #tamaño del nodo (punto)
#     marker_size= str(marker_size)
#     node_fontsize = str(node_fontsize)
#     line_width = str(line_width)
#     x_width=str(x_width) ;y_width=str(y_width);
#
#     #ruta y version de matlab, recordar que se necesita el econometrics toolbox
#     #y ejecutar la version de matlab donde se instalo esa toolbox, ademas
#     #de que debe ser minimo la vesion 2019 de matlab
#     matlab_path =r'"C:\Program Files\MATLAB\R2019a\bin\matlab.exe"'
#     f = open("m_script_markov.m", "w")
#     f.write('%------------------------------------------------------------------------\n')
#     f.write('% Script con los datos de la matriz de python, que seran convertidos a un\n')
#     f.write('% objeto dtmc de MATLAB. Luego se crea una imagen con la cadena de Markov en\n')
#     f.write('% forma grafica y se carga en el notebook de jupyter\n')
#     f.write('%------------------------------------------------------------------------ \n')
#
#     #escribiendo la matriz de transicion de probabilidades en el archivo .m
#     f.write('mat_trans = [')
#     for i in range(len(trans_matrix)):
#         lin = str(trans_matrix.iloc[i].values).replace ('\n', '')
#         f.write(lin[1:-1]+';\n')
#     f.write('];\n')
#     #crear el objeto discrete time markov chain
#     f.write('mc = dtmc(mat_trans);\n')
#     #crear los nombres de los estados
#     state_names = str(trans_matrix.columns.values).replace('\n','') +';\n'
#     state_names =state_names.replace('\'','\"')
#     f.write('mc.StateNames = ' + state_names)
#     f.write('p = graphplot(mc,"ColorEdges",true);\n')
#     f.write('p.MarkerSize ='+ marker_size +';\n')
#     f.write('p.NodeFontSize = '+ node_fontsize +';\n')
#     f.write('p.LineWidth = ' + line_width +';\n')
#     f.write('p.EdgeAlpha = 1;\n')
#     f.write('colormap("hot");\n')
#     f.write('set(gcf, "PaperUnits", "inches");\n')
#     f.write('set(gcf, "PaperPosition", [0 0 '+ x_width +' ' + y_width+']);\n')
#     f.write("saveas(gcf,'graph_mc.jpg');\n")
#     f.close()
#     #corriendo archivo m en matlab por linea de comandos del sistema
#     #result almacena el texto que devuelde la terminal
#     result = subprocess.run(matlab_path + ' -batch "m_script_markov"', stdout=subprocess.PIPE)
#     #cargando y mostrando imagen
#     img = image.imread('graph_mc.jpg')
#
#     plt.figure(figsize=fig_size)
#     plt.imshow(img,aspect='auto')
#     plt.grid(False)
#     plt.axis('off')
#     plt.show()
# %% md
# Plot de direcciones de viento
# %%

# Todo: plot polar
# Todo: poner direcciones en los ejes

def plot_vectors(comp_vel, show_month=None, figsize=(7, 5), fign=100):
    """
    Ploteo de componentes de velocidad en un plot tipo rosa de los vientos.
    :param fign: Numero de figura.
    :param figsize: Tamaño de la figura
    :param show_month: Mes a mostrar, si es cero se muestran todos, si no se muestra n,
                si es None, se muestran todos los meses en uno solo
    :param comp_vel: dataframe con los componentes de velocidad en columnas vx y vy
    """
    # https://stackoverflow.com/questions/42281966/how-to-plot-vectors-in-python-using-matplotlib
    # para no importar mas librerias
    months = ["Unknown", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    f = plt.figure(fign, figsize=figsize)

    limix = [np.floor(comp_vel.vx.min()), np.ceil((comp_vel.vx.max()))]
    limiy = [np.floor(comp_vel.vy.min()), np.ceil((comp_vel.vy.max()))]
    limir = np.ceil(np.max(comp_vel.max()))
    if show_month is None:
        # mostrar todos los meses en un solo plot
        origin = np.array([np.zeros(len(comp_vel)), np.zeros(len(comp_vel))])  # origin point
        plt.suptitle('All months')
        plt.quiver(*origin, comp_vel.vx, comp_vel.vy, color='b', angles='xy', scale_units='xy', scale=1)
        plt.xlim(limix)
        plt.ylim(limiy)

    elif show_month == 0:
        # mostrar todos los meses en 12 plots
        # fig, ax = plt.subplots(3,4,subplot_kw={'projection': 'polar'})
        fig, ax = plt.subplots(3, 4, num=fign)
        counter_month = 1  # contador para la lista de meses
        for i in range(3):
            for j in range(4):
                # slicing mes por mes
                data_month = comp_vel[comp_vel.index.month == i + j + 1]
                origin = np.array([np.zeros(len(data_month)), np.zeros(len(data_month))])  # origin point
                ax[i, j].quiver(*origin, data_month.vx, data_month.vy, color='b', angles='xy', scale_units='xy',
                                scale=1)
                # ax[i,j].title.set_text(months[i+j+1])
                ax[i, j].title.set_text(months[counter_month])
                ax[i, j].set_xlim(limix)
                ax[i, j].set_ylim(limiy)
                counter_month += 1  # ax[i,j].set_ylim([0,np.pi])  # ax[i,j].set_rmax(limir)
    elif 0 < show_month <= 12:
        data_month = comp_vel[comp_vel.index.month == show_month]
        origin = np.array([np.zeros(len(data_month)), np.zeros(len(data_month))])  # origin point
        plt.suptitle(months[show_month])
        plt.quiver(*origin, data_month.vx, data_month.vy, color='b', angles='xy', scale_units='xy', scale=1, lw=1)
        plt.xlim(limix)
        plt.ylim(limiy)
    else:
        print('Error. Parámetro show_month no valido.')
    plt.figtext(0.5, 0.01, 'Figure ' + str(fign), wrap=True, horizontalalignment='center', fontsize=14)
    plt.tight_layout()
    plt.show()
    return f


# %% md
# Combinar columnas de clusters
# %%

# Todo: cargar una lista  con listas de clusters a unir para no tener que llamar varias veces a la funcion de unir
# clusters

def join_clusters(df, clu_to_join):
    """
    Combinas las columnas especificadas en clu_to_join en una sola, es decir, combina clusters, df = dfclvv
    :param df: dataframe con las columnas a combinar.
    :param clu_to_join: clusters a combinar
    :return:
    """
    if df.columns.nlevels == 1:
        # Nombra a la columna combinada como el primer nombre de columna pasado en clu_to_join
        # join (sumar) las columnas elegidas
        # con min_count=1 no se suman los valores si son solo NaN y no se vuelve ese NaN cero, si no se lo pongo, los NaN
        # se vuelven cero
        df = df.assign(C_=df[clu_to_join].sum(1, min_count=1)).drop(clu_to_join, axis=1)
        # cambiar el nombre de columna temporal C_ a el primer valor de la lista de columnas a combinar
        df.rename({'C_': clu_to_join[0]}, axis=1, inplace=True)
        # reordenar columnas alfabeticamente
        df = df.reindex(sorted(df.columns, key=lambda x: float(x[1:])), axis=1)
    elif df.columns.nlevels == 2:
        # multiindice, para el df de componentes de velocidad dividido por clusters
        # groupby agrupa todos las columnas de los clusters seleccionados en una, sum suma esas columnas y min_count
        # hace que n + NaN sea n. Sin min_count creo que la suma da cero
        df_ = df[clu_to_join].groupby(level=1, axis=1).sum(min_count=1)
        # crea el nombre de las columnas
        df_.columns = pd.MultiIndex.from_product([['C_'], ['vx', 'vy']])
        # une las columnas agrupadas al df de entrada
        df = df.join(df_)
        # elimina las columnas individuales que fueron agrupadas
        df.drop(clu_to_join, level=0, axis=1, inplace=True)
        # cambia el nombre de la nueva columna de agrupamientos, de C_ al primer de la lista de clusters que se pasó
        df.rename({'C_': clu_to_join[0]}, axis=1, inplace=True)
    else:
        print('Error: Formato de Dataframe no soportado.')

    return df


# %% md
# Crear plot de la cadena de Markov
# %%
import subprocess
from matplotlib import image
from os.path import exists
import errno
import matplotlib.pyplot as plt


# Todo: el NodeFontSize no funciona para versiones antes de MATLAB 2019,tal vez hacer esto:
# https://la.mathworks.com/matlabcentral/answers/450580-change-font-size-of-node-name-in-a-graph
# Todo: Eliminar imagen anterior para que no se cargue cuando hay un error, o asegurarse de que no haya error al crear
# la imagen.
# Todo: Cambiar la condición para cambiar cero por nan, ahorita busca el string "0." pero no es lo ideal,
# que pasa si es "0" o "0e+0"?
# Todo: revisar bien el formato de las paths [1:-1]?


def create_mc_plot(fign, trans_matrix, filename='graph_mc.jpg', marker_size=30, node_fontsize=15,
                   edge_fontsize = 15, arrow_size =20, line_width=2, \
                   x_width=20, y_width=10, fig_size=(10, 5), replace_zero_to_nan=True, as_pct=True, layout='auto',
                   matlab_path=r"C:\Program Files\MATLAB\R2021b\bin\matlab.exe",
                   matlab_script_path=r"'C:\Users\mungu\Documents\GitHub\aero\m_script_markov.m'"):
    """
    Crea un plot con la cardena de Markov a partir del dataframe que contiene la matriz de transicion de probabilidades.
    El dataframe debe contener los nombres de columnas en el header y en el index (es el mismo que se utiliza para
    crear el heatmap).

    Esta funcion crea un script de matlab con lo necesario para crear el plot de la cadena de Markov
    y lo ejecuta. Este script crea una imagen en el mismo directorio del script de python llamada graph_mc.jpg
    y lo carga en el notebook con matplotlib e image show

    :param filename: Nombre del archivo de la imagen.
    :param fign: numero de figura
    :param layout: opciones de layout de matlab para graphplot. No todas están implementadas: UseGravity, auto, WeightEffect, layered, circle.
    :param as_pct: si el df viene en porcentajes, dividir entre 100
    :param replace_zero_to_nan: reemplazar ceros con np.nan
    :param fig_size: tamaño de la figura que se muestra en el notebook.
    :param trans_matrix: dataframe que contiene la matriz de transicion de probabilidades.
    :param marker_size: tamaño del nodo (punto que representa al estado)
    :param node_fontsize: tamaño de la fuente.
    :param edge_fontsize: tamaño de la fuente de las lineas.
    :param arrow_size: tamaño de la flecha.
    :param line_width: tamaño de linea.
    :param x_width: ancho de la imagen en pulgadas.
    :param y_width: largo de la imagen en pulgadas.
    :param matlab_path: ruta y version de matlab, recordar que se necesita el econometrics toolbox y ejecutar la
    version de matlab donde se instalo esa toolbox, ademas de que debe ser minimo la vesion 2019 de matlab
    :param matlab_script_path: ruta del script de matlab que crea la imagen de la cadena de Markov
    """
    # chek if matlab.exe exists
    if not exists(matlab_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), matlab_path)

    # chek if matlab script exists
    # [1:-1] to remove double quotes from path string
    if not exists(matlab_script_path[1:-1]):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), matlab_script_path[1:-1])
    # tamaño del nodo (punto)
    marker_size = str(marker_size)
    node_fontsize = str(node_fontsize)
    edge_fontsize = str(edge_fontsize)
    arrow_size = str(arrow_size)
    line_width = str(line_width)
    x_width = str(x_width)
    y_width = str(y_width)
    # si se quiere en forma de porcentaje o no
    # revisar si el archivo existe
    im_exists = exists('graph_mc.jpg')
    if im_exists:
        # si la imagen existe, borrar
        os.remove('graph_mc.jpg')

    if not as_pct:
        trans_matrix /= 100

    f = open(matlab_script_path[1:-1], "w")
    f.write('%------------------------------------------------------------------------\n')
    f.write('% Script con los datos de la matriz de python, que seran convertidos a un\n')
    f.write('% objeto dtmc de MATLAB. Luego se crea una imagen con la cadena de Markov en\n')
    f.write('% forma grafica y se carga en el notebook\n')
    f.write('%------------------------------------------------------------------------ \n')

    # escribiendo la matriz de transicion de probabilidades en el archivo .m
    f.write('mat_trans = [')
    if replace_zero_to_nan:
        trans_matrix = np.round(trans_matrix, 4)
        trans_matrix.replace(0, np.nan, inplace=True)
    for i in range(len(trans_matrix)):
        lin = str(trans_matrix.iloc[i].values).replace('\n', '')
        f.write(lin[1:-1] + ';\n')
    f.write('];\n')
    #cambiar nan's por cero
    f.write('mat_trans(isnan(mat_trans))=0;\n')
    # crear el objeto discrete time markov chain
    f.write('mc = dtmc(mat_trans);\n')
    # crear los nombres de los estados
    state_names = str(trans_matrix.columns.values).replace('\n', '') + ';\n'
    state_names = state_names.replace('\'', '\"')
    f.write('mc.StateNames = ' + state_names)
    f.write('p = graphplot(mc,"ColorEdges",true);\n')
    f.write('colorbar off;\n')
    # layout del grafico
    if layout == 'auto':
        f.write("layout(p,'auto');\n")
    elif layout == 'WeightEffect':
        # este layout no acepta valores cero o NaN
        if trans_matrix.eq(0).values.any() or trans_matrix.isnull().values.any():
            f.write("layout(p,'force','WeightEffect','direct');\n")
        else:
            f.write("layout(p,'auto');\n")
    elif layout == 'circle':
        f.write("layout(p,'circle');\n")
    elif layout == 'layered':
        f.write("layout(p,'layered','Direction','right';)\n")
    elif layout == 'UseGravity':
        f.write("layout(p,'force','UseGravity' ,'on');\n")
    else:
        print('Layout no reconocida, usando auto')
        f.write("layout(p,'auto');\n")

    f.write('p.MarkerSize =' + marker_size + ';\n')
    f.write('p.NodeFontSize = ' + node_fontsize + ';\n')
    f.write('p.LineWidth = ' + line_width + ';\n')
    f.write('p.NodeLabelColor ="blue";\n')
    f.write('p.EdgeFontSize = ' + edge_fontsize + ';\n')
    f.write('p.ArrowSize = ' + arrow_size + ';\n')
    f.write('p.ArrowPosition=.93;\n');
    f.write('p.EdgeAlpha = 1;\n')
    f.write('colormap("copper");\n')
    # para saber si esta en porcentaje o no
    # si uso solo max() toma al valor NaN como el maximo y no funciona
    if np.nanmax(trans_matrix.values) > 1:
        f.write('caxis([0,100]);\n')
    # poner los pesos a las flechas
    f.write("if isempty(find(isnan(mat_trans), 1))\n")
    f.write("   p.EdgeLabelMode= 'auto';\n")
    f.write("else\n")
    f.write("   p.EdgeLabelMode= 'manual';\n")
    f.write("   idx =find(~isnan(mat_trans));\n")
    f.write("   vals = mat_trans(idx);\n")
    f.write("   labeledge(p,idx,vals);\n")
    f.write("end\n")
    # tamaño de la imagen
    f.write('set(gcf, "PaperUnits", "inches");\n')
    f.write('set(gcf, "PaperPosition", [0 0 ' + x_width + ' ' + y_width + ']);\n')
    f.write("saveas(gcf,'" + filename + "');\n")
    f.close()

    # corriendo archivo m en matlab por linea de comandos del sistema
    # result almacena el texto que devuelde la terminal
    matlab_cmd = matlab_path + ' -batch run(' + matlab_script_path + ')'
    result = subprocess.run(matlab_cmd, stderr=subprocess.STDOUT)
    if result.stderr:
        raise subprocess.CalledProcessError(returncode=result.returncode, cmd=result.args, stderr=result.stderr)
    # cargando y mostrando imagen
    img = image.imread(filename)

    plt.figure(fign, figsize=fig_size)
    plt.imshow(img, aspect='auto')
    plt.grid(False)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    return result


# %% md
# Unir clusters manualmente
# %%
import logging
# Todo: join also power
from sklearn.metrics.pairwise import nan_euclidean_distances


def join_clusters(df, clu_to_join, clu_to_del=None):
    """
    Combinas las columnas especificadas en clu_to_join en una sola, es decir, combina clusters, df = dfclvv. El orden
     de los elementos de clu_to_join importa, ese seria el "orden natural" (segunda columna) y empieza en cero.
     También es important usar doble corchete.
    :param clu_to_del: Lista de cluster a eliminar
    :param df: dataframe con las columnas a combinar. Puede ser el dataframe con clusters de solo magnitud viento
    (dfclvv) o
    con componentes de velocidad
    :param clu_to_join: clusters a combinar en pares. [[1,2],[7,9] une el primero el cluster 1 y 2 y después une el
    cluster 7,9.
    :return: df con clusters agrupados.
    """
    # revisar que clu_to_join tenga el formato [[a,b]] para un par de clusters a agrupar.
    # mejorar como saber si estan pasando el formato adecudado
    if len(np.array(clu_to_join, dtype='object').shape) != 1:
        logging.error('Formato de lista de grupos errónea. Sigue el formato [[a,b...n]]?')
        return

    # clusters de solo magnitud de viento (dfclvv)
    if df.columns.nlevels == 1:
        for cl in clu_to_join:
            # Nombra a la columna combinada como el primer nombre de columna pasado en clu_to_join
            # join (sumar) las columnas elegidas
            # con min_count=1 no se suman los valores si son solo NaN y no se vuelve ese NaN cero, si no se lo pongo, los NaN
            # se vuelven cero
            df = df.assign(C_=df[cl].sum(1, min_count=1)).drop(cl, axis=1)
            # cambiar el nombre de columna temporal C_ a el primer valor de la lista de columnas a combinar
            df.rename({'C_': cl[0]}, axis=1, inplace=True)
            # reordenar columnas alfabeticamente
            df = df.reindex(sorted(df.columns, key=lambda x: float(x[1:])), axis=1)

        if clu_to_del is not None:
            for cl in clu_to_del:
                df.drop(cl, inplace=True, axis=1)
    elif df.columns.nlevels == 2:
        for cl in clu_to_join:
            # multiindice, para el df de componentes de velocidad dividido por clusters
            # groupby agrupa todos las columnas de los clusters seleccionados en una, sum suma esas columnas y min_count
            # hace que n + NaN sea n. Sin min_count creo que la suma da cero
            df_ = df[cl].groupby(level=1, axis=1).sum(min_count=1)
            # crea el nombre de las columnas
            df_.columns = pd.MultiIndex.from_product([['C_'], ['vx', 'vy']])
            # une las columnas agrupadas al df de entrada
            df = df.join(df_)
            # elimina las columnas individuales que fueron agrupadas
            df.drop(cl, level=0, axis=1, inplace=True)
            # cambia el nombre de la nueva columna de agrupamientos, de C_ al primer de la lista de clusters que se pasó
            df.rename({'C_': cl[0]}, axis=1, inplace=True)

        # eliminando clusters
        if clu_to_del is not None:
            for cl in clu_to_del:
                df.drop(cl, axis=1, level=0, inplace=True)
                # si no hago esto no se quita el C7 del indice y ocurre un error al querer plotear C7 que no existe
                df.columns = df.columns.remove_unused_levels()  # orden en que los clusters fueron agrupados  # quitando letras y dejando solo numeros  # orden_natural = [int(i[1:]) for i in df.columns.levels[0]]  # ordenar clusters por magnitud

    else:
        logging.error('Error: Formato de Dataframe no soportado.')
    return df


# %% md
# Matriz de transición a partir de dataframe
# %%
def trans_matrix_from_df(df, mat_mode='prob'):
    """

    :param mat_mode: "prob" regresa la matriz de probabilidades, "frec" regresa la matriz de frecuencias
    :param df: dataframe con los datos separados en clusters
    :return: dataframe con la matriz de transiciones.
    """
    # matriz de transicion del tamaño del numero de  clusters
    if mat_mode != 'prob' and mat_mode != 'frec':
        print('Modo no reconocido.')
        return None
    n_clusters = len(df.columns)
    mattra = np.zeros([n_clusters, n_clusters])
    for row in range(len(df) - 1):
        # para asegurarse que no sean todos los valores nan, ahora posible cunando se eliminan clusters (joined)
        if not df.iloc[row].isnull().all() and not df.iloc[row + 1].isnull().all():
            # para asegurarse de que no hay filas con cero?
            if df.iloc[row].to_numpy().nonzero()[0].shape[0] > 0 and df.iloc[row + 1].to_numpy().nonzero()[0].shape[
                0] > 0:
                if df.iloc[row][np.argwhere(~np.isnan(df.iloc[row].values) == True)[0][0]] > 0:
                    i = np.argwhere(~np.isnan(df.iloc[row].values) == True)[0][0]  # donde estoy (que estado)
                    j = np.argwhere(~np.isnan(df.iloc[row + 1].values) == True)[0][
                        0]  # siguiente linea ( o estado) (hacia que
                    # estado voy)
                    # revisar si hay mas de un 1, que no deberia de haber
                    #        if len( np.nonzero(dfclpw.iloc[row,:].values)) >1:
                    #            print('si')

                    mattra[i, j] += 1
    # convertir de numpy array to dataframe
    idxclnames = {}
    clidx = range(0, n_clusters)
    columnas = []
    for i in np.arange(1, n_clusters + 1):
        columnas.append('C' + str(i))
    clnames = []
    for i in range(n_clusters):
        clnames.append('C' + str(i + 1))
    for i in clidx:
        idxclnames[i] = columnas[i]

    df_mat_tra = pd.DataFrame(mattra)
    df_mat_tra.columns = df.columns
    # df_mat_tra.rename(index=df.columns)
    df_mat_tra.set_index(df.columns, inplace=True)
    # la funcion se aplica fila por fila
    # se suman todos los valores por fila y se divide entre cada valor, luego se multiplica por 100
    # mprob = df_mat_tra.apply(calculate_vectorprob, axis=1)

    mprob = df_mat_tra.apply(lambda row: row.astype(float) / row.sum() * 100, axis=1)
    mprob.rename(index=idxclnames, inplace=True)
    if mat_mode == 'prob':
        return mprob
    else:
        return df_mat_tra


# %% md
# crear dataframe de datos agrupados en clusters (dfclvv, no se usa la función kmeans)
# %%
# def create_clustered_data(df_comp_vel,df_to_clus,klabels):
#     """
#     Crea un dataframe donde los datos de velocidades estan agrupados en clusters, en formato:
#     ---------------------------
#     |timestamp | C1 | C2 | C3 |
#     |----------|----|----|----|
#     |date      | vv |NaN |NaN |
#     |----------|----|----|----|
#     |date2     |NaN |vv2 |NaN |
#     |----------|----|----|----|
#     |date3     |NaN |NaN |vv3 |
#     | ________________________|
#
#
#     :param df_comp_vel: df con con los componentes de velocidad vx y vy, se utiliza para ordenar los clusters por
#     magnitud de viento, tal vez no se necesite
#     :param df_to_clus: df con datos de viento que se va a agrupar en clusters.
#     :param klabels: las labels resultantes de aplicar kmeans al conjunto de datos.
#     :return: df con datos de viento agrupados en clusters, dfclvv
#     """
#     #orden de aparicion de los clusters kmeans
#     #ordenar el orden de aparicion segun la magnitud de la vv
#     n_clusters = len(np.unique(klabels))
#     clmagni = np.zeros(n_clusters)
#     for i in range(n_clusters):
#         vx = df_comp_vel.vx.values[klabels==i]
#         vy = df_comp_vel.vy.values[klabels==i]
#         clmagni[i]= np.round(np.mean(np.sqrt(vx**2 + vy**2)),1) #magnitud de la vv
#
#     clord = clmagni.argsort()
#
#     columnas=[]
#     for i in np.arange(1,n_clusters+1):
#         columnas.append('C'+str(i))
#
#     dfclvv = pd.DataFrame()
#     for i in range(n_clusters):
#         dfclvv = pd.concat([dfclvv,df_to_clus.vwind[klabels==clord[i]]], ignore_index=True, axis=1)
#     dfclvv.columns=columnas[0:n_clusters]
#     return dfclvv
# %%
def create_clustered_data(df_to_clus, klabels):
    """
    Crea un dataframe donde los datos de velocidades estan agrupados en clusters, en formato:
    ---------------------------
    |timestamp | C1 | C2 | C3 |
    |----------|----|----|----|
    |date      | vv |NaN |NaN |
    |----------|----|----|----|
    |date2     |NaN |vv2 |NaN |
    |----------|----|----|----|
    |date3     |NaN |NaN |vv3 |
    | ________________________|


    :param df_comp_vel: df con con los componentes de velocidad vx y vy, se utiliza para ordenar los clusters por
    magnitud de viento, tal vez no se necesite
    :param df_to_clus: df con datos de viento que se va a agrupar en clusters.
    :param klabels: las labels resultantes de aplicar kmeans al conjunto de datos.
    :return: df con datos de viento agrupados en clusters, dfclvv
    """
    # orden de aparicion de los clusters kmeans
    # ordenar el orden de aparicion segun la magnitud de la vv
    n_clusters = len(np.unique(klabels))
    clmagni = np.zeros(n_clusters)
    for i in range(n_clusters):
        #
        clmagni[i] = df_to_clus.vwind[klabels == i].mean()
    clord = clmagni.argsort()
    dfclvv = pd.DataFrame()
    for i in range(n_clusters):
        dfclvv = pd.concat([dfclvv, df_to_clus.vwind[klabels == clord[i]]], ignore_index=False, axis=1)
    columnas = []
    for i in np.arange(1, n_clusters + 1):
        columnas.append('C' + str(i))

    dfclvv.columns = columnas[0:n_clusters]
    return dfclvv.sort_index()


# %% md
# Matriz  a vector
# %%
def mat_to_vector(df):
    """
    #convertir de matriz a vector  (debe ser igual que kmeans_labels cuando la matriz es la original)
    #tomo el dataframe con los estados ya indicados y la convierto a vector ignorando
    #en este caso NaN's
    :param df:
    :return:
    """
    vect_states = []
    for row in range(len(df)):
        clust = np.argwhere(df.iloc[row].notnull().values)[0][0]
        vect_states.append(
            clust)  # else:  # es una fila de ceros, entonces se agrega un cero, así si queda igual  # que kmeans labels y los otros codigos para hacer la matriz de transicion  # pero quiero esto?, no, no lo quiero por que no quiero que de un estado x  # se regrese al estado cero solo porque no hay datos, pero de todos modos lo hago  # vect_states.append(0)
    return vect_states
