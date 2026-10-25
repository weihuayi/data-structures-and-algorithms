/* D012: finite simple graphs, vertex IDs 0..n-1; unweighted edges.
 * Lists use compact neighbor arrays, not heap-allocated linked nodes.
 * Build: gcc -std=c11 -Wall -Wextra traversal_demo.c -o /tmp/d012
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define CAP 16

typedef struct { int from, to; } Edge;
typedef struct {
    size_t n;
    bool directed, matrix[CAP][CAP];
    int neighbor[CAP][CAP];
    size_t degree[CAP];
} Graph;
typedef enum { MATRIX, LIST } Representation;
typedef struct {
    bool visited[CAP];
    int order[CAP], parent[CAP], distance[CAP];
    size_t count, scans, roots;
} Result;
typedef struct { int vertex; size_t next; } Frame;

/* Failure clears the output. Ascending neighbor order is independent of input order. */
static bool build(size_t n, bool directed, const Edge *edges, size_t m, Graph *g)
{
    *g = (Graph){0};
    if (n == 0 || n > CAP || (m && !edges)) return false;
    Graph tmp = {.n = n, .directed = directed};
    for (size_t i = 0; i < m; ++i) {
        int u = edges[i].from, v = edges[i].to;
        if (u < 0 || v < 0 || (size_t)u >= n || (size_t)v >= n
            || u == v || tmp.matrix[u][v]) return false;
        tmp.matrix[u][v] = true;
        if (!directed) tmp.matrix[v][u] = true;
    }
    for (size_t u = 0; u < n; ++u)
        for (size_t v = 0; v < n; ++v)
            if (tmp.matrix[u][v]) tmp.neighbor[u][tmp.degree[u]++] = (int)v;
    *g = tmp;
    return true;
}

/* Counts every examined matrix cell or stored adjacency entry, including visited ones. */
static int next_neighbor(const Graph *g, int u, Representation rep,
                         bool reverse, size_t *cursor, size_t *scans)
{
    size_t limit = rep == MATRIX ? g->n : g->degree[u];
    while (*cursor < limit) {
        size_t k = reverse ? limit - 1 - *cursor : *cursor;
        ++*cursor; ++*scans;
        if (rep == LIST) return g->neighbor[u][k];
        if (g->matrix[u][k]) return (int)k;
    }
    return -1;
}
static void init(Result *r)
{
    *r = (Result){0};
    for (size_t i = 0; i < CAP; ++i) r->parent[i] = r->distance[i] = -1;
}
/* First visit marks the vertex and records how it was reached. */
static void visit(Result *r, int v, int parent)
{
    assert(!r->visited[v] && r->count < CAP);
    r->visited[v] = true;
    r->parent[v] = parent;
    r->distance[v] = parent < 0 ? 0 : r->distance[parent] + 1;
    r->order[r->count++] = v;
}
static void dfs_recursive(const Graph *g, int u, Representation rep,
                          bool reverse, Result *r)
{
    size_t cursor = 0;
    int v;
    while ((v = next_neighbor(g, u, rep, reverse, &cursor, &r->scans)) >= 0)
        if (!r->visited[v]) {
            visit(r, v, u);
            dfs_recursive(g, v, rep, reverse, r);
        }
}
/* A frame remembers both the vertex and the next neighbor to examine.
 * This reproduces recursive DFS visit order and parent edges exactly. */
static void dfs_stack(const Graph *g, int root, Representation rep,
                      bool reverse, Result *r)
{
    Frame stack[CAP] = {{root, 0}};
    size_t top = 1;
    while (top) {
        Frame *f = &stack[top - 1];
        int v = next_neighbor(g, f->vertex, rep, reverse, &f->next, &r->scans);
        if (v < 0) { --top; continue; }
        if (r->visited[v]) continue;
        visit(r, v, f->vertex);
        assert(top < CAP);
        stack[top++] = (Frame){v, 0};
    }
}
static void bfs(const Graph *g, int root, Representation rep,
                bool reverse, Result *r)
{
    int queue[CAP] = {root};
    size_t front = 0, rear = 1;
    while (front < rear) {
        int u = queue[front++], v;
        size_t cursor = 0;
        while ((v = next_neighbor(g, u, rep, reverse, &cursor, &r->scans)) >= 0) {
            if (r->visited[v]) continue;
            visit(r, v, u); /* Mark before enqueue: each vertex enters once. */
            assert(rear < CAP);
            queue[rear++] = v;
        }
    }
}
typedef enum { RECURSIVE_DFS, STACK_DFS, BFS } Method;
/* all=false: single source; all=true: source then remaining IDs ascending.
 * distance is search-tree depth; it is shortest-edge distance only for BFS.
 * In all=true mode depth restarts at zero for every new root. */
static bool search(const Graph *g, int source, Method method, Representation rep,
                   bool reverse, bool all, Result *r)
{
    init(r);
    if (g->n == 0 || g->n > CAP || source < 0 || (size_t)source >= g->n
        || method < RECURSIVE_DFS || method > BFS || rep < MATRIX || rep > LIST)
        return false;
    for (size_t step = 0; step <= g->n; ++step) {
        int root = step == 0 ? source : (int)step - 1;
        if (step && !all) break;
        if (r->visited[root]) continue;
        ++r->roots; visit(r, root, -1);
        if (method == BFS) bfs(g, root, rep, reverse, r);
        else if (method == STACK_DFS) dfs_stack(g, root, rep, reverse, r);
        else dfs_recursive(g, root, rep, reverse, r);
    }
    return true;
}
static void show(const char *label, const Graph *g, Method method,
                 Representation rep, bool reverse, bool all)
{
    Result r;
    bool ok = search(g, 0, method, rep, reverse, all, &r);
    assert(ok);
    printf("%s: order=", label);
    for (size_t i = 0; i < r.count; ++i) putchar('A' + r.order[i]);
    printf(" scans=%zu roots=%zu\nparent:", r.scans, r.roots);
    for (size_t i = 0; i < g->n; ++i) printf(" %d", r.parent[i]);
    printf("\n%s:", method == BFS && !all ? "distance-from-A" : "tree-depth");
    for (size_t i = 0; i < g->n; ++i) printf(" %d", r.distance[i]);
    putchar('\n');
}
static void checks(void)
{
    Graph g;
    Result r;
    assert(!build(0, false, NULL, 0, &g));
    assert(!build(CAP+1, false, NULL, 0, &g));
    assert(!build(2, false, NULL, 1, &g));
    Edge loop[]={{0,0}}, bad[]={{0,2}}, neg[]={{-1,0}}, dup[]={{0,1},{1,0}};
    assert(!build(2, false, loop, 1, &g));
    assert(!build(2, false, bad, 1, &g));
    assert(!build(2, false, neg, 1, &g));
    assert(!build(2, false, dup, 2, &g));
    assert(build(2, true, dup, 2, &g));
    assert(search(&g, 0, BFS, LIST, false, false, &r) && r.count==2);
    assert(!search(&g, 2, BFS, LIST, false, false, &r) && r.count==0);
    assert(build(1, false, NULL, 0, &g));
    assert(search(&g, 0, BFS, LIST, false, false, &r) && r.count==1 && r.scans==0);
    Edge chain[CAP-1];
    for (int i=0; i<CAP-1; ++i) chain[i]=(Edge){i,i+1};
    assert(build(CAP, false, chain, CAP-1, &g));
    for (int m=RECURSIVE_DFS; m<=BFS; ++m)
        assert(search(&g, 0, (Method)m, LIST, false, false, &r) && r.count==CAP);
}
int main(void)
{
    checks();
    Graph g;
    const Edge roads[]={{0,1},{0,2},{1,2},{2,3}};
    if (!build(5, false, roads, 4, &g)) return 1;
    show("DFS/list", &g, RECURSIVE_DFS, LIST, false, false);
    show("DFS/stack", &g, STACK_DFS, LIST, false, false);
    show("BFS/list", &g, BFS, LIST, false, false);
    show("BFS/matrix", &g, BFS, MATRIX, false, false);
    show("DFS/reverse", &g, STACK_DFS, LIST, true, false);
    show("BFS/reverse", &g, BFS, LIST, true, false);
    show("BFS/all", &g, BFS, LIST, false, true);
    const Edge homework[]={{0,1},{0,2},{1,2},{2,3},{3,4}};
    if (!build(5, false, homework, 5, &g)) return 1;
    show("homework+BFS", &g, BFS, LIST, false, false);
    puts("All classroom checks passed.");
    return 0;
}
