import copy
import os
import tkinter.filedialog
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
from ManoV3 import Mano
from ManoPressione import ManoPressione
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
        self.initTabMovimenti(self.tab_creatore_1)
        self.initPusantiGestionMovimento(self.tab_creatore_1)
        self.initPulsantiAcquisizioneMovimento(self.tab_creatore_1)
        self.initMenu()
        self.initTabMappe()


        self.root.protocol("WM_DELETE_WINDOW",self.chiudiTutto) #per sicurezza
        self.initCartellaLavoro()
        self.disabilitaPulsanti() #in questo modo devo necessariamente aprire un file per abiltiare i comandi


    def initMenu(self):
        self.menu_bar=Menu(self.root)
        self.menu_info = Menu(self.menu_bar, tearoff = 0)
        self.menu_strumenti=Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(menu=self.menu_strumenti, label="Strumenti")
        self.menu_bar.add_cascade(menu=self.menu_info,label="Info")

        self.menu_strumenti.add_command(label="Registrazione",command=self.apriRegistratore)
        self.menu_strumenti.add_command(label="Impostazioni", command=lambda:())
        self.menu_strumenti.add_command(label="Configura mappa", command=lambda:())
        self.menu_strumenti.add_command(label="Impostazioni Arduino", command=lambda:())

        self.menu_info.add_command(label="Manuale", command=lambda:())
        self.menu_info.add_command(label="Protocollo arduino", command=lambda:())

        self.root["menu"] = self.menu_bar

    #-----------------REGISTRA MOVIMENTO ----------------------
    def apriRegistratore(self):
        print("Avvio registratore")
        self.win = Toplevel(self.root)
        self.win.title("Registratore")
        self.win.geometry("800x600+200+200")
        self.win.resizable(False,False)
        self.win.attributes("-topmost", True) #sempre in primo piano
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

        #TAB
        self.notebook_test=ttk.Notebook(self.win, width=400, height=550)
        self.tab_test = Frame(self.notebook_test)
        self.notebook_test.add(self.tab_test, text="Mov")
        self.notebook_test.place(x=380,y=10)




    def chiudiRegistratore(self):
        self.menu_strumenti.entryconfigure(0,state=ACTIVE)
        del self.mano_guanto #distruttore
        self.win.destroy()

    #---------------------------------------------------------

    def initCartellaLavoro(self):
        #al primoa avvio cerca la cartealla /movimenti
        # IMPSOTO LA CARTELLA DI DEFAULT
        try:
            self.cartella = os.path.join(os.getcwd(), "movimenti")  # per compatibilità linux e windows
            self.aggiornaListaFile()
            self.label_cartella["text"] = self.cartella.__str__()
        except:
            self.label_info_creatore["text"]="Cartella di defautl movimenti non trovata "


    def initNotebook(self):
        self.notebook_0 = ttk.Notebook(self.root, width=470, height=self.dim_y - 50)
        self.notebook_1 = ttk.Notebook(self.root,width=340,height=self.dim_y-50)
        self.notebook_2 = ttk.Notebook(self.root,width=400,height=self.dim_y-50)
        self.notebook_3 = ttk.Notebook(self.root,width=470, height=self.dim_y-50)


    def initTab(self):
        #0 Mappe
        self.tab_mappa_controllo=Frame(self.notebook_0)
        self.tab_mappa_pressione = Frame(self.notebook_0)
        self.notebook_0.add(self.tab_mappa_controllo,text="Mappe")
        self.notebook_0.add(self.tab_mappa_pressione, text="Pressione")
        self.notebook_0.place(x=5,y=10)
        #1
        self.tab_controllo = Frame(self.notebook_1)
        self.tab_impostazioni = Frame(self.notebook_1)
        self.notebook_1.add(self.tab_controllo, text="Controllo V1")
        self.notebook_1.add(self.tab_impostazioni, text="Controllo V2")
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



        Label(tab, text="Elenco porte COM").place(x=10, y=150)

        self.label_porte = Label(tab, text="--------------\n--------------")
        self.label_porte.place(x=10, y=170)

        self.bt_connetti=[None,None,None]
        self.bt_connetti[0]=Button(tab, text="Connetti",command=lambda: self.connetti(0))
        self.bt_connetti[0].place(x=350, y=32)
        self.bt_connetti[1]=Button(tab, text="Connetti", command=lambda: self.connetti(1))
        self.bt_connetti[1].place(x=350,y=62)
        self.bt_connetti[2]=Button(tab, text="Connetti", command=lambda: self.connetti(2))
        self.bt_connetti[2].place(x=350, y=92)
        # ***************** INFO ************************
        Label(self.notebook_3, text="INFO: ").place(x=10, y=800)
        self.label_info = ttk.Label(self.notebook_3, text="-----")
        self.label_info.place(x=10, y=820)


    def connetti(self,i):
        print("Mi collego a arduino "+str(i))
        if(self.arduino_connesso[i]==False):
            #connetti
            try:
                self.arduino[i]=serial.Serial(port=self.combo[i].get(),baudrate=9600,stopbits=1,bytesize=8)
                self.label_info["text"] = "Scheda motori connessa " + self.combo[i].get()
                self.combo[i]["state"] = DISABLED
                self.bt_connetti[i]["text"]="Disconnetti"
                self.arduino_connesso[i]=True
                #TODO: startThreadLettura(i)
            except Exception as e:
                self.label_info["text"]="Errore connessione "+self.combo[i].get()
                print(e.__str__())

        else:
            self.arduino_connesso[i]=False
            self.bt_connetti[i]["text"] = "Connetti"
            try:
                self.arduino[i].close()
                self.combo[i]["state"]="readonly"
                self.label_info["text"]="Scheda disconnessa"
                # TODO: stopThreadLettura(i)
            except:
                self.label_info["text"] = "Errore disconnessione"





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
        #print(self.elenco[0])
        #print(self.elenco[1] )
        #print(self.elenco[2] )

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
        self.scheda_seriale.insert(1,ttk.LabelFrame(tab, text="Scheda pressione", width=450, height=250))
        self.scheda_seriale.insert(2,ttk.LabelFrame(tab, text="Scheda guanto", width=450, height=250))
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
        Button(self.scheda_seriale[0], text="Invia", command=lambda:self.inviaComando(0)).place(x=160, y=5)
        Button(self.scheda_seriale[1], text="Invia", command=lambda:self.inviaComando(1)).place(x=160, y=5)
        Button(self.scheda_seriale[2], text="Invia", command=lambda: self.inviaComando(2)).place(x=160, y=5)
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
        #BIND ENTRY
        #TODO: bind entry con parametro event
        self.entry_comando[0].bind("<Return>", lambda event: {}) #la funzione richiede event
        self.entry_comando[1].bind("<Return>", lambda event: {})
        self.entry_comando[2].bind("<Return>", lambda event: {})

    #--------- INVIA COMANDO --------

    def inviaComando(self,i):
        print("Invio comando di entry_comando["+str(i)+"]\nComando da inviare: "+self.entry_comando[i].get())
        if(self.arduino_connesso[i]==True):
            #verifico la presenza di un comando
            if(self.entry_comando[i].get().strip() !=""):
                #provo a inviare
                try:
                    self.arduino[i].write(self.entry_comando[i].get().encode())
                except Exception as e:
                    print(e.__str__())
                    self.label_info["text"]="Errore invio comando"
            else:
                self.label_info["text"]="Inserisci un comando"

        else:
            #notifica che arduino[i] non è connesso
            self.label_info["text"]="Errore: Arduino non connesso"






    def initTabMovimenti(self,tab):
        Label(tab, text="Seleziona cartella").place(x=10, y=10)
        Button(tab, text="Seleziona ", command=self.selezionaCartella).place(x=150, y=10)
        Button(tab, text="Apri cartella", command=self.apriCartella).place(x=250, y=10)
        Label(tab, text="Cartella selezionata: ").place(x=10, y=40)
        #label cartella selezionata
        self.label_cartella=Label(tab, text="------")
        self.label_cartella.place(x=10,y=60)
        #LISTA FILE .TXT NELLA CARTELLA SELEZIONATA
        self.listbox_file = Listbox(tab, height=10, width=30)
        self. listbox_file_scrollbar = Scrollbar(tab, orient='vertical', command=self.listbox_file.yview)
        self.listbox_file["yscrollcommand"] = self.listbox_file_scrollbar.set
        self.listbox_file_scrollbar.place(x=190, y=80, height=160)
        self.listbox_file.place(x=10, y=80)
        #BIND PER APRIRE MICROMOVIMENTI
        self.listbox_file.bind("<Return>", self.visualizzaMicromovimenti)
        self.listbox_file.bind("<Double-1>", self.visualizzaMicromovimenti)
        #ENTRY NUOVO FILE MOVIMENTO
        self.entry_nuovo_movimento = Entry(tab, width=20)
        self.entry_nuovo_movimento.place(x=220, y=83)
        #BUTTON CREA FILE
        self.bt_crea_file = Button(tab, text="Crea", command=self.creaFile)
        self.entry_nuovo_movimento.bind("<Return>", self.creaFile)
        self.bt_crea_file.place(x=350, y=80)
        #BUTTON ELIMINA FILE
        self.bt_elimina = Button(tab, text="Elimina", command=self.eliminaFile)
        self.bt_elimina.place(x=220, y=120)
        #LISTA MICROMOVIMENTI
        Label(tab, text="Elenco micromovimenti:").place(x=10, y=260)
        self.label_file_aperto = Label(tab, text="-----")
        self.label_file_aperto.place(x=150, y=260)
        self.listbox_micromovimenti = Listbox(tab, height=15, width=40)  # listvariable=lista_file2
        self.listbox_micromovimenti.place(x=10, y=280)
        self.listbox_micromovimenti_scrollbar_y = Scrollbar(tab, orient='vertical',command=self.listbox_micromovimenti.yview)
        self.listbox_micromovimenti_scrollbar_x = Scrollbar(tab, orient='horizontal',command=self.listbox_micromovimenti.xview)
        self.listbox_micromovimenti["yscrollcommand"] = self.listbox_micromovimenti_scrollbar_y.set
        self.listbox_micromovimenti["xscrollcommand"] = self.listbox_micromovimenti_scrollbar_x.set
        self.listbox_micromovimenti_scrollbar_y.place(x=254, y=282, height=240)
        self.listbox_micromovimenti_scrollbar_x.place(x=10, y=523, width=250)
        #BIND ELIMINA MICROMOVIMENTO
        self.listbox_micromovimenti.bind("<Delete>", self.eliminaMicromovimento)
        self.listbox_micromovimenti.bind("<BackSpace>", self.eliminaMicromovimento)
        #INFO TAB MOVIMENTI (CREATORE)
        Label(tab, text="Info:").place(x=10, y=780)
        self.label_info_creatore = Label(tab, text="-----")
        self.label_info_creatore["text"] = "-----"
        self.label_info_creatore.place(x=10, y=800)

    def initPusantiGestionMovimento(self,tab):
        # PULSANTI ACQUIZIONE E GESTIONE MICROMOVIMENTI
        self.frame_gestione = Frame(tab)
        self.frame_gestione.place(x=280, y=280)
        Button(self.frame_gestione, text="Invia", command=lambda:print("invia")).grid(row=2, column=0, stick="NW", padx=10,pady=10)
        Button(self.frame_gestione, text="Modifica", command=self.modificaMicromovimento).grid(row=3, column=0, stick="NW",padx=10, pady=10)
        Button(self.frame_gestione, text="Salva", command=self.salvaMovimento).grid(row=4, column=0, stick="NW", padx=10,pady=10)
        Button(self.frame_gestione, text="Deseleziona", command=lambda:()).grid(row=5, column=0, stick="NW", padx=10,pady=10)
        Button(self.frame_gestione, text="Elimina", command=lambda:()).grid(row=6, column=0, stick="NW", padx=10,pady=10)


    def modificaMicromovimento(self):
        #TODO: modificaMicromovimento
        pass

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





    def initPulsantiAcquisizioneMovimento(self,tab):
        self.frame_acquisizione = Frame(tab, width=380, height=150, bg='lightblue')
        self.frame_acquisizione.place(x=10, y=550)
        self.entry_comando_creatore = Entry(self.frame_acquisizione, width=36)
        self.entry_comando_creatore.place(x=10, y=10)
        self.entry_comando_creatore.bind("<Return>",self.aggiungiMicromovimento)
        self.bt_aggiungi_micromovimento = Button(self.frame_acquisizione, text="Aggiungi", command=self.aggiungiMicromovimento)
        self.bt_aggiungi_micromovimento.place(x=240, y=10)
        Button(self.frame_acquisizione, text="Acquisisci Controllo", command=self.acquisisciPosizioneControllo).place(x=10, y=40)
        Button(self.frame_acquisizione, text="Acquisisci Retroazione", command=self.acquisisciPosizioneRetroazione).place(x=10,                                                                                          y=70)
        Button(self.frame_acquisizione, text="Acquisisci Guanto", command=self.acquisisciPosizioneGuanto).place(x=10, y=100)

    def aggiungiMicromovimento(self,event=None):#event mi serve per il bind, metto None se il metodo non è chiamato da bind
        #entry_comando_creatore
        # TODO:aggiungiMicromovimento
        if(self.entry_comando_creatore.get().strip()==""):
            self.label_info_creatore["text"]="Inserisci comando"
        else:
            posizione=self.listbox_micromovimenti.curselection().__len__()
            if(posizione==0):
                self.listbox_micromovimenti.insert(END,self.entry_comando_creatore.get()+"\n")
            else:
                self.listbox_micromovimenti.insert(int(self.listbox_micromovimenti.curselection()[0])+1,self.entry_comando_creatore.get())
        self.entry_comando_creatore.delete(0,END)
        self.listbox_micromovimenti.see(END) #in questo modo si vede sempre l'ultimo comando inserito




    def acquisisciPosizioneControllo(self):
        # TODO:acquisisciPosizioneControllo
        pass

    def acquisisciPosizioneRetroazione(self):
        # TODO:acquisisciPosizioneRetroazione
        pass

    def acquisisciPosizioneGuanto(self):
        #TODO:acquisisciPosizioneGuanto
        pass


    def selezionaCartella(self):
        try:
            self.cartella=tkinter.filedialog.askdirectory(initialdir=os.getcwd(),title="Seleziona cartella movimento")
            self.label_cartella["text"]=self.cartella
            self.aggiornaListaFile()
        except Exception as e:
            self.label_info_creatore["text"]=e.__str__()


    def aggiornaListaFile(self):
        self.elenco_file=os.listdir(self.cartella)
        #elimino tutto
        self.listbox_file.delete(0,END)
        self.listbox_micromovimenti.delete(0,END)
        for x in self.elenco_file:
            self.listbox_file.insert(0,x)



    def apriCartella(self):
        try:
            os.startfile(self.cartella)
        except:
            self.label_info_creatore["text"]="Seleziona una cartella"


    def visualizzaMicromovimenti(self,event): #forse vuole event per la questione del bind...
        self.file_dettagli=self.listbox_file.get(self.listbox_file.curselection())
        self.label_file_aperto["text"] = self.file_dettagli
        print("x="+self.label_file_aperto["text"])
        self.listbox_micromovimenti.delete(0,END)
        try:
            f=open(os.path.join(self.cartella,self.file_dettagli),"r")
            righe=f.readlines()
            for riga in righe:
                self.listbox_micromovimenti.insert(END,riga)
            f.close()

            self.abilitaPulsanti()
        except Exception as e:
            self.label_info_creatore["text"]=e.__str__()


    def salvaMovimento(self):

        try:
            file=open(os.path.join(self.label_cartella["text"],self.label_file_aperto["text"]),"w")
            for x in self.listbox_micromovimenti.get(0,END):
                file.write(x)
            file.close()
            self.label_info_creatore["text"]=self.label_file_aperto["text"]+" salvato"
        except Exception as e:
            tk.messagebox.showerror("Errore", "Errore durante il salvataggio: "+e.__str__())
            #print(e.__str__())



    def creaFile(self,event=None): #con il bind mi serve event, senza bind (cioè solo click) event non serve ma è richiesto
        if(self.entry_nuovo_movimento.get().strip()==""):
            self.label_info_creatore["text"]="Inserisci il nome del file da creare!"
            return
        try:
            os.chdir(self.cartella)
            file=open(self.entry_nuovo_movimento.get()+".txt",'x')
            file.close()
            self.aggiornaListaFile()
            self.entry_nuovo_movimento["text"]=""
            self.label_info_creatore["text"]="File creato"
        except Exception as e:
            print(e.__str__())
            self.label_info_creatore["text"]="Errore creazione file\n"+e.__str__()



    def eliminaFile(self):
        try:
            self.file_eliminare=self.listbox_file.get(self.listbox_file.curselection())
            scelta=messagebox.askyesno("Eliminare "+self.file_eliminare, "Sicuro??")

            if scelta==False:
                return
        except:
            messagebox.showerror("Errore","Seleziona un file")
            return
        try:
            os.chdir(self.cartella) #dove il file si trova
            #nel caso sia un movimento aperto devo chiudere la listbox micromoviemnti e disabilitare i pulsanti
            if(self.file_eliminare==self.label_file_aperto["text"]):
                self.listbox_micromovimenti.delete(0,END)
                self.label_file_aperto["text"]="-----------" #solo se coincide con quello aperto
                self.disabilitaPulsanti()
            os.remove(self.file_eliminare)
            self.aggiornaListaFile()
            self.label_info_creatore["text"]=self.file_eliminare + " eliminato"

        except:
            self.label_info_creatore["text"]="Errore durante eliminazione "+self.file_eliminare



    def eliminaMicromovimento(self):

        #TODO: eliminaMicromoviemnto
        pass


    def chiudiTutto(self):
        #TODO: prima di chiudere verificare se c'è qualcosa da salvare
        self.root.destroy()


#---------------------------------- MAPPA ---------------------------------------

    def initTabMappe(self):
        self.scheda_mappa_controllo = LabelFrame(self.tab_mappa_controllo, text="Controllo", width=350, height=390)
        self.scheda_mappa_controllo.place(x=10, y=10)
        self.scheda_mappa_retroazione = LabelFrame(self.tab_mappa_controllo, text="Retroazione ", width=350, height=390)
        self.scheda_mappa_retroazione.place(x=10, y=430)

        self.scheda_mappa_pressione = LabelFrame(self.tab_mappa_pressione, text="Pressione", width=360, height=400)
        self.scheda_mappa_pressione.place(x=5, y=10)

        #TODO: inserimenti mappe
        #MAPPA CONTROLLO
        self.mano_controllo = Mano()
        # ----- canvas mano --------
        canvas_mano_controllo = FigureCanvasTkAgg(self.mano_controllo.getFig(),master=self.scheda_mappa_controllo)
        canvas_mano_controllo.get_tk_widget().place(x=20, y=10)

        toolbar_mano_controllo = NavigationToolbar2Tk(canvas_mano_controllo,self.scheda_mappa_controllo)
        toolbar_mano_controllo.update()
        toolbar_mano_controllo.place(x=10, y=320)

        self.mano_controllo.visualizzaPosizioneDesiderata()
        canvas_mano_controllo.draw()

        #MAPPA RETROAZIONE
        self.mano_retroazione = Mano('b')
        # ----- canvas mano --------
        canvas_mano_retroazione = FigureCanvasTkAgg(self.mano_retroazione.getFig(), master=self.scheda_mappa_retroazione)
        canvas_mano_retroazione.get_tk_widget().place(x=20, y=10)

        toolbar_mano_retroazione = NavigationToolbar2Tk(canvas_mano_retroazione, self.scheda_mappa_retroazione)
        toolbar_mano_retroazione.update()
        toolbar_mano_retroazione.place(x=10, y=320)

        self.mano_retroazione.visualizzaPosizioneDesiderata()
        canvas_mano_retroazione.draw()

        #MAPPA PRESSIONE
        self.mano_pressione = ManoPressione("Pressione")
        # ----- canvas mano --------
        canvas_mano_pressione = FigureCanvasTkAgg(self.mano_pressione.getFig(),master=self.scheda_mappa_pressione)
        canvas_mano_pressione.get_tk_widget().place(x=20, y=10)

        toolbar_mano_pressione = NavigationToolbar2Tk(canvas_mano_pressione, self.scheda_mappa_pressione)
        toolbar_mano_pressione.update()
        toolbar_mano_pressione.place(x=10, y=320)

        #self.mano_pressione.visualizzaPosizioneDesiderata()
        canvas_mano_pressione.draw()



#---------------- THREAD ------------------------------




mano_dx=finestraMano()
#mano_sx=finestraMano(titolo="mano_sx")
mainloop()
