/* D020 reproducible C11 demo: heap, stable merge and linked-bucket LSD radix.
 * Student may copy the file into any local directory and compile with -std=c11.
 * Mathematics, code output and actual student understanding require separate review.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <errno.h>

typedef struct {
    int key;
    char id;
} Record;

static void swap_int(int *a, int *b) {
    const int t = *a;
    *a = *b;
    *b = t;
}

static void sift_down(int a[], int root, int size) {
    int i = root;
    while (2 * i + 1 < size) {
        int c = 2 * i + 1;
        if (c + 1 < size && a[c + 1] > a[c]) {
            c++;
        }
        if (a[i] >= a[c]) {
            break;
        }
        swap_int(&a[i], &a[c]);
        i = c;
    }
}

static void build_heap(int a[], int size) {
    for (int i = size / 2 - 1; i >= 0; i--) {
        sift_down(a, i, size);
    }
}

static int heap_valid(const int a[], int size) {
    for (int i = 1; i < size; i++) {
        if (a[(i - 1) / 2] < a[i]) {
            return 0;
        }
    }
    return 1;
}

static void print_ints(const char *title, const int a[], int n, int border) {
    printf("%s:", title);
    for (int i = 0; i < n; i++) {
        if (i == border) printf(" |");
        printf(" %d", a[i]);
    }
    putchar('\n');
}

static void heap_example(void) {
    int a[] = {4, 1, 7, 3, 6, 2, 5};
    const int n = (int)(sizeof(a) / sizeof(a[0]));
    print_ints("P1 initial", a, n, n);
    build_heap(a, n);
    print_ints("P1 built", a, n, n);
    swap_int(&a[0], &a[n - 1]);
    sift_down(a, 0, n - 1);
    print_ints("P1 after extract", a, n, n - 1);
}

static int merge_sorted(const Record a[], int na,
                        const Record b[], int nb, Record out[]) {
    int i = 0;
    int j = 0;
    int k = 0;
    while (i < na && j < nb) {
        /* Equality chooses left: preserves origin order for contiguous halves. */
        if (a[i].key <= b[j].key) {
            out[k++] = a[i++];
        } else {
            out[k++] = b[j++];
        }
    }
    while (i < na) out[k++] = a[i++];
    while (j < nb) out[k++] = b[j++];
    return k;
}

static void print_records(const char *title, const Record a[], int n) {
    printf("%s:", title);
    for (int i = 0; i < n; i++) {
        printf(" (%d,%c)", a[i].key, a[i].id);
    }
    putchar('\n');
}

static void merge_example(void) {
    const Record left[] = {{2, 'a'}, {5, 'b'}, {8, 'e'}};
    const Record right[] = {{2, 'c'}, {6, 'd'}, {7, 'f'}};
    Record out[6];
    merge_sorted(left, 3, right, 3, out);
    print_records("P2 stable merge", out, 6);
    puts("Equal keys: a precedes c, preserving original left/right order.");
}

/* Linked distribution: every input element becomes a node in a bucket chain.
 * No input record is lost: next[i] is a link index or -1 for end of chain.
 */
static void radix_lsd(Record a[], int n, int digits) {
    /* This teaching implementation uses fixed buffers of 32 records.
     * Reject unsupported inputs instead of silently truncating higher digits
     * or indexing buckets with negative values. */
    int maximum_digits = 1;
    for (unsigned long long v = (unsigned long long)INT_MAX; v >= 10ULL; v /= 10ULL) {
        maximum_digits++;
    }
    if (n < 0 || n > 32 || digits < 1 || digits > maximum_digits) {
        fputs("Radix requires 0..32 records and a valid C-int decimal digit count\n", stderr);
        exit(EXIT_FAILURE);
    }
    int largest = 0;
    for (int i = 0; i < n; i++) {
        if (a[i].key < 0) {
            fputs("Radix requires nonnegative integer keys\n", stderr);
            exit(EXIT_FAILURE);
        }
        if (a[i].key > largest) largest = a[i].key;
    }
    int needed = 1;
    while (largest >= 10) { largest /= 10; needed++; }
    if (digits < needed) {
        fputs("Radix digits do not cover the entire key\n", stderr);
        exit(EXIT_FAILURE);
    }
    unsigned long long divisor = 1ULL;
    for (int digit = 0; digit < digits; digit++) {
        int head[10];
        int tail[10];
        int next[32];
        Record out[32];
        for (int b = 0; b < 10; b++) {
            head[b] = -1;
            tail[b] = -1;
        }
        for (int i = 0; i < n; i++) {
            const int b = (int)(((unsigned long long)(unsigned int)a[i].key / divisor) % 10ULL);
            next[i] = -1;
            if (head[b] == -1) {
                head[b] = i;
            } else {
                next[tail[b]] = i;
            }
            tail[b] = i;
        }
        int output = 0;
        for (int b = 0; b < 10; b++) {
            for (int i = head[b]; i != -1; i = next[i]) {
                out[output++] = a[i];
            }
        }
        if (output != n) {
            fputs("Radix invariant violated: lost record\n", stderr);
            exit(EXIT_FAILURE);
        }
        for (int i = 0; i < n; i++) a[i] = out[i];
        if (digit + 1 < digits) divisor *= 10ULL;
        print_records("LSD after stable bucket collection", a, n);
    }
}

static void radix_example(void) {
    Record a[] = {{21, 'A'}, {13, 'B'}, {12, 'C'}, {22, 'D'}};
    print_records("LSD input", a, 4);
    radix_lsd(a, 4, 2);
}

/* Deterministic self-tests check the *specified* implementation, not
 * every mathematically valid heap representation or classroom understanding. */
/* A new input, independent of classroom P1, is supplied through the CLI. */
static int heap_custom(int argc, char **argv) {
    const int n = argc - 2;
    int a[32];
    if (n < 2 || n > 32) {
        fputs("heap expects 2..32 integer keys\n", stderr);
        return 2;
    }
    for (int i = 0; i < n; i++) {
        char *end = NULL;
        errno = 0;
        const long key = strtol(argv[i + 2], &end, 10);
        if (errno != 0 || end == argv[i + 2] || *end != '\0' ||
            key < INT_MIN || key > INT_MAX) {
            fputs("heap keys must be valid C int values\n", stderr);
            return 2;
        }
        a[i] = (int)key;
    }
    print_ints("Custom heap input", a, n, n);
    build_heap(a, n);
    if (!heap_valid(a, n)) {
        fputs("heap validation failed\n", stderr);
        return 1;
    }
    print_ints("Custom heap built", a, n, n);
    swap_int(&a[0], &a[n-1]);
    sift_down(a, 0, n-1);
    if (!heap_valid(a, n-1)) {
        fputs("remaining heap validation failed\n", stderr);
        return 1;
    }
    print_ints("Custom heap after extract", a, n, n-1);
    return 0;
}

static int self_test(void) {
    int a[] = {4, 1, 7, 3, 6, 2, 5};
    const int built[] = {7, 6, 5, 3, 1, 2, 4};
    const int extracted[] = {6, 4, 5, 3, 1, 2, 7};
    const int n = 7;
    build_heap(a, n);
    if (!heap_valid(a, n) || memcmp(a, built, sizeof(a)) != 0) {
        fputs("Heap build failure\n", stderr);
        return 1;
    }
    swap_int(&a[0], &a[6]);
    sift_down(a, 0, 6);
    if (!heap_valid(a, 6) || memcmp(a, extracted, sizeof(a)) != 0) {
        fputs("Heap extract failure\n", stderr);
        return 1;
    }

    const Record left[] = {{2, 'a'}, {5, 'b'}, {8, 'e'}};
    const Record right[] = {{2, 'c'}, {6, 'd'}, {7, 'f'}};
    const Record expected_merge[] = {
        {2, 'a'}, {2, 'c'}, {5, 'b'}, {6, 'd'}, {7, 'f'}, {8, 'e'}
    };
    Record result[6];
    if (merge_sorted(left, 3, right, 3, result) != 6) {
        fputs("Merge size failure\n", stderr);
        return 1;
    }
    for (int i = 0; i < 6; i++) {
        if (result[i].key != expected_merge[i].key ||
            result[i].id != expected_merge[i].id) {
            fputs("Stable merge failure\n", stderr);
            return 1;
        }
    }

    Record radix[] = {{21, 'A'}, {13, 'B'}, {12, 'C'}, {22, 'D'}};
    const Record expected_radix[] = {{12, 'C'}, {13, 'B'}, {21, 'A'}, {22, 'D'}};
    radix_lsd(radix, 4, 2);
    for (int i = 0; i < 4; i++) {
        if (radix[i].key != expected_radix[i].key ||
            radix[i].id != expected_radix[i].id) {
            fputs("Radix FIFO failure\n", stderr);
            return 1;
        }
    }

    /* The prerequisite counterexample: root-down alone does not build a heap. */
    int bad[] = {2, 5, 7, 3, 4, 6, 8};
    sift_down(bad, 0, 7);
    if (heap_valid(bad, 7)) {
        fputs("Counterexample unexpectedly became a heap\n", stderr);
        return 1;
    }

    puts("D020 C11 self-test PASS: heap, stable merge, linked radix and false-precondition case.");
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s heap [int ...]|merge|radix|--self-test\n", argv[0]);
        return 2;
    }
    if (strcmp(argv[1], "heap") == 0) {
        if (argc > 2) return heap_custom(argc, argv);
        heap_example();
    } else if (argc != 2) {
        fprintf(stderr, "Usage: %s heap [int ...]|merge|radix|--self-test\n", argv[0]);
        return 2;
    } else if (strcmp(argv[1], "merge") == 0) {
        merge_example();
    } else if (strcmp(argv[1], "radix") == 0) {
        radix_example();
    } else if (strcmp(argv[1], "--self-test") == 0) {
        return self_test();
    } else {
        fprintf(stderr, "Unknown mode: %s\n", argv[1]);
        return 2;
    }
    return 0;
}
