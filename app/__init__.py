"""Acme Desk: a small support-desk web app. Importing this package runs setup() once."""

from learningdantic import has_key, setup

MODEL = setup()  # loads .env, wires Logfire (never call logfire.configure again)
AGENT_MODEL = MODEL if has_key(MODEL) else "test"  # keyless: TestModel demo mode
