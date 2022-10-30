import matplotlib.pyplot as plt
import numpy as np
import os
import math

class ManoPressione():

    def __init__(self, nome, dimensione=600):
        self.dl = np.array([[0] * 3] * 5, dtype='f')  # lascio le 3 dimensioni per usare lo stesso file

        self.d = np.array([[0] * 3] * 5, dtype='f')  # per usare lo stesso file
        self.raccolta_dito_punti = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.raccolta_dito_linee = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.dimensione = dimensione
        self.colore = 'b'
        self.nome = nome
        self.angolo = 135  # 45+90
        self.sensore = [[] * 3, []] * 5  # per grafico x e y
        # ------------------------------------------------------
        self.raccolta_sensori_punti = []
        self.raccolta_sensori_text = []
        self.sensore_valore = [0.2] * 15
        # -------------------------------------------------------
        # raccolta oggetti (servono per fare .remove())
        self.raccolta_palmo_punti = []
        self.raccolta_palmo_linee = []

        self.p = np.array([[0] * 3] * 5, dtype='f')

        self.fig = plt.figure(nome, figsize=(3.0, 3.0))
        self.ax = self.fig.add_subplot()
        self.ax.set(xlim=(-2, 10), ylim=(0, 15))
        # plt.style.use('classic')
        plt.axis('off')
        self.fig.set_facecolor("white")
        plt.tight_layout()

        self.initLunghezza()
        self.initPunto()
        self.initPuntiPressione()
        self.initPalmo()
        self.mostraMappa()


    def mostraMappa(self):
        self.mostraPalmo()
        self.mostraPollice()

        for i in range(1, 5):
            self.mostraDito(i)
        self.mostraSensori()

    def getFig(self):
        return self.fig


    def initPalmo(self):

        f = open(os.path.join(os.getcwd(), "impostazioni", "palmo.txt"), 'r')
        righe = f.readlines()
        i = 0
        for x in righe:
            if len(x) > 1:
                parte = x.split("=")
                y = parte[1].split("#")
                k = 0
                for punto in y[0].split(","):
                    self.p[i][k] = float(punto)
                    k += 1
                i += 1
        f.close()

    def mostraPalmo(self):
        #vertici = [[] * 3] * 5
        for i in range(0,5):
            # stampa i punti
            obj=self.ax.scatter(self.p[i][0],self.p[i][1],color=self.colore,s=10)
            self.raccolta_palmo_punti.append(obj)
            #stampa le linee
            obj = self.ax.plot([self.p[i][0], self.p[i - 1][0]],
                               [self.p[i][1], self.p[i - 1][1]], color=self.colore)
            self.raccolta_palmo_linee.append(obj)




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

    def initPuntiPressione(self):
        f=open(os.path.join(os.getcwd(),"impostazioni","punti_pressione.txt"),'r')
        righe=f.readlines()
        for x in righe:
            if len(x)>1: #in questo modo salto le righe vuote
                parte= x.split("=")
                y=parte[1].split("#")
                i=0
                for punto in y[0].split(","):

                    self.sensore[i].append(float(punto))
                    i+=1
        f.close()




    def mostraSensori(self):
        for i in range(0,len(self.sensore[0])): #self.sensore[0] è l'insieme di TUTTE le coordinate x
            #anche il punto è una lista
            print(self.sensore[0][i],self.sensore[1][i])
            obj=self.ax.scatter(self.sensore[0][i],self.sensore[1][i],s=self.dimensione, edgecolor='black' , facecolor='maroon', alpha=float(self.sensore_valore[i])/1200.0)
            self.raccolta_sensori_punti.append(obj)
            obj=self.ax.text(self.sensore[0][i],self.sensore[1][i]-0.2,str(i))
            self.raccolta_sensori_text.append(obj)
            #s=self.dimensione, edgecolor='black' , facecolor='maroon', alpha=0.8


    def aggiornaSensore(self,i,valore):
        #TODO: scegliere i riferimenti per i sensori con indici
        #per adesso supponiamo che in sensori sono interi (visto che è un unica lista)
        self.sensore_valore[i]=valore #0-1024
        self.aggiornaMappa()



    def aggiornaMappa(self):
        self.eliminaTutto()
        self.mostraMappa()


    def eliminaSensori(self):

        for x in self.raccolta_sensori_punti:
            try:
                x.remove()
            except:
                pass
        for y in self.raccolta_sensori_text:
            try:
                y.remove()
            except:
                pass
        self.raccolta_sensori_text.clear()
        self.raccolta_sensori_punti.clear()



    def mostraDito(self,i):

        di0x = self.d[i][0]
        di0y = self.d[i][1]


        di1x = di0x
        di1y = di0y + self.dl[i][0]

        di2x = di1x
        di2y = di1y + self.dl[i][1]

        di3x = di2x
        di3y = di2y + self.dl[i][2]

        # punti dito
        obj = self.ax.scatter(di0x, di0y,  color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di1x, di1y, color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di2x, di2y,color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)
        obj = self.ax.scatter(di3x, di3y,color='b', s=10)
        self.raccolta_dito_punti[i].append(obj)

        # linee dito
        l1 = self.ax.plot([di0x, di1x], [di0y, di1y], color='b')
        self.raccolta_dito_linee[i].append(l1)
        l2 = self.ax.plot([di1x, di2x], [di1y, di2y], color='b')
        self.raccolta_dito_linee[i].append(l2)
        l3 = self.ax.plot([di3x, di2x], [di3y, di2y], color='b')
        self.raccolta_dito_linee[i].append(l3)


    def mostraPollice(self):
        d00x = self.d[0][0]
        d00y = self.d[0][1]

        d01x = d00x+self.dl[0][0]*math.cos(math.radians(self.angolo))
        d01y = d00y+self.dl[0][0]*math.sin(math.radians(self.angolo))

        d02x = d01x
        d02y = d01y + self.dl[0][1]

        di3x = d02x
        di3y = d02y + self.dl[0][2]

        # punti dito
        obj = self.ax.scatter(d00x, d00y, color='b', s=10)
        self.raccolta_dito_punti[0].append(obj)
        obj = self.ax.scatter(d01x, d01y,  color='b', s=10)
        self.raccolta_dito_punti[0].append(obj)
        obj = self.ax.scatter(d02x, d02y,  color='b', s=10)
        self.raccolta_dito_punti[0].append(obj)
        obj = self.ax.scatter(di3x, di3y, color='b', s=10)
        self.raccolta_dito_punti[0].append(obj)

        # linee dito
        l1 = self.ax.plot([d00x, d01x], [d00y, d01y], color=self.colore)
        self.raccolta_dito_linee[0].append(l1)
        l2 = self.ax.plot([d01x, d02x], [d01y, d02y], color=self.colore)
        self.raccolta_dito_linee[0].append(l2)
        l3 = self.ax.plot([di3x, d02x], [di3y, d02y], color=self.colore)
        self.raccolta_dito_linee[0].append(l3)


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
        self.eliminaSensori()


