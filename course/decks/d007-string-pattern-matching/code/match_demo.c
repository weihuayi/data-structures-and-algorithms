/* match_demo.c — D007 课堂演示：BF 与 KMP 的比较次数对照
 * 口径与 C 语言一致：串下标从 0 开始；BF 失配时 i 退回 i-j+1、j 回 0；
 * KMP 失配时 i 不动、j = next[j]，j = -1 时（首字符就失配）i、j 各进一步。
 * 教材为 1 起始口径（next[j] = l_max+1、next[1] = 0），对应关系见 slides 第 4、14 页。
 * 课堂口径：先预测两例各自的比较次数，再运行核对。
 */
#include <stdio.h>
#include <string.h>

/* BF 模式匹配：失配时 i 退回 i-j+1、j 回 0；cmp 返回字符比较次数 */
static int index_bf(const char *S, const char *T, int n, int m, int *cmp)
{
    int i = 0, j = 0;
    *cmp = 0;
    while (i < n && j < m) {
        (*cmp)++;
        if (S[i] == T[j]) { i++; j++; }
        else { i = i - j + 1; j = 0; }
    }
    return j == m ? i - m : -1;
}

/* 求 next：next[j] = T[0..j-1] 的最长相等前后缀长度（不含自身），next[0] = -1
 * 模式 T 在跟自己匹配：已知 next[j] 推 next[j+1]
 */
static void get_next(const char *T, int m, int next[])
{
    int i = 0, j = -1;
    next[0] = -1;
    while (i < m - 1) {
        if (j == -1 || T[i] == T[j]) { i++; j++; next[i] = j; }
        else j = next[j];
    }
}

/* KMP 模式匹配：失配时 i 不动、j = next[j]；cmp 返回字符比较次数（不含求 next） */
static int index_kmp(const char *S, const char *T, int n, int m,
                     const int next[], int *cmp)
{
    int i = 0, j = 0;
    *cmp = 0;
    while (i < n && j < m) {
        if (j == -1) { i++; j = 0; continue; }
        (*cmp)++;
        if (S[i] == T[j]) { i++; j++; }
        else j = next[j];
    }
    return j == m ? i - m : -1;
}

static void run_case(const char *label, const char *S, const char *T)
{
    int next[64];
    int n = (int)strlen(S), m = (int)strlen(T);
    int cmp_bf, cmp_kmp, pos_bf, pos_kmp;

    get_next(T, m, next);
    pos_bf = index_bf(S, T, n, m, &cmp_bf);
    pos_kmp = index_kmp(S, T, n, m, next, &cmp_kmp);

    printf("== %s ==\n", label);
    printf("S = \"%s\" (n = %d)\n", S, n);
    printf("T = \"%s\" (m = %d)\n", T, m);
    printf("next:");
    for (int j = 0; j < m; j++) printf(" %d", next[j]);
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
