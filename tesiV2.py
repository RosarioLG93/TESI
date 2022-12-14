import json
import os
import tkinter.filedialog
from tkinter import ttk
from tkinter import *
import tkinter as tk
import time
import math
import threading

import numpy as np
import serial.tools.list_ports
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from ManoV3 import Mano
from ManoPressione import ManoPressione

from PIL import ImageTk, Image

from datetime import datetime
import datetime

# from pressione import Pressione


class finestraMano():

    def __init__(self, titolo="TESI"):
        # ----- ARDUINO --------
        self.arduino_motori = None
        self.arduino_pressione = None
        self.arduino_guanto = None
        self.arduino = [self.arduino_motori, self.arduino_pressione, self.arduino_guanto]
        self.arduino_connesso = [False, False, False]  # flag per capire se connesso
        # ------ THREAD ---------
        self.flag_thread = [False, False, False]
        self.thread_lettura = [None, None, None]
        self.thred_rec_flag=False #per registrare i movimenti

        # ------ TKINTER ------
        self.dim_x = 1650
        self.dim_y = 900
        self.x0 = 20
        self.y0 = 20
        self.root = Tk()
        self.root.title(titolo)
        self.root.geometry("{}x{}+{}+{}".format(self.dim_x, self.dim_y, self.x0, self.y0))

        # ------- INIT ----------
        self.initMutex()
        self.initNotebook()
        self.initTab()
        self.initTabMappe()
        self.initTabConnessioni(self.tab_connessioni)
        self.initTabSeriale(self.tab_seriale)
        self.initTabMovimenti(self.tab_creatore_1)
        self.initTabControllo(self.tab_controllo)
        self.initPusantiGestioneMovimento(self.tab_creatore_1)
        self.initPulsantiAcquisizioneMovimento(self.tab_creatore_1)
        self.initMenu()



        self.root.protocol("WM_DELETE_WINDOW", self.chiudiTutto)  # chiudiTutto viene eseguito quando clicco su x rossa
        self.initCartellaLavoro()
        self.disabilitaPulsanti()  # in questo modo devo necessariamente aprire un file per abiltiare i comandi

    #-------------------------- INIT MUTEX --------------------
    def initMutex(self):
        self.mutexSerialeControllo=threading.Lock()
        self.mutexSerialeGuanto=threading.Lock()


        #2 mutex per chiedere un comando alla volta
        self.mutexControlloLuttura=threading.Lock()
        self.mutexControlloScrittura=threading.Lock()
        """
        Ripasso:
        
        """



    # ------------------------- INIT MENU -----------------------

    def initMenu(self):
        self.menu_bar = Menu(self.root)
        self.menu_info = Menu(self.menu_bar, tearoff=0)
        self.menu_strumenti = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(menu=self.menu_strumenti, label="Opzioni")
        self.menu_bar.add_cascade(menu=self.menu_info, label="Info")

        #self.menu_strumenti.add_command(label="Registrazione", command=self.apriRegistratore)
        self.menu_strumenti.add_command(label="Impostazioni", command=self.apriImpostazioni)
        #self.menu_strumenti.add_command(label="Configura mappa", command=lambda: ())
        #self.menu_strumenti.add_command(label="Impostazioni Arduino", command=lambda: ())

        #TODO: manuale da completare
        self.menu_info.add_command(label="Manuale", command=lambda: ())
        #self.menu_info.add_command(label="Protocollo arduino", command=lambda: ())

        self.root["menu"] = self.menu_bar

    # ------------------------ IMPOSTAZIONI-----------------------------
    def apriImpostazioni(self):
        self.root_impostazioni = Toplevel(self.root)
        self.root_impostazioni.geometry("1200x600+400+200")
        self.root_impostazioni.title("Impostazioni")
        self.root_impostazioni.resizable(False, False)
        #self.root_impostazioni.attributes("-topmost", False)
        #self.frame_impostazioni = LabelFrame(self.root_impostazioni, text="Impostazioni", width=1100, height=500)
        #self.frame_impostazioni.place(x=20, y=20)
        self.root_impostazioni.protocol("WM_DELETE_WINDOW", self.chiudiImpostazioni)  # per sicurezza
        self.menu_strumenti.entryconfigure(1, state=DISABLED)
        # ------------- notebook / tab ----------
        self.notebook_impostazioni = ttk.Notebook(self.root_impostazioni, width=1180, height=560)
        self.notebook_impostazioni.place(x=10, y=10)
        self.tab_impostazioni_controllo = Frame(self.notebook_impostazioni)
        self.tab_impostazioni_pressione = Frame(self.notebook_impostazioni)
        self.tab_impostazioni_guanto = Frame(self.notebook_impostazioni)
        self.tab_impostazioni_home = Frame(self.notebook_impostazioni)
        self.notebook_impostazioni.add(self.tab_impostazioni_controllo, text="Angoli Min/Max EEPROM")
        self.notebook_impostazioni.add(self.tab_impostazioni_home, text="Posizione iniziale")
        #self.notebook_impostazioni.add(self.tab_impostazioni_pressione, text="Pressione")
        #self.notebook_impostazioni.add(self.tab_impostazioni_guanto, text="Guanto controllo remoto")
        self.initTabImpostazioniControllo(self.tab_impostazioni_controllo)
        self.initTabImpostazioniPosizioneIniziale(self.tab_impostazioni_home)
        # ---label info impostazioni (comune per tutti)
        Label(self.root_impostazioni, text="INFO:").place(x=30, y=540)
        self.label_info_impostazioni = Label(self.root_impostazioni, text="---")
        self.label_info_impostazioni.place(x=30, y=560)
        self.caricaHomeJson()
        self.caricaLimitJson()

    def initTabImpostazioniPosizioneIniziale(self,tab):
        #TODO:Inserire spinbox valori iniziali, salvati in un json, le mappe inizializzate usano il file json
        self.tetaHome=[[],[],[],[],[]]
        self.fiHome=[]
        self.spinTetaHome = [[], [], [], [], []]
        self.spinFiHome = []
        nome = {0: "Pollice [0]", 1: "Indice[1]", 2: "Medio[2]", 3: "Anulare[3]", 4: "Mignolo[4]"}

        self.label_frame_spin_home = []
        nome = {0: "Pollice [0]", 1: "Indice[1]", 2: "Medio[2]", 3: "Anulare[3]", 4: "Mignolo[4]"}
        for i in range(0, 5):
            self.label_frame_spin_home.append(LabelFrame(tab, text=nome[i], width=100, height=400))
            self.label_frame_spin_home[i].place(x=130 + (130 * i), y=80)

        Button(tab, text="Carica ", command=self.caricaValoriEepromHome).place(x=10, y=10)
        Button(tab, text="Salva su EEPROM", command=self.salvaValoriEepromHome).place(x=10, y=40)

        #JSON
        Button(tab, text="Carica home.json", command=self.caricaHomeJson).place(x=150, y=10)
        Button(tab, text="Salva home.json", command=self.salvaHomeJson).place(x=150, y=40)

        Label(tab, image=self.imgr).place(x=770, y=85)

        for i in range(0,5):
            for j in range(0,3):
                self.spinTetaHome[i].append(ttk.Spinbox(self.label_frame_spin_home[i],from_=-30,to=200,width=10))
                self.spinTetaHome[i][j].place(x=10, y=(j * 90) + 40)

        # LABEL TETA
        for j in range(0, 3):
            #Label(tab, text="teta max[" + str(j) + "]").place(x=30, y=105 + (j * 90))
            Label(tab, text="teta home[" + str(j) + "]").place(x=30, y=135 + (j * 90))

        for i in range(0, 5):
            self.spinFiHome.append(ttk.Spinbox(self.label_frame_spin_home[i],width=10))
            self.spinFiHome[i].place(x=10, y=310)

        Label(tab, text="fi home").place(x=50, y=405)

    def caricaHomeJson(self):
        try:
            file=open(os.path.join("impostazioni","json","home.json"),"r")
            obj_json=json.load(file)
            #TETA
            for i in range(0,5):
                self.spinFiHome[i].set(obj_json["fi"][i])
                for j in range(0,3):
                    self.spinTetaHome[i][j].set(obj_json["d"+str(i)][j])
            file.close()
            self.label_info_impostazioni["text"]="home.json caricato correttamente"
        except Exception as e:
            self.label_info_impostazioni["text"]=e.__str__()

    def salvaHomeJson(self):
        self.homeJsonDict = {}
        temp = [[],[],[],[],[],[]]
        for i in range(0,5):
            for j in range(0,3):
                temp[i].insert(j,self.spinTetaHome[i][j].get())
            self.homeJsonDict["d" + str(i)] =temp[i]
        #FI
        for i in range(0,5):
            temp[5].insert(i,self.spinFiHome[i].get())
        self.homeJsonDict["fi"]=temp[5]
        scelta = messagebox.askyesno("Salvataggio","Sei sicuro di salvare?")

        if scelta == False:
            return
        try:
            file=open(os.path.join("impostazioni","json","home.json"),"w")
            json.dump(self.homeJsonDict,file)
            file.close()
            self.label_info_impostazioni["text"] = "SALVATO"
        except Exception as e:
            self.label_info_impostazioni["text"]=e.__str__()



    def caricaLimitJson(self):
        try:
            """
            self.tetaMin = [[] ,[],[],[],[]] # ATTENZIONE: [[]*3] COPIA GLI INDIRIZZI!!!!!!!! (grosso problema)
            self.tetaMax = [[] ,[],[],[],[]]
            self.fiMin = [[] ,[],[],[],[]]
            self.fiMax = [[] ,[],[],[],[]]
            """
            file = open(os.path.join("impostazioni", "json", "limit.json"), "r")
            obj_json = json.load(file)
            print(obj_json)
            for i in range(0, 5):
                for j in range(0, 3):
                    self.spinTetaMax[i][j].set(obj_json["tetaMax"]["d"+str(i)][j])

            for i in range(0, 5):
                for j in range(0, 3):
                    self.spinTetaMin[i][j].set(obj_json["tetaMin"]["d"+str(i)][j])

            for i in range(0, 5):
                self.spinFiMin[i].set(obj_json["fiMin"][i])

            for i in range(0, 5):
                self.spinFiMax[i].set(obj_json["fiMax"][i])

            file.close()
            self.label_info_impostazioni["text"]="limit.json caricato correttamente"
        except Exception as e:
            self.label_info_impostazioni["text"]=e.__str__()

    def salvaLimitJson(self):
        try:
            tetaMax={}
            tetaMin={}
            fiMin=[]
            fiMax=[]
            self.limitJsonDict={}
            for i in range(0, 5):
                temp=[]
                for j in range(0, 3):
                    temp.insert(j,self.spinTetaMax[i][j].get())
                tetaMax["d"+str(i)]=temp


            for i in range(0, 5):
                temp = []
                for j in range(0, 3):
                    temp.insert(j, self.spinTetaMin[i][j].get())
                tetaMin["d" + str(i)] = temp


            for i in range(0, 5):
                fiMax.append(self.spinFiMax[i].get())

            for i in range(0, 5):
                fiMin.append(self.spinFiMin[i].get())

            self.limitJsonDict["tetaMax"]=tetaMax
            self.limitJsonDict["tetaMin"] = tetaMin
            self.limitJsonDict["fiMin"] = fiMin
            self.limitJsonDict["fiMax"] = fiMax
            print(self.limitJsonDict)


            scelta = messagebox.askyesno("Salvataggio", "Sei sicuro di salvare?")
            if scelta == False:
                return

            #salvataggio file
            file=open(os.path.join("impostazioni","json","limit.json"),"w")
            json.dump(self.limitJsonDict,file)
            file.close()
            self.label_info_impostazioni["text"]="limit.json salvato"
        except Exception as e:
            self.label_info_impostazioni["text"]=e.__str__()




    def initTabImpostazioniControllo(self, tab):
        # ------------- button ---------
        Button(tab, text="Carica ", command=self.caricaValoriEeprom).place(x=10, y=10)
        Button(tab, text="Salva su EEPROM", command=self.salvaValoriEeprom).place(x=10, y=40)

        #--------- json -----------
        # JSON
        Button(tab, text="Carica limit.json", command=self.caricaLimitJson).place(x=150, y=10)
        Button(tab, text="Salva limit.json", command=self.salvaLimitJson).place(x=150, y=40)

        # utile per poter chiamare .set() sulla variabile di tipo IntVar()
        self.tetaMin = [[] ,[],[],[],[]] # ATTENZIONE: [[]*3] COPIA GLI INDIRIZZI!!!!!!!! (grosso problema)
        self.tetaMax = [[] ,[],[],[],[]]
        self.fiMin = [[] ,[],[],[],[]]
        self.fiMax = [[] ,[],[],[],[]]

        self.spinTetaMin = [[],[],[],[],[]]
        self.spinTetaMax = [[],[],[],[],[]]
        self.spinFiMin = [ ]
        self.spinFiMax = [ ]



        self.label_frame_spin = []
        nome = {0: "Pollice [0]", 1: "Indice[1]", 2: "Medio[2]", 3: "Anulare[3]", 4: "Mignolo[4]"}
        for i in range(0, 5):
            self.label_frame_spin.append(LabelFrame(tab,text=nome[i], width=100, height=400))
            self.label_frame_spin[i].place(x=130 + (130 * i), y=80)

        for i in range(0,5):
            for j in range(0,3):
                self.spinTetaMin[i].append(ttk.Spinbox(self.label_frame_spin[i], from_=-30, to=200, width=10 ))#state=DISABLED)
                self.spinTetaMin[i][j].place(x=10, y=(j * 90) + 40)
                #self.spinTetaMin[i][j].set((3*i)+j)
                #self.spinTetaMin[j][i].place(x=10 +(j*2), y=(i * 30) + 10)

        for i in range(0, 5):
            for j in range(0, 3):
                self.spinTetaMax[i].append( ttk.Spinbox(self.label_frame_spin[i], from_=-30, to=200, width=10))  # state=DISABLED)
                self.spinTetaMax[i][j].place(x=10, y=(j * 90) + 10)
                #self.spinTetaMax[i][j].set(15+(3*i)+j)
                # self.spinTetaMin[j][i].place(x=10 +(j*2), y=(i * 30) + 10)

        for i in range(0, 5):
                self.spinFiMin.append(ttk.Spinbox(self.label_frame_spin[i], from_=-30, to=200, width=10))  # state=DISABLED)
                self.spinFiMin[i].place(x=10, y= 340)
                #self.spinFiMin[i].set(30+i)
                # self.spinTetaMin[j][i].place(x=10 +(j*2), y=(i * 30) + 10)

        for i in range(0, 5):
            self.spinFiMax.append(ttk.Spinbox(self.label_frame_spin[i], from_=-30, to=200, width=10))  # state=DISABLED)
            self.spinFiMax[i].place(x=10, y=310)
            #self.spinFiMax[i].set(35+i)
            # self.spinTetaMin[j][i].place(x=10 +(j*2), y=(i * 30) + 10)


        #LABEL TETA
        for j in range(0,3):
            Label(tab,text="teta max["+str(j)+"]").place(x=30,y=105+(j*90))
            Label(tab, text="teta min[" + str(j) + "]").place(x=30, y=135 + (j * 90))

        #LABEL FI
        Label(tab, text="fi max").place(x=50,y=405)
        Label(tab, text="fi min").place(x=50, y=435)
        #immagine
        self.im = Image.open(os.path.join("impostazioni","angoli.png")) # os.path.join() per avare compatibilit?? sistemi window e linux
        self.img = self.im.resize((400, 400))
        self.imgr = ImageTk.PhotoImage(self.img)
        Label(tab, image=self.imgr).place(x=770,y=85)



    def caricaValoriEeprom(self):
        #---------- LETTURA VALORI MIN/MAX ------------------------------------
        if self.arduino_connesso[0]==True:
            self.label_info_impostazioni["text"]="Avvio processo, lock seriale"
            for i in range(0, 5):
                for j in range(0, 3):
                    self.inviaComando(0,"read:"+str((3*i)+j))
                    #sar?? compito di analisiComando() a impostare gli spinbox

                    #self.spinTetaMin[i][j].set((3*i)+j)

            for i in range(0, 5):
                for j in range(0, 3):
                    self.inviaComando(0,"read:"+str(15+(3*i)+j))
                    #self.spinTetaMax[i][j].set(15+(3*i)+j)

            for i in range(0, 5):
                self.inviaComando(0, "read:" + str(30+i))
                #self.spinFiMin[i].set(30+i)

            for i in range(0, 5):
                self.inviaComando(0, "read:" + str(35 + i))
                #self.spinFiMax[i].set(35+i)
            #--------------------------------- LETTURA VALORI HOME -------------------

            for i in range(0,5):
                for j in range(0,3):
                    self.inviaComando(0,"read:"+str(40+(i*3)+j))
                    #self.spinTetaHome.set(....)
            for i in range(0, 5):
                self.inviaComando(0, "read:" + str(52 + i))
            self.label_info_impostazioni["text"] = "Processo terminato, unlock seriale"
        else:
            self.label_info_impostazioni["text"]="Arduino[0] Controllo & Retroazione disconnesso"





    def salvaValoriEeprom(self):
        if self.arduino_connesso[0]==True:
            self.label_info_impostazioni["text"]="---"
            #------------------------ SCRITTURA VALORI MIN/MAX --------------------------------
            #tetaMin
            for i in range(0, 5):
                for j in range(0, 3):
                    #tetaMin[5][3]
                    #self.inviaComando(0,"write:"+str((3*i)+j)+":"+str(self.spinTetaMin[i][j].get()))
                    pass
            #tetaMax
            for i in range(0, 5):
                for j in range(0, 3):
                    #self.inviaComando(0,"write:"+str((3*i)+j)+":"+str(self.spinTetaMin[i][j].get()))
                    pass
            #FiMin
            for i in range(0, 5):
                #self.inviaComando(0,"write:"+str((3*i)+j)+":"+str(self.spinTetaMin[i][j].get()))
                pass
            #FiMax
            for i in range(0, 5):
                #self.inviaComando(0,"write:"+str((3*i)+j)+":"+str(self.spinTetaMin[i][j].get()))
                pass


        else:
            self.label_info_impostazioni["text"]="Arduino[0] Controllo & Retroazione disconnesso"


    def caricaValoriEepromHome(self):
        # --------------------------------- LETTURA VALORI HOME -------------------
        if (self.arduino_connesso[0] == True):
            for i in range(0, 5):
                for j in range(0, 3):
                    #usare mutex per evitare valanga di messaggi in seriale
                    #self.inviaComando(0, "read:" + str(40 + (i * 3) + j))
                    # self.spinTetaHome.set(....)
                    pass
            for i in range(0, 5):
                #self.inviaComando(0, "read:" + str(52 + i))
                pass
        else:
            self.label_info_impostazioni["text"] = "Arduino[0] Controllo & Retroazione disconnesso"



    def salvaValoriEepromHome(self):
        if(self.arduino_connesso[0]==True):
            # ----------------------------- SCRITTURA VALORI HOME --------------------
            for i in range(0, 5):
                for j in range(0, 3):
                    # self.inviaComando(0,"write:"+str(40+(i*3)+j)+":"+str(self.spinTetaHome[i][j].get()))
                    pass

            for i in range(0, 5):
                # self.inviaComando(0,"write:"+str(55+i)+":"+str(self.spinFiHome[i]))
                pass
        else:
            self.label_info_impostazioni["text"] = "Arduino[0] Controllo & Retroazione disconnesso"



    def chiudiImpostazioni(self):
        self.menu_strumenti.entryconfigure(1, state=ACTIVE) #riattivo il menu
        self.root_impostazioni.destroy()

    # -----------------REGISTRA MOVIMENTO ----------------------
    """
    def apriRegistratore(self):
        print("Avvio registratore")
        self.win = Toplevel(self.root)
        self.win.title("Registratore")
        self.win.geometry("800x600+200+200")
        self.win.resizable(False, False)
        self.win.attributes("-topmost", True)  # sempre in primo piano
        self.win.protocol("WM_DELETE_WINDOW", self.chiudiRegistratore)  # per sicurezza
        self.menu_strumenti.entryconfigure(0, state=DISABLED)
        self.scheda_mappa_guanto = LabelFrame(self.win, text="Controllo", width=350, height=390)
        self.scheda_mappa_guanto.place(x=10, y=10)
        # MAPPA CONTROLLO
        self.mano_guanto = Mano('g')
        # ----- canvas mano --------
        canvas_mano_guanto = FigureCanvasTkAgg(self.mano_guanto.getFig(), master=self.scheda_mappa_guanto)
        canvas_mano_guanto.get_tk_widget().place(x=20, y=10)

        toolbar_mano_guanto = NavigationToolbar2Tk(canvas_mano_guanto, self.scheda_mappa_guanto)
        toolbar_mano_guanto.update()
        toolbar_mano_guanto.place(x=10, y=320)

        self.mano_guanto.visualizzaPosizioneDesiderata()
        canvas_mano_guanto.draw()

        # TAB
        self.notebook_test = ttk.Notebook(self.win, width=400, height=550)
        self.tab_test = Frame(self.notebook_test)
        self.notebook_test.add(self.tab_test, text="Mov")
        self.notebook_test.place(x=380, y=10)

    def chiudiRegistratore(self):
        self.menu_strumenti.entryconfigure(0, state=ACTIVE)
        del self.mano_guanto  # distruttore
        self.win.destroy()
    """

    # ------------------ TAB CONTROLLO (SLIDER) --------------------------

    def resetHomeControllo(self):
        self.slider[1][0].set(self.home[1][0])
        self.slider[1][1].set(self.home[1][1])
        self.slider[1][2].set(self.home[1][2])



    def initTabControllo(self,tab):
        #TODO: CONTROLLO DA COMPLETARE (HOME E CONTROLLO REMOTO GUANTO)
        Button(tab,text="Home",command=self.resetHomeControllo).place(x=5,y=10)
        Button(tab, text="ACQUISISCI GUANTO", command=lambda: ()).place(x=200, y=10)
        Label(tab,text="Intervallo").place(x=70, y=15)
        self.delay_guanto_acquisizione = tk.Entry(tab, width=8)
        self.delay_guanto_acquisizione.place(x=130, y=15)
        self.delay_guanto_acquisizione.insert(0, "0")
        Label(tab,text="Pollice[0]   Indice[1]   Medio[2]   Anulare[3]   Mignolo[4]").place(x=30,y=52)

        #TODO: file json locale da caricare per impostare home e min/max
        scheda_movimento_s3 = LabelFrame(tab, text="teta[2]", width=290, height=180)
        scheda_movimento_s3.place(x=20, y=74)

        scheda_movimento_s2 = LabelFrame(tab, text="teta[1]", width=290, height=180)
        scheda_movimento_s2.place(x=20, y=258)


        scheda_movimento_s1 = LabelFrame(tab, text="teta[0]", width=290, height=180)
        scheda_movimento_s1.place(x=20, y=442)

        scheda_movimento_fi = LabelFrame(tab, text="fi", width=290, height=220)
        scheda_movimento_fi.place(x=20, y=625)

        #scheda_movimento_pollice = LabelFrame(tab, text="Pollice", width=90, height=740)
        #scheda_movimento_pollice.place(x=10, y=60)


        #----------
        try:
            file = open(os.path.join("impostazioni", "json", "home.json"), "r")
            obj_json = json.load(file)
            file.close()
            #home=np.array(type=int)
            self.home=[[0] * 3] * 5
            self.home[1][0]=obj_json["d1"][0]
            self.home[1][1] = obj_json["d1"][1]
            self.home[1][2] = obj_json["d1"][2]
        except Exception as e:
            print(e.__str__())
            self.home = 0
            self.home[1][0] = 0
            self.home[1][1] = 0
            self.home[1][2] = 0
            self.label_info_creatore["text"]="file home.json non presente"



        # ------------------------ S2 (angolo[1]) ----------------------------------

        self.slider = [[tk.Scale,tk.Scale,tk.Scale],[tk.Scale,tk.Scale,tk.Scale,],[tk.Scale,tk.Scale,tk.Scale,],[tk.Scale,tk.Scale,tk.Scale],[tk.Scale,tk.Scale,tk.Scale]]

        #----------------- teta[2] angolo[2] ---------------------------------
        # ricorda che S3 si muove perch?? ?? vincolato a S2 (in questa versione)
        # TODO: aggiungere impostazioni slider nella sezione impostazioni per valori MIN & MAX
        # ttk.Scale(scheda_movimento,orient='vertical',length=160,from_=-0, to=130,command=lambda val: aggiorna(val,0)).place(x=10,y=10)
        self.slider[0][2] = tk.Scale(scheda_movimento_s3, orient='vertical', resolution=1, tickinterval=0, length=140,from_=-0, to=110)
        self.slider[0][2].place(x=20, y=10)

        self.slider[1][2]=tk.Scale(scheda_movimento_s3, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-0, to=90, command=lambda val:self.aggiornaAngoloTeta(1,2,val))
        self.slider[1][2].place(x=70, y=10)
        self.slider[1][2].set(self.home[1][2])


        tk.Scale(scheda_movimento_s3, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=90).place(x=120, y=10)
        tk.Scale(scheda_movimento_s3, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=90).place(x=170, y=10)
        tk.Scale(scheda_movimento_s3, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0,to=90).place(x=220, y=10)


        # ---------------- teta[1] (angolo[1]) ----------------------------
        self.slider[0][1]=tk.Scale(scheda_movimento_s2, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=110).place(x=20, y=10)

        self.slider[1][1]=tk.Scale(scheda_movimento_s2, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=110, command=lambda val:self.aggiornaAngoloTeta(1,1,val) )
        self.slider[1][1].place(x=70, y=10)
        self.slider[1][1].set(self.home[1][1])

        self.slider[2][1]=tk.Scale(scheda_movimento_s2, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=110 ).place(x=120, y=10)
        self.slider[3][1]=tk.Scale(scheda_movimento_s2, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=110).place(x=170, y=10)
        self.slider[4][1]=tk.Scale(scheda_movimento_s2, orient='vertical', resolution=1, tickinterval=0, length=140, from_=0, to=110).place(x=220, y=10)

        # ---------------- teta[0] (angolo[0]) ----------------------------
        self.slider[0][0]=tk.Scale(scheda_movimento_s1, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20, to=90)
        self.slider[0][0].place(x=20, y=10)


        self.slider[1][0]=tk.Scale(scheda_movimento_s1, orient='vertical', resolution=1, tickinterval=0, length=140 ,from_=0, to=90 , command=lambda val:self.aggiornaAngoloTeta(1,0,val))
        self.slider[1][0].place(x=70, y=10)
        self.slider[1][0].set(self.home[1][0])


        self.slider[2][0]=tk.Scale(scheda_movimento_s1, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20, to=90 )
        self.slider[2][0].place(x=120, y=10)
        self.slider[3][0]=tk.Scale(scheda_movimento_s1, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20, to=90)
        self.slider[3][0].place(x=170, y=10)
        self.slider[4][0]=tk.Scale(scheda_movimento_s1, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20, to=90)
        self.slider[4][0].place(x=220, y=10)

        #----------- fi -----------------
        tk.Scale(scheda_movimento_fi, orient='horizontal', resolution=1, tickinterval=0, length=140, from_=-15, to=15).place(x=90, y=0)
        tk.Scale(scheda_movimento_fi, orient='horizontal', resolution=1, tickinterval=0, length=140, from_=-15, to=15 ).place(x=90, y=35)
        tk.Scale(scheda_movimento_fi, orient='horizontal', resolution=1, tickinterval=0, length=140, from_=-15, to=15 ).place(x=90, y=70)
        tk.Scale(scheda_movimento_fi, orient='horizontal', resolution=1, tickinterval=0, length=140, from_=-15, to=15).place(x=90, y=105)
        tk.Scale(scheda_movimento_fi, orient='horizontal', resolution=1, tickinterval=0, length=140, from_=-15, to=15).place(x=90, y=140)

        Label(scheda_movimento_fi, text="Pollice[0]").place(x=5, y=15)
        Label(scheda_movimento_fi, text="Indice[1]").place(x=5,y=50)
        Label(scheda_movimento_fi, text="Medio[2]").place(x=5,y=85)
        Label(scheda_movimento_fi, text="Anulare[3]").place(x=5,y=120)
        Label(scheda_movimento_fi, text="Mignolo[4]").place(x=5,y=155)


        """
        #pollice
        tk.Scale(scheda_movimento_pollice, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20,to=90).place(x=10, y=10)
        tk.Scale(scheda_movimento_pollice, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20,
                 to=90).place(x=10, y=160)
        tk.Scale(scheda_movimento_pollice, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20,
                 to=90).place(x=10, y=320)
        tk.Scale(scheda_movimento_pollice, orient='vertical', resolution=1, tickinterval=0, length=140, from_=-20,
                 to=90).place(x=10, y=480)
        """


    # ---------------------------------------------------------------------


    def aggiornaAngoloTeta(self,dito,teta,valore):
        """
        0->pollice
        1->indice
        2->medio
        3->anulare
        4->mignolo
        Aggiorno la mappa e successivamente provo ad inviare
        l'invio ?? annullato se c'?? uno stream attivo!!! (che sia controllo remoto o aggionamento eeprom e posizione iniziale)

        In questo caso utilizziamo "Dij:valore", inutile json perch?? cambio uno slider alla volta


        """

        print("D"+str(dito)+str(teta)+":"+str(valore))
        self.inviaComando(0,"D"+str(dito)+str(teta)+":"+str(valore))
        self.mano_controllo.setAngolo(dito,teta,valore)
        self.canvas_mano_controllo.draw() #per aggiornare la mappa


    def initCartellaLavoro(self):
        # al primoa avvio cerca la cartealla /movimenti
        # IMPSOTO LA CARTELLA DI DEFAULT
        try:
            self.cartella = os.path.join(os.getcwd(), "movimenti")  # per compatibilit?? linux e windows
            self.aggiornaListaFile()
            self.label_cartella["text"] = self.cartella.__str__()
        except:
            self.label_info_creatore["text"] = "Cartella di defautl movimenti non trovata "

    def initNotebook(self):
        self.notebook_0 = ttk.Notebook(self.root, width=470, height=self.dim_y - 50)
        self.notebook_1 = ttk.Notebook(self.root, width=340, height=self.dim_y - 50)
        self.notebook_2 = ttk.Notebook(self.root, width=450, height=self.dim_y - 50)
        self.notebook_3 = ttk.Notebook(self.root, width=450, height=self.dim_y - 50)

    def initTab(self):
        # 0 Mappe
        self.tab_mappa_controllo = Frame(self.notebook_0)
        self.tab_mappa_pressione = Frame(self.notebook_0)
        #self.tab_mappa_guanto = Frame(self.notebook_0)
        self.notebook_0.add(self.tab_mappa_controllo, text="Controllo & Retroazione")
        self.notebook_0.add(self.tab_mappa_pressione, text="Pressione & Guanto")
        #self.notebook_0.add(self.tab_mappa_guanto,text="Controllo remoto")
        self.notebook_0.place(x=5, y=10)
        # 1
        self.tab_controllo = Frame(self.notebook_1)
        self.notebook_1.add(self.tab_controllo, text="Controllo")
        self.notebook_1.place(x=390, y=10)
        # 2
        self.tab_creatore_1 = Frame(self.notebook_2)
        self.notebook_2.add(self.tab_creatore_1, text="Movimenti")
        self.notebook_2.place(x=730, y=10)
        # 3
        self.tab_connessioni = Frame(self.notebook_3)
        self.tab_seriale = Frame(self.notebook_3)
        self.notebook_3.add(self.tab_connessioni, text="Connessioni")
        self.notebook_3.add(self.tab_seriale, text="Monitor Seriale")
        self.notebook_3.place(x=1180, y=10)

    def initTabConnessioni(self, tab):
        self.combo = []
        self.combo_baudrate=[]
        self.baudrate=[4800,9600,19200,38400]
        self.bt_scansiona = Button(tab, text="Scansiona", command=self.scansionePorte)
        self.bt_scansiona.place(x=10, y=5)
        Label(tab, text="Motori & Retroazione: ").place(x=10, y=35)
        Label(tab, text="Pressione: ").place(x=10, y=65)
        Label(tab, text="Guanto: ").place(x=10, y=95)
        ttk.Separator(tab, orient='horizontal').place(x=10, y=145, relwidth=0.9)

        self.elenco = [["Seleziona porta"], ["Seleziona porta"], ["Seleziona porta"]]
        self.combo_valore = [tk.StringVar(value="Seleziona porta"), tk.StringVar(value="Seleziona porta"),
                             tk.StringVar(value="Seleziona porta")]
        # IMPORTANTE: ?? necessario avere
        # COMBO1
        self.combo.append(ttk.Combobox(tab, width=15, textvariable=self.combo_valore[0],state='readonly'))
        self.combo[0].place(x=140, y=35)
        self.combo[0]["state"] = DISABLED
        self.combo_baudrate.append(ttk.Combobox(tab,width=10,values=self.baudrate,state='readonly'))
        self.combo_baudrate[0].place(x=260,y=35)
        self.combo_baudrate[0].current(1)
        self.combo_baudrate[0]["state"] = DISABLED

        # COMBO2
        self.combo.append(ttk.Combobox(tab,width=15, textvariable=self.combo_valore[1],state='readonly'))
        self.combo[1].place(x=140, y=65)
        self.combo[1]["state"] = DISABLED
        self.combo_baudrate.append(ttk.Combobox(tab, width=10, values=self.baudrate, state='readonly'))
        self.combo_baudrate[1].place(x=260, y=65)
        self.combo_baudrate[1].current(1)
        self.combo_baudrate[1]["state"] = DISABLED
        # COMBO3
        self.combo.append(ttk.Combobox(tab,width=15, textvariable=self.combo_valore[2],state='readonly'))
        self.combo[2].place(x=140, y=95)
        self.combo[2]["state"] = DISABLED
        self.combo_baudrate.append(ttk.Combobox(tab, width=10, values=self.baudrate, state='readonly'))
        self.combo_baudrate[2].place(x=260, y=95)
        self.combo_baudrate[2].current(1)
        self.combo_baudrate[2]["state"] = DISABLED

        Label(tab, text="Elenco porte COM").place(x=10, y=150)

        self.label_porte = Label(tab, text="--------------\n--------------")
        self.label_porte.place(x=10, y=170)

        self.bt_connetti = [None, None, None]
        self.bt_connetti[0] = Button(tab, text="Connetti", command=lambda: self.connetti(0))
        self.bt_connetti[0].place(x=360, y=32)
        self.bt_connetti[1] = Button(tab, text="Connetti", command=lambda: self.connetti(1))
        self.bt_connetti[1].place(x=360, y=62)
        self.bt_connetti[2] = Button(tab, text="Connetti", command=lambda: self.connetti(2))
        self.bt_connetti[2].place(x=360, y=92)
        # ***************** INFO ************************
        Label(self.notebook_3, text="INFO: ").place(x=10, y=820)
        self.label_info = ttk.Label(self.notebook_3, text="-----")
        self.label_info.place(x=10, y=840)

    def connetti(self, i):
        print("Mi collego ad arduino " + str(i))
        if (self.arduino_connesso[i] == False):
            # connetti
            try:
                print("Baudrate:"+str(self.combo_baudrate[i].get()))
                self.arduino[i] = serial.Serial(port=self.combo[i].get(), baudrate=self.combo_baudrate[i].get(), stopbits=1, bytesize=8)
                nomi=["motori","pressione","guanto controllo remoto"]
                self.label_info["text"] = "Scheda "+nomi[i]+ " connessa " + self.combo[i].get()
                self.combo[i]["state"] = DISABLED
                self.combo_baudrate[i]["state"]=DISABLED
                self.bt_connetti[i]["text"] = "Disconnetti"
                self.arduino_connesso[i] = True
                self.startThreadLettura(i)
            except Exception as e:
                self.label_info["text"] = "Errore connessione " + self.combo[i].get()
                print("Errore da connetti("+str(i)+"): " + e.__str__())

        else:
            # DISCONNETTO
            self.arduino_connesso[i] = False
            self.bt_connetti[i]["text"] = "Connetti"
            self.stopThreadLettura(i)
            try:
                self.arduino[i].close()
                self.combo[i]["state"] = "readonly"
                self.combo_baudrate[i]["state"] = "readonly"
                self.label_info["text"] = "Scheda disconnessa"
            except:
                self.label_info["text"] = "Errore disconnessione"

    def scansionePorte(self):
        self.port_list = serial.tools.list_ports.comports(include_links=False)
        self.porte = ""
        self.elenco[0].clear()
        self.elenco[1].clear()
        self.elenco[2].clear()

        for x in self.port_list:
            self.porte = x.device + " ---> " + x.description + "\n"  # COM4 --> Arduino Uno
            self.elenco[0].append(x.device)
            self.elenco[1].append(x.device)
            self.elenco[2].append(x.device)
        # print(self.elenco[0])
        # print(self.elenco[1] )
        # print(self.elenco[2] )

        self.combo[0]["values"] = self.elenco[0]
        self.combo[1]["values"] = self.elenco[1]
        self.combo[2]["values"] = self.elenco[2]

        if (self.porte == ""):
            print("Non ho trovato nulla")
            self.label_porte["text"] = "Non ho trovato nulla"
        else:
            self.label_porte["text"] = self.porte
            if (self.arduino_connesso[0] == False):
                self.combo[0]["state"] = "readonly"  # attiva la selezione, opposto di disabled
                self.combo_baudrate[0]["state"] = "readonly"
            if (self.arduino_connesso[1] == False):
                self.combo[1]["state"] = "readonly"
                self.combo_baudrate[1]["state"] = "readonly"
            if (self.arduino_connesso[2] == False):
                self.combo[2]["state"] = "readonly"
                self.combo_baudrate[2]["state"] = "readonly"

    def initTabSeriale(self, tab):
        # LABEL FRAME X3
        self.scheda_seriale = []
        self.scheda_seriale.insert(0, ttk.LabelFrame(tab, text="Scheda motori & Retroazione", width=430, height=250))
        self.scheda_seriale.insert(1, ttk.LabelFrame(tab, text="Scheda pressione", width=430, height=250))
        self.scheda_seriale.insert(2, ttk.LabelFrame(tab, text="Scheda guanto", width=430, height=250))
        self.scheda_seriale[0].place(x=10, y=10)
        self.scheda_seriale[1].place(x=10, y=270)
        self.scheda_seriale[2].place(x=10, y=530)
        # ENTRY TEXT X3
        # self.comando=[]
        self.entry_comando = []
        self.entry_comando.insert(0, Entry(self.scheda_seriale[0], width=20))
        self.entry_comando[0].place(x=10, y=10)
        self.entry_comando.insert(1, Entry(self.scheda_seriale[1], width=20))
        self.entry_comando[1].place(x=10, y=10)
        self.entry_comando.insert(2, Entry(self.scheda_seriale[2], width=20))
        self.entry_comando[2].place(x=10, y=10)
        # BUTTON_INVIA
        Button(self.scheda_seriale[0], text="Invia", command=lambda: self.inviaComando(0)).place(x=160, y=5)
        Button(self.scheda_seriale[1], text="Invia", command=lambda: self.inviaComando(1)).place(x=160, y=5)
        Button(self.scheda_seriale[2], text="Invia", command=lambda: self.inviaComando(2)).place(x=160, y=5)
        #BUTTON_CLEAR
        Button(self.scheda_seriale[0], text="Clear", command=lambda: self.clearSeriale(0)).place(x=300, y=5)
        Button(self.scheda_seriale[1], text="Clear", command=lambda: self.clearSeriale(1)).place(x=300, y=5)
        Button(self.scheda_seriale[2], text="Clear", command=lambda: self.clearSeriale(2)).place(x=300, y=5)
        #BUTTON_SALVA_TESTO
        Button(self.scheda_seriale[0], text="Salva", command=lambda: self.salvaTesto(0)).place(x=350, y=5)
        Button(self.scheda_seriale[1], text="Salva", command=lambda: self.salvaTesto(1)).place(x=350, y=5)
        Button(self.scheda_seriale[2], text="Salva", command=lambda: self.salvaTesto(2)).place(x=350, y=5)

        # TEXT
        self.testo_seriale = []
        self.testo_seriale.insert(0, Text(self.scheda_seriale[0], width=50, height=11, state='normal'))
        self.testo_seriale[0].place(x=10, y=40)
        self.testo_seriale.insert(1, Text(self.scheda_seriale[1], width=50, height=11, state='normal'))
        self.testo_seriale[1].place(x=10, y=40)
        self.testo_seriale.insert(2, Text(self.scheda_seriale[2], width=50, height=11, state='normal'))
        self.testo_seriale[2].place(x=10, y=40)
        # SCROLL
        self.scroll_seriale = []
        self.scroll_seriale.insert(0, ttk.Scrollbar(self.scheda_seriale[0], orient="vertical",
                                                    command=self.testo_seriale[0].yview))
        self.scroll_seriale.insert(1, ttk.Scrollbar(self.scheda_seriale[1], orient="vertical",
                                                    command=self.testo_seriale[1].yview))
        self.scroll_seriale.insert(2, ttk.Scrollbar(self.scheda_seriale[2], orient="vertical",
                                                    command=self.testo_seriale[2].yview))
        self.scroll_seriale[0].place(x=400, y=40, relheight=0.8)
        self.scroll_seriale[1].place(x=400, y=40, relheight=0.8)
        self.scroll_seriale[2].place(x=400, y=40, relheight=0.8)
        self.testo_seriale[0]["yscrollcommand"] = self.scroll_seriale[0].set
        self.testo_seriale[1]["yscrollcommand"] = self.scroll_seriale[1].set
        self.testo_seriale[2]["yscrollcommand"] = self.scroll_seriale[2].set
        # BIND ENTRY
        self.entry_comando[0].bind("<Return>", lambda event: self.inviaComando(0))  # la funzione richiede event
        self.entry_comando[1].bind("<Return>", lambda event: self.inviaComando(1))
        self.entry_comando[2].bind("<Return>", lambda event: self.inviaComando(2))

    # --------- INVIA COMANDO --------

    def inviaComando(self, i,comando=""):
        if (self.arduino_connesso[i] == True):
            # verifico la presenza di un comando
            if (self.entry_comando[i].get().strip() != ""):
                # provo a inviare
                try:
                    print("Comando da inviare: " + self.entry_comando[i].get())
                    self.arduino[i].write(self.entry_comando[i].get().encode())
                    self.testo_seriale[i].insert(END,">>"+self.entry_comando[i].get()+"\n")
                    self.testo_seriale[i].see(END)
                    print("inviato")
                except Exception as e:
                    print("Errore da invioComando(i)" + e.__str__())
                    self.label_info["text"] = "Errore invio comando"
            else:
                if(comando!=""):
                    print("Comando da inviare:"+comando)
                    try:
                        self.arduino[i].write(comando.encode())
                        self.testo_seriale[i].insert(END, ">>" + comando+"\n")
                        self.testo_seriale[i].see(END)
                    except Exception as e:
                        print("Errore da invioComando(i)" + e.__str__())
                        self.label_info["text"] = "Errore invio comando"
                else:
                    self.label_info["text"] = "Inserisci un comando"
            self.entry_comando[i].delete(0, END)
        else:
            # notifica che arduino[i] non ?? connesso
            self.label_info["text"] = "Errore: Arduino non connesso"


    def clearSeriale(self,i):
        self.testo_seriale[i].delete('1.0',END)
        #pass



    def salvaTesto(self,i):
        data=datetime.date.today().strftime("%d_%m_%y")
        orario=datetime.datetime.now().strftime("%H_%M_%S")

        print(data)
        print(orario.__str__())
        try:
            if(i==0):
                #print(os.path.join("log","Controllo__"+str(data)+"___"+str(orario)+".txt"))
                file=open(os.path.join("log","Controllo__"+str(data)+"___"+str(orario)+".txt"),"w")
                for x in self.testo_seriale[i].get(1.0,END):
                    file.write(x)
                file.close()
            if (i == 1):
                file=open(os.path.join("log","Pressione__"+str(data)+"___"+str(orario)+".txt"),"w")
                for x in self.testo_seriale[i].get(1.0, END):
                    file.write(x)
                file.close()
            if (i == 2):
                file=open(os.path.join("log","Guanto__"+str(data)+"___"+str(orario)+".txt"),"w")
                for x in self.testo_seriale[i].get(1.0, END):
                    file.write(x)
                file.close()
        except Exception as e:
            print(e.__str__())

#-------------------------------------------------------------------------------------

    def initTabMovimenti(self, tab):
        Label(tab, text="Seleziona cartella").place(x=10, y=10)
        Button(tab, text="Seleziona ", command=self.selezionaCartella).place(x=150, y=10)
        Button(tab, text="Apri cartella", command=self.apriCartella).place(x=250, y=10)
        Label(tab, text="Cartella selezionata: ").place(x=10, y=40)
        # label cartella selezionata
        self.label_cartella = Label(tab, text="------")
        self.label_cartella.place(x=10, y=60)
        # LISTA FILE .TXT NELLA CARTELLA SELEZIONATA
        self.listbox_file = Listbox(tab, height=10, width=30)
        self.listbox_file_scrollbar = Scrollbar(tab, orient='vertical', command=self.listbox_file.yview)
        self.listbox_file["yscrollcommand"] = self.listbox_file_scrollbar.set
        self.listbox_file_scrollbar.place(x=190, y=80, height=160)
        self.listbox_file.place(x=10, y=80)
        # BIND PER APRIRE MICROMOVIMENTI
        self.listbox_file.bind("<Return>", self.visualizzaMicromovimenti)
        self.listbox_file.bind("<Double-1>", self.visualizzaMicromovimenti)
        # ENTRY NUOVO FILE MOVIMENTO
        self.entry_nuovo_movimento = Entry(tab, width=20)
        self.entry_nuovo_movimento.place(x=220, y=83)
        # BUTTON CREA FILE
        self.bt_crea_file = Button(tab, text="Crea", command=self.creaFile)
        self.entry_nuovo_movimento.bind("<Return>", self.creaFile)
        self.bt_crea_file.place(x=350, y=80)
        # BUTTON ELIMINA FILE
        self.bt_elimina = Button(tab, text="Elimina", command=self.eliminaFile)
        self.bt_elimina.place(x=220, y=120)
        # LISTA MICROMOVIMENTI
        Label(tab, text="Elenco micromovimenti:").place(x=10, y=260)
        self.label_file_aperto = Label(tab, text="-----")
        self.label_file_aperto.place(x=150, y=260)
        self.listbox_micromovimenti = Listbox(tab, height=15, width=40)  # listvariable=lista_file2
        self.listbox_micromovimenti.place(x=10, y=280)
        self.listbox_micromovimenti_scrollbar_y = Scrollbar(tab, orient='vertical',
                                                            command=self.listbox_micromovimenti.yview)
        self.listbox_micromovimenti_scrollbar_x = Scrollbar(tab, orient='horizontal',
                                                            command=self.listbox_micromovimenti.xview)
        self.listbox_micromovimenti["yscrollcommand"] = self.listbox_micromovimenti_scrollbar_y.set
        self.listbox_micromovimenti["xscrollcommand"] = self.listbox_micromovimenti_scrollbar_x.set
        self.listbox_micromovimenti_scrollbar_y.place(x=254, y=282, height=240)
        self.listbox_micromovimenti_scrollbar_x.place(x=10, y=523, width=250)
        # BIND ELIMINA MICROMOVIMENTO
        self.listbox_micromovimenti.bind("<Delete>", self.eliminaMicromovimento)
        self.listbox_micromovimenti.bind("<BackSpace>", self.eliminaMicromovimento)
        # INFO TAB MOVIMENTI (CREATORE)
        Label(tab, text="INFO:").place(x=10, y=790)
        self.label_info_creatore = Label(tab, text="-----")
        self.label_info_creatore["text"] = "-----"
        self.label_info_creatore.place(x=10, y=810)

    def initPusantiGestioneMovimento(self, tab):
        # PULSANTI ACQUIZIONE E GESTIONE MICROMOVIMENTI
        self.frame_gestione = Frame(tab)
        self.frame_gestione.place(x=280, y=280)
        Button(self.frame_gestione, text="Invia intera sequenza", command=self.inviaMovimento).grid(row=1, column=0, stick="NW",
                                                                                       padx=10, pady=10)
        Button(self.frame_gestione, text="Invia comando selezionato", command=self.inviaMicromovimento).grid(row=2, column=0,
                                                                                               stick="NW",
                                                                                               padx=10, pady=10)
        Button(self.frame_gestione, text="Modifica", command=self.modificaMicromovimento).grid(row=3, column=0,
                                                                                               stick="NW", padx=10,
                                                                                               pady=10)
        Button(self.frame_gestione, text="Salva", command=self.salvaMovimento).grid(row=4, column=0, stick="NW",
                                                                                    padx=10, pady=10)
       # Button(self.frame_gestione, text="Deseleziona", command=lambda: ()).grid(row=5, column=0, stick="NW", padx=10,pady=10)
        Button(self.frame_gestione, text="Elimina", command=self.eliminaMicromovimento).grid(row=6, column=0, stick="NW", padx=10,
                                                                           pady=10)

    #intera sequenza
    def inviaMovimento(self):
        pass

    def inviaMicromovimento(self):
        indice = self.listbox_micromovimenti.curselection()
        print(indice)
        if (indice != ()):
            self.inviaComando(0,self.listbox_micromovimenti.get(indice)[0:len(self.listbox_micromovimenti.get(indice))-1])
            print("Micromovimento inviato")
        else:
            print("Seleziona un micromovimento da inviare")

    # -------------------------- MODIFICA MICROMOVIMENTO -----------------------------------------

    def modificaMicromovimento(self):
        indice = self.listbox_micromovimenti.curselection()
        print(indice)
        if(indice!=()):
            try:
                self.root_modifica = Toplevel(self.root)
                self.root_modifica.geometry("800x80+600+600")
                self.root_modifica.title("Modifica")
                self.entry_modifica_comando = Entry(self.root_modifica, width=100)
                self.entry_modifica_comando.place(x=10, y=10)

                self.entry_modifica_comando.insert(0, self.listbox_micromovimenti.get(indice)[0:len(self.listbox_micromovimenti.get(indice))-1])
                Button(self.root_modifica, text="Salva", command=lambda : self.aggiornaMicromovimento(indice)).place(x=350, y=50)
                Button(self.root_modifica, text="Annulla", command=self.annullaAggiornamentoMicromovimento).place(x=400,y=50)
            except Exception as e:
                print("Errore modifica: " + e.__str__())
        else:
            self.label_info_creatore["text"]="Seleziona un movimento da modificare"

    def aggiornaMicromovimento(self,indice):
        print(indice)
        self.listbox_micromovimenti.delete(indice)
        self.listbox_micromovimenti.insert(indice,self.entry_modifica_comando.get()+"\n")


    def annullaAggiornamentoMicromovimento(self):
        self.label_info_creatore["text"] = "Modifica annullata"
        self.root_modifica.destroy()

    """
    #INFO UTILE
    def deseleziona(self):
        listbox_micromovimenti.selection_clear(0, END)
        # listbox.bind('<FocusOut>', lambda e: listbox.selection_clear(0, END)) (utile per il futuro)
    """
    #--------------------------------------------------------------------------------------------------

    def disabilitaPulsanti(self):
        for x in self.frame_gestione.winfo_children():
            x.config(state=DISABLED)
        for x in self.frame_acquisizione.winfo_children():
            x["state"] = DISABLED

    def abilitaPulsanti(self):
        for x in self.frame_gestione.winfo_children():
            x.config(state=NORMAL)
        for x in self.frame_acquisizione.winfo_children():
            x["state"] = NORMAL

    def initPulsantiAcquisizioneMovimento(self, tab):
        #TODO:aggiugngere acquisisizione stream guanto
        self.frame_acquisizione = Frame(tab, width=380, height=200, bg='lightblue')
        self.frame_acquisizione.place(x=10, y=550)
        self.entry_comando_creatore = Entry(self.frame_acquisizione, width=36)
        self.entry_comando_creatore.place(x=10, y=10)
        self.entry_comando_creatore.bind("<Return>", self.aggiungiMicromovimento)
        self.bt_aggiungi_micromovimento = Button(self.frame_acquisizione, text="Aggiungi",
                                                 command=self.aggiungiMicromovimento)
        self.bt_aggiungi_micromovimento.place(x=240, y=10)
        Button(self.frame_acquisizione, text="Acquisisci singola posizione Controllo", command=self.acquisisciPosizioneControllo).place(
            x=10, y=40)
        Button(self.frame_acquisizione, text="Acquisisci singola posizione Retroazione",
               command=self.acquisisciPosizioneRetroazione).place(x=10, y=70)
        Button(self.frame_acquisizione, text="Acquisisci singola posizione Guanto", command=self.acquisisciPosizioneGuanto).place(x=10,
                                                                                                                y=100)
        #TODO: STREAM GUANTO
        Label(self.frame_acquisizione,bg='lightblue',text="Intervallo(ms)").place(x=10,
                                                             y=160)
        self.bt_rec=Button(self.frame_acquisizione, text="Registra Guanto",
               command=self.registraGuanto)
        self.bt_rec.place(x=180,y=158)
        self.delay_guanto_registrazione=tk.Entry(self.frame_acquisizione,width=10)
        self.delay_guanto_registrazione.place(x=100,y=160)
        self.delay_guanto_registrazione.insert(0,"500")

#------------------ REGISTRA GUANTO ---------------------------------------

    def registraGuanto(self):
        if(not self.thred_rec_flag):
            #TODO: registraGuanto da completare
            self.thread_rec=threading.Thread(target=self.registraGuantoThread)
            self.thred_rec_flag=True
            self.thread_rec.start()
            self.bt_rec["text"]="Stop"
        else:
            self.thred_rec_flag = False
            self.bt_rec["text"]="Registra Guanto"


    def registraGuantoThread(self):
        while(self.thred_rec_flag):
            print("thread rec")
            self.acquisisciPosizioneGuanto()
            time.sleep(float(self.delay_guanto_registrazione.get())/1000)

    """
         RIPASSO 
        self.thread_lettura[i] = threading.Thread(target=lambda: self.letturaSeriale(i))
        self.thread_lettura[i].start()
    """

#-----------------------------------------------------------



    def aggiungiMicromovimento(self,
                               event=None):  # event mi serve per il bind, metto None se il metodo non ?? chiamato da bind
        # entry_comando_creatore
        if (self.entry_comando_creatore.get().strip() == ""):
            self.label_info_creatore["text"] = "Inserisci comando"
        else:
            posizione = self.listbox_micromovimenti.curselection().__len__()
            if (posizione == 0):
                self.listbox_micromovimenti.insert(END, self.entry_comando_creatore.get() + "\n")
            else:
                self.listbox_micromovimenti.insert(int(self.listbox_micromovimenti.curselection()[0]) + 1,
                                                   self.entry_comando_creatore.get() + "\n")
        self.entry_comando_creatore.delete(0, END)
        self.listbox_micromovimenti.see(END)  # in questo modo si vede sempre l'ultimo comando inserito

    def acquisisciPosizioneControllo(self):
        print(self.mano_controllo.getJson())
        #DESERIALIZZARE JSON
        file=json.loads(self.mano_controllo.getJson())

        posizione = self.listbox_micromovimenti.curselection().__len__()
        if (posizione == 0):
            self.listbox_micromovimenti.insert(END, self.mano_controllo.getJson() + "\n")
        else:
            self.listbox_micromovimenti.insert(int(self.listbox_micromovimenti.curselection()[0]) + 1,
                                               self.mano_controllo.getJson() + "\n")
        self.entry_comando_creatore.delete(0, END)
        self.listbox_micromovimenti.see(END)  # in questo modo si vede sempre l'ultimo comando inserito
        array_d10=file["d1"];
        #print(array_d10[0])


    def acquisisciPosizioneRetroazione(self):
        posizione = self.listbox_micromovimenti.curselection().__len__()
        if (posizione == 0):
            self.listbox_micromovimenti.insert(END, self.mano_retroazione.getJson() + "\n")
        else:
            self.listbox_micromovimenti.insert(int(self.listbox_micromovimenti.curselection()[0]) + 1,
                                               self.mano_retroazione.getJson() + "\n")
        self.entry_comando_creatore.delete(0, END)
        self.listbox_micromovimenti.see(END)


    def acquisisciPosizioneGuanto(self):
        posizione = self.listbox_micromovimenti.curselection().__len__()
        if (posizione == 0):
            self.listbox_micromovimenti.insert(END, self.mano_guanto.getJson() + "\n")
        else:
            self.listbox_micromovimenti.insert(int(self.listbox_micromovimenti.curselection()[0]) + 1,
                                               self.mano_guanto.getJson() + "\n")
        self.entry_comando_creatore.delete(0, END)
        self.listbox_micromovimenti.see(END)


    def selezionaCartella(self):
        try:
            self.cartella = tkinter.filedialog.askdirectory(initialdir=os.getcwd(),
                                                            title="Seleziona cartella movimento")
            self.label_cartella["text"] = self.cartella
            self.aggiornaListaFile()
        except Exception as e:
            self.label_info_creatore["text"] = e.__str__()

    def aggiornaListaFile(self):
        self.elenco_file = os.listdir(self.cartella)
        # elimino tutto
        self.listbox_file.delete(0, END)
        self.listbox_micromovimenti.delete(0, END)
        for x in self.elenco_file:
            self.listbox_file.insert(0, x)

    def apriCartella(self):
        try:
            os.startfile(self.cartella)
        except:
            self.label_info_creatore["text"] = "Seleziona una cartella"

    def visualizzaMicromovimenti(self, event):  # forse vuole event per la questione del bind...
        self.file_dettagli = self.listbox_file.get(self.listbox_file.curselection())
        self.label_file_aperto["text"] = self.file_dettagli
        print("x=" + self.label_file_aperto["text"])
        self.listbox_micromovimenti.delete(0, END)
        try:
            f = open(os.path.join(self.cartella, self.file_dettagli), "r")
            righe = f.readlines()
            for riga in righe:
                self.listbox_micromovimenti.insert(END, riga)
            f.close()

            self.abilitaPulsanti()
        except Exception as e:
            self.label_info_creatore["text"] = e.__str__()

    def salvaMovimento(self):

        try:
            file = open(os.path.join(self.label_cartella["text"], self.label_file_aperto["text"]), "w")
            for x in self.listbox_micromovimenti.get(0, END):
                file.write(x)
            file.close()
            self.label_info_creatore["text"] = self.label_file_aperto["text"] + " salvato"
        except Exception as e:
            tk.messagebox.showerror("Errore", "Errore durante il salvataggio: " + e.__str__())
            # print(e.__str__())

    def creaFile(self,
                 event=None):  # con il bind mi serve event, senza bind (cio?? solo click) event non serve ma ?? richiesto
        if (self.entry_nuovo_movimento.get().strip() == ""):
            self.label_info_creatore["text"] = "Inserisci il nome del file da creare!"
            return
        try:
            os.chdir(self.cartella)
            file = open(self.entry_nuovo_movimento.get() + ".txt", 'x')
            file.close()
            self.aggiornaListaFile()
            self.entry_nuovo_movimento["text"] = ""
            self.label_info_creatore["text"] = "File creato"
        except Exception as e:
            print("Errore da creaFile() :" + e.__str__())
            self.label_info_creatore["text"] = "Errore creazione file\n" + e.__str__()

    def eliminaFile(self):
        try:
            self.file_eliminare = self.listbox_file.get(self.listbox_file.curselection())
            scelta = messagebox.askyesno("Eliminare " + self.file_eliminare, "Sicuro??")

            if scelta == False:
                return
        except:
            messagebox.showerror("Errore", "Seleziona un file")
            return
        try:
            os.chdir(self.cartella)  # dove il file si trova
            # nel caso sia un movimento aperto devo chiudere la listbox micromoviemnti e disabilitare i pulsanti
            if (self.file_eliminare == self.label_file_aperto["text"]):
                self.listbox_micromovimenti.delete(0, END)
                self.label_file_aperto["text"] = "-----------"  # solo se coincide con quello aperto
                self.disabilitaPulsanti()
            os.remove(self.file_eliminare)
            self.aggiornaListaFile()
            self.label_info_creatore["text"] = self.file_eliminare + " eliminato"

        except:
            self.label_info_creatore["text"] = "Errore durante eliminazione " + self.file_eliminare

    def eliminaMicromovimento(self,val=None):
        try:
            self.listbox_micromovimenti.delete(self.listbox_micromovimenti.curselection())
        except:
            self.label_info_creatore["text"] = "Seleziona un comando da eliminare"

    def chiudiTutto(self):
        # TODO: prima di chiudere verificare se c'?? qualcosa da salvare
        for i in range(0, self.flag_thread.__len__()):
            if self.flag_thread[i] == True:
                print("Chiudo il thread i=" + str(i))
                self.startThreadLettura(i)
        self.root.destroy()

    # ---------------------------------- MAPPA ---------------------------------------

    def initTabMappe(self):
        self.scheda_mappa_controllo = LabelFrame(self.tab_mappa_controllo, text="Controllo", width=360, height=400)
        self.scheda_mappa_controllo.place(x=10, y=10)
        self.scheda_mappa_retroazione = LabelFrame(self.tab_mappa_controllo, text="Retroazione ", width=360, height=400)
        self.scheda_mappa_retroazione.place(x=10, y=430)

        self.scheda_mappa_pressione = LabelFrame(self.tab_mappa_pressione, text="Pressione", width=360, height=400)
        self.scheda_mappa_pressione.place(x=10, y=10)

        self.scheda_mappa_guanto = LabelFrame(self.tab_mappa_pressione, text="Guanto controllo remoto", width=360, height=400)
        self.scheda_mappa_guanto.place(x=10, y=430)

        # MAPPA CONTROLLO
        self.mano_controllo = Mano()
        # ----- canvas mano --------
        self.canvas_mano_controllo = FigureCanvasTkAgg(self.mano_controllo.getFig(), master=self.scheda_mappa_controllo)
        self.canvas_mano_controllo.get_tk_widget().place(x=20, y=10)

        toolbar_mano_controllo = NavigationToolbar2Tk(self.canvas_mano_controllo, self.scheda_mappa_controllo)
        toolbar_mano_controllo.update()
        toolbar_mano_controllo.place(x=10, y=320)

        self.mano_controllo.visualizzaPosizioneDesiderata()
        self.canvas_mano_controllo.draw()

        # MAPPA RETROAZIONE
        self.mano_retroazione = Mano('b')
        # ----- canvas mano --------
        self.canvas_mano_retroazione = FigureCanvasTkAgg(self.mano_retroazione.getFig(),
                                                         master=self.scheda_mappa_retroazione)
        self.canvas_mano_retroazione.get_tk_widget().place(x=20, y=10)

        toolbar_mano_retroazione = NavigationToolbar2Tk(self.canvas_mano_retroazione, self.scheda_mappa_retroazione)
        toolbar_mano_retroazione.update()
        toolbar_mano_retroazione.place(x=10, y=320)

        self.mano_retroazione.visualizzaPosizioneDesiderata()
        self.canvas_mano_retroazione.draw()

        # MAPPA PRESSIONE
        self.mano_pressione = ManoPressione("Pressione")
        # ----- canvas mano --------
        self.canvas_mano_pressione = FigureCanvasTkAgg(self.mano_pressione.getFig(), master=self.scheda_mappa_pressione)
        self.canvas_mano_pressione.get_tk_widget().place(x=20, y=10)

        toolbar_mano_pressione = NavigationToolbar2Tk(self.canvas_mano_pressione, self.scheda_mappa_pressione)
        toolbar_mano_pressione.update()
        toolbar_mano_pressione.place(x=10, y=320)

        # self.mano_pressione.visualizzaPosizioneDesiderata()
        self.canvas_mano_pressione.draw()

        #MAPPA GUANTO
        self.mano_guanto=Mano('g')
        self.canvas_mano_guanto = FigureCanvasTkAgg(self.mano_guanto.getFig(), master=self.scheda_mappa_guanto)
        self.canvas_mano_guanto.get_tk_widget().place(x=20, y=10)

        self.toolbar_mano_guanto = NavigationToolbar2Tk(self.canvas_mano_guanto, self.scheda_mappa_guanto)
        self.toolbar_mano_guanto.update()
        self.toolbar_mano_guanto.place(x=10, y=320)

        self.mano_guanto.visualizzaPosizioneDesiderata()
        self.canvas_mano_guanto.draw()



    # ---------------- THREAD ------------------------------
    """
    il thread_lettura ?? necessario per rimanere sempre in ascolto
    quanto riceve 'ok' vuol dire che pu?? l'arduino ?? pronto per ricevere un comando, questo ?? possibile
    utilizzado doppio mutex
    ripasso:
      mutex1.acquire(blocking=True) (bloccante)
      ....
      mutex2.relase()
    
    
    
    """

    def letturaSeriale(self, i):
        while (self.flag_thread[i]):
            try:
                lettura = self.arduino[i].readline().decode("ascii") #readline ?? bloccante
                self.testo_seriale[i].insert(END, lettura)
                self.testo_seriale[i].see(END)
                self.analisiComando(i, lettura)


            except Exception as e:
                self.flag_thread[i] = False  # in questo modo elimino il thread dopo il giro
                print("Errore da THREAD: " + e.__str__())

    def startThreadLettura(self, i):
        if (self.flag_thread[i] == False):
            self.flag_thread[i] = True
            self.thread_lettura[i] = threading.Thread(target=lambda: self.letturaSeriale(i))
            self.thread_lettura[i].start()
        else:
            pass

    def stopThreadLettura(self, i):
        # TODO: prima di root.destroy assicurarsi che tutti i thread siano stati eliminati (join)
        self.flag_thread[i] = False  # in questo modo termina

    # ------------------- ANALISI COMANDI ----------------

    def analisiComando(self, i, comando):
        #PER LA RETROAZIONE (SPLIT ANGOLI)
        if (i == 0):
            print("Esecuzione comando " + comando)
            # Scheda Motori & retroazione
            # TEST

            try:
                #TEST
                """
                angolo = [0, 0, 0]
                i = 0
                comando_ricevuto = comando.split("|")
                print(comando)
                for x in comando_ricevuto:
                    angolo_ricevuto = x.split(":")
                    angolo[i] = angolo_ricevuto[1]
                    print("angolo i:" + angolo[i])
                    i = i + 1

                print(angolo)
                # TODO: da sistemare errori simili : ['stop\r\n', 0, 0]
                self.mano_retroazione.setAngolo(1, 0, angolo[0])
                self.mano_retroazione.setAngolo(1, 1, angolo[1])
                self.mano_retroazione.setAngolo(1, 2, angolo[2])
                self.canvas_mano_retroazione.draw()
                """
            except Exception as e:
                self.label_info["text"]=e.__str__()
                pass

        elif (i == 1):
            print("Analisi comando 1")
            print("Esecuzione comando " + comando)
            # Scheda Pressione
            #verifico la presenza dei campi "s1" sul json appena ricevuto
            #se presente modifico il valore id pressione e invio ok
            #arduino ad ogni "next" reimposta il flag a true
            try:
                obj_json=json.loads(comando)
                if(obj_json["s1"]!=None):
                    print(obj_json["s1"])
                    self.mano_pressione.aggiornaSensore(5,int(obj_json["s1"]))
                    self.canvas_mano_pressione.draw()
                    #x = threading.Thread(target=self.thread_invia_next, args=(1,))
                    #x.start()
                    #al primo comando errato si ferma, per evitare un loop
                    self.inviaComando(1,"next")
            except Exception as e:
                print(e.__str__())

        elif (i == 2):
            print("Esecuzione comando " + comando)
            # Scheda Guanto
            try:
                obj_json = json.loads(comando)
                self.mano_guanto.setAngolo(1,1,obj_json["d1"][0])
                self.mano_guanto.setAngolo(1, 2, obj_json["d1"][1])
                self.canvas_mano_guanto.draw() #per aggiornare la mappa
                self.inviaComando(2,"next")
            except Exception as e:
                print(e.__str__())
                self.label_info["text"]=e.__str__()

"""
    def thread_invia_next(self,args):
        time.sleep(0.6)
        self.inviaComando(1,"next")
        pass
"""
mano_dx = finestraMano()
# mano_sx=finestraMano(titolo="mano_sx")
mainloop()