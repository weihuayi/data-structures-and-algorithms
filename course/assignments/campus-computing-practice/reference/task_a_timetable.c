#include <stdio.h>
#include <string.h>

#define COURSE_COUNT 6
#define PLACE_COUNT 3

typedef struct {
    char id[8];
    int start; /* minutes after 00:00 */
    int end;
    int place; /* A=0, B=1, C=2 */
} Course;

static const int travel[PLACE_COUNT][PLACE_COUNT] = {
    {0, 25, 8},
    {25, 0, 20},
    {8, 20, 0}
};

/* The task assumes distinct start times and non-overlapping classes. */
static void insertion_sort(Course a[], size_t n) {
    for (size_t i = 1; i < n; ++i) {
        Course key = a[i];
        size_t j = i;
        while (j > 0 && a[j - 1].start > key.start) {
            a[j] = a[j - 1];
            --j;
        }
        a[j] = key;
    }
}

static void print_time(int minute) {
    printf("%02d:%02d", minute / 60, minute % 60);
}

static void analyze(Course courses[], size_t count, int ab_travel) {
    int matrix[PLACE_COUNT][PLACE_COUNT];
    memcpy(matrix, travel, sizeof matrix);
    matrix[0][1] = matrix[1][0] = ab_travel;

    if (count == 0) {
        puts("课表为空：没有相邻课程需要检查。");
        return;
    }

    insertion_sort(courses, count);
    puts("排序后的课程：");
    for (size_t i = 0; i < count; ++i) {
        printf("  %s ", courses[i].id);
        print_time(courses[i].start);
        printf("-");
        print_time(courses[i].end);
        printf(" 地点 %c\n", 'A' + courses[i].place);
    }

    int found = 0;
    for (size_t i = 0; i + 1 < count; ++i) {
        const Course *a = &courses[i];
        const Course *b = &courses[i + 1];
        int available = b->start - a->end;
        int required = matrix[a->place][b->place];
        printf("%s -> %s：可用 %d 分钟，需要 %d 分钟：",
               a->id, b->id, available, required);
        if (available >= required) {
            puts("满足");
        } else {
            printf("不足 %d 分钟\n", required - available);
            found = 1;
        }
    }
    if (!found) puts("所有相邻课程均满足移动时间要求。");
}

int main(void) {
    Course original[COURSE_COUNT] = {
        {"C4", 14 * 60, 15 * 60 + 40, 0},
        {"C2", 10 * 60, 11 * 60 + 30, 1},
        {"C6", 18 * 60, 19 * 60, 1},
        {"C1", 8 * 60, 9 * 60 + 40, 0},
        {"C5", 16 * 60, 17 * 60 + 20, 1},
        {"C3", 11 * 60 + 50, 13 * 60 + 10, 2}
    };

    Course courses[COURSE_COUNT];
    memcpy(courses, original, sizeof courses);
    puts("=== 基础数据：A-B 移动时间 25 分钟 ===");
    analyze(courses, COURSE_COUNT, 25);

    memcpy(courses, original, sizeof courses);
    puts("\n=== 变化测试：A-B 移动时间改为 20 分钟 ===");
    analyze(courses, COURSE_COUNT, 20);

    puts("\n=== 边界测试：空课表 ===");
    analyze(courses, 0, 25);

    puts("\n=== 边界测试：单课程 ===");
    analyze(courses, 1, 25);
    return 0;
}
