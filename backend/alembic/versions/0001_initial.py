"""initial compact demo schema"""
from alembic import op
from app.db.base import Base
import app.models  # noqa: F401

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=bind)

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
