/* Recursion demo, in two parts.
 * Part 1: factorial(4) with a per-layer trace. Each recursive call
 * prints an indented "enter" line (indentation = stack depth) and a
 * "returns" line with the value, so the class can check the manual
 * trace: frames grow down to factorial(0), then unwind 1,1,2,6,24.
 * Part 2: Tower of Hanoi. hanoi(3) prints all 7 moves; hanoi(4) and
 * hanoi(5) print only the step counts (15 and 31), checking T(n) =
 * 2^n - 1.
 */
#include <stdio.h>

static int depth = 0;   /* current recursion depth, for indentation */
static long steps = 0;  /* hanoi move counter */

static void indent(void)
{
    int i;

    for (i = 0; i < depth; ++i)
        printf("  ");
}

/* n! = n * (n-1)!, with the base case 0! = 1. */
static long factorial(int n)
{
    long result;

    indent();
    printf("enter factorial(%d)\n", n);
    ++depth;
    if (n == 0) {
        result = 1;   /* base case: the exit */
    } else {
        result = n * factorial(n - 1);   /* trust the smaller problem */
    }
    --depth;
    indent();
    printf("factorial(%d) returns %ld\n", n, result);
    return result;
}

/* Move n disks from `from` to `to`, using `aux` as the helper peg.
 * One layer of design: move the n-1 "bundle" away, place the largest
 * disk, move the bundle back. The rest is recursion trust.
 */
static void hanoi(int n, char from, char aux, char to, int verbose)
{
    if (n == 0)
        return;   /* base case: nothing to move */
    hanoi(n - 1, from, to, aux, verbose);
    ++steps;
    if (verbose)
        printf("  step %2ld: move disk %d from %c to %c\n", steps, n, from, to);
    hanoi(n - 1, aux, from, to, verbose);
}

int main(void)
{
    long f4;

    printf("=== Part 1: factorial(4), the stack grows and unwinds ===\n");
    depth = 0;
    f4 = factorial(4);
    printf("factorial(4) = %ld\n", f4);

    printf("\n=== Part 2: Tower of Hanoi ===\n");
    steps = 0;
    printf("hanoi(3): move 3 disks from A to C\n");
    hanoi(3, 'A', 'B', 'C', 1);
    printf("total steps: %ld = 2^3 - 1\n", steps);

    steps = 0;
    hanoi(4, 'A', 'B', 'C', 0);
    printf("hanoi(4): %ld steps = 2^4 - 1\n", steps);

    steps = 0;
    hanoi(5, 'A', 'B', 'C', 0);
    printf("hanoi(5): %ld steps = 2^5 - 1\n", steps);
    return 0;
}
