/* D017 C11 demo: BST order and AVL insertion maintenance. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct Node { int key, height; struct Node *left, *right; } Node;
static unsigned rotations=0;
static int height(const Node*p){return p?p->height:0;}
static int max2(int a,int b){return a>b?a:b;}
static void fix(Node*p){if(p)p->height=1+max2(height(p->left),height(p->right));}
static int bf(const Node*p){return p?height(p->left)-height(p->right):0;}
static Node*make(int k){
    Node*p=calloc(1,sizeof(*p));if(!p){fputs("out of memory\n",stderr);exit(1);}
    p->key=k;p->height=1;return p;
}
static Node*bst_insert(Node*p,int k){
    if(!p)return make(k);
    if(k<p->key)p->left=bst_insert(p->left,k);
    else if(k>p->key)p->right=bst_insert(p->right,k);
    fix(p);return p;
}
static Node*right(Node*z){
    assert(z&&z->left);
    Node*y=z->left,*middle=y->right;
    y->right=z;z->left=middle;fix(z);fix(y);++rotations;return y;
}
static Node*left(Node*z){
    assert(z&&z->right);
    Node*y=z->right,*middle=y->left;
    y->left=z;z->right=middle;fix(z);fix(y);++rotations;return y;
}
static Node*avl_insert(Node*p,int k){
    if(!p)return make(k);
    if(k<p->key)p->left=avl_insert(p->left,k);
    else if(k>p->key)p->right=avl_insert(p->right,k);
    else return p; /* duplicate key ignored */
    fix(p);
    if(bf(p)>1){if(bf(p->left)<0)p->left=left(p->left);return right(p);}
    if(bf(p)<-1){if(bf(p->right)>0)p->right=right(p->right);return left(p);}
    return p;
}
static int ordered(const Node*p,long long lo,long long hi){
    return !p||(lo<p->key&&p->key<hi&&ordered(p->left,lo,p->key)&&ordered(p->right,p->key,hi));
}
static int balanced(const Node*p){
    return !p||(abs(bf(p))<=1&&p->height==1+max2(height(p->left),height(p->right))
        &&balanced(p->left)&&balanced(p->right));
}
static Node*build(const int*a,int n,int avl){
    Node*p=NULL;
    for(int i=0;i<n;i++){
        p=avl?avl_insert(p,a[i]):bst_insert(p,a[i]);
        assert(ordered(p,LLONG_MIN,LLONG_MAX));
        if(avl)assert(balanced(p));
    }return p;
}
static int visits(const Node*p,int k){
    int n=0;while(p){n++;if(k==p->key)return n;p=k<p->key?p->left:p->right;}return n;
}
static void inorder(const Node*p){
    if(!p)return;inorder(p->left);printf(" %d",p->key);inorder(p->right);
}
static void release(Node*p){if(!p)return;release(p->left);release(p->right);free(p);}
static void run_bst(void){
    const int a[]={30,20,44,16,27,36,55},b[]={16,20,27,30,36,44,55};
    Node*p=build(a,7,0),*q=build(b,7,0);
    assert(p->height==3&&q->height==7&&visits(p,55)==3&&visits(q,55)==7);
    printf("BST_A height=%d search55=%d inorder:",p->height,visits(p,55));
    inorder(p);puts("");
    printf("BST_B height=%d search55=%d inorder:",q->height,visits(q,55));
    inorder(q);puts("");
    release(p);release(q);
}
static void run_avl(void){
    const int a[]={30,16,20};rotations=0;Node*p=build(a,3,1);
    assert(p->key==20&&p->height==2&&rotations==2);
    printf("AVL_LR root=%d height=%d rotations=%u inorder:",p->key,p->height,rotations);
    inorder(p);puts("");release(p);
}
int main(int argc,char**argv){
    if(argc!=2){fprintf(stderr,"usage: %s bst|avl|test\n",argv[0]);return 2;}
    if(!strcmp(argv[1],"bst")){run_bst();return 0;}
    if(!strcmp(argv[1],"avl")){run_avl();return 0;}
    if(!strcmp(argv[1],"test")){run_bst();run_avl();puts("ALL_TESTS_PASSED");return 0;}
    fprintf(stderr,"unknown mode: %s\n",argv[1]);return 2;
}
