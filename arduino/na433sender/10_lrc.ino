unsigned char LRC(char *input, unsigned int len){
  byte lrc = 0;
  for(unsigned char i=0; i<len; i++){
    lrc += input[i];
  }
  return (lrc ^ 0xFF) + 1;
}
