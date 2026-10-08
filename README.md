# From Logs to Traces in Python

A small learning project: simulate a login request, measure its work, and print
completed spans as structured JSON logs. Uses only Python's standard library.

## Run it

With Python 3 installed, open a terminal in this folder and run:

```sh
python main.py
```

The program pauses for about 200 milliseconds and prints two JSON lines.
See [example-output.jsonl](example-output.jsonl) for a captured run.
IDs, timestamps, and durations change on each run.

```text
login-request                 root span
└── fetch-user                child span, about 200 ms
```

The child prints first because it finishes first. The root duration includes the
child's work; adding both durations would double-count that time.

## How does a log become a span?

A structured log starts as an event with named fields:

```json
{"name": "fetch-user", "attributes": {"user_id": "J-123"}}
```

Add a start timestamp and duration, and it describes an operation over time.
Add a trace ID, span ID, and parent span ID, and it also describes how that
operation relates to other work.

| Field | Meaning |
| --- | --- |
| `name` | The operation being measured |
| `start_time` | When it started, in Unix milliseconds |
| `duration_ms` | How long it took, in milliseconds |
| `trace_id` | Groups operations belonging to the same request |
| `span_id` | Identifies this individual operation |
| `parent_span_id` | Identifies the operation that started this one; `null` for the root |
| `attributes` | Extra context, such as a user ID or service name |

The `Span` class captures these fields while the code runs, then `end()` emits
them as JSON. We are creating span records directly and storing them as log
lines. We are not recovering missing timing or relationships from old logs.

JSON is the text format; a span is what the record represents. A reader could
group these records by `trace_id`, connect children through `parent_span_id`,
and draw a timeline using their start times and durations.

"Traces are fancy logs" is a useful first intuition: the extra timing and
relationships make the records useful together. Arbitrary logs do not necessarily
contain enough information to reconstruct a trace.

## What the Python code teaches

- A dictionary holds the event in memory. `json.dumps()` turns it into JSON text.
- `time.time()` gives seconds since January 1, 1970 UTC. Multiplying by 1,000
  converts seconds to milliseconds; `int()` removes the fractional part.
- `time.perf_counter()` measures elapsed time without system clock adjustments
  changing the duration.
- `secrets.token_hex(16)` creates a 32-character trace ID; `token_hex(8)` creates
  a 16-character span ID. These follow common tracing ID lengths.
- A root gets a new trace ID. A child inherits that trace ID, gets a new span ID,
  and records its parent's span ID.
- `__init__` initializes each span. `self` refers to that particular instance.
- `**attributes` collects extra named arguments into a dictionary.

## Is this distributed tracing?

This is a local simulation in one Python process. In a distributed system, the
calling service must send trace context to the next service, usually through
request headers. The receiving service uses that context when creating its span.

This project does not implement context propagation, export spans to a tracing
backend, or automatically finish spans when operations fail. Call `end()` once
per span. Production instrumentation typically handles those concerns with a
tracing library such as OpenTelemetry.
