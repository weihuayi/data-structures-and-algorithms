/* D009 classroom demo. Legal finite binary trees only: no cycles/shared nodes.
 * Traversal does not modify links. IDs are printable single-byte characters.
 * Fixed buffers bound this demonstration to small inputs (CAP nodes).
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

enum { CAP = 32 };
typedef struct Node {
    char id;
    struct Node *left, *right;
} Node;
typedef enum { PRE, IN, POST } Order;
typedef struct {
    char text[CAP + 1];
    size_t used, limit;
} Output;
typedef struct {
    Node nodes[CAP];
    size_t used;
    Node *root;
} Tree;

/* On failure, a traversal's output may contain a prefix; caller must check it. */
static bool visit(const Node *p, Output *out)
{
    if (out->used >= out->limit || out->used >= CAP) return false;
    out->text[out->used++] = p->id;
    out->text[out->used] = '\0';
    return true;
}

static bool depth_first(const Node *p, Order order, Output *out)
{
    if (!p) return true;
    if (order == PRE && !visit(p, out)) return false;
    if (!depth_first(p->left, order, out)) return false;
    if (order == IN && !visit(p, out)) return false;
    if (!depth_first(p->right, order, out)) return false;
    if (order == POST && !visit(p, out)) return false;
    return true;
}

static bool push(const Node **stack, size_t *top, const Node *p)
{
    if (!p) return true;
    if (*top == CAP) return false;
    stack[(*top)++] = p;
    return true;
}

static bool preorder_stack(const Node *root, Output *out)
{
    const Node *stack[CAP];
    size_t top = 0;
    if (!push(stack, &top, root)) return false;
    while (top != 0) {
        const Node *p = stack[--top];
        if (!visit(p, out)) return false;
        if (!push(stack, &top, p->right)) return false;
        if (!push(stack, &top, p->left)) return false;
    }
    return true;
}

typedef struct {
    const Node *items[CAP];
    size_t front, count;
} Queue;

static bool enqueue(Queue *q, const Node *p)
{
    if (!p) return true;
    if (q->count == CAP) return false;
    q->items[(q->front + q->count) % CAP] = p;
    ++q->count;
    return true;
}

static bool level_order(const Node *root, Output *out)
{
    Queue q = {0};
    if (!enqueue(&q, root)) return false;
    while (q.count != 0) {
        const Node *p = q.items[q.front];
        q.front = (q.front + 1) % CAP;
        --q.count;
        if (!visit(p, out)) return false;
        if (!enqueue(&q, p->left) || !enqueue(&q, p->right)) return false;
    }
    return true;
}

static size_t leaves(const Node *p)
{
    if (!p) return 0;
    if (!p->left && !p->right) return 1;
    return leaves(p->left) + leaves(p->right);
}

static void mirror(Node *p)
{
    if (!p) return;
    Node *temp = p->left;
    p->left = p->right;
    p->right = temp;
    mirror(p->left);
    mirror(p->right);
}

static bool same_tree(const Node *a, const Node *b)
{
    if (!a || !b) return a == b;
    return a->id == b->id && same_tree(a->left, b->left)
                         && same_tree(a->right, b->right);
}

/* Linear search in each segment: O(n^2) worst-case time, O(h) recursion.
 * Output node pool uses O(n) occupied slots; storage reserves CAP slots.
 */
static bool build_segments(const char *pre, const char *in, size_t n,
                           Tree *tree, Node **root)
{
    if (n == 0) { *root = NULL; return true; }
    size_t k = 0;
    while (k < n && in[k] != pre[0]) ++k;
    if (k == n || tree->used == CAP) return false;
    Node *p = &tree->nodes[tree->used++];
    *p = (Node){pre[0], NULL, NULL};
    if (!build_segments(pre + 1, in, k, tree, &p->left)) return false;
    if (!build_segments(pre + 1 + k, in + 1 + k, n - 1 - k,
                        tree, &p->right)) return false;
    *root = p;
    return true;
}

/* Input strings must be NUL-terminated. Reject duplicate IDs and bad splits.
 * Failure resets root/used; no partial tree is exposed. Do not copy Tree by
 * value after construction: internal pointers refer to its own node pool.
 */
static bool restore(const char *pre, const char *in, Tree *tree)
{
    tree->used = 0;
    tree->root = NULL;
    size_t n = strlen(pre);
    if (n != strlen(in) || n > CAP) return false;
    for (size_t i = 0; i < n; ++i) {
        if (strchr(in, pre[i]) == NULL) return false;
        for (size_t j = 0; j < i; ++j)
            if (pre[i] == pre[j] || in[i] == in[j]) return false;
    }
    if (!build_segments(pre, in, n, tree, &tree->root)) {
        tree->used = 0;
        tree->root = NULL;
        return false;
    }
    return true;
}

static void expect(const Node *root, const char *pre, const char *in,
                   const char *post, const char *level, size_t leaf_count)
{
    const char *answers[] = {pre, in, post};
    for (int order = PRE; order <= POST; ++order) {
        Output out = {.limit = CAP};
        assert(depth_first(root, (Order)order, &out));
        assert(strcmp(out.text, answers[order]) == 0);
    }
    Output stack = {.limit = CAP}, queue = {.limit = CAP};
    assert(preorder_stack(root, &stack));
    assert(strcmp(stack.text, pre) == 0);
    assert(level_order(root, &queue));
    assert(strcmp(queue.text, level) == 0);
    assert(leaves(root) == leaf_count);
    Tree restored;
    assert(restore(pre, in, &restored));
    assert(same_tree(root, restored.root));
}

int main(void)
{
    Node d = {'D', NULL, NULL}, e = {'E', NULL, NULL};
    Node b = {'B', NULL, &d}, c = {'C', &e, NULL};
    Node a = {'A', &b, &c};
    expect(&a, "ABDCE", "BDAEC", "DBECA", "ABCDE", 2);
    expect(NULL, "", "", "", "", 0);
    expect(&d, "D", "D", "D", "D", 1);
    Node z = {'Z', NULL, NULL}, y = {'Y', &z, NULL}, x = {'X', &y, NULL};
    expect(&x, "XYZ", "ZYX", "ZYX", "XYZ", 1);
    mirror(&x);
    expect(&x, "XYZ", "XYZ", "ZYX", "XYZ", 1);
    mirror(&a);
    expect(&a, "ACEBD", "CEADB", "ECDBA", "ACBED", 2);
    mirror(&a);
    expect(&a, "ABDCE", "BDAEC", "DBECA", "ABCDE", 2);

    Tree exercise;
    assert(restore("PQSRT", "SQPRT", &exercise));
    expect(exercise.root, "PQSRT", "SQPRT", "SQTRP", "PQRST", 2);
    Tree bad;
    assert(!restore("AB", "A", &bad));
    assert(!restore("AB", "AC", &bad));
    assert(!restore("AA", "AA", &bad));
    assert(!restore("AB", "AA", &bad));
    assert(!restore("ABC", "CAB", &bad));
    assert(bad.root == NULL && bad.used == 0);
    char oversized[CAP + 2];
    memset(oversized, 'X', CAP + 1);
    oversized[CAP + 1] = '\0';
    assert(!restore(oversized, oversized, &bad));
    Output small = {.limit = 2};
    assert(!depth_first(&a, PRE, &small));
    small = (Output){.limit = 2};
    assert(!preorder_stack(&a, &small));
    small = (Output){.limit = 2};
    assert(!level_order(&a, &small));
    Queue full = {.count = CAP};
    assert(!enqueue(&full, &a));
    const Node *full_stack[CAP];
    size_t top = CAP;
    assert(!push(full_stack, &top, &a));
    Queue wrap = {.front = CAP - 1};
    assert(enqueue(&wrap, &a) && enqueue(&wrap, &b));
    assert(wrap.items[CAP - 1] == &a && wrap.items[0] == &b);

    const char *labels[] = {"pre", "in", "post"};
    for (int order = PRE; order <= POST; ++order) {
        Output out = {.limit = CAP};
        if (!depth_first(&a, (Order)order, &out)) return 1;
        printf("%s=%s\n", labels[order], out.text);
    }
    Output stack = {.limit = CAP}, queue = {.limit = CAP};
    if (!preorder_stack(&a, &stack) || !level_order(&a, &queue)) return 1;
    printf("stack-pre=%s\nlevel=%s\nleaves=%zu\n", stack.text, queue.text, leaves(&a));
    mirror(&a);
    Output reflected = {.limit = CAP};
    if (!depth_first(&a, PRE, &reflected)) return 1;
    printf("mirror-pre=%s\n", reflected.text);
    mirror(&a);
    Output rebuilt_post = {.limit = CAP}, rebuilt_level = {.limit = CAP};
    if (!depth_first(exercise.root, POST, &rebuilt_post)
        || !level_order(exercise.root, &rebuilt_level)) return 1;
    printf("restore(PQSRT,SQPRT): post=%s level=%s\n",
           rebuilt_post.text, rebuilt_level.text);
    printf("restore(ABC,CAB): %s\n",
           restore("ABC", "CAB", &bad) ? "accepted" : "rejected");
    /* Homework: move D to the left of B; preserve the fixed main example. */
    Node variant_b = {'B', &d, NULL};
    Node variant_a = {'A', &variant_b, &c};
    expect(&variant_a, "ABDCE", "DBAEC", "DBECA", "ABCDE", 2);
    for (int order = PRE; order <= POST; ++order) {
        Output out = {.limit = CAP};
        if (!depth_first(&variant_a, (Order)order, &out)) return 1;
        printf("variant-%s=%s\n", labels[order], out.text);
    }
    Output variant_level = {.limit = CAP};
    if (!level_order(&variant_a, &variant_level)) return 1;
    printf("variant-level=%s\n", variant_level.text);
    puts("All classroom checks passed.");
    return 0;
}
