/*
 * Topic C: Campus service requests and waiting-time simulation.
 * C11 reference implementation using insertion sort and an array FIFO queue.
 *
 * Build and run:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 topic_c_fifo.c -o topic_c
 *   ./topic_c
 *
 * Variants:
 *   -DR3_SERVICE_MINUTES=1  change R3 service time from 4 to 1 minute
 *   -DREQUEST_COUNT=0       simulate an empty request set
 *   -DREQUEST_COUNT=1       simulate only the first source record (R4)
 */
#include <stdio.h>
#include <string.h>

#ifndef R3_SERVICE_MINUTES
#define R3_SERVICE_MINUTES 4
#endif

#if R3_SERVICE_MINUTES <= 0
#error "R3_SERVICE_MINUTES must be positive"
#endif

#ifndef REQUEST_COUNT
#define REQUEST_COUNT 6
#endif

#define MAX_REQUESTS 6

#if REQUEST_COUNT < 0 || REQUEST_COUNT > MAX_REQUESTS
#error "REQUEST_COUNT must be between 0 and 6"
#endif

typedef struct {
    char id[3];
    int arrival_minute;
    int service_minutes;
} Request;

typedef struct {
    int start_minute;
    int finish_minute;
    int waiting_minutes;
} ServiceResult;

static const Request source_requests[MAX_REQUESTS] = {
    {"R4", 4, 1},
    {"R2", 1, 2},
    {"R6", 10, 1},
    {"R1", 0, 3},
    {"R5", 10, 2},
    {"R3", 1, R3_SERVICE_MINUTES}
};

static int comes_after(const Request *left, const Request *right)
{
    if (left->arrival_minute != right->arrival_minute)
        return left->arrival_minute > right->arrival_minute;
    return strcmp(left->id, right->id) > 0;
}

/* Order by arrival time, then request ID; O(n^2) time and O(1) extra space. */
static void sort_requests(Request requests[], int count)
{
    for (int i = 1; i < count; ++i) {
        Request current = requests[i];
        int j = i;
        while (j > 0 && comes_after(&requests[j - 1], &current)) {
            requests[j] = requests[j - 1];
            --j;
        }
        requests[j] = current;
    }
}

/*
 * Simulate one non-preemptive service window.
 * New arrivals enter the FIFO queue in the established order.
 * When the queue is empty, time advances to the next arrival.
 */
static int simulate_fifo(const Request requests[], int count,
                         ServiceResult results[], int *total_wait,
                         int *maximum_wait)
{
    int queue[MAX_REQUESTS];
    int front = 0;
    int rear = 0;
    int next_arrival = 0;
    int processed = 0;
    int current_time = 0;

    *total_wait = 0;
    *maximum_wait = 0;

    while (processed < count) {
        if (front == rear && next_arrival < count
            && current_time < requests[next_arrival].arrival_minute) {
            current_time = requests[next_arrival].arrival_minute;
        }

        while (next_arrival < count
               && requests[next_arrival].arrival_minute <= current_time) {
            queue[rear++] = next_arrival++;
        }

        if (front == rear)
            return 0;

        int index = queue[front++];
        int start = current_time;
        int finish = start + requests[index].service_minutes;
        int waiting = start - requests[index].arrival_minute;

        results[index].start_minute = start;
        results[index].finish_minute = finish;
        results[index].waiting_minutes = waiting;
        *total_wait += waiting;
        if (waiting > *maximum_wait)
            *maximum_wait = waiting;

        current_time = finish;
        ++processed;

        while (next_arrival < count
               && requests[next_arrival].arrival_minute <= current_time) {
            queue[rear++] = next_arrival++;
        }
    }

    return 1;
}

int main(void)
{
    const int count = REQUEST_COUNT;
    Request requests[MAX_REQUESTS];
    ServiceResult results[MAX_REQUESTS] = {{0, 0, 0}};
    int total_wait;
    int maximum_wait;

    if (count == 0) {
        puts("No requests to simulate.");
        return 0;
    }

    memcpy(requests, source_requests, (size_t)count * sizeof(requests[0]));
    sort_requests(requests, count);

    if (!simulate_fifo(requests, count, results, &total_wait, &maximum_wait)) {
        fputs("Simulation failed: an arrival could not be scheduled.\n", stderr);
        return 1;
    }

    puts("Requests are ordered by arrival time, then request ID.");
    puts("ID  Arrival  Service  Start  Finish  Wait");
    for (int i = 0; i < count; ++i) {
        printf("%-3s %7d %8d %6d %7d %5d\n",
               requests[i].id,
               requests[i].arrival_minute,
               requests[i].service_minutes,
               results[i].start_minute,
               results[i].finish_minute,
               results[i].waiting_minutes);
    }

    printf("Average waiting time: %.2f min\n",
           total_wait / (double)count);
    printf("Maximum waiting time: %d min\n", maximum_wait);
    return 0;
}