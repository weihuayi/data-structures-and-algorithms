/* Call trace demo: main -> f -> g, one frame per call.
 * Entering and leaving each function prints a line indented by the
 * current stack depth, and each function prints the address of its
 * own local variable: every layer has its own frame.
 * The class should first predict the enter/leave order (it is LIFO),
 * then run and check.
 */
#include <stdio.h>

static int depth = 0;   /* current stack depth, used only for indentation */

static void trace_enter(const char *name, const char *var, const int *addr)
{
    int i;

    for (i = 0; i < depth; ++i)
        printf("  ");
    printf("enter %s  (%s at %p)\n", name, var, (const void *)addr);
    ++depth;
}

static void trace_leave(const char *name)
{
    int i;

    --depth;
    for (i = 0; i < depth; ++i)
        printf("  ");
    printf("leave %s\n", name);
}

static void g(void)
{
    int g_local = 30;

    trace_enter("g", "g_local", &g_local);
    /* when g returns, control resumes in f at the line after the call */
    trace_leave("g");
}

static void f(void)
{
    int f_local = 20;

    trace_enter("f", "f_local", &f_local);
    g();
    trace_leave("f");
}

int main(void)
{
    int main_local = 10;

    trace_enter("main", "main_local", &main_local);
    f();
    trace_leave("main");
    return 0;
}
