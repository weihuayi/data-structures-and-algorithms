/* Print the real address of every array element and check the address
 * formula LOC(a_i) = base + (i - 1) * L against the actual layout.
 * Classroom protocol: predict first, then run, then check.
 */
#include <stdio.h>

int main(void)
{
    int a[8] = {101, 103, 105, 107, 109, 111, 113, 115};
    double b[4] = {1.0, 2.0, 3.0, 5.0};
    size_t i;

    printf("=== int a[8], sizeof(int) = %zu bytes ===\n", sizeof(int));
    printf("base = &a[0] = %p\n", (void *)&a[0]);
    for (i = 0; i < 8; ++i) {
        long offset = (char *)&a[i] - (char *)&a[0];
        printf("&a[%zu] = %p   offset = %2ld bytes = %ld x sizeof(int)\n",
               i, (void *)&a[i], offset, offset / (long)sizeof(int));
    }
    printf("prediction: &a[3] - &a[0] = 3 x %zu = %zu bytes\n",
           sizeof(int), 3 * sizeof(int));

    printf("\n=== double b[4], sizeof(double) = %zu bytes ===\n",
           sizeof(double));
    printf("base = &b[0] = %p\n", (void *)&b[0]);
    for (i = 0; i < 4; ++i) {
        long offset = (char *)&b[i] - (char *)&b[0];
        printf("&b[%zu] = %p   offset = %2ld bytes = %ld x sizeof(double)\n",
               i, (void *)&b[i], offset, offset / (long)sizeof(double));
    }

    printf("\ncheck: adjacent addresses differ by exactly sizeof(type);\n");
    printf("the formula gives each address with one multiply and one add.\n");
    return 0;
}
