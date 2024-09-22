"""initial compact demo schema"""
from alembic import op
from app.db.base import Base
import app.models  # noqa: F401

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None
