/*
 * Topic A: Campus timetable movement-gap analysis.
 * C11 reference implementation.
 *
 * Build:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 topic_a_timetable.c -o topic_a
 * Run:
 *   ./topic_a
 *
 * Change the A-B movement time with:
 *   cc ... -DAB_MOVE_MINUTES=20 ...
 */
#include <stdio.h>
#include <string.h>

#ifndef AB_MOVE_MINUTES
#define AB_MOVE_MINUTES 25
#endif

#if AB_MOVE_MINUTES < 0
#error "AB_MOVE_MINUTES must be nonnegative"
#endif

#ifndef COURSE_COUNT
#define COURSE_COUNT 6
#endif

#if COURSE_COUNT < 0 || COURSE_COUNT > 6
#error "COURSE_COUNT must be between 0 and 6"
#endif

enum { LOCATION_A = 0, LOCATION_B = 1, LOCATION_C = 2, LOCATION_COUNT = 3 };

typedef struct {
    const char *id;
    int start_minute;
    int end_minute;
    int location;
} Course;

static Course courses[] = {
    {"C4", 14 * 60, 15 * 60 + 40, LOCATION_A},
    {"C2", 10 * 60, 11 * 60 + 30, LOCATION_B},
    {"C6", 18 * 60, 19 * 60, LOCATION_B},
    {"C1", 8 * 60, 9 * 60 + 40, LOCATION_A},
    {"C5", 16 * 60, 17 * 60 + 20, LOCATION_B},
    {"C3", 11 * 60 + 50, 13 * 60 + 10, LOCATION_C}
};

static const char *location_names[LOCATION_COUNT] = {"A", "B", "C"};

/* The teaching data assumes symmetric movement times. */
static const int movement_minutes[LOCATION_COUNT][LOCATION_COUNT] = {
    {0, AB_MOVE_MINUTES, 8},
    {AB_MOVE_MINUTES, 0, 20},
    {8, 20, 0}
};

static int comes_after(const Course *left, const Course *right)
{
    if (left->start_minute != right->start_minute)
        return left->start_minute > right->start_minute;
    return strcmp(left->id, right->id) > 0;
}

/* Insertion sort: O(n^2) time and O(1) auxiliary space. */
static void sort_courses(Course items[], int count)
{
    for (int i = 1; i < count; ++i) {
        Course current = items[i];
        int j = i;
        while (j > 0 && comes_after(&items[j - 1], &current)) {
            items[j] = items[j - 1];
            --j;
        }
        items[j] = current;
    }
}

static void print_time(int minute_of_day)
{
    printf("%02d:%02d", minute_of_day / 60, minute_of_day % 60);
}

int main(void)
{
    const int count = COURSE_COUNT;

    if (count == 0) {
        puts("No courses provided.");
        return 0;
    }

    sort_courses(courses, count);

    puts("Sorted courses:");
    puts("Course  Start-End       Location");
    for (int i = 0; i < count; ++i) {
        printf("%-7s ", courses[i].id);
        print_time(courses[i].start_minute);
        putchar('-');
        print_time(courses[i].end_minute);
        printf("    %s\n", location_names[courses[i].location]);
    }

    if (count < 2) {
        puts("Not enough courses to compare transitions.");
        return 0;
    }

    puts("\nAdjacent-course movement checks:");
    int insufficient_count = 0;
    for (int i = 0; i + 1 < count; ++i) {
        const Course *current = &courses[i];
        const Course *next = &courses[i + 1];
        int available = next->start_minute - current->end_minute;
        int required = movement_minutes[current->location][next->location];
        int shortfall = required > available ? required - available : 0;

        printf("%s -> %s: gap=%d min, travel=%d min, shortfall=%d min [%s]\n",
               current->id, next->id, available, required, shortfall,
               shortfall == 0 ? "OK" : "INSUFFICIENT");
        if (shortfall > 0)
            ++insufficient_count;
    }

    printf("Insufficient transitions: %d\n", insufficient_count);
    return 0;
}
