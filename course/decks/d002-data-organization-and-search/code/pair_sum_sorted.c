/* Scan PRE-SORTED prices. Sorting is deliberately outside this example.
 * Indices refer to this sorted array, not to the original item numbering.
 * Classroom example: small nonnegative integer prices.
 */
#include <stdio.h>

int main(void)
{
    int price[] = {7, 12, 18, 20, 25, 33};
    int target = 32;
    int n = (int)(sizeof price / sizeof price[0]);
    int left = 0;
    int right = n - 1;
    int checks = 0;

    while (left < right) {
        int sum = price[left] + price[right];
        ++checks;
        if (sum == target) {
            printf("sorted indices: %d, %d\n", left, right);
            printf("prices: %d + %d = %d\n",
                   price[left], price[right], target);
            printf("checks: %d\n", checks);
            return 0;
        }
        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }
    printf("no pair\nchecks: %d\n", checks);
    return 0;
}
