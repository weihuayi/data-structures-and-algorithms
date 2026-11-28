#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REQUEST_COUNT 6

typedef struct {
    char id[8];
    int arrival;
    int service;
} Request;

typedef struct {
    char id[8];
    int arrival;
    int service;
    int start;
    int finish;
    int wait;
} Result;

static int compare_request(const void *lhs, const void *rhs) {
    const Request *a = (const Request *)lhs;
    const Request *b = (const Request *)rhs;
    if (a->arrival != b->arrival)
        return (a->arrival > b->arrival) - (a->arrival < b->arrival);
    return strcmp(a->id, b->id);
}

static void simulate(Request requests[], size_t count, const char *title) {
    if (count == 0) {
        printf("%s：没有请求。\n", title);
        return;
    }

    qsort(requests, count, sizeof requests[0], compare_request);
    Result results[REQUEST_COUNT];
    int available_at = 0;
    long total_wait = 0;
    int max_wait = 0;

    for (size_t i = 0; i < count; ++i) {
        int start = requests[i].arrival > available_at
                    ? requests[i].arrival : available_at;
        int finish = start + requests[i].service;
        int wait = start - requests[i].arrival;

        (void)snprintf(results[i].id, sizeof results[i].id, "%s", requests[i].id);
        results[i].arrival = requests[i].arrival;
        results[i].service = requests[i].service;
        results[i].start = start;
        results[i].finish = finish;
        results[i].wait = wait;

        available_at = finish;
        total_wait += wait;
        if (wait > max_wait) max_wait = wait;
    }

    printf("\n%s\n", title);
    puts("请求 到达 服务 开始 完成 等待");
    for (size_t i = 0; i < count; ++i) {
        printf("%-4s %4d %4d %4d %4d %4d\n",
               results[i].id, results[i].arrival, results[i].service,
               results[i].start, results[i].finish, results[i].wait);
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
    return 0;
}
