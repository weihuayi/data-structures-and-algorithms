/* D014 classroom examples. C11; zero weight and absent edge are distinct. */
#include <stdbool.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { MAXV = 16 };
static const long long INF = LLONG_MAX / 4;

typedef struct {
    int n;
    const char *labels;
    bool directed;
    bool present[MAXV][MAXV];
    long long weight[MAXV][MAXV];
} Graph;

typedef struct {
    long long dist[MAXV];
    int parent[MAXV], order[MAXV], count;
    bool settled[MAXV];
    unsigned select_checks, matrix_checks;
} Result;

static void init_graph(Graph *g, const char *labels, bool directed)
{
    memset(g, 0, sizeof(*g));
    g->n = (int)strlen(labels);
    g->labels = labels;
    g->directed = directed;
}

static void edge(Graph *g, int a, int b, long long w)
{
    g->present[a][b] = true;
    g->weight[a][b] = w;
    if (!g->directed) {
        g->present[b][a] = true;
        g->weight[b][a] = w;
    }
}

/* Small bounded integer examples; reject unsupported data before computing. */
static bool valid_graph(const Graph *g)
{
    if (g->n < 1 || g->n > MAXV) return false;
    for (int u = 0; u < g->n; ++u)
        for (int v = 0; v < g->n; ++v)
            if (g->present[u][v] &&
                (u == v || g->weight[u][v] < 0 ||
                 g->weight[u][v] >= INF / (g->n + 1))) return false;
    return true;
}

static bool dijkstra(const Graph *g, int source, Result *r, bool trace)
{
    if (!valid_graph(g) || source < 0 || source >= g->n) return false;
    memset(r, 0, sizeof(*r));
    for (int v = 0; v < g->n; ++v) {
        r->dist[v] = INF;
        r->parent[v] = -1;
    }
    r->dist[source] = 0;
    for (int round = 0; round < g->n; ++round) {
        int u = -1;
        long long best = INF;
        for (int v = 0; v < g->n; ++v) {
            ++r->select_checks;
            if (!r->settled[v] && r->dist[v] < best) {
                best = r->dist[v];
                u = v;
            }
        }
        if (u == -1) {
            if (trace) puts("stop: no finite unsettled candidate");
            break;
        }
        r->settled[u] = true;
        r->order[r->count++] = u;
        if (trace) printf("confirm %c: distance=%lld\n", g->labels[u], r->dist[u]);
        for (int v = 0; v < g->n; ++v) {
            ++r->matrix_checks;
            if (!g->present[u][v] || r->settled[v]) continue;
            long long candidate = r->dist[u] + g->weight[u][v];
            if (trace) {
                printf("  edge %c->%c weight=%lld candidate=%lld old=",
                       g->labels[u], g->labels[v], g->weight[u][v], candidate);
                if (r->dist[v] == INF) printf("INF");
                else printf("%lld", r->dist[v]);
                puts(candidate < r->dist[v] ? " update" : " keep");
            }
            if (candidate < r->dist[v]) {
                r->dist[v] = candidate;
                r->parent[v] = u;
            }
        }
    }
    return true;
}

static bool floyd(const Graph *g, long long d[MAXV][MAXV])
{
    if (!valid_graph(g)) return false;
    for (int i = 0; i < g->n; ++i)
        for (int j = 0; j < g->n; ++j)
            d[i][j] = i == j ? 0 : g->present[i][j] ? g->weight[i][j] : INF;
    for (int k = 0; k < g->n; ++k)
        for (int i = 0; i < g->n; ++i)
            for (int j = 0; j < g->n; ++j) {
                if (d[i][k] == INF || d[k][j] == INF) continue;
                long long candidate = d[i][k] + d[k][j];
                if (candidate < d[i][j]) d[i][j] = candidate;
            }
    return true;
}

/* -1 means unreachable; 0 means an inconsistent/cyclic record. */
static int recover(const Graph *g, const Result *r, int source, int target, int path[MAXV])
{
    if (r->dist[target] == INF) return -1;
    int count = 0, u = target;
    bool seen[MAXV] = {false};
    while (u >= 0 && u < g->n && !seen[u] && count < g->n) {
        seen[u] = true;
        path[count++] = u;
        if (u == source) {
            for (int i = 0; i < count / 2; ++i) {
                int t = path[i]; path[i] = path[count - 1 - i]; path[count - 1 - i] = t;
            }
            return count;
        }
        u = r->parent[u];
    }
    return 0;
}

static bool example(const char *name, Graph *g, int *source)
{
    *source = 0;
    if (!strcmp(name, "main") || !strcmp(name, "unreachable") || !strcmp(name, "homework")) {
        init_graph(g, "ABCDE", false);
        edge(g, 0, 1, 3); edge(g, 0, 2, 2); edge(g, 1, 2, 2);
        edge(g, 1, 3, 1); edge(g, 2, 3, !strcmp(name, "homework") ? 0 : 5);
        if (strcmp(name, "unreachable")) { edge(g, 1, 4, 7); edge(g, 3, 4, 3); }
    } else if (!strcmp(name, "exercise") || !strcmp(name, "reverse")) {
        init_graph(g, "PQRS", true);
        edge(g, 0, 1, 4); edge(g, 0, 2, 1); edge(g, 2, 1, 2);
        edge(g, 1, 3, 0); edge(g, 2, 3, 6);
        if (!strcmp(name, "reverse")) *source = 3;
    } else if (!strcmp(name, "zero_tie")) {
        init_graph(g, "ABC", false);
        edge(g, 0, 1, 0); edge(g, 0, 2, 1); edge(g, 1, 2, 1);
    } else if (!strcmp(name, "negative")) {
        init_graph(g, "spq", true);
        edge(g, 0, 1, 2); edge(g, 0, 2, 5); edge(g, 2, 1, -4);
    } else return false;
    return true;
}

static void json_number(long long value)
{
    if (value == INF) printf("null"); else printf("%lld", value);
}

static bool run(const char *name, bool json, bool trace)
{
    Graph g;
    Result r;
    int source, path[MAXV];
    if (!example(name, &g, &source)) return false;
    if (!dijkstra(&g, source, &r, trace)) {
        if (json) printf("{\"case\":\"%s\",\"rejected\":true}", name);
        else printf("%s: rejected: requires nonnegative bounded weights\n", name);
        return !strcmp(name, "negative");
    }
    if (json) {
        /* The JSON audit mode additionally reports Floyd for cross-checking.
           Normal classroom execution runs only the requested single source. */
        long long all[MAXV][MAXV];
        if (!floyd(&g, all)) return false;
        printf("{\"case\":\"%s\",\"source\":\"%c\",\"distance\":[", name, g.labels[source]);
        for (int i = 0; i < g.n; ++i) { if (i) putchar(','); json_number(r.dist[i]); }
        printf("],\"parent\":[");
        for (int i = 0; i < g.n; ++i) {
            if (i) putchar(',');
            if (r.parent[i] < 0) printf("null"); else printf("%d", r.parent[i]);
        }
        printf("],\"settled\":[");
        for (int i = 0; i < g.n; ++i) { if (i) putchar(','); printf(r.settled[i] ? "true" : "false"); }
        printf("],\"order\":[");
        for (int i = 0; i < r.count; ++i) { if (i) putchar(','); printf("\"%c\"", g.labels[r.order[i]]); }
        printf("],\"paths\":[");
        for (int v = 0; v < g.n; ++v) {
            if (v) putchar(',');
            int count = recover(&g, &r, source, v, path);
            if (count == -1) printf("null");
            else {
                if (!count) return false;
                putchar('[');
                for (int i = 0; i < count; ++i) { if (i) putchar(','); printf("\"%c\"", g.labels[path[i]]); }
                putchar(']');
            }
        }
        printf("],\"floyd\":[");
        for (int i = 0; i < g.n; ++i) {
            if (i) putchar(',');
            putchar('[');
            for (int j = 0; j < g.n; ++j) { if (j) putchar(','); json_number(all[i][j]); }
            putchar(']');
        }
        printf("],\"select_checks\":%u,\"matrix_checks\":%u}", r.select_checks, r.matrix_checks);
    } else {
        printf("%s: source=%c order=", name, g.labels[source]);
        for (int i = 0; i < r.count; ++i) putchar(g.labels[r.order[i]]);
        putchar('\n');
        for (int v = 0; v < g.n; ++v) {
            printf("  %c distance=", g.labels[v]);
            if (r.dist[v] == INF) printf("INF"); else printf("%lld", r.dist[v]);
            printf(" path=");
            int count = recover(&g, &r, source, v, path);
            if (count == -1) printf("unreachable");
            else {
                if (!count) return false;
                for (int i = 0; i < count; ++i) printf(i ? "->%c" : "%c", g.labels[path[i]]);
            }
            putchar('\n');
        }
        printf("  select checks=%u; matrix positions=%u\n", r.select_checks, r.matrix_checks);
    }
    return true;
}

int main(int argc, char **argv)
{
    const char *names[] = {"main", "exercise", "reverse", "unreachable", "zero_tie", "homework", "negative"};
    if (argc == 2 && !strcmp(argv[1], "--json")) {
        putchar('[');
        for (unsigned i = 0; i < sizeof(names) / sizeof(names[0]); ++i) {
            if (i) putchar(',');
            if (!run(names[i], true, false)) return EXIT_FAILURE;
        }
        puts("]");
        return EXIT_SUCCESS;
    }
    if (argc == 2 && !strcmp(argv[1], "all")) {
        for (unsigned i = 0; i < sizeof(names) / sizeof(names[0]); ++i)
            if (!run(names[i], false, false)) return EXIT_FAILURE;
        return EXIT_SUCCESS;
    }
    const bool trace = argc == 3 && !strcmp(argv[1], "--trace");
    const char *name = argc == 1 ? "main" : trace ? argv[2] : argv[1];
    if (argc > 3 || (argc == 3 && !trace) || !run(name, false, trace)) {
        fputs("usage: shortest_path_demo [main|exercise|reverse|unreachable|zero_tie|homework|negative|all|--json|--trace CASE]\n", stderr);
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
