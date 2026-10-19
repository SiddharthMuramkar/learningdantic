# Contract for specs 01-10

Ten sessions build in parallel. Spec 01 writes every file below, real or as a stub with the exact signature
and a docstring. Later specs fill in only the files they own and never change a signature here. If a signature
must change, stop and report.

## Owners

| File | Owner | Stub in 01 |
|---|---|---|
| pyproject.toml (`app` group), uv.lock, compose.yaml, .gitignore, alembic.ini, migrations/, .github/workflows/ci.yml | 01 (09 adds the Playwright steps to ci.yml) | real |
| app/__init__.py, db.py, models.py, identity.py, seed.py, schemas.py, main.py, app/tests/conftest.py | 01 | real |
| app/routes/tickets.py | 03 | stub |
| app/agents.py, app/memory.py, app/routes/chat.py | 04 (08 adds the shipping expert to agents.py) | stub |
| app/static/index.html, app/static/app.js | 05 | stub page with the ids below |
| app/patterns.py | 06 | stub |
| app/approvals.py, app/routes/approvals.py, app/static/approvals.js | 07 | stub |
| app/evals.py | 08 | stub |
| app/tests/e2e/ | 09 | none |
| track/README.md, .claude/skills/episode/SKILL.md | 02 | none |
| track/NN-slug/EPISODE.md, app/tests/test_epNN_*.py | the spec that teaches episode NN | none |

A stub body is `raise NotImplementedError("spec NN")`, a route answers 501, `approvals.record_pending` returns `None`.

## Signatures

```python
# app/__init__.py
from learningdantic import has_key, setup
MODEL = setup()  # loads .env, wires Logfire (never call logfire.configure again)
AGENT_MODEL = MODEL if has_key(MODEL) else "test"  # keyless: TestModel demo mode

# app/db.py
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://acme:acme@localhost:5432/acme")
engine = create_engine(DATABASE_URL)
def get_session() -> Iterator[Session]: ...
SessionDep = Annotated[Session, Depends(get_session)]

# app/models.py: Base(DeclarativeBase) with a MetaData naming_convention, and
#   Order(id int pk, customer str, items str, status str, amount_cents int)
#   Ticket(id int pk, customer str, subject str, created_at timestamptz now(), conversation JSONB null, version int 0)
#   AuditLog(id int pk, ticket_id fk, tool str, at timestamptz now())
#   Refund(id int pk, ticket_id fk, order_id fk, amount_cents int, tool_call_id str,
#          status str 'pending'|'approved'|'rejected'|'executed', unique(ticket_id, tool_call_id))

# app/identity.py
USERS = {"ada": "customer", "bo": "customer", "sam": "staff"}
@dataclass(frozen=True)
class User: name: str; role: str
def current_user(x_demo_user: Annotated[str | None, Header()] = None) -> User: ...  # 401 unless in USERS
UserDep = Annotated[User, Depends(current_user)]
def require_staff(user: UserDep) -> User: ...  # 403 unless staff
StaffDep = Annotated[User, Depends(require_staff)]

# app/seed.py
def seed(session: Session) -> None: ...  # orders 1042 (ada, "1 blue mug", delivered, 1200) and 2077 (bo, "2 white mugs", in transit, 2400); idempotent

# app/schemas.py
class OrderOut(BaseModel): id: int; items: str; status: str; amount_cents: int
class TicketIn(BaseModel): subject: str  # 1-200 chars
class TicketOut(BaseModel): id: int; customer: str; subject: str
class MessageIn(BaseModel): text: str  # 1-2000 chars
class ApprovalOut(BaseModel): refund_id: int; order_id: int; amount_cents: int
class ReplyOut(BaseModel): ticket_id: int; category: str | None = None; message: str | None = None; approval: ApprovalOut | None = None
class DecisionIn(BaseModel): decision: Literal["approve", "reject"]

# app/routes/tickets.py (03): router
#   POST /tickets  TicketIn -> TicketOut (201)          GET /tickets/{ticket_id} -> TicketOut
#   GET /orders/{order_id} -> OrderOut                  customers see only their own rows (else 404), staff see all

# app/memory.py (04)
class VersionConflict(Exception): ...
def load(ticket_id: int) -> tuple[Conversation | None, int]: ...       # (conversation, version)
def save(ticket_id: int, conversation: Conversation, version: int) -> None: ...  # UPDATE ... WHERE version=:v, 0 rows -> VersionConflict

# app/agents.py (04)
@dataclass
class Deps: ticket_id: int; customer: str; role: str
class Reply(BaseModel): category: Literal["billing", "shipping", "other"]; message: str
billing_expert: Agent; desk: Agent  # desk: deps_type=Deps, output_type=[Reply, DeferredToolRequests]
async def run_desk(ticket_id: int, user: User, text: str | None,
                   deferred_tool_results: DeferredToolResults | None = None) -> AgentRunResult: ...
#   load -> await desk.run(..., conversation=, usage_limits=UsageLimits(request_limit=used + 6)) -> save
#   tools: lookup_order(order_id: Annotated[int, Field(examples=[1042])]), async ask_billing(question),
#   issue_refund(order_id) requires_approval, offered only to staff, body = approvals.execute_refund(...)

# app/routes/chat.py (04): POST /tickets/{ticket_id}/messages  MessageIn -> ReplyOut  (async def; 409 on VersionConflict;
#   on DeferredToolRequests it calls approvals.record_pending and returns its ApprovalOut)

# app/approvals.py (07)
def record_pending(ticket_id: int, requests: DeferredToolRequests) -> ApprovalOut | None: ...  # stub: None
def execute_refund(ticket_id: int, tool_call_id: str) -> str: ...  # guarded UPDATE approved -> executed
# app/routes/approvals.py (07): POST /tickets/{ticket_id}/approvals/{refund_id}  DecisionIn -> ReplyOut  (StaffDep; 409 twice)

# app/patterns.py (06): each returns (answer, model requests)
async def one_agent(text: str) -> tuple[str, int]: ...
async def code_routing(text: str) -> tuple[str, int]: ...
async def delegation(text: str) -> tuple[str, int]: ...

# app/evals.py (08)
desk_evals: Dataset
async def answer(text: str) -> str: ...
```

Page ids (05, 07, 09): `#user` (select: ada, bo, sam), `#subject`, `#new-ticket`, `#message`, `#send`, `#log`;
chat lines `div[data-testid=user-message]` and `div[data-testid=assistant-message]`; `approvals.js` defines
`window.showApproval(ticketId, approval)` which renders `div[data-testid=approval-card]` with buttons
named "Approve" and "Reject". Every string goes in with `textContent`.

## Tests (01's conftest, used by everyone)

`MODEL=test` and `pydantic_ai.models.ALLOW_MODEL_REQUESTS = False` are set before `app` is imported.
`DATABASE_URL` points at the checkout's own test database, `acme_<8 hex of sha1(repo path)>_test`, which is dropped,
created and migrated (`alembic upgrade head`) once per session and dropped again at the end (`ACME_KEEP_TEST_DB=1` keeps it). Before each test: assert the database name ends in `_test`, `TRUNCATE ... RESTART IDENTITY CASCADE`,
then `seed()`. Fixtures: `client` (one session-scoped `TestClient(app)` used as a context manager) and
`session` (a SQLAlchemy Session on acme_test). Requests send `headers={"X-Demo-User": "ada"}`.

## Episode format (track/NN-slug/EPISODE.md, at most ~120 lines)

```
# NN: Title
**You'll see:** one sentence. **Time:** 30-45 min. **With me:** `/episode NN` (tour) or `/episode NN do` (your piece)
## Run it      commands, each followed by "> ✅ Checkpoint: what you should see"
## Read        3 places, `path:line` plus one sentence each
## Predict     at most 3 one-line guesses, each tied to a command above
## Break it    one sabotage, the symptom to guess, undo with `git restore .`
## Your piece  the function to blank, its locked test command, 3 hints from vague to exact
## Words       at most 5 new terms, one line each
```

Plain English, short sentences, the house style of CONTRIBUTING.md. No percentages from research.
