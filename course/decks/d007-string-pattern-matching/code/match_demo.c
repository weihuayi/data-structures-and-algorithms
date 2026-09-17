/* match_demo.c — D007 课堂演示：BF 与 KMP 的比较次数对照
 * 口径与教材一致：串下标从 1 开始；BF 失配时 i 退回 i-j+2、j 退回 1；
 * KMP 失配时 i 不动、j = next[j]，j = 0 时 i、j 各进一步。
 * 课堂口径：先预测两例各自的比较次数，再运行核对。
 */
#include <stdio.h>
#include <string.h>

#define MAXLEN 64

/* 教材算法 4.1：BF 模式匹配，cmp 返回字符比较次数 */
static int index_bf(const char *S, const char *T, int n, int m, int *cmp)
{
    int i = 1, j = 1;
    *cmp = 0;
    while (i <= n && j <= m) {
        (*cmp)++;
        if (S[i] == T[j]) { i++; j++; }
        else { i = i - j + 2; j = 1; }
    }
    return j > m ? i - m : 0;
}

/* 教材算法 4.3：求 next 函数值——模式 T 在与自己匹配 */
static void get_next(const char *T, int m, int next[])
{
    int i = 1, j = 0;
    next[1] = 0;
    while (i < m) {
        if (j == 0 || T[i] == T[j]) { i++; j++; next[i] = j; }
        else j = next[j];
    }
}

/* KMP 模式匹配，cmp 返回字符比较次数（不含求 next 的预处理） */
static int index_kmp(const char *S, const char *T, int n, int m,
                     const int next[], int *cmp)
{
    int i = 1, j = 1;
    *cmp = 0;
    while (i <= n && j <= m) {
        if (j == 0) { i++; j = 1; continue; }
        (*cmp)++;
        if (S[i] == T[j]) { i++; j++; }
        else j = next[j];
    }
    return j > m ? i - m : 0;
}

static void run_case(const char *label, const char *s, const char *t)
{
    char S[MAXLEN], T[MAXLEN];
    int next[MAXLEN];
    int n = (int)strlen(s), m = (int)strlen(t);
    int cmp_bf, cmp_kmp, pos_bf, pos_kmp;

    S[0] = T[0] = ' ';
    strcpy(S + 1, s);
    strcpy(T + 1, t);

    get_next(T, m, next);
    pos_bf = index_bf(S, T, n, m, &cmp_bf);
    pos_kmp = index_kmp(S, T, n, m, next, &cmp_kmp);

    printf("== %s ==\n", label);
    printf("S = \"%s\" (n = %d)\n", s, n);
    printf("T = \"%s\" (m = %d)\n", t, m);
    printf("next:");
    for (int j = 1; j <= m; j++) printf(" %d", next[j]);
    printf("\n");
    printf("BF : 匹配位置 %d，比较 %d 次\n", pos_bf, cmp_bf);
    printf("KMP: 匹配位置 %d，比较 %d 次\n\n", pos_kmp, cmp_kmp);
}

int main(void)
{
    run_case("例 A（教材例 4.1）", "abaabaabcde", "abaabc");
    run_case("例 B", "aaaaaaab", "aaab");
    return 0;
}
