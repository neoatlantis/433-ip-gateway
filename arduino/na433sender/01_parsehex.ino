char parsehexchar(char c){
  if('0' <= c && c <= '9') return c - '0';
  if('a' <= c && c <= 'f') return 10 + c - 'a';
  if('A' <= c && c <= 'F') return 10 + c - 'A';
  return -1;  
}



unsigned long parsehex4(char *str){
  char c3 = parsehexchar(str[0]);
  char c2 = parsehexchar(str[1]);
  char c1 = parsehexchar(str[2]);
  char c0 = parsehexchar(str[3]);

  if(c0 < 0 || c1 < 0 || c2 < 0 || c3 < 0) return -1;
  return (c3 << 12) | (c2 << 8) | (c1 << 4) | c0;
}

unsigned long parsehex2(char *str){
  char c1 = parsehexchar(str[0]);
  char c0 = parsehexchar(str[1]);

  if(c1 < 0 || c0 < 0) return -1;
  return (c1 << 4) | c0;
}
