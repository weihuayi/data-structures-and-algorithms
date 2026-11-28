#include <stdio.h>
#include <string.h>

#define VERTEX_COUNT 7

typedef struct {
    int adjacent[VERTEX_COUNT][VERTEX_COUNT];
} Graph;

static void add_undirected_edge(Graph *g, int u, int v) {
    g->adjacent[u][v] = 1;
    g->adjacent[v][u] = 1;
}

/* BFS: returns 1 if target is reachable; parent[] reconstructs one shortest path. */
static int bfs(const Graph *g, int start, int target, int parent[]) {
    int visited[VERTEX_COUNT] = {0};
    int queue[VERTEX_COUNT];
    int head = 0, tail = 0;

    for (int i = 0; i < VERTEX_COUNT; ++i) parent[i] = -1;
    visited[start] = 1;
    queue[tail++] = start;

    while (head < tail) {
        int u = queue[head++];
        if (u == target) return 1;

        /* Ascending neighbor order makes the selected path deterministic. */
        for (int v = 0; v < VERTEX_COUNT; ++v) {
            if (g->adjacent[u][v] && !visited[v]) {
                visited[v] = 1; /* mark when enqueued, avoiding duplicate enqueue */
                parent[v] = u;
                queue[tail++] = v;
            }
        }
    }
    return visited[target];
}

static void print_path(int target, const int parent[]) {
    int reverse_path[VERTEX_COUNT];
    int length = 0;
    for (int v = target; v != -1 && length < VERTEX_COUNT; v = parent[v])
        reverse_path[length++] = v;

    printf("路径（%d 条边）：", length - 1);
    for (int i = length - 1; i >= 0; --i)
        printf("%d%s", reverse_path[i], i == 0 ? "\n" : " -> ");
}

static Graph make_graph(int close_e3) {
    Graph g = {{{0}}};
    add_undirected_edge(&g, 0, 1); /* E1 */
    add_undirected_edge(&g, 0, 2); /* E2 */
    if (!close_e3) add_undirected_edge(&g, 1, 4); /* E3 */
    add_undirected_edge(&g, 2, 3); /* E4 */
    add_undirected_edge(&g, 3, 5); /* E5 */
    add_undirected_edge(&g, 4, 5); /* E6 */
    add_undirected_edge(&g, 1, 2); /* E7 */
    return g;
}

static void run_case(const char *title, const Graph *g, int start, int target) {
    int parent[VERTEX_COUNT];
    printf("%s：%d -> %d\n", title, start, target);
    if (bfs(g, start, target, parent)) print_path(target, parent);
    else puts("不可达");
}

int main(void) {
    Graph original = make_graph(0);
    run_case("基础路网", &original, 0, 5);
    run_case("基础路网不可达测试", &original, 0, 6);

    Graph changed = make_graph(1); /* close E3 */
    run_case("关闭 E3 后", &changed, 0, 5);
    run_case("起点等于终点", &original, 2, 2);
    return 0;
}
