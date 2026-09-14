/* Singly linked list: a class roster of student IDs.
 * Builds the list by tail insertion, inserts 104 in order, and deletes
 * one node, printing what happens at each step so the class can check:
 *   - insertion changes two links (successor first, then predecessor);
 *   - deletion is not finished until free returns the memory.
 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int id;
    struct Node *next;
} Node;

static Node *new_node(int id)
{
    Node *p = malloc(sizeof(Node));

    if (p == NULL) {
        printf("malloc failed\n");
        exit(1);
    }
    p->id = id;
    p->next = NULL;
    return p;
}

/* Append id at the tail of the list. */
static void append(Node **head, int id)
{
    Node *node = new_node(id);
    Node *p;

    if (*head == NULL) {
        *head = node;
        return;
    }
    for (p = *head; p->next != NULL; p = p->next) {
    }
    p->next = node;
}

/* Insert id keeping the list sorted; prints the two relinking steps. */
static void insert_sorted(Node **head, int id)
{
    Node *node = new_node(id);
    Node *p = *head;

    if (*head == NULL || (*head)->id > id) {
        node->next = *head;
        *head = node;
        return;
    }
    while (p->next != NULL && p->next->id < id) {
        p = p->next;
    }
    /* The order of the next two assignments matters:
     * link the successor first, then relink the predecessor. */
    printf("  step 1: new node %d points to its successor %d\n",
           id, p->next == NULL ? -1 : p->next->id);
    node->next = p->next;
    printf("  step 2: predecessor %d points to the new node %d\n", p->id, id);
    p->next = node;
}

/* Delete the first node with the given id; free completes the duty. */
static void delete_id(Node **head, int id)
{
    Node *p = *head;
    Node *victim;

    if (*head == NULL) {
        return;
    }
    if ((*head)->id == id) {
        victim = *head;
        *head = (*head)->next;
    } else {
        while (p->next != NULL && p->next->id != id) {
            p = p->next;
        }
        if (p->next == NULL) {
            printf("  id %d not found\n", id);
            return;
        }
        victim = p->next;
        p->next = victim->next;   /* unlink first */
    }
    printf("  unlinked node %d; now free returns its memory\n", id);
    free(victim);
}

static void print_list(const Node *head)
{
    const Node *p;

    printf("  roster:");
    for (p = head; p != NULL; p = p->next) {
        printf(" %d", p->id);
    }
    printf("\n");
}

static void free_list(Node *head)
{
    while (head != NULL) {
        Node *victim = head;

        head = head->next;
        free(victim);
    }
}

int main(void)
{
    Node *roster = NULL;
    int ids[8] = {101, 103, 105, 107, 109, 111, 113, 115};
    int i;

    for (i = 0; i < 8; ++i) {
        append(&roster, ids[i]);
    }
    printf("initial roster of 8 students (by ID):\n");
    print_list(roster);

    printf("\ninsert new student 104 in order (nobody moves!):\n");
    insert_sorted(&roster, 104);
    print_list(roster);

    printf("\ndelete student 109:\n");
    delete_id(&roster, 109);
    print_list(roster);

    free_list(roster);
    return 0;
}
