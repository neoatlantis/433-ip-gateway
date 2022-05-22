#define RADIO_PIN          13



void(* resetFunc) (void) = 0;//declare reset function at address 0























void setup() {
  pinMode(RADIO_PIN, OUTPUT);    // sets the digital pin as output
  Serial.begin(115200);
  radio_silence();
}

void loop() {
  /*digitalWrite(ledPin, HIGH); // sets the LED on
  delay(10);                // waits for a second
  digitalWrite(ledPin, LOW);  // sets the LED off
  delay(10);                // waits for a second*/
  int serial_byte = -1;
  serial_byte = Serial.read();
  if(serial_byte >= 0){
    // Serial.write(serial_byte); // echo back
    serial_buffer_recv_byte(serial_byte & 0xFF);
  }

  radio_silence();
}
