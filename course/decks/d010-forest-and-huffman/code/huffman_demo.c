/* D010: positive integer weights, small binary prefix codes.
 * Build: gcc -std=c11 -Wall -Wextra huffman_demo.c -o /tmp/d010-huffman
 * Tie rule: lower weight first, then earlier node ID; first selected is left.
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

enum { MAX_LEAVES = 16, MAX_NODES = 2 * MAX_LEAVES - 1, NONE = -1 };
typedef unsigned long long Weight;
typedef struct {
    Weight weight;
    int parent, left, right;
} HNode;
typedef struct {
    HNode node[MAX_NODES];
    size_t n, used;
    int root;
    Weight merge_sum;
    char code[MAX_LEAVES][MAX_LEAVES + 1];
} Huffman;

static bool add(Weight a, Weight b, Weight *out)
{
    if (a > ULLONG_MAX - b) return false;
    *out = a + b;
    return true;
}

static int smallest_root(const Huffman *h, int exclude)
{
    int best = NONE;
    for (size_t i = 0; i < h->used; ++i) {
        if ((int)i == exclude || h->node[i].parent != NONE) continue;
        if (best == NONE || h->node[i].weight < h->node[best].weight)
            best = (int)i;
    }
    return best;
}

/* Failure leaves an empty object; caller must check the boolean result. */
static bool build(const Weight *weights, size_t n, Huffman *out)
{
    *out = (Huffman){.root = NONE};
    if (!weights || n == 0 || n > MAX_LEAVES) return false;
    Huffman h = {.n = n, .used = n, .root = NONE};
    for (size_t i = 0; i < n; ++i) {
        if (!weights[i]) return false;
        h.node[i] = (HNode){weights[i], NONE, NONE, NONE};
    }
    while (h.used < 2 * n - 1) {
        int a = smallest_root(&h, NONE), b = smallest_root(&h, a);
        Weight sum;
        if (a == NONE || b == NONE || !add(h.node[a].weight, h.node[b].weight, &sum)
            || !add(h.merge_sum, sum, &h.merge_sum)) return false;
        int p = (int)h.used++;
        h.node[p] = (HNode){sum, NONE, a, b};
        h.node[a].parent = h.node[b].parent = p;
    }
    h.root = (int)h.used - 1;
    for (size_t i = 0; i < n; ++i) {
        char reverse[MAX_LEAVES];
        size_t len = 0;
        int p = (int)i;
        while (h.node[p].parent != NONE) {
            int parent = h.node[p].parent;
            reverse[len++] = h.node[parent].left == p ? '0' : '1';
            p = parent;
        }
        /* A single symbol has structural depth zero. Wire convention: code 0. */
        if (len == 0) reverse[len++] = '0';
        for (size_t j = 0; j < len; ++j) h.code[i][j] = reverse[len - 1 - j];
        h.code[i][len] = '\0';
    }
    *out = h;
    return true;
}

/* Returns encoded payload cost, including the one-symbol wire convention. */
static bool payload_cost(const Huffman *h, Weight *total)
{
    *total = 0;
    for (size_t i = 0; i < h->n; ++i) {
        size_t length = strlen(h->code[i]);
        if (length == 0 || h->node[i].weight > ULLONG_MAX / length) return false;
        Weight term = h->node[i].weight * length;
        if (!add(*total, term, total)) return false;
    }
    return true;
}

/* Symbols are A, B, ... in leaf-index order. Failed output is discarded. */
static bool encode(const Huffman *h, const char *text, char *bits, size_t cap)
{
    if (!cap) return false;
    bits[0] = '\0';
    if (h->root == NONE) return false;
    size_t used = 0;
    for (; *text; ++text) {
        int id = (unsigned char)*text - 'A';
        if (id < 0 || (size_t)id >= h->n) { bits[0] = '\0'; return false; }
        size_t len = strlen(h->code[id]);
        if (len > cap - 1 - used) { bits[0] = '\0'; return false; }
        memcpy(bits + used, h->code[id], len);
        used += len;
        bits[used] = '\0';
    }
    return true;
}

static bool decode(const Huffman *h, const char *bits, char *text, size_t cap)
{
    if (!cap) return false;
    text[0] = '\0';
    if (h->root == NONE) return false;
    size_t used = 0;
    int p = h->root;
    for (; *bits; ++bits) {
        if (*bits != '0' && *bits != '1') goto fail;
        if (h->n == 1) {
            if (*bits != '0') goto fail;
        } else {
            p = *bits == '0' ? h->node[p].left : h->node[p].right;
            if (p == NONE) goto fail;
        }
        if (h->node[p].left == NONE && h->node[p].right == NONE) {
            if (used == cap - 1) goto fail;
            text[used++] = (char)('A' + p);
            text[used] = '\0';
            p = h->root;
        }
    }
    if (p != h->root) goto fail; /* Truncated codeword. */
    return true;
fail:
    text[0] = '\0';
    return false;
}

static void verify(const Huffman *h)
{
    assert(h->used == 2 * h->n - 1);
    for (size_t i = 0; i < h->n; ++i) {
        for (size_t j = 0; j < h->n; ++j) {
            if (i != j) assert(strncmp(h->code[i], h->code[j], strlen(h->code[i])) != 0);
        }
        char input[] = {(char)('A' + i), '\0'}, bits[MAX_LEAVES + 1], back[2];
        assert(encode(h, input, bits, sizeof bits));
        assert(decode(h, bits, back, sizeof back));
        assert(strcmp(input, back) == 0);
    }
    Weight total;
    assert(payload_cost(h, &total));
    assert(total == (h->n == 1 ? h->node[0].weight : h->merge_sum));
}

static bool show(const char *label, const Weight *weights)
{
    Huffman h;
    Weight total, fixed;
    if (!build(weights, 4, &h) || !payload_cost(&h, &total)) return false;
    verify(&h);
    if (h.node[h.root].weight > ULLONG_MAX / 2) return false;
    fixed = h.node[h.root].weight * 2;
    printf("%s\n", label);
    for (size_t i = 0; i < h.n; ++i)
        printf("%c weight=%llu code=%s\n", (int)('A' + i), weights[i], h.code[i]);
    printf("merge weights:");
    for (size_t i = h.n; i < h.used; ++i) printf(" %llu", h.node[i].weight);
    printf("\nWPL=%llu merge-sum=%llu fixed=%llu average=%.2f\n", total,
           h.merge_sum, fixed, (double)total / (double)h.node[h.root].weight);
    char bits[128], back[32];
    if (!encode(&h, "ABCD", bits, sizeof bits)
        || !decode(&h, bits, back, sizeof back)) return false;
    printf("ABCD -> %s -> %s\n", bits, back);
    return strcmp(back, "ABCD") == 0;
}

int main(void)
{
    Weight skew[] = {8, 4, 2, 2}, equal[] = {4, 4, 4, 4};
    Weight exercise[] = {5, 2, 1, 1}, one[] = {7}, zero[] = {1, 0};
    Weight overflow[] = {ULLONG_MAX, 1};
    Weight cost_overflow[] = {ULLONG_MAX / 3, ULLONG_MAX / 3, ULLONG_MAX / 3};
    Huffman h;
    assert(!build(skew, 0, &h));
    assert(!build(NULL, 4, &h));
    assert(!build(skew, MAX_LEAVES + 1, &h));
    assert(!build(zero, 2, &h));
    assert(!build(overflow, 2, &h));
    assert(!build(cost_overflow, 3, &h));
    assert(h.root == NONE);
    assert(build(one, 1, &h)); verify(&h);
    char bits[128], back[32];
    assert(encode(&h, "AAA", bits, sizeof bits) && strcmp(bits, "000") == 0);
    assert(decode(&h, bits, back, sizeof back) && strcmp(back, "AAA") == 0);
    assert(!decode(&h, "1", back, sizeof back));
    assert(build(exercise, 4, &h)); verify(&h);
    assert(h.merge_sum == 15);
    Weight full[MAX_LEAVES];
    for (size_t i = 0; i < MAX_LEAVES; ++i) full[i] = 1;
    assert(build(full, MAX_LEAVES, &h)); verify(&h);
    assert(h.merge_sum == 64);
    assert(build(skew, 4, &h)); verify(&h);
    assert(h.merge_sum == 28 && strcmp(h.code[0], "0") == 0);
    assert(!decode(&h, "11", back, sizeof back));
    assert(!decode(&h, "02", back, sizeof back));
    assert(!encode(&h, "X", bits, sizeof bits));
    assert(!encode(&h, "ABCD", bits, 2));
    assert(!decode(&h, "010", back, 2));
    assert(!encode(&h, "A", bits, 0));
    assert(!decode(&h, "0", back, 0));
    assert(encode(&h, "", bits, 1) && bits[0] == '\0');
    assert(decode(&h, "", back, 1) && back[0] == '\0');
    if (!show("weights=8,4,2,2", skew) || !show("weights=4,4,4,4", equal)) return 1;
    Weight homework[] = {7, 3, 2, 1};
    assert(build(homework, 4, &h)); verify(&h);
    assert(h.merge_sum == 22);
    if (!show("homework weights=7,3,2,1", homework)) return 1;
    puts("All classroom checks passed.");
    return 0;
}
