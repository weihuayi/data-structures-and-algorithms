/* D011: same fixed-vertex simple graph in a matrix and outgoing lists.
 * No loops/parallel edges; nonnegative integer weights including zero.
 * Build: gcc -std=c11 -Wall -Wextra graph_demo.c -o /tmp/d011
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { MAX_V = 8 };
typedef struct { int from, to, weight; } Edge;
typedef enum { INVALID_VERTEX, ABSENT, FOUND } Result;
typedef struct {
    size_t n, m;
    bool directed;
    bool present[MAX_V][MAX_V];
    int weight[MAX_V][MAX_V];
} Matrix;
typedef struct Arc {
    int to, weight;
    struct Arc *next;
} Arc;
typedef struct {
    size_t n, m;
    bool directed;
    Arc *head[MAX_V];
} Lists;

static bool valid_id(size_t n, int id)
{
    return id >= 0 && (size_t)id < n;
}

/* Failure leaves an empty matrix. An undirected reversed duplicate is rejected. */
static bool matrix_build(size_t n, bool directed, const Edge *edges, size_t m,
                         Matrix *out)
{
    *out = (Matrix){0};
    if (n == 0 || n > MAX_V || (m && !edges)) return false;
    size_t max_edges = directed ? n * (n - 1) : n * (n - 1) / 2;
    if (m > max_edges) return false;
    Matrix g = {.n = n, .m = m, .directed = directed};
    for (size_t i = 0; i < m; ++i) {
        int u = edges[i].from, v = edges[i].to, w = edges[i].weight;
        if (!valid_id(n, u) || !valid_id(n, v) || u == v || w < 0
            || g.present[u][v]) return false;
        g.present[u][v] = true;
        g.weight[u][v] = w;
        if (!directed) { g.present[v][u] = true; g.weight[v][u] = w; }
    }
    *out = g;
    return true;
}

static void lists_destroy(Lists *g)
{
    for (size_t u = 0; u < g->n; ++u) {
        Arc *p = g->head[u];
        while (p) { Arc *next = p->next; free(p); p = next; }
    }
    *g = (Lists){0};
}

/* Input is a valid matrix built above. out must not own existing allocations.
 * Neighbor order is increasing ID; failure frees all newly allocated nodes.
 * Conversion scans n^2 cells; this is not a linear-time edge-list builder.
 */
static bool lists_from_matrix(const Matrix *source, Lists *out)
{
    *out = (Lists){.n = source->n, .m = source->m, .directed = source->directed};
    for (size_t u = 0; u < source->n; ++u) {
        for (size_t j = source->n; j > 0; --j) {
            size_t v = j - 1;
            if (!source->present[u][v]) continue;
            Arc *p = malloc(sizeof *p);
            if (!p) { lists_destroy(out); return false; }
            *p = (Arc){(int)v, source->weight[u][v], out->head[u]};
            out->head[u] = p;
        }
    }
    return true;
}

/* weight is meaningful only when the result is FOUND. */
static Result matrix_get(const Matrix *g, int u, int v, int *weight)
{
    if (!valid_id(g->n, u) || !valid_id(g->n, v)) return INVALID_VERTEX;
    if (!g->present[u][v]) return ABSENT;
    *weight = g->weight[u][v];
    return FOUND;
}

static Result lists_get(const Lists *g, int u, int v, int *weight)
{
    if (!valid_id(g->n, u) || !valid_id(g->n, v)) return INVALID_VERTEX;
    for (const Arc *p = g->head[u]; p; p = p->next)
        if (p->to == v) { *weight = p->weight; return FOUND; }
    return ABSENT;
}

static void matrix_degrees(const Matrix *g, size_t *in, size_t *out)
{
    for (size_t i = 0; i < g->n; ++i) in[i] = out[i] = 0;
    for (size_t u = 0; u < g->n; ++u)
        for (size_t v = 0; v < g->n; ++v)
            if (g->present[u][v]) { ++out[u]; ++in[v]; }
}

static void lists_degrees(const Lists *g, size_t *in, size_t *out)
{
    for (size_t i = 0; i < g->n; ++i) in[i] = out[i] = 0;
    for (size_t u = 0; u < g->n; ++u)
        for (const Arc *p = g->head[u]; p; p = p->next) { ++out[u]; ++in[p->to]; }
}

static Result matrix_remove(Matrix *g, int u, int v)
{
    int weight;
    Result found = matrix_get(g, u, v, &weight);
    if (found != FOUND) return found;
    g->present[u][v] = false;
    g->weight[u][v] = 0;
    if (!g->directed) { g->present[v][u] = false; g->weight[v][u] = 0; }
    --g->m;
    return FOUND;
}

static void unlink_arc(Lists *g, int u, int v)
{
    Arc **link = &g->head[u];
    while (*link && (*link)->to != v) link = &(*link)->next;
    if (*link) { Arc *removed = *link; *link = removed->next; free(removed); }
}

/* g is a valid representation; undirected reciprocal entries already agree. */
static Result lists_remove(Lists *g, int u, int v)
{
    int weight;
    Result found = lists_get(g, u, v, &weight);
    if (found != FOUND) return found;
    unlink_arc(g, u, v);
    if (!g->directed) unlink_arc(g, v, u);
    --g->m;
    return FOUND;
}

static void verify(const Matrix *a, const Lists *b)
{
    assert(a->n == b->n && a->m == b->m && a->directed == b->directed);
    size_t ai[MAX_V], ao[MAX_V], bi[MAX_V], bo[MAX_V], total = 0;
    matrix_degrees(a, ai, ao); lists_degrees(b, bi, bo);
    for (size_t u = 0; u < a->n; ++u) {
        assert(ai[u] == bi[u] && ao[u] == bo[u]);
        total += ao[u];
        for (size_t v = 0; v < a->n; ++v) {
            int x = -1, y = -1;
            Result rx = matrix_get(a, (int)u, (int)v, &x);
            assert(rx == lists_get(b, (int)u, (int)v, &y));
            if (rx == FOUND) assert(x == y);
            if (!a->directed) assert(a->present[u][v] == a->present[v][u]);
        }
    }
    assert(total == (a->directed ? a->m : 2 * a->m));
}

static void print_degrees(const Matrix *g)
{
    size_t in[MAX_V], out[MAX_V], si = 0, so = 0;
    matrix_degrees(g, in, out);
    printf("%s:", g->directed ? "out-degree" : "degree");
    for (size_t i = 0; i < g->n; ++i) { printf(" %zu", out[i]); so += out[i]; }
    printf(" sum=%zu\n", so);
    if (g->directed) {
        printf("in-degree:");
        for (size_t i = 0; i < g->n; ++i) { printf(" %zu", in[i]); si += in[i]; }
        printf(" sum=%zu\n", si);
    }
}

int main(void)
{
    const Edge roads[] = {{0,1,1},{0,2,1},{1,2,1},{2,3,1}};
    const Edge times[] = {{0,1,4},{0,2,0},{1,2,2},{2,3,3},{3,1,1}};
    Matrix m;
    Lists l;
    if (!matrix_build(5, false, roads, 4, &m) || !lists_from_matrix(&m, &l)) return 1;
    verify(&m, &l);
    printf("undirected: vertices=%zu edges=%zu\n", m.n, m.m);
    print_degrees(&m);
    int matrix_neighbors[MAX_V];
    size_t matrix_scanned = 0, matrix_count = 0;
    for (size_t v = 0; v < m.n; ++v) {
        ++matrix_scanned;
        if (m.present[2][v]) matrix_neighbors[matrix_count++] = (int)v;
    }
    printf("neighbors(C):");
    size_t scanned = 0;
    for (Arc *p = l.head[2]; p; p = p->next) {
        assert(scanned < matrix_count && matrix_neighbors[scanned] == p->to);
        printf(" %c", 'A' + p->to); ++scanned;
    }
    assert(scanned == matrix_count);
    printf("\nneighbor scan: matrix=%zu list=%zu\n", matrix_scanned, scanned);
    if (matrix_remove(&m, 1, 2) != FOUND || lists_remove(&l, 1, 2) != FOUND) {
        lists_destroy(&l); return 1;
    }
    verify(&m, &l);
    assert(matrix_remove(&m, 1, 2) == ABSENT && lists_remove(&l, 1, 2) == ABSENT);
    printf("after remove BC: edges=%zu\n", m.m); print_degrees(&m);
    lists_destroy(&l);
    if (!matrix_build(5, true, times, 5, &m) || !lists_from_matrix(&m, &l)) return 1;
    verify(&m, &l);
    printf("directed: vertices=%zu arcs=%zu\n", m.n, m.m); print_degrees(&m);
    int weight;
    if (lists_get(&l, 0, 2, &weight) != FOUND) { lists_destroy(&l); return 1; }
    printf("A->C: FOUND weight=%d\n", weight);
    assert(matrix_get(&m, 0, 2, &weight) == FOUND && weight == 0);
    Result absent = lists_get(&l, 0, 4, &weight);
    printf("A->E: %s\n", absent == ABSENT ? "ABSENT" : "unexpected");
    assert(absent == ABSENT);
    assert(lists_get(&l, -1, 0, &weight) == INVALID_VERTEX);
    assert(matrix_get(&m, 0, 5, &weight) == INVALID_VERTEX);
    assert(lists_remove(&l, 5, 0) == INVALID_VERTEX);
    assert(matrix_remove(&m, 5, 0) == INVALID_VERTEX);
    lists_destroy(&l);
    /* Edgeless nonempty graphs and a singleton are legal. */
    assert(matrix_build(1, false, NULL, 0, &m));
    assert(lists_from_matrix(&m, &l)); verify(&m, &l); lists_destroy(&l);
    assert(matrix_build(5, true, NULL, 0, &m));
    assert(lists_from_matrix(&m, &l)); verify(&m, &l); lists_destroy(&l);
    Edge self[] = {{0,0,1}}, bad_id[] = {{0,5,1}}, negative[] = {{0,1,-1}};
    Edge dup[] = {{0,1,1},{0,1,2}}, reverse[] = {{0,1,1},{1,0,2}};
    assert(!matrix_build(0, false, NULL, 0, &m));
    assert(!matrix_build(MAX_V+1, false, NULL, 0, &m));
    assert(!matrix_build(5, false, NULL, 1, &m));
    assert(!matrix_build(5, false, self, 1, &m));
    assert(!matrix_build(5, false, bad_id, 1, &m));
    assert(!matrix_build(5, false, negative, 1, &m));
    assert(!matrix_build(5, true, dup, 2, &m));
    assert(!matrix_build(5, false, reverse, 2, &m));
    assert(matrix_build(5, true, reverse, 2, &m));
    assert(lists_from_matrix(&m, &l)); verify(&m, &l);
    assert(matrix_remove(&m, 0, 1) == FOUND && lists_remove(&l, 0, 1) == FOUND);
    assert(lists_get(&l, 1, 0, &weight) == FOUND && weight == 2);
    verify(&m, &l); lists_destroy(&l);
    /* Independent copy: homework removes AC, not BC. */
    if (!matrix_build(5, false, roads, 4, &m) || !lists_from_matrix(&m, &l)) return 1;
    if (matrix_remove(&m, 0, 2) != FOUND || lists_remove(&l, 0, 2) != FOUND) {
        lists_destroy(&l); return 1;
    }
    verify(&m, &l);
    assert(m.m == 3 && !m.present[0][2] && !m.present[2][0]);
    printf("homework after remove AC: edges=%zu\n", m.m); print_degrees(&m);
    lists_destroy(&l);
    puts("All classroom checks passed.");
    return 0;
}
