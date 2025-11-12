from time import perf_counter
from collections import defaultdict, deque


class _Metrics:
    def __init__(self):
        self.endpoint_counts = defaultdict(int)
        self.status_counts = defaultdict(int)
        self.endpoint_durations = defaultdict(lambda: deque(maxlen=200))

    def record(self, path: str, status_code: int, duration_sec: float) -> None:
        self.endpoint_counts[path] += 1
        self.status_counts[status_code] += 1
        self.endpoint_durations[path].append(duration_sec)

    def summary(self) -> dict:
        endpoints = {}
        for path, cnt in self.endpoint_counts.items():
            durs = list(self.endpoint_durations[path])
            avg_ms = round((sum(durs) / len(durs)) * 1000, 2) if durs else 0.0
            max_ms = round((max(durs)) * 1000, 2) if durs else 0.0
            endpoints[path] = {
                "count": cnt,
                "avg_ms": avg_ms,
                "p95_ms": round(sorted(durs)[int(0.95 * (len(durs) - 1))] * 1000, 2) if len(durs) > 1 else avg_ms,
                "max_ms": max_ms,
            }
        return {
            "endpoints": endpoints,
            "status_counts": dict(self.status_counts),
        }


metrics = _Metrics()


async def metrics_middleware(request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration = perf_counter() - start
    # Use path without query for aggregation
    path = request.url.path
    try:
        status_code = response.status_code
    except Exception:
        status_code = 500
    metrics.record(path, status_code, duration)
    return response


def get_metrics_summary() -> dict:
    return metrics.summary()