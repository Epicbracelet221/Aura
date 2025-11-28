#include <Servo.h>

Servo s[12];
int pins[12] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
int rev[12] = { 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0 };
int homeAngle[12] = { 90, 120, 60, 90, 120, 60, 90, 60, 150, 90, 120, 60 };

#define TRIG A0
#define ECHO A1

String currentCmd = "stop";
unsigned long lastTelemetry = 0;
int currentDistance = 100;

void checkSerial() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); 
    if (cmd.length() > 0) {
      currentCmd = cmd;
      Serial.print("CMD RECV: ");
      Serial.println(currentCmd);
    }
  }
}


void moveServo(int id, int angle) {
  if (rev[id] == 1) angle = 180 - angle;
  s[id].write(angle);
}

void setLeg(int leg, int coxa, int femur, int tibia) {
  int base = leg * 3;
  moveServo(base + 0, coxa);
  moveServo(base + 1, femur);
  moveServo(base + 2, tibia);
}

void stand() {
  for (int i = 0; i < 12; i++) {
    moveServo(i, homeAngle[i]);
  }
  delay(10);
}


void liftLeg(int leg) {
  setLeg(leg, homeAngle[leg * 3 + 0],
         homeAngle[leg * 3 + 1] - 25,
         homeAngle[leg * 3 + 2] + 25);
}

void dropLeg(int leg) {
  setLeg(leg, homeAngle[leg * 3 + 0],
         homeAngle[leg * 3 + 1],
         homeAngle[leg * 3 + 2]);
}


void stepForward(int leg) {
  liftLeg(leg); delay(80);

  setLeg(leg, homeAngle[leg * 3 + 0] + 30,
         homeAngle[leg * 3 + 1] - 25,
         homeAngle[leg * 3 + 2] + 25);
  delay(80);
  dropLeg(leg);
  delay(80);
}

void stepBackward(int leg) {
  liftLeg(leg); delay(80);
  setLeg(leg, homeAngle[leg * 3 + 0] - 30,
         homeAngle[leg * 3 + 1] - 25,
         homeAngle[leg * 3 + 2] + 25);
  delay(80);
  dropLeg(leg);
  delay(80);
}

void stepTurn(int leg, int angleOffset) {
  liftLeg(leg); delay(80);
  setLeg(leg, homeAngle[leg * 3 + 0] + angleOffset,
         homeAngle[leg * 3 + 1] - 25,
         homeAngle[leg * 3 + 2] + 25);
  delay(80);
  dropLeg(leg);
  delay(80);
}


void walkForward() {
  if(currentDistance < 20 && currentDistance > 0) {
    stand();
    currentCmd = "stop";
    return;
  }
  
  stepForward(0); checkSerial(); if (currentCmd != "forward") return;
  stepForward(2); checkSerial(); if (currentCmd != "forward") return;
  stepForward(1); checkSerial(); if (currentCmd != "forward") return;
  stepForward(3);
}

void walkBackward() {
  stepBackward(0); checkSerial(); if (currentCmd != "back") return;
  stepBackward(2); checkSerial(); if (currentCmd != "back") return;
  stepBackward(1); checkSerial(); if (currentCmd != "back") return;
  stepBackward(3);
}

void turnLeft() {
  
  stepTurn(0, 30);  checkSerial(); if (currentCmd != "left") return; 
  stepTurn(1, -30); checkSerial(); if (currentCmd != "left") return;
  stepTurn(2, 30);  checkSerial(); if (currentCmd != "left") return;
  stepTurn(3, -30); 
}

void turnRight() {
  
  stepTurn(0, -30); checkSerial(); if (currentCmd != "right") return;
  stepTurn(1, 30);  checkSerial(); if (currentCmd != "right") return;
  stepTurn(2, -30); checkSerial(); if (currentCmd != "right") return;
  stepTurn(3, 30);
}


int getDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  long dur = pulseIn(ECHO, HIGH, 25000); 
  int d = dur * 0.034 / 2;
  
  if (d == 0 || d > 400) return 0; 
  return d;
}


void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  
  for (int i = 0; i < 12; i++) {
    s[i].attach(pins[i]);
    delay(10);
  }
  stand();
  Serial.println("Robot Ready");
}

void loop() {
  checkSerial();

  if (millis() - lastTelemetry >= 150) {
    int dist = getDistance();
    Serial.print("DIST:");
    Serial.println(dist);
    
    if (dist > 0) {
      currentDistance = dist; 
    }
    lastTelemetry = millis();
  }

  if (currentCmd == "forward") walkForward();
  else if (currentCmd == "back") walkBackward();
  else if (currentCmd == "left") turnLeft();
  else if (currentCmd == "right") turnRight();
  else {
    stand();
  }
}