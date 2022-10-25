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
#from ManoV2 import Mano
#from pressione import Pressione




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
        self.initTabConnessioni(self.tab_connessioni)
        self.initTabSeriale(self.tab_seriale)


    def initNotebook(self):
        self.notebook_1 = ttk.Notebook(self.root,width=340,height=self.dim_y-50)
        self.notebook_2 = ttk.Notebook(self.root,width=400,height=self.dim_y-50)
        self.notebook_3 = ttk.Notebook(self.root,width=470, height=self.dim_y-50)

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



    def initTabConnessioni(self,tab):
        self.combo=[]
        self.bt_scansiona=Button(tab,text="Scansiona",command=self.scansionePorte)
        self.bt_scansiona.place(x=10,y=5)
        Label(tab, text="Motori & Retroazione: ").place(x=10, y=35)
        Label(tab, text="Pressione: ").place(x=10, y=65)
        Label(tab, text="Guanto: ").place(x=10, y=95)
        ttk.Separator(tab, orient='horizontal').place(x=10, y=145, relwidth=0.9)

        self.elenco=[["Seleziona porta"],["Seleziona porta"],["Seleziona porta"]]
        self.combo_valore=[tk.StringVar(value="Seleziona porta"),tk.StringVar(value="Seleziona porta"),tk.StringVar(value="Seleziona porta")]
        #IMPORTANTE: è necessario avere
        #COMBO1
        self.combo.append(ttk.Combobox(tab, textvariable=self.combo_valore[0]))
        self.combo[0].place(x=140, y=35)
        self.combo[0]["state"]=DISABLED

        #COMBO2
        self.combo.append(ttk.Combobox(tab, textvariable=self.combo_valore[1]))
        self.combo[1].place(x=140, y=65)
        self.combo[1]["state"] = DISABLED
        # COMBO3
        self.combo.append(ttk.Combobox(tab, textvariable=self.combo_valore[2]))
        self.combo[2].place(x=140, y=95)
        self.combo[2]["state"] = DISABLED

        print(self.combo[0])
        print(self.combo[1])

        Label(tab, text="Elenco porte COM").place(x=10, y=150)

        self.label_porte = Label(tab, text="--------------\n--------------")
        self.label_porte.place(x=10, y=170)

        Button(tab, text="Connetti",command=lambda: self.connetti(0)).place(x=350, y=32)
        Button(tab, text="Connetti", command=lambda: self.connetti(1)).place(x=350,y=62)
        Button(tab, text="Connetti", command=lambda: self.connetti(2)).place(x=350, y=92)

        # ***************** INFO ************************
        Label(tab, text="INFO: ").place(x=10, y=780)
        self.label_info = ttk.Label(tab, text="-----")
        self.label_info.place(x=10, y=800)


    def connetti(self,i):
        print("Mi collego a arduino "+str(i))
        #TODO: funzione connetti(i) da implemetare


    def scansionePorte(self):
        self.port_list=serial.tools.list_ports.comports(include_links=False)
        self.porte=""
        self.elenco[0].clear()
        self.elenco[1].clear()
        self.elenco[2].clear()

        for x in self.port_list:
            self.porte=x.device+" ---> "+x.description+"\n" #COM4 --> Arduino Uno
            self.elenco[0].append(x.device)
            self.elenco[1].append(x.device)
            self.elenco[2].append(x.device)
        print(self.elenco[0])
        print(self.elenco[1] )
        print(self.elenco[2] )

        self.combo[0]["values"] = self.elenco[0]
        self.combo[1]["values"] = self.elenco[1]
        self.combo[2]["values"] = self.elenco[2]

        if(self.porte==""):
            print("Non ho trovato nulla")
            self.label_porte["text"]="Non ho trovato nulla"
        else:
            self.label_porte["text"] = self.porte
            if(self.arduino_connesso[0]==False):
                self.combo[0]["state"] = "readonly" #attiva la selezione, opposto di disabled
            if (self.arduino_connesso[1] == False):
                self.combo[1]["state"] = "readonly"
            if (self.arduino_connesso[2] == False):
                self.combo[2]["state"] = "readonly"


    def initTabSeriale(self,tab):
        #LABEL FRAME X3
        self.scheda_seriale=[]
        self.scheda_seriale.insert(0,ttk.LabelFrame(tab,text="Scheda motori & Retroazione", width=450, height=250))
        self.scheda_seriale.insert(0,ttk.LabelFrame(tab, text="Scheda pressione", width=450, height=250))
        self.scheda_seriale.insert(0,ttk.LabelFrame(tab, text="Scheda guanto", width=450, height=250))
        self.scheda_seriale[0].place(x=10, y=10)
        self.scheda_seriale[1].place(x=10, y=270)
        self.scheda_seriale[2].place(x=10, y=530)
        #ENTRY TEXT X3
        #self.comando=[]
        self.entry_comando=[]
        self.entry_comando.insert(0,Entry(self.scheda_seriale[0], width=20))
        self.entry_comando[0].place(x=10,y=10)
        self.entry_comando.insert(1, Entry(self.scheda_seriale[1], width=20))
        self.entry_comando[1].place(x=10, y=10)
        self.entry_comando.insert(2, Entry(self.scheda_seriale[2], width=20))
        self.entry_comando[2].place(x=10, y=10)
        #BUTTON
        #TODO: impletare invia() per le schede seriali
        Button(self.scheda_seriale[0], text="Invia", command=lambda: {}).place(x=160, y=5)
        Button(self.scheda_seriale[1], text="Invia", command=lambda:{}).place(x=160, y=5)
        Button(self.scheda_seriale[2], text="Invia", command=lambda: {}).place(x=160, y=5)
        #TEXT
        self.testo_seriale=[]
        self.testo_seriale.insert(0,Text(self.scheda_seriale[0],width=50, height=11, state='normal'))
        self.testo_seriale[0].place(x=10,y=40)
        self.testo_seriale.insert(1, Text(self.scheda_seriale[1], width=50, height=11, state='normal'))
        self.testo_seriale[1].place(x=10, y=40)
        self.testo_seriale.insert(2, Text(self.scheda_seriale[2], width=50, height=11, state='normal'))
        self.testo_seriale[2].place(x=10, y=40)
        #SCROLL
        self.scroll_seriale=[]
        self.scroll_seriale.insert(0,ttk.Scrollbar(self.scheda_seriale[0], orient="vertical", command=self.testo_seriale[0].yview))
        self.scroll_seriale.insert(1, ttk.Scrollbar(self.scheda_seriale[1], orient="vertical",command=self.testo_seriale[1].yview))
        self.scroll_seriale.insert(2, ttk.Scrollbar(self.scheda_seriale[2], orient="vertical",command=self.testo_seriale[2].yview))
        self.scroll_seriale[0].place(x=400, y=40, relheight=0.8)
        self.scroll_seriale[1].place(x=400, y=40, relheight=0.8)
        self.scroll_seriale[2].place(x=400, y=40, relheight=0.8)
        self.testo_seriale[0]["yscrollcommand"] = self.scroll_seriale[0].set
        self.testo_seriale[1]["yscrollcommand"] = self.scroll_seriale[1].set
        self.testo_seriale[2]["yscrollcommand"] = self.scroll_seriale[2].set





mano_dx=finestraMano()
mainloop()
