
#include <ArduinoJson.h>
/*
COMANDI
? -> Nome scheda e versione programma
start -> avvia il loop (usare flag)
stop -> ferma il loop (usare flag)

delay? -> ritorna il valore del delay, di default 300

delay:500 -> setta il delay 



set_offset:200 , il valore di offset



*/

#define s1 A0


String info="SCHEDA PRESSIONE V1.0\n";
int delay_ms=300;
String comando="";
bool start=false;
volatile bool next=false;
int pressione[15];

int offset=500;



void setup() {

    Serial.begin(9600,SERIAL_8N1);
  //timeout di defautl 1 secondo
  Serial.setTimeout(5); //in questo modo i messaggi sono considerati separati
  while(!Serial){
    }

}

void loop() {
 if(next){
   delay(delay_ms);
   inviaPressione();
   next=false;
  }

  

}

void inviaPressione(){
  int  adc_value=analogRead(s1);
  pressione[0]=adc_value-offset;
  if(pressione[0]<0){
    pressione[0]=0;
  }
  StaticJsonDocument<50> doc;
  doc["s1"]=pressione[0];
  //formato json utile per inserire tutti gli altri sensori
  //Serial.println("s1:"+String(pressione[0]))
  //serializeJson(doc, Serial);  
  char json_string[50];
  serializeJson(doc, json_string);
  Serial.println(json_string);  

}


void serialEvent(){
  comando="";
  comando=Serial.readString();

  if(comando=="?"){
    Serial.println(info);
   }else if(comando=="next"){
      next=true;

  }else if(comando=="start"){
    next=true;
  }else if(comando=="stop"){
      next=false;

  }else if(comando.substring(0,6)=="delay:"){
    int indice=comando.indexOf(":");
    String new_delay=comando.substring(indice+1);
    delay_ms=new_delay.toInt();
  

  }else if(comando.substring(0,6)=="offset:"){
    int indice=comando.indexOf(":");
    String new_offset=comando.substring(indice);
    offset=new_offset.toInt();

  }else if(comando.substring(0,7)=="offset?"){
    Serial.println(String(offset));

  }else if(comando.substring(0,6)=="delay?"){
    Serial.println(String(delay_ms));
  }else{

    Serial.println("comando sconosciuto");
  }



}

