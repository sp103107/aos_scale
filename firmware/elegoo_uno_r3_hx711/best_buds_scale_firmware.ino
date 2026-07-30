#include "HX711.h"
#define HX_DOUT 2
#define HX_SCK 3
#define MAX_COMMAND 80
HX711 scale;
char commandBuffer[MAX_COMMAND + 1];
uint8_t commandLength = 0;
bool streaming = false;
bool scaleReady = false;
float calibrationFactor = 1.0f;
const char* firmwareVersion = "0.1.3";
const char* deviceId = "BBWS-USB-001";
const unsigned long streamIntervalMs = 150;
unsigned long lastStreamMs = 0;
void ack(const char* cmd,const char* status){ Serial.print("A,");Serial.print(cmd);Serial.print(",");Serial.println(status); }
void errorLine(const char* code,const char* msg){ Serial.print("E,");Serial.print(code);Serial.print(",");Serial.println(msg); }
void statusLine(){ Serial.print("S,");Serial.print(firmwareVersion);Serial.print(",");Serial.print(deviceId);Serial.print(",");Serial.print(calibrationFactor,6);Serial.println(",g"); }
bool waitHx711Ready(unsigned long timeoutMs){
  unsigned long start=millis();
  while((millis()-start)<timeoutMs){
    if(scale.is_ready()){return true;}
    delay(2);
  }
  return scale.is_ready();
}
bool ensureScale(){
  if(scaleReady){return true;}
  // begin(..., doReset=false) avoids Tillaart reset()->read() hang when HX711 is absent/unready.
  scale.begin(HX_DOUT,HX_SCK,false,false);
  scale.set_scale(calibrationFactor);
  scaleReady = true;
  return true;
}
void weightLine(){
  ensureScale();
  if(!waitHx711Ready(400)){errorLine("HX711_NOT_READY","sensor unavailable");return;}
  long raw=(long)scale.read_average(5);
  float grams=scale.get_units(5);
  Serial.print("W,");Serial.print(millis());Serial.print(",");Serial.print(raw);Serial.print(",");Serial.print(grams,3);Serial.println(",1");
}
void processCommand(char* cmd){
  if(strcmp(cmd,"PING")==0){Serial.println("A,PONG");}
  else if(strcmp(cmd,"STATUS")==0){statusLine();}
  else if(strcmp(cmd,"TARE")==0){
    ensureScale();
    if(!waitHx711Ready(600)){errorLine("HX711_NOT_READY","tare rejected");}
    else{scale.tare(10);ack("TARE","OK");}
  }
  else if(strcmp(cmd,"READ")==0){weightLine();}
  else if(strcmp(cmd,"STREAM_ON")==0){streaming=true;ack("STREAM_ON","OK");}
  else if(strcmp(cmd,"STREAM_OFF")==0){streaming=false;ack("STREAM_OFF","OK");}
  else if(strncmp(cmd,"SET_CAL,",8)==0){
    float f=atof(cmd+8);
    if(f==0.0f){errorLine("BAD_CAL","factor must be nonzero");}
    else{
      calibrationFactor=f;
      if(scaleReady){scale.set_scale(calibrationFactor);}
      ack("SET_CAL","OK");
    }
  }
  else if(strcmp(cmd,"SET_UNIT,g")==0){ack("SET_UNIT","OK");}
  else if(strncmp(cmd,"SET_UNIT,",9)==0){errorLine("UNSUPPORTED_UNIT","firmware output remains grams");}
  else{errorLine("BAD_COMMAND","unknown or malformed command");}
}
void setup(){
  Serial.begin(115200);
  // Keep setup non-blocking so PING/STATUS work even if HX711 wiring is incomplete.
  ensureScale();
}
void loop(){
 while(Serial.available()>0){
   char c=(char)Serial.read();
   if(c=='\r')continue;
   if(c=='\n'){
     commandBuffer[commandLength]='\0';
     if(commandLength>0)processCommand(commandBuffer);
     commandLength=0;
   }else if(commandLength<MAX_COMMAND){
     commandBuffer[commandLength++]=c;
   }else{
     commandLength=0;
     errorLine("LINE_TOO_LONG","command rejected");
   }
 }
 if(streaming && millis()-lastStreamMs>=streamIntervalMs){
   lastStreamMs=millis();
   weightLine();
 }
}
