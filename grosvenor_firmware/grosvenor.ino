#include <Wire.h>
#include "pins.h"

int LeftPWM;                                                  // PWM value for left  motor speed / brake
int RightPWM;
int Leftmode=1;                                              // 0=reverse, 1=brake, 2=forward
int Rightmode=1;  
int count = 0;

long lastupdate;

struct sensor_Data 
{
  uint16_t volts; 
  uint16_t leftamps;
  uint16_t rightamps;  
}sensorValues;

void setup() {
  // put your setup code here, to run once:
  
  pinMode (Charger,OUTPUT);                                   // change Charger pin to output
  digitalWrite (Charger,1);                                   // disable current regulator to charge battery

  //Serial.begin(115200);
  Wire.begin(0x04);                // join i2c bus with address #1
  Wire.onReceive(receiveData); // register event
  Wire.onRequest(sendData);
//  Serial.println("Ready!");

  set_motors();
}

void loop() {
  noInterrupts();
  if ((millis() - lastupdate) > 10000){
    count = 0;
    Leftmode = 1;
    Rightmode = 1;
    set_motors();
  }
  interrupts();
}

void set_motors() {
        switch (Leftmode)                                     // if left motor has not overloaded recently
        {
        case 2:                                               // left motor forward
          analogWrite(LmotorA,0);
          analogWrite(LmotorB,LeftPWM);
          break;

        case 1:                                               // left motor brake
          analogWrite(LmotorA,LeftPWM);
          analogWrite(LmotorB,LeftPWM);
          break;

        case 0:                                               // left motor reverse
          analogWrite(LmotorA,LeftPWM);
          analogWrite(LmotorB,0);
          break;
        }
        switch (Rightmode)                                    // if right motor has not overloaded recently
        {
        case 2:                                               // right motor forward
          analogWrite(RmotorA,0);
          analogWrite(RmotorB,RightPWM);
          break;

        case 1:                                               // right motor brake
          analogWrite(RmotorA,RightPWM);
          analogWrite(RmotorB,RightPWM);
          break;

        case 0:                                               // right motor reverse
          analogWrite(RmotorA,RightPWM);
          analogWrite(RmotorB,0);
          break;
        }

}


void receiveData(int numByte){
  while (Wire.available()) {
    lastupdate = millis();
      if(count == 0){
        Leftmode = Wire.read();
        count++;
        //Serial.print(Leftmode);
        //Serial.println(" - 1st byte received!");
      }
      else if(count == 1){
        LeftPWM = Wire.read();
        count++;
        //Serial.print(LeftPWM);
        //Serial.println(" - 2nd byte received!");
      }
      else if(count == 2){
        Rightmode = Wire.read();
        count++;
        //Serial.print(Rightmode);
        //Serial.println(" - 3rd byte received!");
      }
      else if(count == 3){
        RightPWM = Wire.read();
        //Serial.print(RightPWM);
        //Serial.println(" - 4th byte received!");
        count++;
      }
      else {
        //Serial.print(count);
        //Serial.println("go!");
        Wire.read();
        count = 0;
        set_motors();
      }
  }
}  

// callback for sending data
void sendData(){
  sensorValues.volts = analogRead(Battery); 
  sensorValues.leftamps = analogRead(LmotorC);
  sensorValues.rightamps = analogRead(RmotorC);
  int len = sizeof(struct sensor_Data);
  char values[len];
  memcpy(values, &sensorValues, len);
  Wire.write(values, len);
}

