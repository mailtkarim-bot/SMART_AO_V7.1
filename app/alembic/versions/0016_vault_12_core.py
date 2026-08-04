"""
SMART_AO V7 - 0016_vault_12_core.py
================================
Migration for Vault Core tables (VaultDocument, DocumentChunk)
Source: ARCHITECTURE_V7_ENGINE.md §4.3
Models: app/models/vault_core.py
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic revision metadata
revision = '0016'
down_revision = None
branch_labels = None
depends_on = None


# =============================================================================
# UPGRADE - Create Vault Core tables
# =============================================================================

def upgrade():
    """Create vault_documents and document_chunks tables"""
    
    # Create vault_documents table
    op.create_table(
        'vault_documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('document_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('file_name', sa.String(length=512), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_type', sa.String(length=128), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True, index=True),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True, default={}),
        sa.Column('status', sa.String(length=64), nullable=False, server_default='uploaded'),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', name='uq_vault_document_id'),
        sa.Index('idx_vault_document_status', 'status'),
        sa.Index('idx_vault_document_created_at', 'created_at'),
        sa.Index('idx_vault_document_content_hash', 'content_hash'),
    )
    
    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('document_id', sa.Integer(), nullable=False, index=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('start_page', sa.Integer(), nullable=True),
        sa.Column('end_page', sa.Integer(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True, default={}),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'chunk_index', name='uq_document_chunk'),
        sa.ForeignKeyConstraint(['document_id'], ['vault_documents.id'], ondelete='CASCADE'),
        sa.Index('idx_document_chunk_document_id', 'document_id'),
        sa.Index('idx_document_chunk_chunk_index', 'chunk_index'),
    )


# =============================================================================
# DOWNGRADE - Drop Vault Core tables
# =============================================================================

def downgrade():
    """Drop vault_documents and document_chunks tables"""
    op.drop_table('document_chunks')
    op.drop_table('vault_documents')

