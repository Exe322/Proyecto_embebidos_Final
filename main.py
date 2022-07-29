import serial
import time
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import tkinter as tk
import sys


# Encontrar puerto en raspberry: dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1

class App:
    # definir inicio de clase
    def __init__(self):

        # ventana y funciones principales
        self.root = tk.Tk()
        self.root.title('Control de temperatura')
        self.inicio()
        self.label()
        self.grafico()
        self.root.mainloop()

    # función para iniciar el puerto serial, definir figura y vectores
    def inicio(self):

        # Iniciar puerto serial en el 'COM9' a 9600 baudios
        self.ser = serial.Serial(port='COM9', baudrate=9600)
        # borrar buffer de entrada
        self.ser.flushInput()
        # Crear figura para el gráfico, tamaño y proporción
        self.fig = plt.figure(figsize=(6, 4), dpi=100)
        # posición del plot
        self.ax = self.fig.add_subplot(111)
        # vectores vacíos xs,ys,rs
        self.xs = []
        self.ys = []
        self.rs = []

    # función para encender o apagar relé
    def rele(self, T_medida):

        # Condición para una temperatura medida menor que la de referencia
        if float(T_medida) < t_ref:
            # variable string 'ON' para enviar a arduino y encender relé
            self.dato = "ON"
            self.ser.write(self.dato.encode())
        # Condición para una temperatura medida mayor o igual que la de referencia
        elif float(T_medida) >= t_ref:
            # variable string 'OFF' para enviar a arduino y apagar relé
            self.dato = "OFF"
            self.ser.write(self.dato.encode())

    # función para mostrar valores en la ventana
    def label(self):

        # label de temperatura medida y posición
        self.label_Tmedida = ttk.Label(self.root, text="Temperatura medida : ")
        self.label_Tmedida.grid(column=0, row=2, padx=160, pady=10, sticky='e', columnspan=2)

        # label de Corriente rms medida y posición
        self.label_Irms = ttk.Label(self.root, text="Corriente: ")
        self.label_Irms.grid(column=0, row=3, padx=10, pady=10, sticky='w')

        # label de consumo y posición
        self.label_consumo = ttk.Label(self.root, text="Consumo: ")
        self.label_consumo.grid(column=0, row=3, padx=120, pady=10, sticky='w')

    # función para realizar dos gráficas en tiempo real
    def animate(self, i, xs, ys, rs):

        # lectura de bytes de arduino temperatura, corriente
        line = self.ser.readline()  # ascii
        # divide los bytes recibidos en ','
        temperatura = line.split(b',')
        # variable de temperatura en formato decimal (0,00)
        T_medida = float(temperatura[0])
        # comienzo de la variable de corriente
        c = temperatura[1]
        # segunda variable corriente
        lista_corriente = c.split(b'\n')
        # variable de corriente en formato decimal (0,00)
        corriente = float(lista_corriente[0])
        # corriente rms en Ampere con 3 decimales
        I_rms = round(corriente * 0.707, 3)
        # Consumo en watt con 2 decimales
        consumo = round(I_rms * 220, 2)

        # Condicional Filtro de temperatura
        if T_medida == -127.00:
            # filtro para el error de medición de temperatura (temperatura = -127)
            T_medida = ys[-1]
            # agregar al vector el valor de T_medida
            ys.append(T_medida)

        else:
            # agregar al vector el valor de T_medida
            ys.append(T_medida)

        # Llamar a la función relé con la medida de temperatura
        self.rele(str(T_medida))

        # label de temperatura medida y posición
        self.label_Tmedida.config(text="Temperatura medida : " + str(T_medida) + ' ')
        #self.label_Tmedida.grid(column=0, row=2, padx=160, pady=10, sticky='e', columnspan=2)

        # label de Corriente rms medida y posición
        self.label_Irms.config(text="Corriente: " + str(I_rms) + ' ')
        #self.label_Irms.grid(column=0, row=3, padx=10, pady=10, sticky='w')

        # label de consumo y posición
        self.label_consumo.config(text="Consumo: " + str(consumo) + ' ')
        #self.label_consumo.grid(column=0, row=3, padx=120, pady=10, sticky='w')

        # Mostrar las variables de temperatura y corriente
        print('temperatura, corriente =', '(', T_medida, ',', I_rms, ')')

        # agregar al vector xs el parámetro i [0,1,...,i]
        xs.append(i)
        # agregar al vector rs el parámetro temperatura de referencia
        rs.append(t_ref)

        # límite de items en el gráfico (200 puntos de muestra) para xs, ys y rs
        self.xs = xs[-200:]
        self.ys = ys[-200:]
        self.rs = rs[-200:]

        # borrar datos para no almacenar en la memoria ram
        self.ax.clear()
        # crear graficar datos del sensor de temperatura
        self.ax.plot(xs, ys)
        # crear grafica de  temperatura referencia
        self.ax.plot(xs, rs)
        # borrar valores numéricos del eje x
        self.ax.set_xticks([])

        # Formato del grafico
        plt.subplots_adjust(top=None, bottom=None)
        self.ax.set_title('')
        self.ax.set_ylabel('Temperatura (°C)')

    # Función salir
    def salir(self):
        # pausar animación de la función animate
        ani.pause()
        # tiempo de espera de 1 segundo
        time.sleep(1)
        # enviar string 'OFF' para apagar relé
        dato = "OFF"
        self.ser.write(dato.encode())
        # tiempo de espera de 1 segundo
        time.sleep(1)
        # cerrar todos los procesos
        sys.exit()

    # función para iniciar el gráfico
    def grafico(self):
        # variable global ani
        global ani
        # crear label para la temperatura de referencia y posición
        self.label_t = ttk.Label(self.root, text="Temperatura de referencia:")
        self.label_t.grid(column=0, row=2, padx=10, pady=10, sticky='w')

        # botón de Salir y posición del botón
        boton = ttk.Button(self.root, text="Salir", command=lambda: self.salir())
        boton.grid(column=0, row=2, padx=5, pady=10, sticky='e')

        # cuadro de entrada para la temperatura de referencia y posición
        self.entrada = tk.Entry(self.root, width=4)
        self.entrada.grid(column=0, row=2, padx=155, pady=10, sticky='w')

        # botón para seleccionar la temperatura de referencia
        boton1 = ttk.Button(text='Set', width=5, command=lambda: self.t_input())
        boton1.grid(column=0, row=2, padx=188, pady=5, sticky='w')

        # Crear lienzo para la gráfica y posición
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().grid(column=0, row=1)

        # gráfica en tiempo real
        ani = animation.FuncAnimation(self.fig, self.animate, fargs=(self.xs, self.ys, self.rs),
                                      interval=1500, repeat=False)
        # Actualizar ventana
        self.root.update()

    # temperatura de referencia de entrada
    def t_input(self):
        # variable global de t_ref
        global t_ref
        # condicional de entrada distinto de vacío
        if self.entrada.get() != '':
            # crear variable t
            t = self.entrada.get()
            # asignar t como numero flotante
            t_ref = float(t)
        # devolver el valor de t_ref
        return t_ref


# Iniciar la aplicación
if __name__ == '__main__':
    t_ref = 0
    App()
