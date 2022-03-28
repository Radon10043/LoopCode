/*
 * @Author: Radon
 * @Date: 2022-03-28 15:08:33
 * @LastEditors: Radon
 * @LastEditTime: 2022-03-28 17:09:58
 * @Description: Hi, say something
 */
#include <stdio.h>

int main(int arhc, char **argv) {
  int arr[3] = {0};
  scanf("%d %d %d", &arr[0], &arr[1], &arr[2]);

  int i = 0;
  while (i < 3) {
    if (arr[i] < 0)
      printf("arr[%d] is %d, < 0!\n", i, arr[i]);
    else if (arr[i] > 0)
      printf("arr[%d] is %d, > 0!\n", i, arr[i]);
    else
      printf("arr[%d] is 0!\n", i);
    i++;
  }

  switch (arr[0]) {
    case 0:
      printf("arr[0] is 0.\n");
      break;
    case 1:
      printf("arr[0] is 1.\n");
      break;
    case -1:
      printf("arr[0] is -1.\n");
      break;
    default:
      printf("arr[0] is not -1, 0 or 1.\n");
  }

  return 0;
}