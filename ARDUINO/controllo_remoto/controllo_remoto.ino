#include <ArduinoJson.h>

/*
COMANDI
? -> Nome scheda e versione programma
start -> avvia il loop (usare flag)
stop -> ferma il loop (usare flag)

delay? -> ritorna il valore del delay, di default 300

delay:500 -> setta il delay




*/

String info="SCHEDA CONTROLLO REMOTO V1.0\n";
int delay_ms=300;
String comando="";

bool next=false;

int teta[5][3];

int adc[5][3];

int offset1=500;
int offset2=500;

void setup() {
    Serial.setTimeout(5); //in questo modo i messaggi sono considerati separati
  Serial.begin(9600);
  while(!Serial){
    }

}

void loop() {

  if(next){
    delay(delay_ms);
    inviaJson();
    next=false;
  }

}




void testGuanto(){
  adc[1][0]=analogRead(A0);
  adc[1][1]=analogRead(A1);
  teta[1][0]=map(adc[1][0],offset1,1023,0,120);//map(value, fromLow, fromHigh, toLow, toHigh)
  teta[1][1]=map(adc[1][1],offset2,0,0,90);//map(value, fromLow, fromHigh, toLow, toHigh)
  
  //pressione=map(pressione_adc,200,1024,0,90);
  //Serial.println("R10:"+String(d10_angolo)); //ricorda di fare il casting
}





void inviaJson(){

  //convertire angolo
  testGuanto();
  StaticJsonDocument<50> doc;
  doc["d1"][0] = teta[1][0];
  doc["d1"][1]  = teta[1][1];
  char json_string[50];
  serializeJson(doc, json_string);  
  Serial.println(json_string);  
}



void serialEvent(){
  comando="";
  comando=Serial.readString();

  if(comando=="?"){
    Serial.println(info);
  }else if(comando=="start"){
      next=true;

  }else if(comando=="next"){
    next=true;

  }else if(comando=="stop"){
      next=false;



  }else if(comando.substring(0,7)=="offset1:"){
    int indice=comando.indexOf(":");
    String new_offset=comando.substring(indice);
    offset1=new_offset.toInt();

    }else if(comando.substring(0,7)=="offset2:"){
    int indice=comando.indexOf(":");
    String new_offset=comando.substring(indice);
    offset2=new_offset.toInt();

  }else if(comando.substring(0,8)=="offset1?"){
    Serial.println(String(offset1));


  }else if(comando.substring(0,8)=="offset2?"){
    Serial.println(String(offset2));


  }else if(comando.substring(0,6)=="delay?"){
    Serial.println(String(delay_ms));
 
  }else if(comando.substring(0,6)=="delay:"){
    int indice=comando.indexOf(":");
    String new_delay=comando.substring(indice+1);
    delay_ms=new_delay.toInt();
  

  }else{

    Serial.println("comando sconosciuto");
    
  }    




}




