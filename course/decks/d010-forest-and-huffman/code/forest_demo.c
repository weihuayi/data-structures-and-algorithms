/* D010: ordered forest <-> first-child/next-sibling representation.
 * IDs are array indices, scanned in increasing order to fix sibling/root order.
 * Build: gcc -std=c11 -Wall -Wextra forest_demo.c -o /tmp/d010-forest
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

enum { CAP = 16, NONE = -1 };
typedef struct {
    size_t n;
    int root, first[CAP], next[CAP];
} Forest;

static bool valid_parents(const int *parent, size_t n)
{
    if (n > CAP || (n && !parent)) return false;
    for (size_t i = 0; i < n; ++i)
        if (parent[i] < NONE || (parent[i] != NONE && (size_t)parent[i] >= n))
            return false;
    for (size_t i = 0; i < n; ++i) {
        size_t steps = 0;
        int p = (int)i;
        while (p != NONE) {
            if (++steps > n) return false;
            p = parent[p];
        }
    }
    return true;
}

static bool encode_forest(const int *parent, size_t n, Forest *out)
{
    *out = (Forest){.root = NONE};
    if (!valid_parents(parent, n)) return false;
    out->n = n;
    int tail[CAP], root_tail = NONE;
    for (size_t i = 0; i < n; ++i) out->first[i] = out->next[i] = tail[i] = NONE;
    for (size_t i = 0; i < n; ++i) {
        int p = parent[i];
        if (p == NONE) {
            if (root_tail == NONE) out->root = (int)i;
            else out->next[root_tail] = (int)i;
            root_tail = (int)i;
        } else {
            if (tail[p] == NONE) out->first[p] = (int)i;
            else out->next[tail[p]] = (int)i;
            tail[p] = (int)i;
        }
    }
    return true;
}

static bool decode_chain(const Forest *f, int node, int parent,
                         int *result, bool *seen)
{
    while (node != NONE) {
        if (node < 0 || (size_t)node >= f->n || seen[node]) return false;
        seen[node] = true;
        result[node] = parent;
        if (!decode_chain(f, f->first[node], node, result, seen)) return false;
        node = f->next[node];
    }
    return true;
}

/* On failure result may be partial; caller must discard it. */
static bool decode_forest(const Forest *f, int *result)
{
    if (f->n > CAP || (f->n && !result)) return false;
    bool seen[CAP] = {false};
    if (!decode_chain(f, f->root, NONE, result, seen)) return false;
    for (size_t i = 0; i < f->n; ++i) if (!seen[i]) return false;
    return true;
}

/* Traversal functions below require a validated representation. */
static void binary_pre(const Forest *f, int p)
{
    if (p == NONE) return;
    putchar('A' + p);
    binary_pre(f, f->first[p]);
    binary_pre(f, f->next[p]);
}

static void binary_in(const Forest *f, int p)
{
    if (p == NONE) return;
    binary_in(f, f->first[p]);
    putchar('A' + p);
    binary_in(f, f->next[p]);
}

static size_t child_count(const Forest *f, int p)
{
    size_t count = 0;
    for (int c = f->first[p]; c != NONE; c = f->next[c]) ++count;
    return count;
}

static void check_roundtrip(const int *parent, size_t n)
{
    Forest f;
    int restored[CAP];
    assert(encode_forest(parent, n, &f));
    assert(decode_forest(&f, restored));
    size_t nonleaf = 0, right_null = 0;
    for (size_t i = 0; i < n; ++i) {
        assert(restored[i] == parent[i]);
        nonleaf += f.first[i] != NONE;
        right_null += f.next[i] == NONE;
    }
    assert(right_null == (n ? nonleaf + 1 : 0));
}

int main(void)
{
    const int parent[] = {NONE, 0, 0, 0, 1, 1, NONE, 6};
    const int single[] = {NONE}, roots[] = {NONE, NONE, NONE};
    const int chain[] = {NONE, 0, 1, 2};
    const int later_parent[] = {2, 2, NONE};
    check_roundtrip(parent, 8);
    check_roundtrip(NULL, 0);
    check_roundtrip(single, 1);
    check_roundtrip(roots, 3);
    check_roundtrip(chain, 4);
    check_roundtrip(later_parent, 3);
    Forest f;
    const int cycle[] = {1, 0}, invalid[] = {NONE, 2};
    const int negative[] = {NONE, -2};
    assert(!encode_forest(cycle, 2, &f));
    assert(!encode_forest(invalid, 2, &f));
    assert(!encode_forest(negative, 2, &f));
    assert(!encode_forest(NULL, 1, &f));
    assert(!encode_forest(parent, CAP + 1, &f));
    assert(encode_forest(parent, 8, &f));
    Forest broken = f;
    int restored[CAP];
    broken.next[0] = 0;
    assert(!decode_forest(&broken, restored));
    broken = f; broken.first[6] = 4; /* Shared child. */
    assert(!decode_forest(&broken, restored));
    broken = f; broken.first[6] = 99;
    assert(!decode_forest(&broken, restored));
    broken = f; broken.next[0] = NONE; /* Unreachable second tree. */
    assert(!decode_forest(&broken, restored));
    if (!decode_forest(&f, restored)) return 1;
    for (size_t i = 0; i < f.n; ++i) if (parent[i] != restored[i]) return 1;
    printf("A children=%zu\nforest-pre=", child_count(&f, 0));
    binary_pre(&f, f.root);
    printf("\nforest-post=");
    binary_in(&f, f.root);
    size_t right_null = 0;
    for (size_t i = 0; i < f.n; ++i) right_null += f.next[i] == NONE;
    printf("\nright-null=%zu\nparent roundtrip: OK\n", right_null);
    puts("All classroom checks passed.");
    return 0;
}
