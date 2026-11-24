/* Independent model-oriented checks for the D020 C11 teaching demo.
 * The reference sorts do not call the implementation under test.
 * Compile with:
 * gcc -std=c11 -Wall -Wextra -Werror -pedantic -fsanitize=undefined -fno-sanitize-recover=all \
 *   tests/test_professional_oracles.c -o /tmp/d020_oracles && /tmp/d020_oracles
 */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#define main d020_original_demo_main
#include "../code/sorting_d020_demo.c"
#undef main

static unsigned int seed = 20261124U;
static unsigned int rand_deterministic(void) {
    seed = 1664525U * seed + 1013904223U; /* unsigned wrap is intentional */
    return seed;
}
static int compare_int(const void *x, const void *y) {
    const int a = *(const int *)x;
    const int b = *(const int *)y;
    return (a > b) - (a < b);
}
static void validate_heap(const int *input, int n) {
    int a[32], expected[32];
    memcpy(a, input, (size_t)n * sizeof(int));
    memcpy(expected, input, (size_t)n * sizeof(int));
    qsort(expected, (size_t)n, sizeof(int), compare_int);
    build_heap(a, n);
    assert(heap_valid(a, n));
    qsort(a, (size_t)n, sizeof(int), compare_int);
    for (int i = 0; i < n; i++) assert(a[i] == expected[i]);
    memcpy(a, input, (size_t)n * sizeof(int));
    build_heap(a, n);
    if (n >= 2) {
        swap_int(&a[0], &a[n-1]);
        sift_down(a, 0, n-1);
        assert(heap_valid(a, n-1));
        assert(a[n-1] == expected[n-1]);
    }
}
static void stable_reference(Record *a, int n) {
    for (int i = 1; i < n; i++) {
        const Record v = a[i];
        int j = i;
        while (j > 0 && a[j-1].key > v.key) {
            a[j] = a[j-1]; --j;
        }
        a[j] = v; /* equality does not move old records */
    }
}
static void compare_records(const Record *got, const Record *expected, int n) {
    for (int i = 0; i < n; i++) {
        assert(got[i].key == expected[i].key);
        assert(got[i].id == expected[i].id);
    }
}
static void validate_merge_case(const int *lk, int nl, const int *rk, int nr) {
    Record l[32], r[32], expect[64], got[64];
    for (int i = 0; i < nl; i++) {
        l[i] = (Record){lk[i], (char)('!' + i)};
        expect[i] = l[i];
    }
    for (int j = 0; j < nr; j++) {
        r[j] = (Record){rk[j], (char)('A' + j)};
        expect[nl + j] = r[j];
    }
    stable_reference(expect, nl + nr);
    assert(merge_sorted(l,nl,r,nr,got) == nl + nr);
    compare_records(got,expect,nl+nr);
}
static void validate_radix_case(const int *keys, int n, int digits) {
    Record actual[32], expected[32];
    for (int i = 0; i < n; i++) {
        actual[i] = (Record){keys[i], (char)('!' + i)};
        expected[i] = actual[i];
    }
    stable_reference(expected, n);
    radix_lsd(actual,n,digits);
    compare_records(actual,expected,n);
}
int main(void) {
    const int repeated[] = {INT_MIN, 0, INT_MAX, -1, 1, 0, INT_MIN, INT_MAX};
    validate_heap(repeated,8);
    for (int n = 0; n <= 32; n++) {
        int a[32];
        for (int i = 0; i < n; i++) a[i] = (int)(rand_deterministic() % 23U)-11;
        validate_heap(a,n);
    }
    const int l[] = {2,2,5,8}, r[] = {1,2,2,6};
    validate_merge_case(l,4,r,4);
    validate_merge_case(l,0,r,4);
    validate_merge_case(l,4,r,0);
    validate_merge_case(l,0,r,0);
    const int extreme[] = {INT_MAX, 0, 100, INT_MAX, 1, 0, 2147483646};
    validate_radix_case(extreme,7,10);
    const int zeroes[] = {0,0,0,0};
    validate_radix_case(zeroes,4,1);
    for (int n = 0; n <= 32; n += 4) {
        int a[32];
        for (int i = 0; i < n; i++) a[i] = (int)(rand_deterministic() % 1000U);
        validate_radix_case(a,n,3);
    }
    puts("PASS independent C11 oracle checks: heap, stable merge, linked radix (including INT_MAX and duplicate keys)");
    return 0;
}
