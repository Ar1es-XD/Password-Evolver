import sys

from alembic import command
from alembic.config import Config


def main() -> int:
    config = Config("backend/alembic.ini")
    command.upgrade(config, "head")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
