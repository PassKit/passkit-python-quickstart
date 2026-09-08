# PassKit Python Quickstart

[![CI](https://github.com/PassKit/passkit-python-quickstart/actions/workflows/ci.yml/badge.svg)](https://github.com/PassKit/passkit-python-quickstart/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/passkit-python-grpc-sdk.svg)](https://pypi.org/project/passkit-python-grpc-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Create a working PassKit membership card, coupon, event ticket, or flight
boarding pass with the official Python SDK. Each guided example runs with one
command, prints the resulting wallet pass URL, and removes the test resources
it created.

## Quick start

You need Python 3.9 or newer, a free
[PassKit account](https://app.passkit.com/signup), and PassKit SDK credentials.

### 1. Download and install

```bash
git clone https://github.com/PassKit/passkit-python-quickstart.git
cd passkit-python-quickstart
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Get your PassKit credentials

1. Sign in to [PassKit](https://app.passkit.com).
2. Open **Developer Tools** from the account menu.
3. Under **Account Credentials**, select **SDK Credentials**.
4. Choose a strong password when prompted.
5. Download the three files sent to your registered email address:

   - `certificate.pem`
   - `key.pem`
   - `ca-chain.pem`

The password encrypts your private key; it is not your PassKit account
password. Generating another credential set invalidates the existing one.

### 3. Configure the quickstart

Create `certs/`, copy in all three credential files, and create `.env`:

```bash
mkdir -p certs
cp /path/to/downloads/certificate.pem certs/
cp /path/to/downloads/key.pem certs/
cp /path/to/downloads/ca-chain.pem certs/
cp .env.example .env
```

Open `.env` and set `PASSKIT_PASSPHRASE` to the SDK credential password.
Check **Developer Tools → API Region** and use:

- `grpc.pub1.passkit.io` for Europe
- `grpc.pub2.passkit.io` for the USA

The files under `certs/` and your `.env` are ignored by Git. Never commit or
share them.

### 4. Run an example

```bash
python main.py membership
python main.py coupons
python main.py event-tickets
python main.py flights
```

`loyalty` is an alias for `membership`, and `tickets` is an alias for
`event-tickets`.

A successful run prints output similar to:

```text
Created resources:
  bronzePassId: https://pub1.pskt.io/4MEIqDFudziP4ZFKx5osw3
Cleaning up generated resources...
```

Open the URL on a phone to add the pass to Apple Wallet or Google Wallet. On a
desktop, the PassKit page displays a QR code you can scan.

## What each workflow demonstrates

| Workflow | Included operations |
| --- | --- |
| Membership | Images, two templates, program and tiers, member enrolment, update, ID and external-ID lookup, check-in/out, earn and burn points, list, count, event history, and cleanup |
| Coupons | Images, before/after templates, campaign and offers, issue, update, get, list, count, redeem, void, and cleanup |
| Event tickets | Images, template, production, venue, future-dated event, ticket type, issue, update, lookup by ID/ticket/order number, list, count, validate, redeem, and cleanup |
| Flights | Images, template, carrier and airport create-or-reuse, future-dated flight and designator, lookup, boarding-pass issue and lookup, and ordered cleanup |

The focused implementations are under `quickstarts/workflows/`. Shared image,
template, cleanup, configuration, and connection logic is kept under
`quickstarts/`.

Each product also provides focused reusable calls through its own `methods.py`:
[`membership`](membership/README.md), [`coupons`](coupons/README.md),
[`event_tickets`](event_tickets/README.md), and [`flights`](flights/README.md).
The original individual scripts remain as compatible entry points. The guided
workflows are self-contained and use the maintained implementations under
`quickstarts/workflows/`.

## Flights

Flights require an Apple pass certificate uploaded to PassKit. Copy its pass
type identifier into `.env`:

```dotenv
PASSKIT_APPLE_CERTIFICATE=pass.com.example.airline
```

The default `YY` carrier and `YY4`/`ADP` airports are reused if they already
exist in your account. Reused infrastructure is never deleted. The flight
number and departure date are generated for each run.

## Keep generated resources

Cleanup runs even if an example fails partway through. To keep the generated
records for inspection, set:

```dotenv
PASSKIT_KEEP_ASSETS=true
```

You must then delete them manually. Return the value to `false` for normal use.

## Configuration reference

| Variable | Default | Purpose |
| --- | --- | --- |
| `PASSKIT_PASSPHRASE` | Empty | Password required when `key.pem` is encrypted |
| `PASSKIT_ADDRESS` | `grpc.pub1.passkit.io` | PassKit API region hostname |
| `PASSKIT_PORT` | `443` | gRPC port |
| `PASSKIT_ROOT_CERT` | `certs/ca-chain.pem` | PassKit CA chain |
| `PASSKIT_PRIVATE_KEY` | `certs/key.pem` | SDK private key |
| `PASSKIT_CERTIFICATE` | `certs/certificate.pem` | SDK client certificate |
| `PASSKIT_CONNECTION_MODE` | `pool` | `pool` or `single` |
| `PASSKIT_POOL_SIZE` | `5` | Number of reusable connections |
| `PASSKIT_KEEP_ASSETS` | `false` | Keep resources created by a run |
| `PASSKIT_RECIPIENT_EMAIL` | Empty | Optional real recipient email |
| `PASSKIT_APPLE_CERTIFICATE` | Empty | Apple pass type identifier for flights |
| `PASSKIT_FLIGHT_CARRIER` | `YY` | Two-character carrier code |
| `PASSKIT_FLIGHT_ORIGIN` | `YY4` | Origin airport code |
| `PASSKIT_FLIGHT_DESTINATION` | `ADP` | Destination airport code |

Values already set in your terminal take precedence over `.env`.

## Use the complete SDK API

`quickstarts/api.py` exposes all generated SDK services and methods. Print the
current operation list without credentials or a network connection:

```bash
python main.py operations
```

Create the API with the same reusable connection pool used by the examples:

```python
from passkit.io.common.common_objects_pb2 import Id

from quickstarts.api import PassKitApi
from quickstarts.client import ConnectionPool
from quickstarts.config import Config

config = Config.load()
config.validate()
pool = ConnectionPool(config)

try:
    api = PassKitApi(pool)
    program = api.members.getProgram(Id(id="YOUR_PROGRAM_ID"))
    print(program)
finally:
    pool.close()
```

Server-streaming methods return normal Python iterators. Use
`api.members.collect("listPrograms", request)` when a small result should be
collected into a list.

Sensitive account, credential, bulk-delete, and bulk-update operations are
blocked through the facade by default. They require an explicit opt-in:

```python
api = PassKitApi(pool, allow_destructive=True)
```

## Tests and project checks

These checks do not connect to PassKit or require credentials:

```bash
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
```

The live workflows create and delete PassKit resources and require `.env` and
the three credential files.

## Troubleshooting

### A credential file cannot be found

Confirm all three `.pem` files are under `certs/` and run the command from the
repository root.

### The private key cannot be decrypted

`PASSKIT_PASSPHRASE` must be the password chosen when generating the SDK
credentials. It is not your PassKit login password. Replace all three files
together if you generate a new credential set.

### Authentication or connection fails

Confirm your PassKit API region. Also check whether a firewall or VPN blocks
outbound HTTPS/gRPC traffic.

### Flights stop before connecting

Upload an Apple pass certificate to PassKit and set
`PASSKIT_APPLE_CERTIFICATE` to its pass type identifier.

### Resources remain after a failed run

Remove them in the PassKit portal and ensure `PASSKIT_KEEP_ASSETS=false`.

## Documentation and support

- [PassKit API documentation](https://docs.passkit.io/)
- [PassKit Help Centre](https://help.passkit.com/)
- [Open an issue](https://github.com/PassKit/passkit-python-quickstart/issues)
- Email [support@passkit.com](mailto:support@passkit.com)

## Licence

Distributed under the [MIT Licence](LICENSE).
