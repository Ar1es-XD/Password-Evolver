import sys

from alembic import command
from alembic.config import Config


def main() -> int:
    config = Config("backend/alembic.ini")
    message = " ".join(sys.argv[1:]) or "auto"
    command.revision(config, message=message, autogenerate=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
