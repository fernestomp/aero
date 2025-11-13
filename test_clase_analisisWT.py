#script para probar la "clase_analisisWT"
#para el archivo de excel con 16 aerogeneradores
from clase_analisisWT import analisisWT

rutaxls = '.\datos\Datos WTG 01ene2017 201916sept.xlsx'
#instanciar clasea
wt = analisisWT(rutaxls)
#generar reporte en formato pdf (primero, para que no se cierren los plot)
wt.generar_reporte_pdf()
#plot de la serie de tiempo de velocidades de viento
wt.plot_ts_viento()
#plot de la serie de tiempo de potencias acumuladas
wt.plot_ts_pot_ac()
#plot de la serie de tiempo de potencias instantaneas
wt.plot_ts_pot_ins()
#plot de la grafica v-p
wt.plot_vp()
#resumen de los datos, como numero de registro, potencia anual, etc..
wt.imprimir_reporte()

#para que no finalice el script y no se cierren las ventanas
input('Presione cualquier tecla para finalizar...')
print('Script finalizado.')
