#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REQUEST_COUNT 6

typedef struct {
    char id[8];
    int arrival;
    int service;
} Request;

/* IDs are R followed by a positive integer; compare numeric IDs on ties. */
static int later(Request a, Request b) {
    if (a.arrival != b.arrival) return a.arrival > b.arrival;
    return strtol(a.id + 1, NULL, 10) > strtol(b.id + 1, NULL, 10);
}

static void insertion_sort(Request a[], size_t n) {
    for (size_t i = 1; i < n; ++i) {
        Request key = a[i];
        size_t j = i;
        while (j > 0 && later(a[j - 1], key)) {
            a[j] = a[j - 1];
            --j;
        }
        a[j] = key;
    }
}

static void simulate(Request requests[], size_t count, const char *title) {
    if (count == 0) {
        printf("%s：没有请求。\n", title);
        return;
    }

    insertion_sort(requests, count);
    int available_at = 0;
    long total_wait = 0;
    int max_wait = 0;

    printf("\n%s\n", title);
    puts("请求 到达 服务 开始 完成 等待");
    for (size_t i = 0; i < count; ++i) {
        int start = requests[i].arrival > available_at
                    ? requests[i].arrival : available_at;
        int finish = start + requests[i].service;
        int wait = start - requests[i].arrival;

        printf("%-4s %4d %4d %4d %4d %4d\n", requests[i].id,
               requests[i].arrival, requests[i].service, start, finish, wait);

        available_at = finish;
        total_wait += wait;
        if (wait > max_wait) max_wait = wait;
    }

    printf("平均等待时间：%.2f 分钟\n", (double)total_wait / (double)count);
    printf("最大等待时间：%d 分钟\n", max_wait);
}

int main(void) {
    const Request original[REQUEST_COUNT] = {
        {"R4", 4, 1}, {"R2", 1, 2}, {"R6", 10, 1},
        {"R1", 0, 3}, {"R5", 10, 2}, {"R3", 1, 4}
    };
    Request requests[REQUEST_COUNT];

    memcpy(requests, original, sizeof requests);
    simulate(requests, REQUEST_COUNT, "基础数据");

    memcpy(requests, original, sizeof requests);
    for (size_t i = 0; i < REQUEST_COUNT; ++i)
        if (strcmp(requests[i].id, "R3") == 0) requests[i].service = 1;
    simulate(requests, REQUEST_COUNT, "变化测试：R3 服务时间改为 1 分钟");

    simulate(requests, 0, "边界测试：空请求集合");

    Request single[] = {{"R9", 5, 2}};
    simulate(single, 1, "边界测试：单个延迟到达请求");
    Request ties[] = {{"R10", 0, 1}, {"R2", 0, 1}};
    simulate(ties, 2, "边界测试：编号数值排序");
    return 0;
}
