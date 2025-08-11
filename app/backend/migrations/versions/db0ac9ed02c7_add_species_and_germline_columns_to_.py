"""add_species_and_germline_columns_to_sequence_domains

Revision ID: db0ac9ed02c7
Revises: 769431e017ff
Create Date: 2025-08-11 18:31:37.247731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db0ac9ed02c7'
down_revision = '769431e017ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add species and germline columns to sequence_domains table
    op.add_column('sequence_domains', sa.Column('species', sa.String(50), nullable=True))
    op.add_column('sequence_domains', sa.Column('germline', sa.String(100), nullable=True))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_sequence_domains_species'), 'sequence_domains', ['species'], unique=False)
    op.create_index(op.f('ix_sequence_domains_germline'), 'sequence_domains', ['germline'], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index(op.f('ix_sequence_domains_germline'), table_name='sequence_domains')
    op.drop_index(op.f('ix_sequence_domains_species'), table_name='sequence_domains')
    
    # Remove columns
    op.drop_column('sequence_domains', 'germline')
    op.drop_column('sequence_domains', 'species')
