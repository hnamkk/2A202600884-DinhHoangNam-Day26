import os
import pytest
from db import SQLiteAdapter, ValidationError

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sqlite_lab.db")

@pytest.fixture(scope="module")
def adapter():
    # Make sure DB exists and initialized
    import init_db
    init_db.create_database(DB_PATH)
    return SQLiteAdapter(DB_PATH)

def test_list_tables(adapter):
    tables = adapter.list_tables()
    assert "students" in tables
    assert "courses" in tables
    assert "enrollments" in tables

def test_get_table_schema(adapter):
    schema = adapter.get_table_schema("students")
    cols = [col["name"] for col in schema]
    assert "id" in cols
    assert "name" in cols

def test_invalid_table_schema(adapter):
    with pytest.raises(ValidationError):
        adapter.get_table_schema("nonexistent_table")

def test_search_valid(adapter):
    results = adapter.search("students", filters=[{"column": "cohort", "operator": "=", "value": "A1"}])
    assert len(results) > 0
    for r in results:
        assert r["cohort"] == "A1"

def test_search_invalid_column(adapter):
    with pytest.raises(ValidationError):
        adapter.search("students", columns=["bad_column"])

def test_search_invalid_operator(adapter):
    with pytest.raises(ValidationError):
        adapter.search("students", filters=[{"column": "name", "operator": "BAD_OP", "value": "test"}])

def test_insert_valid(adapter):
    new_student = {"name": "Frank", "cohort": "C3", "score": 88.5}
    inserted = adapter.insert("students", new_student)
    assert inserted["name"] == "Frank"
    assert "id" in inserted

def test_insert_invalid_column(adapter):
    bad_student = {"name": "Grace", "bad_col": 123}
    with pytest.raises(ValidationError):
        adapter.insert("students", bad_student)

def test_aggregate_valid(adapter):
    results = adapter.aggregate("students", metric="count")
    assert len(results) == 1
    assert results[0]["value"] >= 5

def test_aggregate_group_by(adapter):
    results = adapter.aggregate("students", metric="avg", column="score", group_by="cohort")
    assert len(results) > 0
    for r in results:
        assert "cohort" in r
        assert "value" in r

def test_aggregate_invalid_metric(adapter):
    with pytest.raises(ValidationError):
        adapter.aggregate("students", metric="invalid_metric")
