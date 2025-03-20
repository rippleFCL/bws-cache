from telnetlib import GA
from prometheus_client import Counter, Gauge
from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder

from models import StatsResponse


class PromMetricsClient:
    REGISTRY = REGISTRY

    def __init__(self):
        self.cache_hit = Counter("cache_hits", "cache hits", ["type"])
        self.cache_miss = Counter("cache_miss", "cache miss", ["type"])
        self.cache_size = Gauge("cache_size", "cache size", ["type", "client"])
        self.num_clients = Gauge("num_clients", "number of clients")
        self.http_request_total = Counter(
            "http_request_total", "http request total", ["endpoint", "status_code"]
        )
        self.http_request_duration = Gauge(
            "http_request_duration", "http request duration", ["endpoint"]
        )

    def tick_cache_hits(self, type: str):
        self.cache_hit.labels(type=type).inc()

    def tick_cache_miss(self, type: str):
        self.cache_miss.labels(type=type).inc()

    def tick_http_request_total(self, endpoint: str, status_code: str):
        self.http_request_total.labels(endpoint=endpoint, status_code=status_code).inc()

    def tick_http_request_duration(self, endpoint: str, duration):
        self.http_request_duration.labels(endpoint=endpoint).set(duration)

    def tick_stats(self, stats: StatsResponse):
        self.num_clients.set(stats.num_clients)
        for client, client_stats in stats.client_stats.items():
            self.cache_size.labels(type="secret", client=client).set(client_stats.secret_cache_size)
            self.cache_size.labels(type="keymap", client=client).set(client_stats.keymap_cache_size)
        self.cache_size.labels(type="secret", client="total").set(stats.total_stats.secret_cache_size)
        self.cache_size.labels(type="keymap", client="total").set(stats.total_stats.keymap_cache_size)

    def generate_metrics(self, accept_header):
        generate_latest, content_type = choose_encoder(accept_header)
        generated_content = generate_latest(self.REGISTRY).decode("utf-8")
        return generated_content, content_type
