/* D015: C11 adjacency-list topological order and fixed-duration CPM.
 * gcc -std=c11 -Wall -Wextra -Werror dependency_demo.c -o /tmp/d015
 * /tmp/d015 topo --trace | /tmp/d015 main | /tmp/d015 tied --json
 * /tmp/d015 --stdin --json < graph.txt   (n m source sink; then u v duration)
 * Input limits bound all sums well below LLONG_MAX. No path enumeration.
 */
#include <stdio.h>
#include <string.h>

#define MAXV 32
#define MAXE 256
#define MAXW 1000000LL

typedef struct { int u, v, next; long long w; } Edge;
typedef struct { int n, m, source, sink, head[MAXV]; Edge edge[MAXE]; } Graph;
typedef struct {
    int count, order[MAXV], degree[MAXV], critical[MAXE], path[MAXE], path_n;
    long long ve[MAXV], vl[MAXV], earliest[MAXE], latest[MAXE], slack[MAXE], total;
} Result;

static void init(Graph *g, int n, int source, int sink) {
    memset(g, 0, sizeof(*g)); g->n=n; g->source=source; g->sink=sink;
    for (int i=0;i<MAXV;i++) g->head[i]=-1;
}
static int add(Graph *g, int u, int v, long long w) {
    if (u<0 || u>=g->n || v<0 || v>=g->n || w<0 || w>MAXW || g->m>=MAXE) return 0;
    for (int i=0;i<g->m;i++) if (g->edge[i].u==u && g->edge[i].v==v) return 0;
    g->edge[g->m++]=(Edge){u,v,-1,w}; return 1;
}
static void adjacency(Graph *g) {
    /* Prepend in reverse input order, so scans preserve input order. */
    for (int i=g->m-1;i>=0;i--) {
        int u=g->edge[i].u; g->edge[i].next=g->head[u]; g->head[u]=i;
    }
}
static void topological(const Graph *g, Result *r, int trace) {
    int stack[MAXV], size=0; r->count=0;
    for (int v=0;v<g->n;v++) r->degree[v]=0;
    for (int i=0;i<g->m;i++) r->degree[g->edge[i].v]++;
    for (int v=0;v<g->n;v++) if (r->degree[v]==0) stack[size++]=v;
    while (size>0) {
        int u=stack[--size]; r->order[r->count++]=u;
        if (trace) printf("output %d (ordering, not real task completion)\n",u);
        for (int e=g->head[u];e!=-1;e=g->edge[e].next) {
            int v=g->edge[e].v, old=r->degree[v];
            --r->degree[v];
            if (r->degree[v]==0) stack[size++]=v;
            if (trace) printf("release %d->%d: %d->%d\n",u,v,old,r->degree[v]);
        }
        if (trace) printf("boundary %d: outgoing arcs processed\n",u);
    }
}
static int cpm(const Graph *g, Result *r, int trace) {
    topological(g,r,trace);
    if (r->count!=g->n) return 0;
    int incoming[MAXV]={0}, sources=0, sinks=0;
    for (int i=0;i<g->m;i++) incoming[g->edge[i].v]++;
    for (int v=0;v<g->n;v++) {
        if (incoming[v]==0) { sources++; if (v!=g->source) return 0; }
        if (g->head[v]==-1) { sinks++; if (v!=g->sink) return 0; }
        r->ve[v]=0;
    }
    if (sources!=1 || sinks!=1) return 0;
    for (int i=0;i<g->n;i++) {
        int u=r->order[i];
        for (int e=g->head[u];e!=-1;e=g->edge[e].next) {
            int v=g->edge[e].v; long long candidate=r->ve[u]+g->edge[e].w;
            if (candidate>r->ve[v]) r->ve[v]=candidate;
        }
        if (trace) printf("ve[%d]=%lld; outgoing propagation complete\n",u,r->ve[u]);
    }
    r->total=r->ve[g->sink];
    for (int v=0;v<g->n;v++) r->vl[v]=r->total;
    for (int i=g->n-1;i>=0;i--) {
        int u=r->order[i];
        for (int e=g->head[u];e!=-1;e=g->edge[e].next) {
            int v=g->edge[e].v; long long candidate=r->vl[v]-g->edge[e].w;
            if (candidate<r->vl[u]) r->vl[u]=candidate;
        }
        if (trace) printf("vl[%d]=%lld; all successor deadlines combined\n",u,r->vl[u]);
    }
    for (int e=0;e<g->m;e++) {
        r->earliest[e]=r->ve[g->edge[e].u]; r->latest[e]=r->vl[g->edge[e].v]-g->edge[e].w;
        r->slack[e]=r->latest[e]-r->earliest[e]; r->critical[e]=(r->slack[e]==0);
    }
    r->path_n=0;
    for (int u=g->source;u!=g->sink;) {
        int e=g->head[u]; while (e!=-1 && !r->critical[e]) e=g->edge[e].next;
        if (e==-1) return 0;
        r->path[r->path_n++]=e; u=g->edge[e].v;
    }
    return 1;
}
static int builtin(Graph *g, const char *name) {
    if (!strcmp(name,"exercise")) {
        init(g,4,2,1);
        return add(g,2,0,2)&&add(g,2,3,3)&&add(g,0,3,1)&&add(g,0,1,4)&&add(g,3,1,2);
    }
    if (!strcmp(name,"topo") || !strcmp(name,"cycle")) {
        init(g,6,0,5);
        if (!(add(g,0,2,0)&&add(g,1,3,0)&&add(g,4,3,0)&&add(g,0,4,0)&&add(g,2,5,0)&&add(g,3,5,0))) return 0;
        return strcmp(name,"cycle") || add(g,4,0,0);
    }
    init(g,5,0,4);
    long long b=!strcmp(name,"tied")?4:!strcmp(name,"faster")?3:5;
    long long a=!strcmp(name,"shared")?4:3, e=!strcmp(name,"shared")?2:1;
    if (!(add(g,0,1,a)&&add(g,0,2,b)&&add(g,1,3,2)&&add(g,2,3,!strcmp(name,"homework")?2:3)&&add(g,1,2,e)&&add(g,3,4,2))) return 0;
    if (!strcmp(name,"endpoint")) return add(g,0,3,1);
    return !strcmp(name,"main") || !strcmp(name,"tied") || !strcmp(name,"faster") || !strcmp(name,"shared") || !strcmp(name,"homework");
}
static int input(Graph *g) {
    int n,m,s,t; if (scanf("%d%d%d%d",&n,&m,&s,&t)!=4 || n<1 || n>MAXV || m<0 || m>MAXE || s<0 || s>=n || t<0 || t>=n) return 0;
    init(g,n,s,t);
    for (int i=0;i<m;i++) {int u,v;long long w; if (scanf("%d%d%lld",&u,&v,&w)!=3 || !add(g,u,v,w)) return 0;}
    return 1;
}
static void ints(const int *a,int n) { putchar('[');for(int i=0;i<n;i++)printf("%s%d",i?",":"",a[i]);putchar(']'); }
static void longs(const long long *a,int n) { putchar('[');for(int i=0;i<n;i++)printf("%s%lld",i?",":"",a[i]);putchar(']'); }
int main(int argc,char **argv) {
    const char *name="main"; int json=0,trace=0,from_stdin=0;
    for(int i=1;i<argc;i++) {
        if(!strcmp(argv[i],"--json"))json=1;else if(!strcmp(argv[i],"--trace"))trace=1;
        else if(!strcmp(argv[i],"--stdin"))from_stdin=1;else name=argv[i];
    }
    if(json && trace) {fputs("Choose --json or --trace\n",stderr);return 2;}
    Graph g;Result r={0};
    if(!(from_stdin?input(&g):builtin(&g,name))) {puts("{\"valid\":false,\"error\":\"input\"}");return 2;}
    adjacency(&g);
    int only_topo=!from_stdin && (!strcmp(name,"topo") || !strcmp(name,"cycle"));
    int valid;
    if(only_topo) {topological(&g,&r,trace);valid=(r.count==g.n);} else valid=cpm(&g,&r,trace);
    if(json) {
        printf("{\"valid\":%s,\"order\":",valid?"true":"false");ints(r.order,r.count);
        if(!only_topo && valid) {
            printf(",\"source\":%d,\"sink\":%d,\"T\":%lld,\"early\":",g.source,g.sink,r.total);longs(r.ve,g.n);
            printf(",\"late\":");longs(r.vl,g.n);printf(",\"earliest\":");longs(r.earliest,g.m);
            printf(",\"latest\":");longs(r.latest,g.m);printf(",\"slack\":");longs(r.slack,g.m);
            printf(",\"critical\":");ints(r.critical,g.m);printf(",\"onePath\":");ints(r.path,r.path_n);
        }
        puts("}");
    } else if(only_topo) {
        printf("order:");for(int i=0;i<r.count;i++)printf(" %c",'A'+r.order[i]);
        puts(valid?"\nAll vertices ordered.":"\nCycle exists in remaining subgraph; not all remaining vertices lie on a cycle.");
    } else if(valid) {
        printf("T = %lld hours; event times:\n",r.total);
        for(int v=0;v<g.n;v++)printf("event %d: ve=%lld vl=%lld\n",v,r.ve[v],r.vl[v]);
        puts("activity e l slack critical:");
        for(int i=0;i<g.m;i++)printf("%c (%d->%d): %lld %lld %lld %s\n",(!strcmp(name,"exercise")?'a':'A')+i,g.edge[i].u,g.edge[i].v,r.earliest[i],r.latest[i],r.slack[i],r.critical[i]?"yes":"no");
        puts("One representative critical path:");
        for(int i=0;i<r.path_n;i++) {
            if(from_stdin) printf("%s%d",i?" ":"",r.path[i]);
            else printf("%s%c",i?" ":"",(!strcmp(name,"exercise")?'a':'A')+r.path[i]);
        } puts("");
    } else puts("Invalid project: require a DAG and one declared source/sink.");
    return valid?0:2;
}
