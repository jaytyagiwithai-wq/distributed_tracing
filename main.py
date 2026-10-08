"""A small local tracing simulation that writes completed spans as JSON logs."""

import json
import secrets
import time


class Span:
    """Record the timing and relationships of one operation."""

    def __init__(self, name, parent=None, **attributes):
        self.name = name
        self.span_id = secrets.token_hex(8)
        self.attributes = attributes

        if parent is None:
            self.trace_id = secrets.token_hex(16)
            self.parent_span_id = None
        else:
            self.trace_id = parent.trace_id
            self.parent_span_id = parent.span_id

        # Wall-clock time answers "when?"; the elapsed timer answers "how long?"
        self.start_time = int(time.time() * 1000)
        self._timer = time.perf_counter()

    def end(self):
        duration_ms = (time.perf_counter() - self._timer) * 1000
        event = {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time,
            "duration_ms": round(duration_ms, 2),
            "attributes": self.attributes,
        }
        print(json.dumps(event))


def main():
    root = Span("login-request", user_id="J-123")

    child = Span("fetch-user", parent=root, service="auth-service")
    time.sleep(0.2)  # Simulate a database operation lasting about 200 ms.
    child.end()

    root.end()


if __name__ == "__main__":
    main()
