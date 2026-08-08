"""
SMART_AO V7 - 0018_events_v7.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - 0018_events_v7.py
=========================
Migration for Event and EventType models
Source: ARCHITECTURE_V7_ENGINE.md §4.4
"""

from alembic import op
import sqlalchemy as sa

# Alembic revision metadata
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None

# =============================================================================
# UPGRADE
# =============================================================================

def upgrade():
    """Create event tables"""
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('event_type', sa.String(length=64), nullable=False, index=True),
        sa.Column('event_data', sa.JSON(), nullable=True, default={}),
        sa.Column('source', sa.String(length=128), nullable=True),
        sa.Column('mission_id', sa.Integer(), nullable=True),
        sa.Column('step_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['step_id'], ['mission_steps.id'], ondelete='CASCADE'),
        sa.Index('idx_events_event_type', 'event_type'),
        sa.Index('idx_events_mission_id', 'mission_id'),
        sa.Index('idx_events_created_at', 'created_at'),
    )


# =============================================================================
# DOWNGRADE
# =============================================================================

def downgrade():
    """Drop event tables"""
    op.drop_table('events')

