/* D018: linear probing, tombstones and finite termination, C11. */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

enum { CAP = 7 };
typedef enum { EMPTY, OCCUPIED, DELETED } SlotState;
typedef struct { int key; SlotState state; } Slot;
typedef struct { Slot slot[CAP]; } HashTable;
typedef enum { INSERTED, EXISTS, TABLE_FULL } InsertResult;

static unsigned start(int key) {
    /* The lesson deliberately limits keys to nonnegative integers. */
    assert(key >= 0);
    return (unsigned)key % CAP;
}
static unsigned position(int key, unsigned probe) {
    return (start(key) + probe) % CAP;
}
static void reset(HashTable *t) { memset(t, 0, sizeof(*t)); }
static const char *state_name(SlotState s) {
    return s == EMPTY ? "EMPTY" : s == OCCUPIED ? "OCCUPIED" : "DELETED";
}
static int lookup(const HashTable *t, int key, unsigned *probes, bool trace) {
    *probes = 0;
    for (unsigned i = 0; i < CAP; ++i) {
        unsigned p = position(key, i);
        ++*probes;
        if (trace) printf("%s%u", i ? " -> " : "", p);
        if (t->slot[p].state == EMPTY) {
            if (trace) puts(" [EMPTY, miss]");
            return -1;
        }
        if (t->slot[p].state == OCCUPIED && t->slot[p].key == key) {
            if (trace) puts(" [hit]");
            return (int)p;
        }
    }
    if (trace) puts(" [bounded miss]");
    return -1;
}
static InsertResult insert(HashTable *t, int key) {
    int first_deleted = -1;
    for (unsigned i = 0; i < CAP; ++i) {
        unsigned p = position(key, i);
        Slot *s = &t->slot[p];
        if (s->state == OCCUPIED && s->key == key) return EXISTS;
        if (s->state == DELETED && first_deleted == -1) first_deleted = (int)p;
        if (s->state == EMPTY) {
            unsigned where = first_deleted < 0 ? p : (unsigned)first_deleted;
            t->slot[where] = (Slot){ key, OCCUPIED };
            return INSERTED;
        }
    }
    if (first_deleted != -1) {
        t->slot[first_deleted] = (Slot){ key, OCCUPIED };
        return INSERTED;
    }
    return TABLE_FULL;
}
static bool erase(HashTable *t, int key) {
    unsigned probes = 0;
    int p = lookup(t, key, &probes, false);
    if (p < 0) return false;
    t->slot[p].state = DELETED;
    return true;
}
static void dump(const HashTable *t) {
    for (unsigned i = 0; i < CAP; ++i)
        if (t->slot[i].state == OCCUPIED)
            printf("%u:%d%s", i, t->slot[i].key, i == CAP-1 ? "" : "  ");
        else
            printf("%u:%s%s", i, state_name(t->slot[i].state),
                   i == CAP-1 ? "" : "  ");
    puts("");
}
static void self_test(void) {
    HashTable t; unsigned probes; reset(&t);
    assert(lookup(&t, 24, &probes, false) == -1 && probes == 1);
    assert(insert(&t, 10) == INSERTED);
    assert(insert(&t, 17) == INSERTED);
    assert(insert(&t, 24) == INSERTED);
    assert(insert(&t, 13) == INSERTED);
    assert(t.slot[3].key == 10 && t.slot[4].key == 17 &&
           t.slot[5].key == 24 && t.slot[6].key == 13);
    assert(lookup(&t, 24, &probes, false) == 5 && probes == 3);
    assert(erase(&t, 17) && t.slot[4].state == DELETED);
    assert(lookup(&t, 24, &probes, false) == 5 && probes == 3);
    assert(lookup(&t, 31, &probes, false) == -1 && probes == 5);
    assert(insert(&t, 24) == EXISTS);
    assert(insert(&t, 31) == INSERTED && t.slot[4].key == 31);
    assert(lookup(&t, 31, &probes, false) == 4 && probes == 2);
    assert(!erase(&t, 99));
    assert(insert(&t, 3) == INSERTED);
    assert(insert(&t, 4) == INSERTED);
    assert(insert(&t, 5) == INSERTED);
    assert(insert(&t, 100) == TABLE_FULL);
    assert(lookup(&t, 100, &probes, false) == -1 && probes == CAP);
    assert(erase(&t, 13));
    assert(insert(&t, 100) == INSERTED); /* Reuse tombstone in otherwise full table. */
    assert(insert(&t, 100) == EXISTS);
    puts("D018 self-test: PASS");
}
static void demo(void) {
    HashTable t; unsigned probes; reset(&t);
    const int keys[] = {10, 17, 24, 13};
    for (unsigned i = 0; i < sizeof(keys)/sizeof(keys[0]); ++i)
        assert(insert(&t, keys[i]) == INSERTED);
    puts("After insertion:"); dump(&t);
    printf("find(24): "); (void)lookup(&t, 24, &probes, true);
    printf("probes=%u\n", probes);
    assert(erase(&t, 17)); puts("After erase(17):"); dump(&t);
    printf("find(24): "); (void)lookup(&t, 24, &probes, true);
    printf("probes=%u\n", probes);
    printf("find(31): "); (void)lookup(&t, 31, &probes, true);
    printf("probes=%u\n", probes);
    printf("insert(24) = %s\n", insert(&t, 24)==EXISTS ? "EXISTS" : "UNEXPECTED");
    printf("insert(31) = %s\n", insert(&t, 31)==INSERTED ? "INSERTED" : "UNEXPECTED");
    puts("After insert(31):"); dump(&t);
}
int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--self-test") == 0) self_test();
    else if (argc == 1 || (argc > 1 && strcmp(argv[1], "demo") == 0)) demo();
    else { fputs("usage: hash_demo [demo|--self-test]\n", stderr); return 2; }
    return 0;
}
