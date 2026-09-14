/* Linked nodes for the polynomial 3x^2 + 2x + 1.
 * Each term lives in its own malloc'd node; next pointers form the chain.
 * Prints every node's address so the class can check the prediction
 * "malloc'd nodes are NOT neighbours in memory" -- the counterpart of
 * D003's addr_demo.c, where array elements always are.
 * Same classroom protocol: predict first, run, then check.
 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int coef;
    int exp;
    struct Node *next;
} Node;

static Node *new_term(int coef, int exp)
{
    Node *p = malloc(sizeof(Node));

    if (p == NULL) {
        printf("malloc failed\n");
        exit(1);
    }
    p->coef = coef;
    p->exp = exp;
    p->next = NULL;
    return p;
}

int main(void)
{
    Node *a = new_term(3, 2);   /* 3x^2 */
    Node *b = new_term(2, 1);   /* 2x   */
    Node *c = new_term(1, 0);   /* 1    */
    Node *p;

    printf("sizeof(Node) = %zu bytes\n\n", sizeof(Node));
    printf("addresses of the three nodes (prediction: NOT adjacent):\n");
    printf("  3x^2 lives at %p\n", (void *)a);
    printf("  2x   lives at %p\n", (void *)b);
    printf("  1    lives at %p\n", (void *)c);

    printf("\nlink them: a->next = b; b->next = c; c->next stays NULL\n");
    a->next = b;
    b->next = c;

    printf("\nwalk the chain from the head:\n");
    for (p = a; p != NULL; p = p->next) {
        printf("  at %p: coef = %d, exp = %d\n", (void *)p, p->coef, p->exp);
    }

    printf("\nfree every node (memory responsibility):\n");
    p = a;
    while (p != NULL) {
        Node *victim = p;

        p = p->next;
        printf("  free node at %p\n", (void *)victim);
        free(victim);
    }

    return 0;
}
