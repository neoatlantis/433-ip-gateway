const int RADIO_PIN = 13;
const int PULSE_UNIT = 270;


void(* resetFunc) (void) = 0;//declare reset function at address 0




const int RADIO_BUFFER_SIZE = 255;
byte radio_buffer[RADIO_BUFFER_SIZE] = {};
unsigned int radio_buffer_data_size = 0;

void radio_silence(){
  digitalWrite(RADIO_PIN, LOW);
}

void radio_send_sync(){
  digitalWrite(RADIO_PIN, HIGH);
  delayMicroseconds(PULSE_UNIT);
  digitalWrite(RADIO_PIN, LOW);
  delayMicroseconds(PULSE_UNIT * 10);
}

void radio_send_short(){
  digitalWrite(RADIO_PIN, HIGH);
  delayMicroseconds(PULSE_UNIT);
  digitalWrite(RADIO_PIN, LOW);
  delayMicroseconds(PULSE_UNIT);
}

void radio_send_long(){
  digitalWrite(RADIO_PIN, HIGH);
  delayMicroseconds(PULSE_UNIT);
  digitalWrite(RADIO_PIN, LOW);
  delayMicroseconds(PULSE_UNIT * 5);
}

void radio_send_buffer_once(){
  unsigned int i = 0;
  radio_send_sync();
  for(i=0; i<radio_buffer_data_size; i++){
    if(radio_buffer[i] & 0x01){
      radio_send_short();
    } else {
      radio_send_long();
    }
  }
  radio_send_long();
  radio_silence();
}

void radio_send_buffer(){
  unsigned int i = 0;
  for(i=0; i<6; i++){
    radio_send_buffer_once();
    delay(10);
  }
}




const int SERIAL_BUFFER_SIZE = 255;
char serial_buffer[SERIAL_BUFFER_SIZE];
unsigned int serial_buffer_write_i = 0;

void serial_buffer_recv_byte(char b){
  if(b == '\n' || b == '\r'){
    serial_buffer[serial_buffer_write_i] = '\0';
    serial_buffer_on_newline();
    serial_buffer_write_i = 0;
  } else {
    serial_buffer[serial_buffer_write_i] = b;
    serial_buffer_write_i++;
    if(serial_buffer_write_i >= SERIAL_BUFFER_SIZE){
      serial_buffer_write_i = 0;
      Serial.println("! overflow");
    }
  }
}

void serial_buffer_on_newline(){
  Serial.print("# ");
  Serial.println(serial_buffer);

  if(serial_buffer[0] == '>'){
    radio_send_buffer();
    Serial.println(">OK");
    return;
  }

  if(serial_buffer[0] == '+'){
    // replace serial buffer with 0 and 1s
    unsigned int i, o;
    for(unsigned int i=1; i<SERIAL_BUFFER_SIZE; i++){
      if(0 == serial_buffer[i]) break;
      o = i-1;
      if(o >= RADIO_BUFFER_SIZE){
        Serial.println("+OVERFLOW");
        break;
      }
      if(serial_buffer[i] == '0'){
        radio_buffer[o] = 0;
      } else if (serial_buffer[i] == '1'){
        radio_buffer[o] = 1;
      } else {
        Serial.println("+ERROR");
        radio_buffer_data_size = 0;
      }
      radio_buffer_data_size = i;
    }
    Serial.print("+");
    Serial.println(radio_buffer_data_size);
    return;
  }

  if(serial_buffer[0] == '?'){
    Serial.print("? NA433GATEWAY ");
    for(unsigned int i=0; i<radio_buffer_data_size; i++){
      Serial.print(radio_buffer[i]);
    }
    Serial.print("\n");
    return;
  }

  if(serial_buffer[0] == 'R'){
    resetFunc();
  }
}













void setup() {
  pinMode(RADIO_PIN, OUTPUT);    // sets the digital pin as output
  Serial.begin(9600);
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
