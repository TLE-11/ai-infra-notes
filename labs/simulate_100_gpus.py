"""100 张 GPU 的教学模拟。运行：python3 labs/simulate_100_gpus.py"""

from dataclasses import dataclass

TOTAL = 100


@dataclass
class Queue:
    name: str
    share: int
    jobs: list[int]  # 每个数字表示一个运行中任务占用的卡数。
    limit: int = TOTAL

    @property
    def used(self):
        return sum(self.jobs)


def show(a, b):
    for queue in (a, b):
        borrowed = max(0, queue.used - queue.share)
        print(f"  {queue.name}: 已分配 {queue.used:2} | 应得 {queue.share} | 借用 {borrowed:2}")
    print(f"  池内空闲: {TOTAL - a.used - b.used}\n")


def request(queue, other, demand):
    """增加一个队列的总需求。新增任务各用 1 卡，回收时只能停止完整任务。"""
    if not isinstance(demand, int) or demand < queue.used:
        raise ValueError("需求必须是整数，且不能小于当前分配量；本例只演示增加需求")
    if queue.used > queue.limit or other.used > other.limit or queue.used + other.used > TOTAL:
        raise ValueError("起点分配不能超过队列上限或资源池总量")

    print(f"[需求] {queue.name} 总需求变为 {demand} 张（当前 {queue.used} 张）")
    before_borrowed = max(0, queue.used - queue.share)
    target = min(demand, queue.limit)
    if demand > queue.limit:
        print(f"[上限] {queue.name} 最多只能使用 {queue.limit} 张")

    # 先分配空闲卡，不需要打断任何任务。
    free = TOTAL - queue.used - other.used
    granted = min(target - queue.used, free)
    if granted:
        queue.jobs.extend([1] * granted)
        print(f"[分配] {queue.name} 从空闲池获得 {granted} 张，无需抢占")

    # 只为恢复自身份额而回收；不能拿走对方应得份额内的资源。
    need = target - queue.used
    own_room = max(0, queue.share - queue.used)
    other_extra = max(0, other.used - other.share)
    reclaim = min(need, own_room, other_extra)
    if reclaim:
        print(f"[回收] {queue.name} 为恢复自身份额，计划从 {other.name} 收回 {reclaim} 张")
        freed = 0
        stopped = 0
        # 从最后一个任务开始找。停止完整任务，但不能把对方压到应得份额以下。
        for index in range(len(other.jobs) - 1, -1, -1):
            size = other.jobs[index]
            if other.used - size < other.share:
                continue
            freed += other.jobs.pop(index)
            stopped += 1
            if freed >= reclaim:
                break
        if stopped:
            print(f"[抢占] 停止 {other.name} 的 {stopped} 个完整任务，释放 {freed} 张")
            granted = min(reclaim, freed)
            queue.jobs.extend([1] * granted)
            print(f"[分配] {queue.name} 获得 {granted} 张，多释放的 {freed - granted} 张留在空闲池")
        else:
            print("[等待] 没有能完整退出且不侵入对方应得份额的任务")

    borrowed = max(0, queue.used - queue.share)
    if borrowed > before_borrowed:
        print(f"[借用] {queue.name} 新增借用 {borrowed - before_borrowed} 张，当前共借用 {borrowed} 张")
    if queue.used < demand:
        print(f"[等待] {queue.name} 还有 {demand - queue.used} 张需求未满足；不会越过回收边界")
    show(queue, other)


def make_queues(a, b, b_size=1, b_limit=TOTAL):
    if a < 0 or b < 0 or b_size <= 0 or b % b_size:
        raise ValueError("初始卡数不能为负，B 的卡数必须能按任务大小整除")
    return Queue("A", 60, [1] * a), Queue("B", 40, [b_size] * (b // b_size), b_limit)


def main():
    print("=== 1. 连续演示：借用 → 回收并抢占 → 等待 ===")
    a, b = make_queues(20, 40)
    show(a, b)
    request(b, a, 80)
    request(a, b, 50)
    request(a, b, 60)
    print("A 又提出高优需求；本模型未授予跨份额抢占权限。")
    request(a, b, 70)

    print("=== 2. 独立起算：池里有空闲，但队列有上限 ===")
    a, b = make_queues(10, 40, b_limit=70)
    request(b, a, 90)

    print("=== 3. 独立起算：先用空闲 10 张，再回收 20 张 ===")
    a, b = make_queues(20, 70)
    request(a, b, 50)

    print("=== 4. 独立起算：B 每个任务固定占 8 张卡 ===")
    a, b = make_queues(20, 80, b_size=8)
    show(a, b)
    request(a, b, 50)


if __name__ == "__main__":
    main()
