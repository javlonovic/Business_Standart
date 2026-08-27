"""Add orders, payments, pricing rules, currency rates

Revision ID: 002
Revises: 001
Create Date: 2024-01-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('estimate_total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM(name='orderstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    op.create_index('idx_orders_user_status_created', 'orders', ['user_id', 'status', 'created_at'])
    
    # Order status history table
    op.create_table('order_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('old_status', sa.String(length=30), nullable=False),
        sa.Column('new_status', sa.String(length=30), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_status_history_id'), 'order_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_order_status_history_order_id'), 'order_status_history', ['order_id'], unique=False)
    
    # Payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('provider', postgresql.ENUM(name='paymentprovider'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM(name='paymentstatus'), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('webhook_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_payments_external_id'), 'payments', ['external_id'], unique=True)
    
    # Pricing rules table
    op.create_table('pricing_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('param_key', sa.String(length=100), nullable=False),
        sa.Column('rate_type', sa.String(length=20), nullable=False),
        sa.Column('base_fee', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('tiers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pricing_rules_id'), 'pricing_rules', ['id'], unique=False)
    op.create_index(op.f('ix_pricing_rules_service_id'), 'pricing_rules', ['service_id'], unique=False)
    
    # Currency rates table
    op.create_table('currency_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=False), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=15, scale=6), nullable=False),
        sa.Column('change', sa.Numeric(precision=15, scale=6), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'currency_code', name='uq_date_currency')
    )
    op.create_index(op.f('ix_currency_rates_id'), 'currency_rates', ['id'], unique=False)
    op.create_index(op.f('ix_currency_rates_date'), 'currency_rates', ['date'], unique=False)
    op.create_index(op.f('ix_currency_rates_currency_code'), 'currency_rates', ['currency_code'], unique=False)


def downgrade() -> None:
    op.drop_table('currency_rates')
    op.drop_table('pricing_rules')
    op.drop_table('payments')
    op.drop_table('order_status_history')
    op.drop_table('orders')
