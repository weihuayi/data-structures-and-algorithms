/* D018: linear probing, tombstones and finite termination, C11. */
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

enum { CAP = 7 };
typedef enum { EMPTY, OCCUPIED, DELETED } SlotState;
typedef struct { int key; SlotState state; } Slot;
typedef struct { Slot slot[CAP]; } HashTable;
typedef enum { INSERTED, EXISTS, TABLE_FULL } InsertResult;
static void require(bool valid) {
    if (!valid) { fputs("D018 check failed\n", stderr); exit(EXIT_FAILURE); }
}

static unsigned start(int key) {
    /* The lesson deliberately limits keys to nonnegative integers. */
    require(key >= 0);
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
/* Chain-addressing example: head array and linked records, no dynamic allocation. */
typedef struct ChainNode {
    int key;
    struct ChainNode *next;
} ChainNode;
typedef struct {
    ChainNode *head[CAP];
    ChainNode node[4];
} ChainTable;
static void chain_reset(ChainTable *ct) { memset(ct, 0, sizeof(*ct)); }
static void chain_append(ChainTable *ct, unsigned slot, int key) {
    require(slot < 4);
    ChainNode *n = &ct->node[slot];
    n->key = key; n->next = NULL;
    ChainNode **link = &ct->head[start(key)];
    while (*link) link = &(*link)->next;
    *link = n;
}
static bool chain_find(const ChainTable *ct, int key, unsigned *comparisons) {
    *comparisons = 0;
    for (const ChainNode *n = ct->head[start(key)]; n != NULL; n = n->next) {
        ++*comparisons;
        if (n->key == key) return true;
    }
    return false;
}
static void chain_dump(const ChainTable *ct) {
    for (unsigned b = 0; b < CAP; ++b) {
        printf("bucket[%u] head -> ", b);
        for (const ChainNode *n = ct->head[b]; n != NULL; n = n->next)
            printf("%d -> ", n->key);
        puts("NULL");
    }
}
static void chain_self_test(void) {
    ChainTable ct; unsigned comparisons = 0;
    const int keys[] = {10, 17, 24, 13};
    chain_reset(&ct);
    for (unsigned i = 0; i < 4; ++i) chain_append(&ct, i, keys[i]);
    require(ct.head[3] == &ct.node[0]);
    require(ct.node[0].next == &ct.node[1]);
    require(ct.node[1].next == &ct.node[2]);
    require(ct.node[2].next == NULL);
    require(ct.head[6] == &ct.node[3]);
    require(chain_find(&ct, 24, &comparisons) && comparisons == 3);
    require(!chain_find(&ct, 31, &comparisons) && comparisons == 3);
}
static void chain_demo(void) {
    ChainTable ct; unsigned comparisons;
    const int keys[] = {10, 17, 24, 13};
    chain_reset(&ct);
    for (unsigned i = 0; i < 4; ++i) chain_append(&ct, i, keys[i]);
    puts("Chain table (append to bucket tail):");
    chain_dump(&ct);
    printf("chain find(24): %s", chain_find(&ct, 24, &comparisons) ? "HIT" : "MISS");
    printf(", comparisons=%u\n", comparisons);
    printf("chain find(31): %s", chain_find(&ct, 31, &comparisons) ? "HIT" : "MISS");
    printf(", comparisons=%u\n", comparisons);
}
static void build_demo(void) {
    HashTable t; reset(&t);
    const int keys[] = {10, 17, 24, 13};
    for (unsigned n = 0; n < 4; ++n) {
        int key = keys[n];
        printf("insert(%d): check ", key);
        for (unsigned i = 0; i < CAP; ++i) {
            unsigned p = position(key, i);
            printf("%s%u", i ? " -> " : "", p);
            if (t.slot[p].state == EMPTY) break;
        }
        puts(" (only checks so far)");
        require(insert(&t, key) == INSERTED);
        dump(&t); /* Actual write happens only after finding the empty slot. */
    }
}
static void scenario_demo(void) {
    HashTable correct, wrong; unsigned probes;
    const int keys[] = {10, 17, 24, 13};
    reset(&correct);
    for (unsigned i = 0; i < 4; ++i) require(insert(&correct, keys[i]) == INSERTED);
    puts("A: valid table before deletion:");
    dump(&correct);
    wrong = correct;
    wrong.slot[4].state = EMPTY; /* Deliberately INCORRECT deletion; never continue from W. */
    puts("W: WRONG deletion makes slot 4 EMPTY (counterexample only):");
    dump(&wrong);
    printf("W find(24): ");
    require(lookup(&wrong, 24, &probes, true) == -1 && probes == 2);
    puts("Return to A; do not use W as the next valid state.");
    require(erase(&correct, 17)); /* Tombstone preserves the search path. */
    puts("B: valid tombstone deletion:");
    dump(&correct);
    printf("B find(24): ");
    require(lookup(&correct, 24, &probes, true) == 5 && probes == 3);
    printf("B find(31): ");
    require(lookup(&correct, 31, &probes, true) == -1 && probes == 5);
    require(insert(&correct, 24) == EXISTS);
    require(insert(&correct, 31) == INSERTED);
    puts("C: after checking duplicates and inserting 31:");
    dump(&correct);
}
static void self_test(void) {
    HashTable t; unsigned probes; reset(&t);
    require(lookup(&t, 24, &probes, false) == -1 && probes == 1);
    require(insert(&t, 10) == INSERTED);
    require(insert(&t, 17) == INSERTED);
    require(insert(&t, 24) == INSERTED);
    require(insert(&t, 13) == INSERTED);
    require(t.slot[3].key == 10 && t.slot[4].key == 17 &&
           t.slot[5].key == 24 && t.slot[6].key == 13);
    /* Cross-check the classroom success and failure ASL numerators. */
    const int present[] = {10, 17, 24, 13};
    const unsigned succ[] = {1, 2, 3, 1};
    const unsigned miss[] = {1, 1, 1, 5, 4, 3, 2};
    unsigned succ_sum = 0, fail_sum = 0;
    for (unsigned i = 0; i < 4; ++i) {
        require(lookup(&t, present[i], &probes, false) >= 0);
        require(probes == succ[i]);
        succ_sum += probes;
    }
    for (unsigned r = 0; r < CAP; ++r) {
        require(lookup(&t, (int)(700 + r), &probes, false) == -1);
        require(probes == miss[r]);
        fail_sum += probes;
    }
    require(succ_sum == 7 && fail_sum == 17);
    /* An incorrect EMPTY deletion loses key 24 (intentional W counterexample). */
    HashTable wrong = t;
    wrong.slot[4].state = EMPTY;
    require(lookup(&wrong, 24, &probes, false) == -1 && probes == 2);
    require(t.slot[4].state == OCCUPIED); /* W never replaces valid A. */
    chain_self_test();
    require(lookup(&t, 24, &probes, false) == 5 && probes == 3);
    require(erase(&t, 17) && t.slot[4].state == DELETED);
    require(lookup(&t, 24, &probes, false) == 5 && probes == 3);
    require(lookup(&t, 31, &probes, false) == -1 && probes == 5);
    require(insert(&t, 24) == EXISTS);
    require(insert(&t, 31) == INSERTED && t.slot[4].key == 31);
    require(lookup(&t, 31, &probes, false) == 4 && probes == 2);
    require(!erase(&t, 99));
    require(insert(&t, 3) == INSERTED);
    require(insert(&t, 4) == INSERTED);
    require(insert(&t, 5) == INSERTED);
    require(insert(&t, 100) == TABLE_FULL);
    require(lookup(&t, 100, &probes, false) == -1 && probes == CAP);
    require(erase(&t, 13));
    require(insert(&t, 100) == INSERTED); /* Reuse tombstone in otherwise full table. */
    require(insert(&t, 100) == EXISTS);
    puts("D018 self-test: PASS");
}
static void demo(void) {
    HashTable t; unsigned probes; reset(&t);
    const int keys[] = {10, 17, 24, 13};
    for (unsigned i = 0; i < sizeof(keys)/sizeof(keys[0]); ++i)
        require(insert(&t, keys[i]) == INSERTED);
    puts("After insertion:"); dump(&t);
    printf("find(24): "); (void)lookup(&t, 24, &probes, true);
    printf("probes=%u\n", probes);
    require(erase(&t, 17)); puts("After erase(17):"); dump(&t);
    printf("find(24): "); (void)lookup(&t, 24, &probes, true);
    printf("probes=%u\n", probes);
    printf("find(31): "); (void)lookup(&t, 31, &probes, true);
    printf("probes=%u\n", probes);
    printf("insert(24) = %s\n", insert(&t, 24)==EXISTS ? "EXISTS" : "UNEXPECTED");
    printf("insert(31) = %s\n", insert(&t, 31)==INSERTED ? "INSERTED" : "UNEXPECTED");
    puts("After insert(31):"); dump(&t);
}
int main(int argc, char **argv) {
    if (argc == 1 || (argc == 2 && strcmp(argv[1], "demo") == 0)) demo();
    else if (argc == 2 && strcmp(argv[1], "build") == 0) build_demo();
    else if (argc == 2 && strcmp(argv[1], "chain") == 0) chain_demo();
    else if (argc == 2 && strcmp(argv[1], "scenarios") == 0) scenario_demo();
    else if (argc == 2 && strcmp(argv[1], "--self-test") == 0) self_test();
    else {
        fputs("usage: hash_demo [demo|build|chain|scenarios|--self-test]\n", stderr);
        return 2;
    }
    return 0;
}
