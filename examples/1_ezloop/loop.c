#include <stdio.h>

int main(int argc, char **argv) {
  int a = 1, b = 2;
  for (int i = 0; i < 5; i++) {
    if (a)
      printf("a>0");
    if (b) {
      b++;
      b++;
      b++;
      printf("b>0");
    }
  }
  return 0;
}