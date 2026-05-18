import sys

from alembic import command
from alembic.config import Config


def main() -> int:
    config = Config("backend/alembic.ini")
    target = sys.argv[1] if len(sys.argv) > 1 else "-1"
    command.downgrade(config, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
