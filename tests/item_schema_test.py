import pytest
from pydantic import ValidationError

from app.schemas.item import ItemCreate, ItemUpdate

SCHEMAS = [ItemCreate, ItemUpdate]


@pytest.mark.parametrize("schema", SCHEMAS)
def test_title_is_kept(schema):
  assert schema(title="Buy milk").title == "Buy milk"


@pytest.mark.parametrize("schema", SCHEMAS)
def test_title_is_trimmed(schema):
  assert schema(title="  Buy milk  ").title == "Buy milk"


@pytest.mark.parametrize("schema", SCHEMAS)
def test_title_keeps_inner_spaces(schema):
  assert schema(title="Buy  oat   milk").title == "Buy  oat   milk"


@pytest.mark.parametrize("bad_title", ["", " ", "   ", "\t", "\n", " \t\n "])
@pytest.mark.parametrize("schema", SCHEMAS)
def test_blank_title_is_rejected(schema, bad_title):
  with pytest.raises(ValidationError) as exc:
    schema(title=bad_title)

  assert exc.value.errors()[0]["loc"] == ("title",)


@pytest.mark.parametrize("bad_title", [123, 1.5, True, ["a"], {"a": 1}])
@pytest.mark.parametrize("schema", SCHEMAS)
def test_non_string_title_is_rejected(schema, bad_title):
  with pytest.raises(ValidationError):
    schema(title=bad_title)


def test_create_requires_title():
  with pytest.raises(ValidationError) as exc:
    ItemCreate()

  assert exc.value.errors()[0]["type"] == "missing"


def test_create_title_cannot_be_null():
  with pytest.raises(ValidationError):
    ItemCreate(title=None)


def test_update_title_is_optional():
  data = ItemUpdate(completed=True)

  assert data.title is None
  assert data.model_dump(exclude_unset=True) == {"completed": True}


def test_update_trims_title_when_given():
  data = ItemUpdate(title="  New  ")

  assert data.model_dump(exclude_unset=True) == {"title": "New"}
