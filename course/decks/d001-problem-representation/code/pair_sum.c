/* Find any two DISTINCT items whose integer prices sum to target.
 * Classroom example: small, nonnegative integer prices; no input parser.
 * Output indices are zero-based. Array order is preserved.
 */
#include <stdio.h>

int main(void)
{
    int price[] = {18, 7, 25, 12, 33, 20};
    int target = 32;
    int n = (int)(sizeof price / sizeof price[0]);
    int checks = 0;

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            ++checks;
            if (price[i] + price[j] == target) {
                printf("indices: %d, %d\n", i, j);
                printf("prices: %d + %d = %d\n",
                       price[i], price[j], target);
                printf("checks: %d\n", checks);
                return 0;
            }
        }
    }
    printf("no pair\nchecks: %d\n", checks);
    return 0;
}
