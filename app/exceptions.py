from functools import cache

from sqlalchemy.exc import IntegrityError

from app.database import Base

class DomainError(Exception):
  def __init__(self, msg: str, field: str | None = None) -> None:
    super().__init__(msg)
    self.msg = msg
    self.field = field

  def to_detail(self) -> list[dict]:
    loc = ["body", self.field] if self.field else ["body"]
    return [{"loc": loc, "msg": self.msg}]


@cache
def constraint_errors() -> dict[str, DomainError]:
  errors: dict[str, DomainError] = {}
  for table in Base.metadata.tables.values():
    for rule in (*table.constraints, *table.indexes):
      if rule.name and "msg" in rule.info:
        errors[rule.name] = DomainError(rule.info["msg"], rule.info.get("field"))
  return errors

def translate(exc: IntegrityError) -> DomainError | None:
  err = exc.orig
  while err is not None:
    if name := getattr(err, "constraint_name", None):
      return constraint_errors().get(name)
    err = err.__cause__
  return None
