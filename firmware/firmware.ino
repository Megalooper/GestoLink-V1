int leds[] = {2, 3, 4, 5, 6};

void setup() {
  Serial.begin(9600);
  for(int i = 0; i < 5; i++) pinMode(leds[i], OUTPUT);
}

void loop() {
  if (Serial.available() >= 5) {
    for (int i = 0; i < 5; i++) {
      char estado = Serial.read();
      digitalWrite(leds[i], (estado == '1') ? HIGH : LOW);
    }
    while(Serial.available() > 0) Serial.read(); // Limpiar buffer
  }
}