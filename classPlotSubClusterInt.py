""'''
Crear plot interactivo para cluster y subcluster
TODO:
    -que de una opción de mostrar solo viento o potencia aunque tenga subclusters
    -que funcione si solo incluyo dfclvv aunque tenga subclusters
    -que imprima a consola con OS

'''
import matplotlib.pyplot as plt
from IPython.display import display as wgdisplay
import ipywidgets as widgets
from ipywidgets import Layout
import datetime
from matplotlib.ticker import EngFormatter
import matplotlib.patheffects as path_effects #efectos de texto
from matplotlib import font_manager
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib
import numpy as np
import os
sns.set()
plt.style.use('seaborn-white')
sns.set_style("whitegrid")

class PlotSubClusterInt:
    """
    Descripcion:
    Clase para dibujar dos subplots, uno vx vs vy y otro vviento vs Pw.

    Metodos:
        createPlot: Construye el plot de matplotlib.
            self.dfclvv: dataframe multiindice con dos columnas vx y vy agrupadas por cluster
            dfclpw: dataframe multiindice con dos columnas vviento y Pw agrupadas por cluster
            cl_method: string que almacena el metodo usado para hacer el cluster
                     |   C1    |   C2   |...
                    ----------------------
            Timestamp|  vx vy  |  vx vy |...            datavp: dataframe original de los datos de

        updatePlot: actuliza el plot en "tiempo real" segun los valores de los controles

        onClick: Es el la funcion que esta ligada al click en el plot. Solo ejecuta annotatePlot.

        annotatePlot: Crea una anotacion en el plot que indica donde el nombre del cluster mas cercano al conjunto de
              coordenadas donde se hizo click en el plot VP. Ademas muestra el cluster en el plot VV.

        blinkCluster: Resalta el cluster al que se hace referencia.

    Argumentos:
        cl_scl_order: el orden en que se hicieron los clusters (viento,viento), (viento,potencia),
            (potencia,viento),(potencia,potencia)
    """

    def __init__(self):
        self.save_fig = None
        self.text_log = None
        self.pw_col_name = None
        self.wind_col_name = None
        self.axvp = None
        self.formatterPw = None
        self.fig = None
        self.axvv = None
        self.tbFilePath = None
        self.wchkcls = None
        self.tbreta = None
        self.wradText = None
        self.chkShowCPotFab = None
        self.chkShowBetz = None
        self.chkLimGlob = None
        self.chkShowCnt = None
        self.wdgPSize = None
        self.btnSelNoneChk = None
        self.btnSelAllChk = None
        self.btnUpdate = None
        self.vxmaxGlob = None
        self.pmaxGlob = None
        self.vvmaxGlob = None
        self.vvminGlob = None
        self.pminGlob = None
        self.vymaxGlob = None
        self.vyminGlob = None
        self.vxminGlob = None
        self.cl_avail = None
        self.clnames_all = None
        self.n_tot_clusters = None
        self.idx_centroids_sc = None
        self.idx_centroids = None
        self.dfclvp = None
        self.n_clusters = None
        self.showLegends = None
        self.savepath = None
        self.showlBetz = None
        self.showCent = None
        self.showMfgCurve = None
        self.showOpts = None
        self.vvento = None
        self.PMaxViento = None
        self.cl_scl_order = None
        from colorsys import hls_to_rgb
        self.fignum=999
        self.filename=None
        self.fisize = (5, 5)
        self.fontsize = 13
        self.labelFontSize = 13
        self.tickFontSize = 12
        self.markerSize = 100
        self.fontNameLabel = {'fontname':'Times New Roman'}
        self.fontNameCluster = {'fontname':'Arial'}
        self.ticks_font = font_manager.FontProperties(family='Times New Roman', style='normal',
                                                      size=self.labelFontSize, weight='normal', stretch='normal')
        self.n_subclu = 0
        colors1 = plt.cm.tab20(np.linspace(0., 1, 20))
        colors2 = plt.cm.Spectral(np.linspace(0, 1, 10))
        colorstab = np.vstack((colors1, colors2))
        self.mapa_colores=colorstab
        self.fisize = None
        self.dfclvv = None
        self.datavp = None
        self.dfMfgCurve=None
        self.dfclvp_is_empty = True
        #este backend junto con %matplotlib notebook
        #hacen que el plot se actualice bien y aparecen
        #los controles
        #matplotlib.use('nbAgg')

    def create_plot(self, dfclvv, dfclvp=None,datavp=None,figsize=(5, 5), cl_scl_order=(None, None),
                    idx_centroids=None,idx_centroids_sc=None,fign=999, save_folder='', showCent =True,
                    showlBetz = False,showMfgCurve=False, showOpt = 'Magnitud',dfMfgCurve=None,
                    showLegends = True, wind_col_name ='vwind',pw_col_name='pw',save_fig=False, filename = 'None'):
        """

        :param filename: Nombre de archivo con el que se guarda la figura.
        :param pw_col_name: Nombre que tiene el encabezado de la columna de potencia.
        :param wind_col_name: Nombre que tiene el encabezado de la columna de viento.
        :param dfclvv: df que contiene los clusters de viento en forma de Cx(vx,vy)
        :param dfclvp: df que contiene los clusters de potencia en forma de Cx(vv,pw)
        :param datavp: df con los datos de viento y potencia.
        :param figsize: tamaño de la figura
        :param cl_scl_order: En el caso de ser doble clusterizado, es el orden en que se hizo el clusterizado.
        :param idx_centroids: contiene los identificadores de los centroides, tales como, el numero de cluster, la
        posicion (vx,vy) del centroide, etc.
        :param idx_centroids_sc: contiene los identificadores de los centroides de los subclusters, tales como, el
        numero de cluster, la posicion (vx,vy) del centroide, etc.
        :param fign: numero de figura.
        :param save_folder: ruta donde se guardará la imagen del plot, sin el nombre de la figura.
        :param showCent: Valor boleano que define si se mostrarán los centroides o no en el plot.
        :param showlBetz: Valor boleano que define si se mostrará el límite de Beltz o no.
        :param showMfgCurve: Valor boleano que define si se mostrará la curva del fabricante o no.
        :param showOpt: Pertenece al widget option, que da la opción de mostrar el número de cluster, la magnitud o
        el nombre del cluster.
        :param dfMfgCurve: df que contiene los datos de viento y potencia de la curva del fabricante.
        :param showLegends: Mostrar las leyendas o no.
        """
        self.dfMfgCurve=dfMfgCurve
        if self.dfMfgCurve is None:
            print('Manufacturer power curve missing')
        self.showLegends = showLegends
        self.cl_scl_order = cl_scl_order
        self.save_fig=save_fig
        self.dfclvp =dfclvp
        self.dfclvv = dfclvv
        self.datavp = datavp
        self.n_clusters = len(self.dfclvv.columns.levels[0])
        self.n_tot_clusters =self.n_clusters
        self.fignum = fign
        self.wind_col_name = wind_col_name
        self.pw_col_name = pw_col_name
        self.idx_centroids = idx_centroids
        self.idx_centroids_sc = idx_centroids_sc
        self.save_folder = save_folder
        self.filename = filename
        self.showlBetz = showlBetz # show Betz's limit
        self.showCent = showCent # show clusters centroids
        self.showMfgCurve = showMfgCurve #show manufacturer's curve
        #which value is shown in the plot magnitude,cluster number,cluster name, none
        self.showOpts = showOpt

        #check if power data was passed
        if self.dfclvp is not None:
            self.dfclvp_is_empty = False

        ##################################
        #        limite de betz          #
        ##################################
        if not self.dfclvp_is_empty:
            A=np.pi*45**2
            Cp = 0.59 #limite de Betz
            rho = 1.1349
            self.vvento = np.unique(datavp[wind_col_name].values)
            self.PMaxViento = 1/2*rho*A*self.vvento**3*Cp

        #########################################
        #           CREAR PLOT                  #
        #########################################

        #para poner el plot dentro de un widget
        #self.output = widgets.Output()
        plt.ioff()
        self.fig = plt.figure(self.fignum, figsize=self.fisize,constrained_layout=True)
        #1k, 1M
        self.formatterPw = EngFormatter(places=1, sep="\N{THIN SPACE}")  # U+2009
        # 3 because is cluster,subcluster,vx and vy
        if len(dfclvv.columns[0]) == 3:
            #last column has the last subcluster name SCn, this gives n
            self.n_subclu=int(dfclvv.columns[-1][1][2:])

        if not self.dfclvp_is_empty:
            self.axvv = self.fig.add_subplot(121)
            if self.n_subclu > 0:  # existen subclusters , sino seria 2
                #numero total de clusters incluidos los subclusters
                self.n_tot_clusters = self.n_subclu*self.n_clusters
                # solo aplica cuando hay subclusters
                lev0 = self.dfclvv.columns.get_level_values(0)
                lev1 = self.dfclvp.columns.get_level_values(1)
                namcl = [(lev0[i],lev1[i]) for i in range(len(lev0))]
                #self.clnames_all = sorted(namcl[::2]) #todos los clusters y subclusters disponibles
                self.clnames_all = namcl[::2] #todos los clusters y subclusters disponibles
                #ordenar
                vv = [self.idx_centroids_sc.loc[c][wind_col_name] for c in self.clnames_all]
                idx = np.argsort(vv)
                x=[self.clnames_all[i] for i in idx]
                self.clnames_all=x.copy()
                del x
                #nombre de los clusters disponibles sin el nombre de los subclusters
                #self.cl_avail =sorted(set(item[0] for item in self.clnames_all))
                self.cl_avail =set(item[0] for item in self.clnames_all)
                #### BUSCAR MINIMOS Y MAXIMOS GLOBALES  (hacerlo más elegante)
                l=[self.dfclvv[cl].min() for cl in self.clnames_all]
                self.vxminGlob,self.vyminGlob =   np.amin(l,axis=0)
                l=[self.dfclvv[cl].max() for cl in self.clnames_all]
                self.vxmaxGlob,self.vymaxGlob =   np.amax(l,axis=0)

            else:  # no hay subcluster
                #lista ordenada con numeros y letras
                #self.clnames_all=sorted(dfclvv.columns.levels[0],
                #                        key=lambda x: int("".join([i for i in x if i.isdigit()])))
                self.clnames_all = self.dfclvv_in.columns.levels[0]
                #self.cl_avail =sorted(set(item for item in self.clnames_all))
                self.cl_avail =set(item for item in self.clnames_all)
            l=[self.dfclvp[cl].min() for cl in self.clnames_all]
            self.vvminGlob,self.pminGlob =   np.amin(l,axis=0)
            l=[self.dfclvp[cl].max() for cl in self.clnames_all]
            self.vvmaxGlob,self.pmaxGlob =   np.amax(l,axis=0)
        else:
            self.axvv = self.fig.add_subplot()
            #lista ordenada con numeros y letras
            self.clnames_all=sorted(dfclvv.columns.levels[0],
                                    key=lambda x: int("".join([i for i in x if i.isdigit()])))
            #self.cl_avail =sorted(set(item for item in self.clnames_all))
            self.cl_avail =set(item for item in self.clnames_all)
        #### BUSCAR MINIMOS Y MAXIMOS GLOBALES  (hacerlo más elegante)
        l=[self.dfclvv[cl].min() for cl in self.clnames_all]
        self.vxminGlob,self.vyminGlob =   np.amin(l,axis=0)
        l=[self.dfclvv[cl].max() for cl in self.clnames_all]
        self.vxmaxGlob,self.vymaxGlob =   np.amax(l,axis=0)

        if not self.dfclvp_is_empty:
            self.axvp = self.fig.add_subplot(122)
            self.axvp.yaxis.set_major_formatter(self.formatterPw)



        ##############################################################################
        #                             WIDGETS                                        #
        ##############################################################################

        self.btnUpdate = widgets.Button(description='Actualizar')

        self.btnUpdate.on_click(self.update_plot)
        self.btnSelAllChk = widgets.Button(description='Sel. todo')
        self.btnSelAllChk.on_click(self.sel_all_chk)
        self.btnSelNoneChk = widgets.Button(description='Des. todo')
        self.btnSelNoneChk.on_click(self.sel_none_chk)
        self.wdgPSize = widgets.IntSlider(
            value=2,
            min=1,
            max=20,
            step=1,
            description='Point size:',
            continuous_update=False)
        self.chkLimGlob = widgets.Checkbox(
            value=True, description='Límites Globales')
        self.chkShowCnt = widgets.Checkbox(
            value=self.showCent, description='Mostrar centroides')
        self.chkShowBetz = widgets.Checkbox(
            value=self.showlBetz, description='Mostrar línea Betz')
        self.chkShowCPotFab = widgets.Checkbox(
            value=self.showMfgCurve, description='Mostrar curva Fab.')
        if not self.dfclvp_is_empty:
            if self.dfMfgCurve is not None:
                self.chkShowCPotFab.disabled= False
            else:
                self.chkShowCPotFab.disabled= True
        else:
            self.chkShowBetz.disabled=True


        self.tbreta = widgets.IntText(
            value=0, description='Retardo:', layout=Layout(width='90%', height='80px'))
        self.wradText = widgets.RadioButtons(
            options=['Magnitud', 'Numero', 'Clusters', 'Ninguno'],
            description='Mostrar texto:')
        self.wradText.value= self.showOpts
        # figsave_folder = self.save_folder
        # figsavetime = datetime.datetime.now().strftime("%d-%m-%Y_%H_%M_%S_%f")
        # if self.filename is None:
        #     #poner como nombre del archivo los datos de la creacion de la imagen
        #     figsavename = 'clustersplot'+str(self.n_clusters)+'SCl'+str(self.n_subclu)+'_'
        #
        # else:
        #     figsavename = self.filename
        self.tbFilePath = widgets.Text(description='Save path:', layout=Layout(width='90%', height='80px'))
        self.chkShowCnt.observe(self.update_plot, 'value')
        self.wdgPSize.observe(self.update_plot, 'value')
        self.wradText.observe(self.update_plot, 'value')
        self.chkShowBetz.observe(self.update_plot, 'value')
        self.chkShowCPotFab.observe(self.update_plot, 'value')


        self.wchkcls=[] #lista de checbox con los nombresde los clusters
        n=1#para numerar la lista de clusters
        for i in range(len(self.clnames_all)):
            self.wchkcls.append(widgets.Checkbox(
                value=True, description=str(n) +'-' +str(self.clnames_all[i])))
            n+=1
        box_layout = Layout(display='flex',
                            flex_flow='column',
                            align_items='stretch',
                            height='200px',
                            )
        vbchkcls = widgets.VBox(self.wchkcls, layout=box_layout)

        self.text_log=widgets.Text(
            value='',
            placeholder='Log',
            disabled=False
        )

        # -------------   WIDGETS EN CAJAS ----------------------
        vbopt1 = widgets.VBox([self.chkShowCnt,self.chkShowBetz, self.chkShowCPotFab,self.chkLimGlob, self.tbreta])
        vbopt2 = widgets.VBox([self.wradText, self.wdgPSize ])
        vbButtons = widgets.VBox([self.btnSelAllChk,self.btnSelNoneChk, self.btnUpdate, self.tbFilePath])
        vblog = widgets.VBox([self.text_log])
        items = [vbButtons, vbchkcls,vbopt1,vbopt2]
        hb = widgets.HBox(items)
        wgdisplay(hb)
        wgdisplay(vblog)
        #wgdisplay(self.fig)
        #####################################
        #               PLOTs               #
        #####################################

        self.update_plot(1)

    def sel_all_chk(self,val):
        """

        :param self:
        :param val:
        """
        for item in self.wchkcls:
            item.value=True
    def sel_none_chk(self,val):
        """

        :param self:
        :param val:
        """
        for item in self.wchkcls:
            item.value=False
    def save_plot(self,val):
        """
        Guarda la imagen del plot.
        :param self:
        :param val:
        """
        self.text_log.value ='Guardando plot...'
        #check variable names, etc..
        #si no tiene el caracter diagonal al final, lo pone
        if self.save_folder.find('/') ==-1:
            self.save_folder+= '/'
        #revisar si la carpeta existe
        if not os.path.isdir(self.save_folder):
            #crear carpeta
            os.mkdir(self.save_folder)
            text = 'El directorio no existe. ' + self.save_folder + ' ha sido creado.'
            os.write(1,bytes(text))

        if self.filename is None:
            #poner como nombre del archivo los datos de la creacion de la imagen
            figsavename = 'clustersplot'+str(self.n_clusters)+'SCl'+str(self.n_subclu)+'_'
        else:
            figsavename = self.filename
        figsavetime = datetime.datetime.now().strftime("%d-%m-%Y_%H_%M_%S_%f")
        self.tbFilePath = widgets.Text(
            value=self.save_folder+figsavename+ '_' +figsavetime+'.jpg',
            description='Save path:', layout=Layout(width='90%', height='80px'))
        plt.savefig(  self.tbFilePath.value, bbox_inches='tight', pad_inches=0.1)
        #print('Saved in ' +  self.tbFilePath.value)
        self.text_log.value ='Plot guardado en: ' + self.tbFilePath.value
    def update_plot(self, val):
        """
        :param self:
        :param val:
        """
        self.text_log.value = 'Actualizando plot...'
        pSize = self.wdgPSize.value
        self.axvv.axes.clear()
        self.axvv.grid(visible = True)

        if not self.dfclvp_is_empty:
            self.axvp.axes.clear()
            self.axvp.grid()

        if self.n_subclu>0 :  # existen subclusters
            clnames= [eval(el.description.split('-')[1]) for el in self.wchkcls if el.value==True]
            #ordenar subclusters por velocidad
            #los subclusters se ordenan dentro de cada grupo de clusters en idx_centrods_sc
            #hay que ordenarlos tambien globalmente y no solo localmente
            #self.cl_avail =sorted(set(item[0] for item in clnames))
            vv = [self.idx_centroids_sc.loc[c][self.wind_col_name] for c in clnames]
            idx = np.argsort(vv)
            x=[clnames[i] for i in idx]
            clnames=x.copy()
            del x
            #self.clnames_all =clnames# REV: SE OCUPA CLNAMES_ALL???
            self.cl_avail =set(item[0] for item in clnames)

        else :
            clnames=[el.description.split('-')[1] for el in self.wchkcls if el.value==True]
            #aqui tambien va por si se eliminan todos los subclusters del mismo cluster. Solo lista los clusters
            #self.cl_avail =sorted(set(item for item in clnames))
            self.cl_avail =set(item for item in clnames)

        #################### DEFINIR LIMITES DE PLOT #######################

        #buscar los minimos y maximos de los clusters
        #debede haber una forma mas elegante de hacerlo. Como hago sliced elmultiindex con tuplas

        lvxmin=np.empty(self.n_tot_clusters)
        lvxmin.fill(np.nan)
        lvymin=np.empty(self.n_tot_clusters)
        lvymin.fill(np.nan)
        lvxmax=np.empty(self.n_tot_clusters)
        lvxmax.fill(np.nan)
        lvymax=np.empty(self.n_tot_clusters)
        lvymax.fill(np.nan)
        lvvmin=np.empty(self.n_tot_clusters)
        lvvmin.fill(np.nan)
        lvvmax=np.empty(self.n_tot_clusters)
        lvvmax.fill(np.nan)
        lpmin =np.empty(self.n_tot_clusters)
        lpmin.fill(np.nan)
        lpmax= np.empty(self.n_tot_clusters)
        lpmax.fill(np.nan)
        n=0
        for cl in clnames:
            lvxmin[n],lvymin[n]= self.dfclvv[cl].min()
            lvxmax[n],lvymax[n] = self.dfclvv[cl].max()
            if not self.dfclvp_is_empty:
                lvvmin[n],lpmin[n] = self.dfclvp[cl].min()
                lvvmax[n],lpmax[n] = self.dfclvp[cl].max()
            n+=1
        vxmin=np.nanmin(lvxmin)
        if np.isnan(vxmin):
            vxmin=0
        vymin = np.nanmin(lvymin)
        if np.isnan(vymin):
            vymin =0
        vxmax = np.nanmax(lvxmax)
        if np.isnan(vxmax):
            vxmax=1
        vymax = np.nanmax(lvymax)
        if np.isnan(vymax):
            vymax=1

        if not self.dfclvp_is_empty:
            vvmin = np.nanmin(lvvmin)
            if np.isnan(vvmin):
                vvmin=0
            vvmax = np.nanmax(lvvmax)
            if np.isnan(vvmax):
                vvmax=1
            pmin= np.nanmin(lpmin)
            if np.isnan(pmin):
                pmin=0
            pmax = np.nanmax(lpmax)
            if np.isnan(pmax):
                pmax=1

        if self.chkLimGlob.value:#plotear con limites globales o con los limites del cluster
            self.axvv.set_xlim((self.vxminGlob, self.vxmaxGlob))
            self.axvv.set_ylim((self.vyminGlob, self.vymaxGlob))
            if not self.dfclvp_is_empty:
                self.axvp.set_xlim((self.vvminGlob, self.vvmaxGlob))
                self.axvp.set_ylim((self.pminGlob, self.pmaxGlob))
        else:
            self.axvv.set_xlim((vxmin, vxmax))
            self.axvv.set_ylim((vymin, vymax))
            if not self.dfclvp_is_empty:
                self.axvp.set_xlim((vvmin, vvmax))
                self.axvp.set_ylim((pmin, pmax))


        #####################   PLOTEAR   #########################

        for item in clnames:
            #busca el cluster actual y devuelve el indice dentro de la lista de clusters donde lo encuentra
            #es decir, asocia un numero unico a un nombre de cluster
            #es para que el color de los clusters sea el mismo siempre
            idxClName = [ncl_ for ncl_, clname_ in enumerate(self.clnames_all) if clname_ == item]
            #self.fig.suptitle('Grupos de velocidad de viento y potencia', y=1)
            # magnitud del vector

            magni = round(
                np.mean(
                    np.sqrt(self.dfclvv[item].vx**2 +
                            self.dfclvv[item].vy**2)),
                1)  # magnitud de la vv

            self.axvv.scatter(
                self.dfclvv[item].vx,
                self.dfclvv[item].vy,
                s=pSize,
                c=self.mapa_colores[idxClName],
                alpha=1)
            if not self.dfclvp_is_empty:
                self.axvp.scatter(
                    self.dfclvp[item][self.wind_col_name],
                    self.dfclvp[item][self.pw_col_name],
                    s=pSize,
                    c=self.mapa_colores[idxClName],
                    alpha=1)

            ###########################  MOSTRAR TEXTO ###########################
            if self.wradText.index == 0: #magnitud

                text = self.axvv.text(
                    self.dfclvv[item].vx.mean(),
                    self.dfclvv[item].vy.mean(),
                    magni,
                    fontsize=self.fontsize,
                    weight='bold',
                    color='w',
                    alpha=1,
                    zorder=100,
                    **self.fontNameCluster
                )
                text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                       path_effects.Normal()])

                if not self.dfclvp_is_empty:
                    text = self.axvp.text(
                        self.dfclvp[item][self.wind_col_name].mean(),
                        self.dfclvp[item][self.pw_col_name].mean(),
                        magni,
                        fontsize=self.fontsize,
                        weight='bold',
                        color='w',
                        alpha=1,
                        zorder=100,
                        **self.fontNameCluster
                    )
                    text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                           path_effects.Normal()])

            elif self.wradText.index == 1: #numero
                text = self.axvv.text(
                    self.dfclvv[item].vx.mean(),
                    self.dfclvv[item].vy.mean(),
                    idxClName[0]+1,
                    fontsize=self.fontsize,
                    weight='bold',
                    color='w',
                    alpha=1,
                    zorder=100,
                    **self.fontNameCluster
                )
                text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                       path_effects.Normal()])

                if not self.dfclvp_is_empty:
                    text = self.axvp.text(
                        self.dfclvp[item][self.wind_col_name].mean(),
                        self.dfclvp[item][self.pw_col_name].mean(),
                        idxClName[0]+1,
                        fontsize=self.fontsize,
                        weight='bold',
                        color='w',
                        alpha=1,
                        zorder=100,
                        **self.fontNameCluster
                    )
                    text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                           path_effects.Normal()])

            elif self.wradText.index == 2:
                text = self.axvv.text(
                    self.dfclvv[item].vx.mean(),
                    self.dfclvv[item].vy.mean(),
                    item,
                    fontsize=self.fontsize,
                    weight='bold',
                    color='w',
                    alpha=1,
                    zorder=100,
                    **self.fontNameCluster
                )
                text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                       path_effects.Normal()])

                if not self.dfclvp_is_empty:
                    text = self.axvp.text(
                        self.dfclvp[item][self.wind_col_name].mean(),
                        self.dfclvp[item][self.pw_col_name].mean(),
                        item,
                        fontsize=self.fontsize,
                        weight='bold',
                        color='w',
                        alpha=1,
                        zorder=100,
                        **self.fontNameCluster
                    )
                    text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='k'),
                                           path_effects.Normal()])

        #################### MOSTRAR CENTROIDES#######################
        if self.chkShowCnt.value:

            for cl in self.cl_avail:

                #el nombred el cluster esta en el indice
                #le quito la letra con cl[1:] y dejo solo el numero como
                #esta en el dataframe
                numcl = int(cl[1:])
                self.axvv.scatter(
                    self.idx_centroids.loc[numcl].vx,
                    self.idx_centroids.loc[numcl].vy,
                    marker='X',
                    edgecolor='black',
                    linewidth=1,
                    facecolor='yellow',
                    s=self.markerSize)
                if not self.dfclvp_is_empty:
                    self.axvp.scatter(
                        self.idx_centroids.loc[numcl][self.wind_col_name],
                        self.idx_centroids.loc[numcl][self.pw_col_name],
                        marker='X',
                        edgecolor='black',
                        linewidth=1,
                        facecolor='yellow',
                        s=self.markerSize)

            ################# MOSTRAR CENTROIDES SUBCLUSTERS #####################
            if self.n_subclu > 0:
                for el in clnames:
                    self.axvv.scatter(
                        self.idx_centroids_sc.loc[el].vx,
                        self.idx_centroids_sc.loc[el].vy,
                        marker='h',
                        edgecolor='black',
                        linewidth=1,
                        facecolor='aqua',
                        s=self.markerSize)
                    if not self.dfclvp_is_empty:
                        self.axvp.scatter(
                            self.idx_centroids_sc.loc[el][self.wind_col_name],
                            self.idx_centroids_sc.loc[el][self.pw_col_name],
                            marker='h',
                            edgecolor='black',
                            linewidth=1,
                            facecolor='aqua',
                            s=self.markerSize)
        ################## MOSTRAR CURVA DEL FABRICANTE #####################
        if not self.dfclvp_is_empty:
            if self.chkShowCPotFab.value:
                self.axvp.plot(self.dfMfgCurve.index, self.dfMfgCurve.pw, c='red', label='Manufacturer')
        ################## MOSTRAR LIMITE DE BETZ ###########################
        if not self.dfclvp_is_empty:
            if self.chkShowBetz.value:
                self.axvp.plot(self.vvento,self.PMaxViento,label='Betz',c='y')
        ################# CONFIGURAR TEXTOS DEL PLOT #########################
        self.axvv.set_xlabel('vx [m/s]',fontsize = self.labelFontSize, **self.fontNameLabel)
        self.axvv.set_ylabel('vy [m/s]',fontsize = self.labelFontSize, **self.fontNameLabel)
        self.axvv.tick_params(axis='both', which='major')

        #con esto cambio el texto de las thicks a el que defino en self.tick_font
        for label in self.axvv.get_xticklabels():
            label.set_fontproperties(self.ticks_font)
        for label in self.axvv.get_yticklabels():
            label.set_fontproperties(self.ticks_font)

        if not self.dfclvp_is_empty:
            self.axvp.set_xlabel('Wind Speed [m/s]',fontsize = self.labelFontSize, **self.fontNameLabel)
            self.axvp.set_ylabel('Power [W]',fontsize = self.labelFontSize, **self.fontNameLabel)
            self.axvp.tick_params(axis='both', which='major')
            for label in self.axvp.get_xticklabels():
                label.set_fontproperties(self.ticks_font)
            for label in self.axvp.get_yticklabels():
                label.set_fontproperties(self.ticks_font)
        ################### MOSTRAR LEYENDA ################################
        if self.showLegends:
            legCentroids = mlines.Line2D([], [], color='yellow', marker='X', linestyle='None',
                                         markersize=10, label='Centroids',markeredgecolor='black',markeredgewidth=1.5)
            if self.n_subclu > 0:
                legSecCentroids = mlines.Line2D([], [], color='aqua', marker='h', linestyle='None',
                                                markersize=10, label='Sec. centroids',markeredgecolor='black',markeredgewidth=1)
                if not self.dfclvp_is_empty:
                    self.axvp.legend(handles=[legCentroids, legSecCentroids],facecolor = 'gainsboro',
                                     frameon=True, loc='upper left')
                self.axvv.legend(handles=[legCentroids, legSecCentroids],facecolor = 'gainsboro',
                                 frameon=True, loc='upper right')
            else:
                self.axvv.legend(handles=[legCentroids],facecolor = 'gainsboro',frameon=True, loc='upper right')
                if not self.dfclvp_is_empty:
                    self.axvp.legend(handles=[legCentroids],facecolor = 'gainsboro',frameon=True, loc='upper left')
        ################### MOSTRAR PLOT #################################
        self.fig.canvas.toolbar_position= 'left'
        self.fig.canvas.toolbar_visible = True
        # Disable the resizing feature
        self.fig.canvas.resizable = True
        # If true then scrolling while the mouse is over the canvas will not move the entire notebook
        self.fig.canvas.capture_scroll = True
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.text_log.value = 'Plot actualizado.'
        if self.save_fig:
            self.save_plot(val)
        plt.show()