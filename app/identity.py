"""The demo login: an `X-Demo-User` header. This is a labelled fake, not real authentication."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException

USERS = {"ada": "customer", "bo": "customer", "sam": "staff"}


@dataclass(frozen=True)
class User:
    name: str
    role: str


def current_user(x_demo_user: Annotated[str | None, Header()] = None) -> User:
    if x_demo_user not in USERS:
        raise HTTPException(status_code=401, detail="Send an X-Demo-User header: ada, bo or sam")
    return User(name=x_demo_user, role=USERS[x_demo_user])


UserDep = Annotated[User, Depends(current_user)]


def require_staff(user: UserDep) -> User:
    if user.role != "staff":
        raise HTTPException(status_code=403, detail="Staff only")
    return user


StaffDep = Annotated[User, Depends(require_staff)]
