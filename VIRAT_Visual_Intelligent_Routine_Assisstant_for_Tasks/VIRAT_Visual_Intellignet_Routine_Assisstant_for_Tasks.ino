//V.I.R.A.T. (Visual Intelligent Routine Assistant for Tasks)

#define pirSensorPin 12
#define ledPin1 14
#define ledPin2 13
#define buttonPin 27

bool ledState = false;
bool motionDetected = false;
bool studyMode = false;

unsigned long lastMotionTime = 0;
const unsigned long cooldown = 10000;  // 10 seconds cooldown for motion

const int calibrationTime = 10;

void setup() {
  pinMode(pirSensorPin, INPUT);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); // Button with internal pull-up
  Serial.begin(115200);

  Serial.println("Calibrating sensor...");
  for (int i = 0; i < calibrationTime; i++) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nSensor calibrated. Ready!");
}

void loop() {
  int pirValue = digitalRead(pirSensorPin);
  int buttonState = digitalRead(buttonPin);

  unsigned long now = millis();

  // Allow study mode only if lights are ON
  if (buttonState == LOW && ledState && !studyMode) {
    studyMode = true;
    Serial.println("Button pressed - Entering Study Mode");
    delay(500); // Debounce
  }

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "LIGHT ON") {
      digitalWrite(ledPin1, HIGH);
      digitalWrite(ledPin2, HIGH);
      ledState = true;
      Serial.println("LED manually turned ON");
    } else if (command == "BLINK") {
      for (int i = 0; i < 5; i++) {
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        delay(300);
        digitalWrite(ledPin1, HIGH);
        digitalWrite(ledPin2, HIGH);
        delay(300);
      }
      Serial.println("LED blinked for task completion");
      studyMode = false;
      ledState = true; // Keep lights ON after blink unless reset manually
    }
  }

  // Normal motion detection when not in study mode
  if (!studyMode) {
    if (pirValue == HIGH && (now - lastMotionTime > cooldown)) {
      ledState = !ledState;
      digitalWrite(ledPin1, ledState);
      digitalWrite(ledPin2, ledState);
      Serial.println("Motion detected ON");
      lastMotionTime = now;
    }
  }

  delay(10);
}
