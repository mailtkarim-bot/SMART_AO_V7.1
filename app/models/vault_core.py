"""
SMART_AO V7 - Vault Core Model
==============================
PostgreSQL Vault model for document storage and semantic search
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.database import Base


class VaultDocument(Base):
    """
    Vault document model for storing uploaded documents
    
    Attributes:
        id: Unique identifier
        document_id: Human-readable document ID
        file_name: Original file name
        file_path: Storage path
        file_type: MIME type
        file_size: File size in bytes
        content_hash: SHA256 hash of content
        embedding: Vector embedding for semantic search
        metadata: Extracted metadata (pages, author, etc.)
        status: Processing status
        processed_at: When document was processed
        created_at: Upload timestamp
    """
    __tablename__ = "vault_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(64), unique=True, index=True, nullable=False)
    file_name = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(String(128), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    embedding = Column(ARRAY(Float), nullable=True)
    extra_metadata = Column(JSON, default={}, nullable=True)
    status = Column(String(64), default="uploaded", nullable=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VaultDocument(id={self.id}, document_id={self.document_id}, file_name={self.file_name})>"


class DocumentChunk(Base):
    """
    Document chunk model for semantic search
    
    Attributes:
        id: Unique identifier
        document_id: Reference to parent document
        chunk_index: Index within document
        content: Text content of chunk
        embedding: Vector embedding
        start_page: Starting page number
        end_page: Ending page number
        metadata: Chunk metadata
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    extra_metadata = Column(JSON, default={}, nullable=True)
    
    # Relationships
    document = relationship("VaultDocument", back_populates="chunks")
    
    __table_args__ = (
        # Composite unique constraint
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
    )
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"

