import matplotlib.pyplot as plt
import os
import math
import numpy as np

class Mano():


    def __init__(self,colore='r'):
        self.fig=plt.Figure(figsize=(3.0,3.0))
        self.ax=self.fig.add_subplot(111,projection='3d')
        #plt.axis('off')
        self.ax.set(xlim=(-3, 10), ylim=(0, 13), zlim=(-3, 10))
        # estetica grafico
        #plt.style.use('classic')
        self.ax.view_init(25, -210)  # rotazione
        #plt.tight_layout()

        self.p = np.array([[0] * 3] * 5, dtype='f')  # sono i punti del palmo
        self.dl = np.array([[0] * 3] * 5, dtype='f')  # lunghezza delle sezioni di ogni dito
        self.d = np.array([[0] * 3] * 5,dtype='f')  # sono i punti che collegano ogni dito al palmo (cioè i punti iniziali)
        self.angolo_t = np.array([[0] * 3] * 5,dtype='int')  # per la posizione iniziale all'avvio (modificati successivamente dagli slider)


        # raccolta oggetti (servono per fare .remove())
        #ricorda di fare .clear() dopo aver fatto .remove()
        self.raccolta_palmo_punti = []
        self.raccolta_palmo_linee = []
        self.raccolta_dito_punti = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.raccolta_dito_linee = {0: [], 1: [], 2: [], 3: [], 4: []}

        self.configPlt()
        self.initLunghezza()
        self.initPalmo()
        self.initPunto()
        self.initAngolo() #necessario file ./impostazioni/home.txt
        self.colore=colore


    @staticmethod
    def configPlt():
        plt.axis('off')
        plt.style.use('classic')
        plt.tight_layout()


    def getFig(self):
        return self.fig

    def initAngolo(self):
        f = open(os.path.join(os.getcwd(), "impostazioni", "home.txt"), 'r')
        righe = f.readlines()
        i = 0
        for x in righe:
            if len(x) > 1:
                parte = x.split("=")
                y = parte[1].split("#") #separo i commenti
                k = 0
                for punto in y[0].split(","):
                    self.angolo_t[i][k] = float(punto)
                    k += 1
                i += 1
        f.close()


    def initLunghezza(self):
        f = open(os.path.join(os.getcwd(), "impostazioni", "lunghezza.txt"), 'r')
        righe = f.readlines()
        i = 0
        for x in righe:
            if len(x) > 1:
                parte = x.split("=")
                y = parte[1].split("#")
                k = 0
                for punto in y[0].split(","):
                    self.dl[i][k] = float(punto)
                    # print("i: " + str(i) + " k: " + str(k) + " valore: " + punto)
                    k += 1
                i += 1
        f.close()
        #self.stampaLunghezza()


    def initPalmo(self):
        #TODO: aggiungere try
        f = open(os.path.join(os.getcwd(), "impostazioni", "palmo.txt"), 'r')
        righe = f.readlines()
        i = 0
        for x in righe:
            if len(x)>1:
                parte = x.split("=")
                y=parte[1].split("#")
                k = 0
                for punto in y[0].split(","):
                    self.p[i][k]=float(punto)
                    k += 1
                i += 1
        f.close()

    def initPunto(self):
        f = open(os.path.join(os.getcwd(), "impostazioni", "dita.txt"), 'r')
        righe = f.readlines()
        i = 0
        for x in righe:
            if len(x) > 1:
                parte = x.split("=")
                y = parte[1].split("#")
                k = 0
                for punto in y[0].split(","):
                    self.d[i][k] = punto
                    # print("i: " + str(i) + " k: " + str(k) + " valore: " + punto)
                    k += 1
                i += 1
        f.close()
        # self.stampaDita()



    def visualizzaPosizioneDesiderata(self):
        self.visualizzaPalmo()
        self.visualizzaDito(0)
        self.visualizzaDito(1)
        self.visualizzaDito(2)
        self.visualizzaDito(3)
        self.visualizzaDito(4)


        #plt.show(block=False) #ricorda di mettere in false



    def visualizzaDito(self,i):

        # stampa_dito
        # PUNTO CONNESSIONE AL PALMO
        di0x = self.d[i][0]
        di0y = self.d[i][1]
        di0z = self.d[i][2]


        di1x = di0x #TODO: implementare l'angolo azimutale per le dita ?
        di1y = di0y + self.dl[i][0] * math.cos(math.radians(self.angolo_t[i][0]))
        di1z = di0z - self.dl[i][0] * math.sin(math.radians(self.angolo_t[i][0]))  # metto il segno meno così è rivolto verso il basso

        di2x = di1x
        di2y = di1y + self.dl[i][1] * math.cos(math.radians(self.angolo_t[i][1] + self.angolo_t[i][0]))
        di2z = di1z - self.dl[i][1] * math.sin(math.radians(self.angolo_t[i][1] + self.angolo_t[i][0]))

        di3x = di2x
        di3y = di2y + self.dl[i][2] * math.cos(math.radians(self.angolo_t[i][1] + self.angolo_t[i][0] + self.angolo_t[i][2]+self.angolo_t[i][1]*(70/110)))
        di3z = di2z - self.dl[i][2] * math.sin(math.radians(self.angolo_t[i][1] + self.angolo_t[i][0] + self.angolo_t[i][2]+self.angolo_t[i][1]*(70/110)))
        #TODO: inserire range di angolo in un file (oppure modificabile dalle impostazioni)

        #punti dito
        obj = self.ax.scatter(di0x, di0y, di0z, color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di1x, di1y, di1z, color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di2x, di2y, di2z, color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di3x, di3y, di3z, color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)

        #linee dito
        l1 = self.ax.plot([di0x, di1x], [di0y, di1y], [di0z, di1z], color=self.colore)
        self.raccolta_dito_linee[i].append(l1)
        l2 = self.ax.plot([di1x, di2x], [di1y, di2y], [di1z, di2z], color=self.colore)
        self.raccolta_dito_linee[i].append(l2)
        l3 = self.ax.plot([di3x, di2x], [di3y, di2y], [di3z, di2z], color=self.colore)
        self.raccolta_dito_linee[i].append(l3)

    def visualizzaPalmo(self):
        vertici = [[] * 3] * 5
        for i in range(0,5):
            # stampa i punti
            obj=self.ax.scatter(self.p[i][0],self.p[i][1],self.p[i][2],color=self.colore,s=10)
            self.raccolta_palmo_punti.append(obj)
            #stampa le linee
            obj = self.ax.plot([self.p[i][0], self.p[i - 1][0]],
                               [self.p[i][1], self.p[i - 1][1]],
                               [self.p[i][2], self.p[i - 1][2]], color=self.colore)
            self.raccolta_palmo_linee.append(obj)


            vertici[i].append([self.p[i][0],self.p[i][1],self.p[i][2]])
            #print(vertici[i])

        #print(vertici)
        #self.palmo["palmo"]=self.ax.add_collection3d(Poly3DCollection(vertici, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))



    def eliminaPalmo(self):
        try:
            for x in self.raccolta_palmo_punti:
                x.remove()
        except Exception as e:
            print("Errore palmo punti"+e.__str__())
        try:
            for x in self.raccolta_palmo_linee:
                for y in x:
                    y.remove()
        except Exception as e:
            print("errore  palmo linee: "+e.__str__())
        self.raccolta_palmo_punti.clear()
        self.raccolta_palmo_linee.clear()



    def eliminaTutto(self):
        self.eliminaPalmo()
        self.eliminaDito(0)
        self.eliminaDito(1)
        self.eliminaDito(2)
        self.eliminaDito(3)
        self.eliminaDito(4)



    def eliminaDito(self,i):
        #print("i:" ,i , self.raccolta_dito_linee[i])
        try:
            for x in self.raccolta_dito_punti[i]:
                x.remove()
        except Exception as e:
            print("Errore dito punti: "+e.__str__())
        try:
            for k in self.raccolta_dito_linee[i]:
                for y in k:
                    y.remove()
        except Exception as e:
            print("errore dito linee: "+e.__str__())
        self.raccolta_dito_punti[i].clear()
        self.raccolta_dito_linee[i].clear()




    def setAngolo(self, dito, sezione, valore):
        self.eliminaTutto()
        # TODO: aggiungere controllo dei valori inseriti qui? oppure ci pensa il programma tesi?
        self.angolo_t[dito][sezione] = valore
        self.visualizzaPosizioneDesiderata()


#***************** TEST ********************************
    def stampaPalmo(self):
        print("Punti palmo:")
        for i in range(0, 5):
            print(self.p[i])

    def stampaDita(self):
        print("Punti iniziali dita:")
        for i in range(0, 5):
            print(self.d[i])

    def stampaLunghezza(self):
        print("Lunghezza dita a partire dal pollice:")
        for i in range(0, 5):
            print(self.dl[i])
#***********************************************************




