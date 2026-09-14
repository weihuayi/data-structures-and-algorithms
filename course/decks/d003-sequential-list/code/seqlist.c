/* Sequential list with fixed capacity: a class roster of student IDs.
 * insert/delete report how many elements were moved, so the class can
 * check the prediction "inserting at position i moves n - i + 1 elements".
 */
#include <stdio.h>

#define CAPACITY 10

typedef struct {
    int data[CAPACITY];
    int length;
} SeqList;

static void init(SeqList *list)
{
    list->length = 0;
}

/* Insert value so that it becomes the pos-th element (1-based).
 * Returns the number of moved elements, or -1 when rejected. */
static int insert(SeqList *list, int pos, int value)
{
    int j;
    int moved = 0;

    if (list->length >= CAPACITY) {
        printf("  list is full (capacity %d); insert of %d rejected\n",
               CAPACITY, value);
        return -1;
    }
    if (pos < 1 || pos > list->length + 1) {
        printf("  illegal position %d; insert of %d rejected\n", pos, value);
        return -1;
    }
    for (j = list->length; j >= pos; --j) {
        list->data[j] = list->data[j - 1];
        ++moved;
    }
    list->data[pos - 1] = value;
    ++list->length;
    return moved;
}

/* Delete the pos-th element (1-based).
 * Returns the number of moved elements, or -1 when rejected. */
static int delete_at(SeqList *list, int pos)
{
    int j;
    int moved = 0;

    if (pos < 1 || pos > list->length) {
        printf("  illegal position %d; delete rejected\n", pos);
        return -1;
    }
    for (j = pos; j < list->length; ++j) {
        list->data[j - 1] = list->data[j];
        ++moved;
    }
    --list->length;
    return moved;
}

static void print_list(const SeqList *list)
{
    int j;

    printf("  roster (length %d):", list->length);
    for (j = 0; j < list->length; ++j) {
        printf(" %d", list->data[j]);
    }
    printf("\n");
}

int main(void)
{
    SeqList roster;
    int ids[8] = {101, 103, 105, 107, 109, 111, 113, 115};
    int i;
    int moved;

    init(&roster);
    for (i = 0; i < 8; ++i) {
        insert(&roster, roster.length + 1, ids[i]);
    }
    printf("initial roster of 8 students (by ID):\n");
    print_list(&roster);

    printf("\ninsert new student 104 at position 3\n");
    printf("  prediction: move n - i + 1 = 8 - 3 + 1 = 6 elements\n");
    moved = insert(&roster, 3, 104);
    printf("  actual moves: %d\n", moved);
    print_list(&roster);

    printf("\ndelete the student at position 6\n");
    printf("  prediction: move n - i = 9 - 6 = 3 elements\n");
    moved = delete_at(&roster, 6);
    printf("  actual moves: %d\n", moved);
    print_list(&roster);

    printf("\nfill the list to capacity %d, then try one more insert\n", CAPACITY);
    insert(&roster, roster.length + 1, 117);
    insert(&roster, roster.length + 1, 119);
    print_list(&roster);
    insert(&roster, roster.length + 1, 121);

    return 0;
}
