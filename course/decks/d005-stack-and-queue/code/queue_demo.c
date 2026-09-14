/* Sequential vs circular queue: a classroom demo in two parts.
 * Part 1 reproduces the "fake full" of a plain sequential queue:
 * dequeue only moves front forward, so after rear reaches the end of
 * the array, the empty slots before front can no longer be used.
 * Part 2 implements a circular queue (one slot sacrificed) and traces
 * front/rear until the full test (rear + 1) % N == front fires.
 */
#include <stdio.h>

#define N 5

/* ---------------- Part 1: plain sequential queue ---------------- */

static void demo_fake_full(void)
{
    int q[N];
    int front = 0;
    int rear = 0;   /* elements live in q[front .. rear-1] */
    int task = 1;

    printf("=== Part 1: plain sequential queue (N = %d) ===\n", N);
    printf("enqueue moves rear forward; dequeue only moves front forward.\n\n");

    while (task <= 8) {
        if (rear < N) {
            q[rear] = task;
            rear++;
            printf("enqueue %d  -> front = %d, rear = %d\n", task, front, rear);
        } else {
            printf("enqueue %d  -> REJECTED: rear = %d reached the end\n",
                   task, rear);
        }
        task++;
        if (front < rear && task % 2 == 0) {
            printf("dequeue %d  -> front = %d, rear = %d\n",
                   q[front], front + 1, rear);
            front++;
        }
    }
    printf("\nrear is stuck at %d, yet %d slot(s) before front = %d sit empty.\n",
           rear, front, front);
    printf("This is the \"fake full\": space exists, but cannot be used.\n");
}

/* --------------- Part 2: circular queue (one slot lost) --------------- */

static int cq_full(int front, int rear)
{
    return (rear + 1) % N == front;   /* one slot is always left empty */
}

static void enqueue(int *q, int *front, int *rear, int task)
{
    if (cq_full(*front, *rear)) {
        printf("enqueue %d  -> FULL: (rear + 1) %% %d = %d == front, task waits\n",
               task, N, (*rear + 1) % N);
        return;
    }
    q[*rear] = task;
    *rear = (*rear + 1) % N;
    printf("enqueue %d  -> front = %d, rear = %d\n", task, *front, *rear);
}

static void dequeue(const int *q, int *front, int rear)
{
    printf("dequeue %d  -> front = %d, rear = %d\n",
           q[*front], (*front + 1) % N, rear);
    *front = (*front + 1) % N;
}

static void demo_circular(void)
{
    int q[N];
    int front = 0;
    int rear = 0;
    int task;

    printf("\n=== Part 2: circular queue (N = %d, one slot sacrificed) ===\n", N);
    printf("rear = (rear + 1) %% N; full when (rear + 1) %% N == front.\n\n");

    printf("-- phase 1: enqueue 1..5 into an array of %d --\n", N);
    for (task = 1; task <= 5; ++task) {
        enqueue(q, &front, &rear, task);
    }

    printf("\n-- phase 2: dequeue 2 --\n");
    dequeue(q, &front, rear);
    dequeue(q, &front, rear);

    printf("\n-- phase 3: enqueue 2 more, rear wraps around --\n");
    enqueue(q, &front, &rear, 6);
    enqueue(q, &front, &rear, 7);

    printf("\nfront = %d, rear = %d: rear wrapped from %d back to 0 and reused\n",
           front, rear, N - 1);
    printf("the slots freed by dequeue. The queue is full again with N - 1 = %d\n",
           N - 1);
    printf("tasks, one slot sacrificed to tell full from empty.\n");
}

int main(void)
{
    demo_fake_full();
    demo_circular();
    return 0;
}
