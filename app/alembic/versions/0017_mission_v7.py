"""
SMART_AO V7 - 0017_mission_v7.py
=========================
Migration for Mission, MissionStep, and MissionEvent models
Source: ARCHITECTURE_V7_ENGINE.md §4.1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# =============================================================================
# UPGRADE
# =============================================================================

def upgrade():
    """Create mission tables"""
    # Create missions table
    op.create_table(
        'missions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('mission_id', sa.String(length=64), nullable=False, index=True, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False, default='CREATED'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_steps', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True, default={}),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mission_id', name='uq_mission_id'),
        sa.Index('idx_mission_status', 'status'),
        sa.Index('idx_mission_project_id', 'project_id'),
    )
    
    # Create mission_steps table
    op.create_table(
        'mission_steps',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('mission_id', sa.Integer(), nullable=False, index=True),
        sa.Column('step_name', sa.String(length=64), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, default='PENDING'),
        sa.Column('input_data', sa.JSON(), nullable=True, default={}),
        sa.Column('output_data', sa.JSON(), nullable=True, default={}),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('agent_name', sa.String(length=128), nullable=True),
        sa.Column('execution_time_ms', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('mission_id', 'step_order', name='uq_mission_step'),
        sa.Index('idx_mission_step_mission_id', 'mission_id'),
    )
    
    # Create mission_events table
    op.create_table(
        'mission_events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('mission_id', sa.Integer(), nullable=True, index=True),
        sa.Column('step_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['step_id'], ['mission_steps.id'], ondelete='CASCADE'),
        sa.Index('idx_mission_events_mission_id', 'mission_id'),
        sa.Index('idx_mission_events_step_id', 'step_id'),
    )


# =============================================================================
# DOWNGRADE
# =============================================================================

def downgrade():
    """Drop mission tables"""
    op.drop_table('mission_events')
    op.drop_table('mission_steps')
    op.drop_table('missions')

