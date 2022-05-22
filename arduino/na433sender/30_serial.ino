#include <Arduino.h>


#define SERIAL_BUFFER_SIZE 255





char serial_buffer[SERIAL_BUFFER_SIZE];
unsigned int serial_buffer_write_i = 0;

void serial_buffer_recv_byte(char b){
  if(b == '\n' || b == '\r'){
    serial_buffer[serial_buffer_write_i] = '\0';
    serial_buffer_on_newline(serial_buffer_write_i);
    serial_buffer_write_i = 0;
  } else {
    serial_buffer[serial_buffer_write_i] = b;
    serial_buffer_write_i++;
    if(serial_buffer_write_i >= SERIAL_BUFFER_SIZE){
      serial_buffer_write_i = 0;
      Serial.println("OVERFLOW");
    }
  }
}




void serial_buffer_on_newline(unsigned int len){
  // Only one type of input:
  //
  // 00FF020310110101010101010....0100101FF
  // ^^^^
  // |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  // |   |                               ^^
  // |   |_data            LRC checksum__|
  // |_duration
  //
  // If LRC check successes, play the signal, returns "OK, FF(LRC checksum)"
  // Or return:
  //  - !OVERFLOW, if input buffer has got overflow
  //  - !LRC, if LRC checksum fails
  //  - !INVALID, if command format invalid
  if(len < 6){
    return Serial.println("!INVALID");
  }

  byte lrc_calc = LRC(serial_buffer, len-2);
  byte lrc_recv = parsehex2(serial_buffer+len-2);

  if(lrc_calc ^ lrc_recv){
    Serial.println("!LRC");
    return;
  }

  unsigned long duration = parsehex4(serial_buffer);
  unsigned int o;
  char c;
  
  for(unsigned int i=4; i<len-2; i++){
    o = i-4;
    if(o >= RADIO_BUFFER_SIZE){
      Serial.println("!OVERFLOW");
      break;
    }

    c = parsehexchar(serial_buffer[i]);
    if(c < 0){
      Serial.println("!INVALID");
      radio_buffer_data_size = 0;
      return;
    }

    radio_buffer[o] = c;
    radio_buffer_data_size = o+1;
  }

  radio_set_pulsewidth(duration);
  radio_send_buffer();

  Serial.print("OK,");
  Serial.print(radio_buffer_data_size);
  Serial.print(",");
  Serial.println(duration);

  return;



  /*if(serial_buffer[0] == '+'){
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
  }*/
}
