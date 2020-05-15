#include <Servo.h>

Servo pan;
Servo tilt;
Servo feeder;

int panPin = 6;
int tiltPin = 9;
int feederPin = 10;

int speedPin = 5;
int in1 = 2;
int in2 = 4;
int potPin = A3;

double currentPanPos = 80;
double currentTiltPos = 50;
double currentFeederPos = 130;

double panServoPos = 80;
double tiltServoPos = 50;
double feederPos = 150;

int panUpperLimit = 170;
int panLowerLimit = 25;

int tiltUpperLimit = 100;
int tiltLowerLimit = 40;

int feederUpperLimit = 130;
int feederLowerLimit = 3;

double panSpeed = 0.025;
double tiltSpeed = 0.025;
double feederSpeed = 0.05;

boolean set = false;

char input = ' ';

int count = 0;

int start = millis();
int endTime = 0;
boolean myBoolean = false;


void setup() {
  // put your setup code here, to run once:
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(13, INPUT);
  pan.attach(panPin);
  tilt.attach(tiltPin);
  feeder.attach(feederPin);
  Serial.begin(9600);

  
}

void loop() {
 start = millis();
 if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("You sent me: ");
    Serial.println(data);
    if (data.indexOf('P') > 0) {
      data.remove(0,2);
      panServoPos = data.toInt();
    }else if (data.indexOf('T') > 0) {
      data.remove(0,2);
      tiltServoPos = data.toInt(); 
    }else if (data.indexOf('F') > 0) {
      data.remove(0,2);
      feederPos = data.toInt(); 
    }

  }

  if (panServoPos > currentPanPos){
    currentPanPos+=panSpeed;
  }else if (panServoPos < currentPanPos) {
    currentPanPos-=panSpeed;
  }
  if (tiltServoPos > currentTiltPos) {
    currentTiltPos+=tiltSpeed;
  }else if (tiltServoPos < currentTiltPos) {
    currentTiltPos-=tiltSpeed;
  }
  if (feederPos > currentFeederPos){
    currentFeederPos+=feederSpeed;
  }else if (feederPos < currentFeederPos) {
    currentFeederPos-=feederSpeed;
  }
  currentTiltPos = constrain(currentTiltPos, tiltLowerLimit, tiltUpperLimit);
  currentPanPos = constrain(currentPanPos, panLowerLimit, panUpperLimit);
  
  delay(1);
  // Lower hard limit of the range of travel is 72
  // Fully Retracted = 150, Fully Engaged = 72
  currentFeederPos = constrain(currentFeederPos, feederLowerLimit, feederUpperLimit);
  feeder.write(currentFeederPos);
  pan.write(round(currentPanPos));
  tilt.write(round(currentTiltPos));
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);

  count+=1;
}
