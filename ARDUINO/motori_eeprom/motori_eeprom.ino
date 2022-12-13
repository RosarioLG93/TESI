#include <Servo.h>
#include <EEPROM.h>
#include <ArduinoJson.h>


/*
 * Autore: Rosario La Greca
 * Descrizione: Programma tesi mano robotica
 * Ultima modifica: 05/11/22
 * Versione: 2.0
*  Info: + lettura eeprom min max angoli
 * 
*/

/*
Divido la memoria in banchi
2 array per limite teta  => 2* [5][3] = 2*15=30 int =>  30*2 byte= 60 byte
 0-99 per array teta
 100 - 199 per fi
 200 - ...  per altro

 Quando considero gli indici, devo sommare questo "offset" (in questo caso solo per gli angoli fi, mettere +100 agli indirizzi addr_h e addr_l)

*/

#define pin_indice 3
String info="VERSIONE 2.0\n";
String angolo="";
String comando="";
int indice_pwm=0;


Servo dito[5][3];

int pin[5][3];

int minValueTeta[5][3];
int maxValueTeta[5][3];

int minValueFi[5]; //da implementare successivamente
int maxValueFi[5]; //da implementare successivamente


int offset[5][3];



void setup(){
  initValori();
  pin[1][0]=3;
  pin[1][1]=5;
  pin[1][2]=6;

  offset[1][0]=30;
  offset[1][1]=0;
  offset[1][2]=0;

  
  Serial.begin(9600,SERIAL_8N1);
  //timeout di defautl 1 secondo
  Serial.setTimeout(5); //in questo modo i messaggi sono considerati separati
  while(!Serial){
    }


  dito[1][0].attach(pin[1][0]);
  dito[1][1].attach(pin[1][1]);
  dito[1][2].attach(pin[1][2]);

  //sistemare con valori iniziali in EEPROM 
  dito[1][0].write(offset[1][0]);
  dito[1][1].write(offset[1][1]);
  dito[1][2].write(offset[1][2]);
}



//------------------------------ LOOP --------------------------------

void loop(){

  //delay(200);
  
}




//---------------------------- SERIAL -------------------

void serialEvent(){
  angolo="";
  comando="";
  comando=Serial.readString();
  Serial.println("Ho ricevuto il comando:"+comando);
  if(comando=="+1"){
    Serial.println("indice +1");
    if(indice_pwm>=255){
      Serial.println("MAX INDICE RAGGIUNTO");
    }else{
      indice_pwm++;
      dito[1][0].write(indice_pwm);
    }
  }else if(comando=="?"){
    Serial.println("SCHEDA MOTORI V1");
  }else if(comando=="test"){
   //giro avanti e indietro
   for(int i=0;i<180;i++){
    dito[1][0].write(i);
    delay(100);
    Serial.println("indice: "+String(i));
   }

   for(int i=180;i>0;i--){
    dito[1][0].write(i);
    delay(100);
    Serial.println("indice: "+String(i));
   }

  }else if(comando.substring(0,4)=="D10:"){
    angolo=comando.substring(4,7);
    Serial.println("Angolo:"+angolo);
    dito[1][0].write(angolo.toInt());
    delay(10);
   }else if(comando.substring(0,4)=="D11:"){
    angolo=comando.substring(4,7);
    Serial.println("Angolo:"+angolo);
    dito[1][1].write(angolo.toInt());
    delay(10);
    

   }else if(comando.substring(0,4)=="D12:"){
    angolo=comando.substring(4,7);
    Serial.println("Angolo:"+angolo);
    dito[1][2].write(angolo.toInt());
    delay(10);


  }else if(comando=="-1"){
    Serial.println("indice -1");
      if(indice_pwm<=0){
        Serial.println("MIN INDICE RAGGIUNTO");
      }else{
        indice_pwm--;
        dito[1][0].write(indice_pwm); 
      }
    
  }else if(comando=="help"){
      Serial.println(info);
    
  }else if(comando.substring(0,5)=="read:"){
    //INVIA TUTTI I VALORI EEPROM
    String n_str=comando.substring(5);
    int n=n_str.toInt();
    leggi(n);
    Serial.println("OK");

  }else if(comando.substring(0,6)=="write:"){
    //INVIA TUTTI I VALORI EEPROM
    //write:8:16
    int indice=comando.substring(6).indexOf(":");
    Serial.println("Indice:"+String(indice));

    String addr_str=comando.substring(6,indice+6);//+6 per la parola "write:"
    String n_str=comando.substring(6+indice+1);
    int addr=addr_str.toInt();
    int value=n_str.toInt();
    scrivi(addr,value);
    Serial.println("OK");
  

  }else if(comando.substring(0,1)=="{"){
    //file json
    //{"d0": [0, 20, 15], "d1": [0, 50, 15], "d2": [0, 20, 15], "d3": [0, 20, 15], "d4": [0, 20, 15]}
    int angolo_des[5][4]; //
    DynamicJsonDocument json(1024);
    deserializeJson(json, comando); //comando in formato json
    angolo_des[1][0]=json["d1"][0];
    angolo_des[1][1]=json["d1"][1];
    angolo_des[1][2]=json["d1"][2];
    //aggiungere verifica valori max e min
    //mappatura dei valori con la funzione map
    dito[1][0].write(angolo_des[1][0]);
    dito[1][1].write(angolo_des[1][1]);
    dito[1][2].write(angolo_des[1][2]);
    Serial.println();




  }else{
    Serial.println("Comando sconosciuto");
  }




  
  
}



//Definire la funzioni 

void initValori(){
  //0 pollice
  //1 indice
  // ....

  /*
  
  */


}

void leggi(int n){
  //ricorda: H1|L1|H2|L2|H3|L3 è in ordine 
  int addr_h=2*n; 
  int addr_l=(2*n)+1;
  byte value_h=EEPROM.read(addr_h);
  byte value_l=EEPROM.read(addr_l);
  int value=word(value_h,value_l);
  Serial.println("Lettura valore "+String(n) + ":"+ String(value));

}

/*
       byte hi = highByte(value);
       byte lw = lowByte(value);
       EEPROM.write(COUNT_ADDR1, hi); 
       EEPROM.write(COUNT_ADDR2,lw); 
       Serial.println("value written on EEPROM");


*/



void scrivi(int n, int value){
  int ADDR_H=2*n;
  int ADDR_L=(2*n)+1;
  Serial.println("Scrivo il valore "+String(value)+" nella variabile numero "+String(n));
  byte value_h=highByte(value);
  byte value_l=lowByte(value);
  EEPROM.write(ADDR_H,value_h);
  EEPROM.write(ADDR_L,value_l);


}
