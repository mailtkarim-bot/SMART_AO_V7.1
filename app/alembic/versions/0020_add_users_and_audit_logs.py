"""0020_add_users_and_audit_logs.py

Revision: 0020
Down Revision: 0019
Create Date: 2026-08-08

Add missing users and audit_logs tables, plus tenant_id columns for multi-tenant support.
"""

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add tenant_id columns to existing tables (with default for backward compatibility)
    op.add_column("missions", sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"))
    op.create_index("ix_missions_tenant_id", "missions", ["tenant_id"])
    
    op.add_column("mission_steps", sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"))
    op.create_index("ix_mission_steps_tenant_id", "mission_steps", ["tenant_id"])
    
    op.add_column("mission_events", sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"))
    op.create_index("ix_mission_events_tenant_id", "mission_events", ["tenant_id"])
    
    op.add_column("projects", sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"))
    op.create_index("ix_projects_tenant_id", "projects", ["tenant_id"])
    
    op.add_column("vault_documents", sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"))
    op.create_index("ix_vault_documents_tenant_id", "vault_documents", ["tenant_id"])
    
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(128), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="conducteur_travaux"),
        sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default", index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lock_until", sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create audit_logs table (WORM-compliant for ISO 27001 / RGPD)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("user_id", sa.String(64), index=True),
        sa.Column("username", sa.String(128)),
        sa.Column("role", sa.String(64)),
        sa.Column("tenant_id", sa.String(64), index=True),
        sa.Column("action", sa.String(64), nullable=False, index=True),
        sa.Column("level", sa.String(32), nullable=False, server_default="INFO"),
        sa.Column("resource_type", sa.String(64), index=True),
        sa.Column("resource_id", sa.String(128), index=True),
        sa.Column("details", sa.JSON()),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("hash", sa.String(64), index=True),
        sa.Column("is_modified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("users")
    
    op.drop_index("ix_vault_documents_tenant_id")
    op.drop_column("vault_documents", "tenant_id")
    
    op.drop_index("ix_projects_tenant_id")
    op.drop_column("projects", "tenant_id")
    
    op.drop_index("ix_mission_events_tenant_id")
    op.drop_column("mission_events", "tenant_id")
    
    op.drop_index("ix_mission_steps_tenant_id")
    op.drop_column("mission_steps", "tenant_id")
    
    op.drop_index("ix_missions_tenant_id")
    op.drop_column("missions", "tenant_id")
