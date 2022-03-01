#include <stdio.h>
#include <stdlib.h>

void loop(int x) {
  int c = 0, p = 0;
  while (1) {
    if (x <= 0)
      break;
    if (c == 50)
      abort();
    c = c + 1;
    p = p + c;
    x = x - 1;
  }
  if (c == 30)
    abort();
}

int main(int argc, char **argv) {
  int x = 0;
  char str[10];
  fgets(str, 10, stdin);

  x = atoi(str);
  loop(x);

  return 0;
}