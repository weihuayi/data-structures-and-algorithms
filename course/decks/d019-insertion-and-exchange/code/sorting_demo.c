/* D019 teaching examples: C11, zero-based indices; record identity is preserved. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct { int key; int id; } Record;
typedef struct { long long compares, moves, swaps; } Counters;
#define MAX_N 256
static void show(const char *label, const Record *a, size_t n) {
    printf("%s: [", label);
    for(size_t i=0;i<n;i++) printf("%s%d_%d", i?", ":"", a[i].key,a[i].id);
    printf("]\n");
}
static bool ordered(const Record *a, size_t n) {
    for(size_t i=1;i<n;i++) if(a[i-1].key>a[i].key) return false;
    return true;
}
static bool stable(const Record *a, size_t n) {
    for(size_t i=0;i<n;i++) for(size_t j=i+1;j<n;j++)
        if(a[i].key==a[j].key && a[i].id>a[j].id) return false;
    return true;
}
static bool same_records(const Record *a,const Record *b,size_t n) {
    for(size_t i=0;i<n;i++) {
        int count_a=0,count_b=0;
        for(size_t j=0;j<n;j++) {
            if(a[j].id==a[i].id && a[j].key==a[i].key) count_a++;
            if(b[j].id==a[i].id && b[j].key==a[i].key) count_b++;
        }
        if(count_a!=count_b) return false;
    }
    return true;
}
static void insertion(Record *a,size_t n,Counters *c,bool verbose) {
    for(size_t i=1;i<n;i++) {
        Record x=a[i]; size_t j=i;
        while(j>0) {
            c->compares++;
            if(a[j-1].key<=x.key) break; /* strict > preserves stability */
            a[j]=a[j-1];c->moves++;j--;
        }
        a[j]=x;c->moves++;
        if(verbose) { char label[64];snprintf(label,sizeof label,"after insertion %zu",i);show(label,a,n); }
    }
}
static void binary_insertion(Record *a,size_t n,Counters *c,bool verbose) {
    for(size_t i=1;i<n;i++) {
        Record x=a[i];size_t lo=0,hi=i;
        while(lo<hi) {
            size_t m=lo+(hi-lo)/2;c->compares++;
            if(a[m].key<=x.key)lo=m+1;else hi=m;/* upper_bound: stable */
        }
        for(size_t j=i;j>lo;j--){a[j]=a[j-1];c->moves++;}
        a[lo]=x;c->moves++;
        if(verbose){char label[64];snprintf(label,sizeof label,"after binary insertion %zu",i);show(label,a,n);}
    }
}
static void shell(Record *a,size_t n,Counters *c,bool verbose) {
    /* This is an explicit classroom gap sequence, not a universal claim. */
    const size_t gaps[]={5,3,1};
    for(size_t g=0;g<sizeof gaps/sizeof gaps[0];g++) {
        const size_t gap=gaps[g];
        if(gap>=n)continue;
        for(size_t i=gap;i<n;i++){
            Record x=a[i];size_t j=i;
            while(j>=gap) {
                c->compares++;if(a[j-gap].key<=x.key)break;
                a[j]=a[j-gap];c->moves++;j-=gap;
            }
            a[j]=x;c->moves++;
        }
        if(verbose){char label[64];snprintf(label,sizeof label,"after gap %zu",gap);show(label,a,n);}
    }
}
static void bubble(Record *a,size_t n,Counters *c,bool verbose) {
    for(size_t end=n;end>1;end--) {
        bool changed=false;
        for(size_t j=1;j<end;j++) {
            c->compares++;
            if(a[j-1].key>a[j].key) {
                Record temp=a[j-1];a[j-1]=a[j];a[j]=temp;
                c->swaps++;changed=true;
            }
        }
        if(verbose){char label[64];snprintf(label,sizeof label,"after bubble pass %zu",n-end+1);show(label,a,n);}
        if(!changed)break;
    }
}
static size_t partition_hole(Record *a,size_t left,size_t right,Counters *c,bool verbose,size_t n) {
    Record pivot=a[left];size_t lo=left,hi=right;
    /* Conceptual hole at lo: pivot is held in temp. Array slot remains accessible,
       but that slot is logically vacant until filled. */
    while(lo<hi) {
        while(lo<hi) {c->compares++;if(a[hi].key<pivot.key)break;hi--;}
        if(lo<hi){a[lo]=a[hi];c->moves++;lo++;}
        while(lo<hi) {c->compares++;if(a[lo].key>pivot.key)break;lo++;}
        if(lo<hi){a[hi]=a[lo];c->moves++;hi--;}
    }
    a[lo]=pivot;c->moves++;
    if(verbose){printf("pivot index = %zu\n",lo);show("after Partition",a,n);}
    return lo;
}
static void quick_range(Record *a,size_t lo,size_t hi,Counters *c) {
    if(lo>=hi)return;
    size_t pivot=partition_hole(a,lo,hi,c,false,0);
    if(pivot>lo)quick_range(a,lo,pivot-1,c);
    if(pivot<hi)quick_range(a,pivot+1,hi,c);
}
static void quick(Record *a,size_t n,Counters *c) {if(n>1)quick_range(a,0,n-1,c);}
static int by_key(const void *p,const void *q) {
    int a=((const Record*)p)->key,b=((const Record*)q)->key;
    return (a>b)-(a<b);
}
static unsigned int rng=0x13579bdfU;
static unsigned int rand_u(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static int self_test(void) {
    for(int round=0;round<1200;round++) {
        size_t n=(size_t)(round%53);
        Record original[MAX_N],expected[MAX_N];
        for(size_t i=0;i<n;i++){
            int k=(int)(rand_u()%17U)-8;
            if(round%31==0)k=(int)i; /* sorted */
            if(round%31==1)k=(int)(n-i); /* reverse */
            if(round%31==2)k=5; /* all equal */
            original[i]=(Record){k,(int)i};expected[i]=original[i];
        }
        qsort(expected,n,sizeof expected[0],by_key);
        for(int method=0;method<5;method++) {
            Record a[MAX_N];memcpy(a,original,n*sizeof a[0]);Counters c={0,0,0};
            switch(method) {
                case 0:insertion(a,n,&c,false);break;
                case 1:binary_insertion(a,n,&c,false);break;
                case 2:shell(a,n,&c,false);break;
                case 3:bubble(a,n,&c,false);break;
                default:quick(a,n,&c);break;
            }
            if(!ordered(a,n)||!same_records(original,a,n)){
                fprintf(stderr,"FAIL method %d round %d\n",method,round);return 1;
            }
            for(size_t i=0;i<n;i++)if(a[i].key!=expected[i].key){
                fprintf(stderr,"FAIL reference comparison method %d round %d\n",method,round);return 1;
            }
            if((method==0||method==1||method==3)&&!stable(a,n)){
                fprintf(stderr,"FAIL stability method %d round %d\n",method,round);return 1;
            }
        }
        if(n) {
            Record a[MAX_N];memcpy(a,original,n*sizeof a[0]);Counters c={0,0,0};
            size_t p=partition_hole(a,0,n-1,&c,false,n);
            if(a[p].key!=original[0].key||!same_records(original,a,n))return 1;
            for(size_t i=0;i<p;i++)if(a[i].key>a[p].key)return 1;
            for(size_t i=p+1;i<n;i++)if(a[i].key<a[p].key)return 1;
        }
    }
    puts("PASS --self-test: 1200 inputs x 5 sorting methods; Partition also checked");
    return 0;
}
int main(int argc,char **argv) {
    if(argc<2){
        fprintf(stderr,"usage: %s insert|binary|shell|bubble|partition|quick [key ...] | --self-test\n",argv[0]);
        return 2;
    }
    if(strcmp(argv[1],"--self-test")==0) return argc==2?self_test():2;
    const int demo[]={4,7,2,8,3,6,1};
    Record a[MAX_N];size_t n=0;
    if(argc==2){
        n=sizeof demo/sizeof demo[0];
        for(size_t i=0;i<n;i++)a[i]=(Record){demo[i],(int)i};
    }else{
        n=(size_t)(argc-2);
        if(n>MAX_N){fprintf(stderr,"at most %d records\n",MAX_N);return 2;}
        for(size_t i=0;i<n;i++) {
            char *end=NULL;
            long v=strtol(argv[i+2],&end,10);
            if(end==argv[i+2]||*end!='\0'||v<INT32_MIN||v>INT32_MAX) {
                fprintf(stderr,"invalid C11 integer: %s\n",argv[i+2]);return 2;
            }
            a[i]=(Record){(int)v,(int)i};
        }
    }
    Counters c={0,0,0};show("input",a,n);
    if(strcmp(argv[1],"insert")==0)insertion(a,n,&c,true);
    else if(strcmp(argv[1],"binary")==0)binary_insertion(a,n,&c,true);
    else if(strcmp(argv[1],"shell")==0)shell(a,n,&c,true);
    else if(strcmp(argv[1],"bubble")==0)bubble(a,n,&c,true);
    else if(strcmp(argv[1],"partition")==0){
        if(n==0){fprintf(stderr,"partition requires at least one key\n");return 2;}
        (void)partition_hole(a,0,n-1,&c,true,n);
    }
    else if(strcmp(argv[1],"quick")==0){quick(a,n,&c);show("after quicksort",a,n);}
    else{fprintf(stderr,"unknown mode\n");return 2;}
    printf("comparisons=%lld, record assignments=%lld, swaps=%lld\n",c.compares,c.moves,c.swaps);
    return 0;
}
