"""
SMART_AO V7 - 0019_project.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - 0019_project.py
=========================
Migration for Project model
Source: ARCHITECTURE_V7_ENGINE.md §4.2
Models: app/models/project.py
"""

# Alembic revision metadata
revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


# =============================================================================
# UPGRADE - Create Project table
# =============================================================================

def upgrade():
    """Create projects table"""
    
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('project_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=512), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=64), nullable=False, server_default='active'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('extra_metadata', sa.JSON(), nullable=True, default={}),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', name='uq_project_id'),
        sa.Index('idx_project_status', 'status'),
        sa.Index('idx_project_created_at', 'created_at'),
        sa.Index('idx_project_updated_at', 'updated_at'),
    )


# =============================================================================
# DOWNGRADE - Drop Project table
# =============================================================================

def downgrade():
    """Drop projects table"""
    op.drop_table('projects')
