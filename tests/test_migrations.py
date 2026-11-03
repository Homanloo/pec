import pytest
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db
def test_all_migrations_applied():
    executor = MigrationExecutor(connection)
    assert executor.migration_plan(executor.loader.graph.leaf_nodes()) == []


@pytest.mark.django_db
def test_models_match_migrations():
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)
