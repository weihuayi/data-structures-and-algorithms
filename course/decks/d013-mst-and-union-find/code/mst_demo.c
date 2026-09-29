/* D013: simple undirected weighted graphs, 1..16 vertices.
 * Edge weights are integers in [-1000000,1000000], including zero.
 * Build: gcc -std=c11 -Wall -Wextra mst_demo.c -o /tmp/d013
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#define CAP 16
#define MAX_EDGES (CAP * (CAP - 1) / 2)
#define WEIGHT_LIMIT 1000000

typedef struct { int u, v, weight; } Edge;
typedef struct {
    size_t n, m;
    bool present[CAP][CAP];
    int weight[CAP][CAP];
    Edge edges[MAX_EDGES];
} Graph;
typedef struct { int parent[CAP]; size_t size[CAP]; } DSU;
typedef struct {
    Edge edges[CAP - 1];
    size_t count, components;
    long long total;
} Forest;

/* Validated construction, separate existence from weight. Output cleared on failure. */
static bool build(size_t n, const Edge *edges, size_t m, Graph *g)
{
    *g = (Graph){0};
    if (n == 0 || n > CAP || m > MAX_EDGES || (m && !edges)) return false;
    Graph temp = {.n = n, .m = m};
    for (size_t i = 0; i < m; ++i) {
        Edge e = edges[i];
        if (e.u < 0 || e.v < 0 || (size_t)e.u >= n || (size_t)e.v >= n
            || e.u == e.v || temp.present[e.u][e.v]
            || e.weight < -WEIGHT_LIMIT || e.weight > WEIGHT_LIMIT) return false;
        if (e.u > e.v) { int t = e.u; e.u = e.v; e.v = t; }
        temp.edges[i] = e;
        temp.present[e.u][e.v] = temp.present[e.v][e.u] = true;
        temp.weight[e.u][e.v] = temp.weight[e.v][e.u] = e.weight;
    }
    *g = temp;
    return true;
}
static void dsu_init(DSU *d, size_t n)
{
    *d = (DSU){0};
    for (size_t i = 0; i < n; ++i) { d->parent[i] = (int)i; d->size[i] = 1; }
}
/* Roots represent equivalence classes, not original graph vertices' tree parents. */
static int find(DSU *d, int x)
{
    if (d->parent[x] != x) d->parent[x] = find(d, d->parent[x]);
    return d->parent[x];
}
static bool unite(DSU *d, int u, int v)
{
    int a = find(d, u), b = find(d, v);
    if (a == b) return false;
    if (d->size[a] < d->size[b]) { int t = a; a = b; b = t; }
    d->parent[b] = a;
    d->size[a] += d->size[b];
    return true;
}
static bool before(Edge a, Edge b)
{
    if (a.weight != b.weight) return a.weight < b.weight;
    if (a.u != b.u) return a.u < b.u;
    return a.v < b.v;
}
/* Merge sort: O(m log m) comparisons; tie order makes output reproducible. */
static void sort(Edge *e, Edge *tmp, size_t begin, size_t end)
{
    if (end - begin < 2) return;
    size_t mid = begin + (end - begin) / 2;
    sort(e, tmp, begin, mid); sort(e, tmp, mid, end);
    size_t i = begin, j = mid, k = begin;
    while (i < mid && j < end) tmp[k++] = before(e[j], e[i]) ? e[j++] : e[i++];
    while (i < mid) tmp[k++] = e[i++];
    while (j < end) tmp[k++] = e[j++];
    for (k = begin; k < end; ++k) e[k] = tmp[k];
}
static void take(Forest *f, Edge e)
{
    assert(f->count < CAP - 1);
    f->edges[f->count++] = e;
    f->total += e.weight; /* bounded weights and CAP make this sum safe */
}
/* Preconditions for both algorithms: g is successfully built and unchanged. */
static Forest kruskal(const Graph *g)
{
    DSU d; dsu_init(&d, g->n);
    Edge sorted[MAX_EDGES], tmp[MAX_EDGES];
    for (size_t i = 0; i < g->m; ++i) sorted[i] = g->edges[i];
    sort(sorted, tmp, 0, g->m);
    Forest f = {.components = g->n};
    for (size_t i = 0; i < g->m; ++i)
        if (unite(&d, sorted[i].u, sorted[i].v)) {
            take(&f, sorted[i]); --f.components;
        }
    return f;
}
/* Matrix Prim. When no crossing candidate exists, start a new component.
 * key[v] is one-edge cost from the selected region, NOT path distance. */
static Forest prim(const Graph *g)
{
    bool used[CAP] = {0}, has_key[CAP] = {0};
    int key[CAP] = {0}, parent[CAP];
    for (size_t i = 0; i < g->n; ++i) parent[i] = -1;
    Forest f = {0};
    for (size_t step = 0; step < g->n; ++step) {
        int u = -1;
        for (size_t v = 0; v < g->n; ++v)
            if (!used[v] && has_key[v] && (u < 0 || key[v] < key[u])) u = (int)v;
        if (u < 0) {
            for (size_t v = 0; v < g->n; ++v)
                if (!used[v]) { u = (int)v; break; }
            ++f.components;
        }
        assert(u >= 0);
        used[u] = true;
        if (parent[u] >= 0) take(&f, (Edge){parent[u], u, key[u]});
        for (size_t v = 0; v < g->n; ++v)
            if (!used[v] && g->present[u][v]
                && (!has_key[v] || g->weight[u][v] < key[v])) {
                has_key[v] = true; key[v] = g->weight[u][v]; parent[v] = u;
            }
    }
    return f;
}
/* Structural check, deliberately separate from an optimality proof. */
static void verify(const Graph *g, const Forest *f)
{
    DSU d; dsu_init(&d, g->n);
    long long sum = 0;
    for (size_t i = 0; i < f->count; ++i) {
        Edge e = f->edges[i];
        assert(g->present[e.u][e.v] && g->weight[e.u][e.v] == e.weight);
        assert(unite(&d, e.u, e.v)); sum += e.weight;
    }
    size_t components = 0;
    for (size_t v = 0; v < g->n; ++v) if (find(&d, (int)v) == (int)v) ++components;
    for (size_t i = 0; i < g->m; ++i)
        assert(find(&d, g->edges[i].u) == find(&d, g->edges[i].v));
    assert(components == f->components && f->count + components == g->n);
    assert(sum == f->total);
}
static void print_forest(const char *method, const Graph *g, const Forest *f)
{
    verify(g, f);
    printf("%s: %s components=%zu edges=%zu total=%lld\n", method,
           f->components == 1 ? "MST" : "MSF", f->components, f->count, f->total);
    for (size_t i = 0; i < f->count; ++i)
        printf(" %c%c:%d", 'A' + f->edges[i].u, 'A' + f->edges[i].v, f->edges[i].weight);
    putchar('\n');
}
static bool demo(const char *label, size_t n, const Edge *edges, size_t m)
{
    Graph g;
    if (!build(n, edges, m, &g)) return false;
    Forest p = prim(&g), k = kruskal(&g);
    printf("%s\n", label); print_forest("Prim", &g, &p); print_forest("Kruskal", &g, &k);
    assert(p.total == k.total && p.components == k.components);
    return true;
}
static void checks(void)
{
    Graph g;
    Edge loop[]={{0,0,1}}, dup[]={{0,1,1},{1,0,2}}, bad[]={{0,2,1}};
    Edge too_large[]={{0,1,WEIGHT_LIMIT+1}};
    assert(!build(0,NULL,0,&g)); assert(!build(CAP+1,NULL,0,&g));
    assert(!build(2,NULL,1,&g)); assert(!build(2,loop,1,&g));
    assert(!build(2,dup,2,&g)); assert(!build(2,bad,1,&g));
    assert(!build(2,too_large,1,&g));
    assert(build(1,NULL,0,&g));
    Forest p=prim(&g), k=kruskal(&g); verify(&g,&p); verify(&g,&k);
    assert(p.count==0 && p.components==1 && p.total==0);
    Edge chain[CAP-1];
    for (int i=0;i<CAP-1;++i) chain[i]=(Edge){i,i+1,-WEIGHT_LIMIT};
    assert(build(CAP,chain,CAP-1,&g));p=prim(&g);k=kruskal(&g);
    verify(&g,&p);verify(&g,&k);assert(p.total==-(long long)(CAP-1)*WEIGHT_LIMIT&&p.total==k.total);
    DSU d;dsu_init(&d,4);assert(unite(&d,0,1));assert(unite(&d,2,3));
    assert(unite(&d,0,2));assert(!unite(&d,1,3));
    int root=find(&d,3);assert(d.parent[3]==root && d.size[root]==4);
}
int main(void)
{
    checks();
    const Edge base[]={{0,1,1},{0,2,4},{1,2,2},{1,3,5},{2,3,3},{2,4,6},{3,4,7}};
    const Edge ties[]={{0,1,1},{0,2,4},{1,2,2},{1,3,5},{2,3,3},{2,4,7},{3,4,7}};
    const Edge homework[]={{0,1,1},{0,2,4},{1,2,2},{1,3,5},{2,3,3},{2,4,6},{3,4,0}};
    const Edge disconnected[]={{0,1,1},{0,2,4},{1,2,2},{1,3,5},{2,3,3}};
    const Edge negative[]={{0,1,-2},{1,2,0},{0,2,5}};
    if (!demo("base",5,base,7) || !demo("ties",5,ties,7)
        || !demo("homework DE=0",5,homework,7)
        || !demo("isolated E",5,disconnected,5)
        || !demo("negative and zero",3,negative,3)) return 1;
    puts("All classroom checks passed.");
    return 0;
}
