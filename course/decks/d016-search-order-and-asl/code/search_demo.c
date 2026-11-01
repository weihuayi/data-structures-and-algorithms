/* D016, C11: query cost counts examined record keys, not relational operators.
 * Preconditions: 0<=n<=MAXN, valid storage; binary input nondecreasing.
 * The CLI validates stdin once, outside the query. Query routines do not sort.
 */
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { MAXN = 256 };
typedef struct { int low, high, mid, value; } Probe;
typedef struct {
    Probe steps[MAXN];
    int count, index_count, selected;
} Trace;
static const int main_keys[] = {5,16,20,27,30,36,44,55,60,67,71};
static const int miss_keys[] = {4,10,18,23,28,33,40,49,57,63,69,72};
static const int block_keys[] = {16,5,20,36,27,30,44,71,55,67,60};
static const int maxima[] = {20,36,71};
static const int starts[] = {0,3,6};

static void init(Trace *t) { t->count=0; t->index_count=0; t->selected=-1; }
static void probe(Trace *t, int low, int high, int mid, int value) {
    t->steps[t->count++] = (Probe){low,high,mid,value};
}
static int sequential_find(const int a[], int n, int key, Trace *t) {
    for (int i=0;i<n;i++) {
        probe(t,i,n-1,i,a[i]);
        if (a[i]==key) return i;
    }
    return -1;
}
static int binary_find(const int a[], int n, int key, Trace *t) {
    int low=0, high=n-1;
    while (low<=high) {
        int mid=low+(high-low)/2;
        probe(t,low,high,mid,a[mid]);
        if (a[mid]==key) return mid;
        if (a[mid]<key) low=mid+1;
        else high=mid-1;
    }
    return -1;
}
static int block_find(int key, Trace *t) {
    for (int b=0;b<3;b++) {
        t->index_count++;
        if (key<=maxima[b]) {
            t->selected=b;
            int end=(b+1<3 ? starts[b+1] : 11);
            for (int i=starts[b];i<end;i++) {
                probe(t,starts[b],end-1,i,block_keys[i]);
                if (block_keys[i]==key) return i;
            }
            return -1;
        }
    }
    return -1;
}
static int integer(const char *s, int *out) {
    char *end;
    errno=0;
    long v=strtol(s,&end,10);
    if (errno || end==s || *end || v<INT_MIN || v>INT_MAX) return 0;
    *out=(int)v; return 1;
}
static int read_integer(int *out) {
    char text[80];
    return scanf("%79s",text)==1 && integer(text,out);
}
static void print_result(int result, const Trace *t, int json) {
    if (json) {
        printf("{\"valid\":true,\"result\":%d,\"probes\":%d,\"indexProbes\":%d,\"selectedBlock\":%d,\"trace\":[",
               result,t->count,t->index_count,t->selected);
        for (int i=0;i<t->count;i++) {
            Probe p=t->steps[i];
            printf("%s{\"low\":%d,\"high\":%d,\"mid\":%d,\"value\":%d}",i?",":"",p.low,p.high,p.mid,p.value);
        }
        puts("]}");
    } else {
        if (t->selected>=0)
            printf("定位 B%d（索引项下标 %d）；索引比较 %d 次。\n",t->selected+1,t->selected,t->index_count);
        for (int i=0;i<t->count;i++) {
            Probe p=t->steps[i];
            printf("第 %d 次：范围 [%d,%d]，读取 A[%d]=%d\n",i+1,p.low,p.high,p.mid,p.value);
        }
        printf("返回 %d；已比较 %d 个记录关键字。\n",result,t->count);
        puts("计数不等于 C 条件测试次数或实测时间。");
    }
}
static int invalid(void) {
    puts("{\"valid\":false,\"error\":\"invalid case, length, key or binary ordering\"}");
    return 2;
}
int main(int argc, char **argv) {
    const char *mode=argc>1 ? argv[1] : "binary27";
    int json=argc>2 && strcmp(argv[argc-1],"--json")==0;
    Trace t; init(&t);
    if (!strcmp(mode,"profile")) {
        printf("{\"binary\":[");
        for (int i=0;i<11;i++) {
            init(&t); (void)binary_find(main_keys,11,main_keys[i],&t);
            printf("%s%d",i?",":"",t.count);
        }
        printf("],\"sequential\":[");
        for (int i=0;i<11;i++) {
            init(&t); (void)sequential_find(main_keys,11,main_keys[i],&t);
            printf("%s%d",i?",":"",t.count);
        }
        printf("],\"failure\":[");
        for (int i=0;i<12;i++) {
            init(&t); (void)binary_find(main_keys,11,miss_keys[i],&t);
            printf("%s%d",i?",":"",t.count);
        }
        puts("]}"); return 0;
    }
    if (!strcmp(mode,"block") || !strcmp(mode,"block30") || !strcmp(mode,"block28")) {
        int key=!strcmp(mode,"block28") ? 28 : 30;
        if (!strcmp(mode,"block") && (argc<3 || !integer(argv[2],&key))) return invalid();
        int result=block_find(key,&t);
        print_result(result,&t,json); return 0;
    }
    if (!strcmp(mode,"--stdin")) {
        int a[MAXN], n, key;
        if (!read_integer(&n) || !read_integer(&key) || n<0 || n>MAXN) return invalid();
        for (int i=0;i<n;i++) if (!read_integer(&a[i])) return invalid();
        /* Construction/CLI validation, not part of the query or probe counter. */
        for (int i=1;i<n;i++) if (a[i-1]>a[i]) return invalid();
        int result=binary_find(a,n,key,&t);
        print_result(result,&t,json); return 0;
    }
    const int *a=main_keys;
    int n=11,key=27,seq=0;
    int single[]={27}, pair[]={5,16}, duplicates[]={5,16,16,16,30};
    if (!strcmp(mode,"seq27")) seq=1;
    else if (!strcmp(mode,"seq65")) {seq=1;key=65;}
    else if (!strcmp(mode,"binary65")) key=65;
    else if (!strcmp(mode,"last")) key=71;
    else if (!strcmp(mode,"empty")) n=0;
    else if (!strcmp(mode,"single")) {a=single;n=1;}
    else if (!strcmp(mode,"pair")) {a=pair;n=2;key=16;}
    else if (!strcmp(mode,"duplicate")) {a=duplicates;n=5;key=16;}
    else if (strcmp(mode,"binary27")) return invalid();
    int result=seq ? sequential_find(a,n,key,&t) : binary_find(a,n,key,&t);
    print_result(result,&t,json);
    return 0;
}
