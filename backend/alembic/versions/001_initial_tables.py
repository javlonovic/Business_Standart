    """Initial tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('client', 'admin', 'superadmin')")
    op.execute("CREATE TYPE orderstatus AS ENUM ('draft', 'awaiting_payment', 'paid', 'in_progress', 'ready', 'delivered', 'cancelled')")
    op.execute("CREATE TYPE paymentprovider AS ENUM ('payme', 'click')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'success', 'failed', 'cancelled')")
    
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', postgresql.ENUM(name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Services table
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name_ru', sa.String(length=255), nullable=False),
        sa.Column('description_ru', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)
    op.create_index(op.f('ix_services_slug'), 'services', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_table('services')
    op.drop_table('users')
    op.execute("DROP TYPE userrole")
    op.execute("DROP TYPE orderstatus")
    op.execute("DROP TYPE paymentprovider")
    op.execute("DROP TYPE paymentstatus")
