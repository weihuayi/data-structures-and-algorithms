/* Sequential stack demo: push/pop trace plus bracket matching.
 * The stack is an array with an index top; the invariant is
 * "top always points at the youngest element".
 * Two strings are checked so the class can verify its predictions:
 *   - "({[}]"  must be reported mismatched (at the 4th character);
 *   - "({[]})" must be reported matched.
 */
#include <stdio.h>

#define MAX 100

static char stack[MAX];
static int top = -1;   /* invariant: top indexes the youngest element */

static int is_empty(void)
{
    return top == -1;
}

static void push(char c)
{
    stack[++top] = c;
    printf("  push '%c'  stack: %.*s\n", c, top + 1, stack);
}

static char pop(void)
{
    char c = stack[top--];
    printf("  pop  '%c'  stack: %.*s\n", c, top + 1, stack);
    return c;
}

/* The right bracket that a left bracket expects. */
static char expected_close(char left)
{
    switch (left) {
    case '(':
        return ')';
    case '{':
        return '}';
    case '[':
        return ']';
    }
    return '\0';
}

/* Check the bracket string s; returns 1 if matched, 0 if not. */
static int check_brackets(const char *s)
{
    int i;

    top = -1;   /* start with an empty stack */
    printf("checking \"%s\":\n", s);
    for (i = 0; s[i] != '\0'; ++i) {
        char c = s[i];

        if (c == '(' || c == '{' || c == '[') {
            push(c);
        } else {
            char left;

            if (is_empty()) {
                printf("  position %d: '%c' has no left bracket -> MISMATCH\n",
                       i + 1, c);
                return 0;
            }
            left = pop();
            if (expected_close(left) != c) {
                printf("  position %d: '%c' cannot close '%c' -> MISMATCH\n",
                       i + 1, c, left);
                return 0;
            }
            printf("  '%c' closes '%c' -- ok\n", c, left);
        }
    }
    if (!is_empty()) {
        printf("  %d left bracket(s) never closed -> MISMATCH\n", top + 1);
        return 0;
    }
    printf("  every bracket found its partner -> MATCHED\n");
    return 1;
}

int main(void)
{
    printf("=== push/pop trace: the youngest element leaves first ===\n");
    push('A');
    push('B');
    push('C');
    printf("pop gives '%c' (not 'A'): this is LIFO\n", pop());

    printf("\n=== bracket matching with a stack ===\n");
    check_brackets("({[}]");
    printf("\n");
    check_brackets("({[]})");
    return 0;
}
