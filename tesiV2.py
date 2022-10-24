from tkinter import ttk
from tkinter import *
import tkinter as tk
import time
import math
import threading
import serial.tools.list_ports
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import TESI.Scheda
from ManoV2 import Mano
from pressione import Pressione




class finestraMano():


    def __init__(self,titolo="Mano"):
        self.arduino_motori = None
        self.arduino_pressione = None
        self.arduino_guanto = None
        self.arduino=[self.arduino_motori,self.arduino_pressione,self.arduino_guanto]
        self.arduino_connesso=[False,False,False] #flag per capire se connesso
        self.dim_x = 1650
        self.dim_y = 900
        self.x0 = 20
        self.y0 = 20
        self.root=Tk()
        self.root.title(titolo)
        self.root.geometry("{}x{}+{}+{}".format(self.dim_x,self.dim_y,self.x0,self.y0))

        self.initNotebook()
        self.initTab()
        self.tabConnessioni(self.tab_connessioni)


    def initNotebook(self):
        self.notebook_1 = ttk.Notebook(self.root,width=340,height=self.dim_y-50)
        self.notebook_2 = ttk.Notebook(self.root,width=400,height=self.dim_y-50)
        self.notebook_3 = ttk.Notebook(self.root,width=470, height=self.dim_y - 50)

    def initTab(self):
        #1
        self.tab_controllo = Frame(self.notebook_1)
        self.tab_impostazioni = Frame(self.notebook_1)
        self.notebook_1.add(self.tab_controllo, text="Controllo")
        self.notebook_1.add(self.tab_impostazioni, text="Impostazioni")
        self.notebook_1.place(x=390, y=10)
        #2
        self.tab_creatore_1 = Frame(self.notebook_2)
        self.notebook_2.add(self.tab_creatore_1, text="Movimenti")
        self.notebook_2.place(x=730, y=10)
        #3
        self.tab_connessioni=Frame(self.notebook_3)
        self.tab_seriale=Frame(self.notebook_3)
        self.notebook_3.add(self.tab_connessioni,text="Connessioni")
        self.notebook_3.add(self.tab_seriale,text="Monitor Seriale")
        self.notebook_3.place(x=1130,y=10)



    def tabConnessioni(self,tab):
        self.bt_scansiona=Button(tab,text="Scansiona",command=self.scansionePorte)
        self.bt_scansiona.place(x=10,y=5)
        Label(tab, text="Motori & Retroazione: ").place(x=10, y=35)
        Label(tab, text="Pressione: ").place(x=10, y=65)
        Label(tab, text="Guanto: ").place(x=10, y=95)
        ttk.Separator(tab, orient='horizontal').place(x=10, y=145, relwidth=0.9)

        self.elenco=[]
        anteprima = tk.StringVar(value="Seleziona porta")
        #COMBO1
        self.combo1 = ttk.Combobox(tab, textvariable=anteprima)
        self.combo1.place(x=140, y=35)
        self.combo1["state"]=DISABLED

        #COMBO2
        self.combo2 = ttk.Combobox(tab, textvariable=anteprima)
        self.combo2.place(x=140, y=65)
        self.combo2["state"] = DISABLED
        # COMBO3
        self.combo3 = ttk.Combobox(tab, textvariable=anteprima)
        self.combo3.place(x=140, y=95)
        self.combo3["state"] = DISABLED

        Label(tab, text="Elenco porte COM").place(x=10, y=150)

        self.label_porte = Label(tab, text="--------------\n--------------")
        self.label_porte.place(x=10, y=170)

        Button(tab, text="Connetti",command=lambda: self.connetti(0)).place(x=350, y=32)
        Button(tab, text="Connetti", command=lambda: self.connetti(1)).place(x=350,y=62)
        Button(tab, text="Connetti", command=lambda: self.connetti(2)).place(x=350, y=92)



    def connetti(self,i):
        print("Mi collego a arduino "+str(i))


    def scansionePorte(self):
        self.port_list=serial.tools.list_ports.comports(include_links=False)
        self.porte=""
        self.elenco.clear()
        for x in self.port_list:
            self.porte=x.device+" ---> "+x.description+"\n" #COM4 --> Arduino Uno
            self.elenco.append(x.device)

        self.combo1["values"] = self.elenco
        self.combo2["values"] = self.elenco
        self.combo3["values"] = self.elenco

        if(self.porte==""):
            print("Non ho trovato nulla")
            self.label_porte["text"]="Non ho trovato nulla"
        else:
            self.label_porte["text"] = self.porte
            if(self.arduino_connesso[0]==False):
                self.combo1["state"] = "readonly" #attiva la selezione, opposto di disabled
            if (self.arduino_connesso[1] == False):
                self.combo2["state"] = "readonly"
            if (self.arduino_connesso[2] == False):
                self.combo3["state"] = "readonly"






mano_dx=finestraMano()
mainloop()
