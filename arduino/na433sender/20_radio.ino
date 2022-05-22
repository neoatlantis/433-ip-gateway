/*
 * Radio sending control
 * 
 * Radio signal sent by 433 MHz module is controlled here.
 * 
 * The signal is specified via serial input, and stored in radio_buffer with
 * maximal RADIO_BUFFER_SIZE bytes.
 * 
 * Each byte corresponds to a single value of 0-15, where if the actual value
 * ranges between 0 - 7, it's sent as a LOW. With 8-15 the signal is a HIGH.
 * 
 * The actual value is the multiplicating factor for the actual duration of
 * that signal. A basic signal duration is set by function radio_set_pulsewidth
 * in microseconds (0-65535 us). This basical duration, multiplied by the value
 * of each byte (1-8), gives the actual sent duration:
 * 
 * Byte value       Output level    Duration factor
 * 0                Low             1
 * 1                Low             2
 * ..               Low
 * 7                Low             8
 * 8                High            1
 * 9                High            2
 * ..               High
 * 15               High            8
 * 
 * This design enables sending signals of different modulation.
 */


#define RADIO_BUFFER_SIZE  255

byte radio_buffer[RADIO_BUFFER_SIZE];
static unsigned int radio_buffer_data_size = 0;
static unsigned int radio_pulse_width = 0;

void radio_silence(){
  digitalWrite(RADIO_PIN, LOW);
}

/*void radio_send_sync(){
  digitalWrite(RADIO_PIN, HIGH);
  delayMicroseconds(PULSE_UNIT);
  digitalWrite(RADIO_PIN, LOW);
  delayMicroseconds(PULSE_UNIT * 10);
}*/

void radio_set_pulsewidth(unsigned int i){
  radio_pulse_width = i;
}

void radio_send_1(char pulse_duration){
  digitalWrite(RADIO_PIN, HIGH);
  delayMicroseconds(radio_pulse_width * pulse_duration);
  digitalWrite(RADIO_PIN, LOW);
}

void radio_send_0(char pulse_duration){
  digitalWrite(RADIO_PIN, LOW);
  delayMicroseconds(radio_pulse_width * pulse_duration);
}

void radio_send_buffer_once(){
  unsigned int i = 0;
  for(i=0; i<radio_buffer_data_size; i++){
    if(radio_buffer[i] < 8){
      radio_send_0((radio_buffer[i] & 0x0F)+1);
    } else {
      radio_send_1((radio_buffer[i] & 0x0F)-7);
    }
  }
  radio_silence();
}

void radio_send_buffer(){
  unsigned int i = 0;
  for(i=0; i<6; i++){
    radio_send_buffer_once();
    delay(10);
  }
}
