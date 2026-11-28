/*
 * Topic B: Campus road network and minimum-edge path analysis.
 * C11 reference implementation using an adjacency matrix and BFS.
 *
 * Build and run:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 topic_b_bfs.c -o topic_b
 *   ./topic_b
 *
 * Variants:
 *   -DCLOSE_E3=1       remove road E3 (1--4)
 *   -DTARGET_VERTEX=6  query the isolated vertex
 *   -DTARGET_VERTEX=0  query from the start vertex to itself
 */
#include <stdbool.h>
#include <stdio.h>

#ifndef CLOSE_E3
#define CLOSE_E3 0
#endif

#ifndef START_VERTEX
#define START_VERTEX 0
#endif

#ifndef TARGET_VERTEX
#define TARGET_VERTEX 5
#endif

#define VERTEX_COUNT 7

#if START_VERTEX < 0 || START_VERTEX >= VERTEX_COUNT
#error "START_VERTEX is outside the graph"
#endif
#if TARGET_VERTEX < 0 || TARGET_VERTEX >= VERTEX_COUNT
#error "TARGET_VERTEX is outside the graph"
#endif
#if CLOSE_E3 != 0 && CLOSE_E3 != 1
#error "CLOSE_E3 must be 0 or 1"
#endif

typedef struct {
    bool adjacent[VERTEX_COUNT][VERTEX_COUNT];
} Graph;

static void add_undirected_edge(Graph *graph, int u, int v)
{
    graph->adjacent[u][v] = true;
    graph->adjacent[v][u] = true;
}

static void build_campus_graph(Graph *graph)
{
    *graph = (Graph){0};
    add_undirected_edge(graph, 0, 1); /* E1 */
    add_undirected_edge(graph, 0, 2); /* E2 */
    if (!CLOSE_E3)
        add_undirected_edge(graph, 1, 4); /* E3 */
    add_undirected_edge(graph, 2, 3); /* E4 */
    add_undirected_edge(graph, 3, 5); /* E5 */
    add_undirected_edge(graph, 4, 5); /* E6 */
    add_undirected_edge(graph, 1, 2); /* E7 */
}

/*
 * BFS marks a vertex when it is enqueued, so each vertex enters the queue once.
 * Scanning matrix columns in ascending order makes the example deterministic.
 * Returns the number of vertices reached from source.
 */
static int breadth_first_search(const Graph *graph, int source,
                                bool visited[VERTEX_COUNT],
                                int parent[VERTEX_COUNT],
                                int order[VERTEX_COUNT])
{
    int queue[VERTEX_COUNT];
    int front = 0;
    int rear = 0;
    int order_count = 0;

    for (int v = 0; v < VERTEX_COUNT; ++v) {
        visited[v] = false;
        parent[v] = -1;
    }

    visited[source] = true;
    queue[rear++] = source;

    while (front < rear) {
        int u = queue[front++];
        order[order_count++] = u;

        for (int v = 0; v < VERTEX_COUNT; ++v) {
            if (graph->adjacent[u][v] && !visited[v]) {
                visited[v] = true;
                parent[v] = u;
                queue[rear++] = v;
            }
        }
    }

    return order_count;
}

static int recover_path(int source, int target,
                        const int parent[VERTEX_COUNT],
                        int path[VERTEX_COUNT])
{
    int reversed[VERTEX_COUNT];
    int length = 0;
    int current = target;

    while (current != -1 && length < VERTEX_COUNT) {
        reversed[length++] = current;
        if (current == source)
            break;
        current = parent[current];
    }

    if (length == 0 || reversed[length - 1] != source)
        return 0;

    for (int i = 0; i < length; ++i)
        path[i] = reversed[length - 1 - i];

    return length;
}

int main(void)
{
    Graph graph;
    bool visited[VERTEX_COUNT];
    int parent[VERTEX_COUNT];
    int order[VERTEX_COUNT];
    int path[VERTEX_COUNT];

    build_campus_graph(&graph);
    int order_count = breadth_first_search(&graph, START_VERTEX,
                                           visited, parent, order);

    printf("Graph: undirected and unweighted; E3 is %s.\n",
           CLOSE_E3 ? "closed" : "open");
    printf("BFS order from %d: ", START_VERTEX);
    for (int i = 0; i < order_count; ++i)
        printf("%s%d", i == 0 ? "" : " -> ", order[i]);
    putchar('\n');

    if (!visited[TARGET_VERTEX]) {
        printf("No path from %d to %d.\n", START_VERTEX, TARGET_VERTEX);
        return 0;
    }

    int path_length = recover_path(START_VERTEX, TARGET_VERTEX, parent, path);
    if (path_length == 0) {
        fputs("Internal error: failed to recover a reached vertex.\n", stderr);
        return 1;
    }

    printf("Minimum-edge path from %d to %d: ", START_VERTEX, TARGET_VERTEX);
    for (int i = 0; i < path_length; ++i)
        printf("%s%d", i == 0 ? "" : " -> ", path[i]);
    printf("\nMinimum edge count: %d\n", path_length - 1);

    puts("Parent array (-1 means source or not reached):");
    for (int v = 0; v < VERTEX_COUNT; ++v)
        printf("  %d: %d%s\n", v, parent[v], visited[v] ? " (reached)" : " (unreached)");

    return 0;
}