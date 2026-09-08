# Event ticket methods

[`methods.py`](methods.py) contains focused functions for creating a production,
venue, event and ticket type; issuing, updating, finding, listing, counting,
validating and redeeming tickets; and deleting generated resources.

The methods include resource creation, retrieval, update, list, copy and
deletion; ticket issue and lookup; downloadable pass retrieval; and individual
or order-level redemption and deletion. Each function accepts a gRPC channel,
so several calls can reuse one pooled connection:

```python
from event_tickets import create_production
from quickstarts.client import ConnectionPool
from quickstarts.config import Config

config = Config.load()
config.validate()
pool = ConnectionPool(config)

try:
    production_id = create_production(pool.service("event_tickets"))
    print(production_id)
finally:
    pool.close()
```

For a complete example with automatic dependency creation and cleanup, run:

```bash
python main.py event-tickets
```
