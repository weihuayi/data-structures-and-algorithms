/* D008: representation checks, not a general-purpose tree library.
 * Build: gcc -std=c11 -Wall -Wextra tree_demo.c -o /tmp/d008-tree
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct Node {
    char data;
    struct Node *left;
    struct Node *right;
} Node;

typedef struct {
    /* max_position is meaningful only when nodes > 0. */
    size_t nodes, leaves, height, max_position, degree_two;
} Stats;

/* Precondition: a finite tree with no cycles or shared nodes. All complete-tree
 * positions start at zero; position numbers must fit in size_t. Classroom inputs have height <= 4.
 * D009 will unpack this recursive visit. NULL has height zero.
 */
static Stats inspect(const Node *node, size_t position)
{
    if (node == NULL) return (Stats){0, 0, 0, 0, 0};
    Stats l = node->left ? inspect(node->left, 2 * position + 1) : (Stats){0};
    Stats r = node->right ? inspect(node->right, 2 * position + 2) : (Stats){0};
    size_t deepest_position = l.max_position > r.max_position
                            ? l.max_position : r.max_position;
    return (Stats){
        1 + l.nodes + r.nodes,
        (!node->left && !node->right) + l.leaves + r.leaves,
        1 + (l.height > r.height ? l.height : r.height),
        position > deepest_position ? position : deepest_position,
        (node->left != NULL && node->right != NULL) + l.degree_two + r.degree_two
    };
}

/* Root sentinel: -1. IDs: 0 .. n-1. A bounded parent walk detects cycles.
 * O(n^2) worst-case time, O(1) auxiliary space; intended for tiny examples.
 */
static bool valid_parents(const int *parent, size_t n)
{
    if (n == 0) return true;
    if (parent == NULL) return false;
    size_t roots = 0;
    for (size_t i = 0; i < n; ++i) {
        if (parent[i] == -1) ++roots;
        else if (parent[i] < 0 || (size_t)parent[i] >= n) return false;
    }
    if (roots != 1) return false;
    for (size_t i = 0; i < n; ++i) {
        size_t current = i, steps = 0;
        while (parent[current] != -1) {
            if (++steps >= n) return false;
            current = (size_t)parent[current];
        }
    }
    return true;
}

static void check(const Node *root, size_t n, size_t leaves,
                  size_t height, size_t position)
{
    Stats s = inspect(root, 0);
    assert(s.nodes == n && s.leaves == leaves);
    assert(s.height == height && s.max_position == position);
    if (root) assert(s.leaves == s.degree_two + 1);
}

static void show(const char *label, const Node *root)
{
    Stats s = inspect(root, 0);
    printf("%s: n=%zu leaves=%zu height=%zu max_position=",
           label, s.nodes, s.leaves, s.height);
    if (s.nodes) printf("%zu\n", s.max_position);
    else puts("none");
}

int main(void)
{
    Node a = {'a', NULL, NULL}, b = {'b', NULL, NULL};
    Node minus = {'-', &a, &b};
    Node c = {'c', NULL, NULL}, d = {'d', NULL, NULL};
    Node plus = {'+', &c, &d};
    Node root = {'*', &minus, &plus};
    Node chain[4] = {{'A', NULL, NULL}, {'B', NULL, NULL},
                     {'C', NULL, NULL}, {'D', NULL, NULL}};
    for (size_t i = 0; i < 3; ++i) chain[i].right = &chain[i + 1];

    check(&root, 7, 4, 3, 6);
    check(chain, 4, 1, 4, 14);
    check(NULL, 0, 0, 0, 0);
    check(&a, 1, 1, 1, 0);
    Node left_only = {'L', &a, NULL}, right_only = {'R', NULL, &a};
    check(&left_only, 2, 1, 2, 1);
    check(&right_only, 2, 1, 2, 2);
    Node pruned = {'*', &minus, NULL};
    check(&pruned, 4, 2, 3, 4);

    const int parents[] = {-1, 0, 0, 1, 1, 2, 2};
    const int cycle[] = {-1, 3, 0, 1, 1, 2, 2};
    const int two_roots[] = {-1, -1};
    const int out_of_range[] = {-1, 2};
    const int negative[] = {-1, -2};
    const int self_cycle[] = {-1, 1};
    const int no_root[] = {1, 0};
    const int single[] = {-1};
    assert(valid_parents(parents, 7));
    assert(valid_parents(single, 1));
    assert(valid_parents(NULL, 0));
    assert(!valid_parents(NULL, 1));
    assert(!valid_parents(cycle, 7));
    assert(!valid_parents(two_roots, 2));
    assert(!valid_parents(out_of_range, 2));
    assert(!valid_parents(negative, 2));
    assert(!valid_parents(self_cycle, 2));
    assert(!valid_parents(no_root, 2));

    /* EXPERIMENT: edit only this root's links, not the shared child nodes. */
    Node experiment = root;
    /* Set experiment.right = NULL here after recording a prediction. */
    show("experiment", &experiment);

    show("expression", &root);
    show("right-chain", chain);
    show("empty", NULL);
    printf("parent-cycle: %s\n", valid_parents(cycle, 7) ? "accepted" : "rejected");
    puts("All classroom checks passed.");
    return 0;
}
