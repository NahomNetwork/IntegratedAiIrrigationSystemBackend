"""created table auto

Revision ID: bfff27e6f121
Revises: 
Create Date: 2025-05-19 21:13:46.559397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfff27e6f121'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensordata',
    sa.Column('Air_humidity_', sa.Float(), nullable=True),
    sa.Column('Air_temperature_C', sa.Float(), nullable=True),
    sa.Column('Pressure_KPa', sa.Float(), nullable=True),
    sa.Column('Soil_Humidity', sa.Float(), nullable=True),
    sa.Column('Soil_Moisture', sa.Float(), nullable=True),
    sa.Column('Temperature', sa.Float(), nullable=True),
    sa.Column('Time', sa.Float(), nullable=True),
    sa.Column('Wind_speed_Kmh', sa.Float(), nullable=True),
    sa.Column('number_of_working_sensors', sa.Float(), nullable=True),
    sa.Column('prediction', sa.Integer(), nullable=True),
    sa.Column('rainfall', sa.Float(), nullable=True),
    sa.Column('received_at', sa.DateTime(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensordata_id'), 'sensordata', ['id'], unique=False)
    op.create_table('nonworkingsensor',
    sa.Column('sensor_name', sa.String(), nullable=False),
    sa.Column('sensor_data_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['sensor_data_id'], ['sensordata.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nonworkingsensor_id'), 'nonworkingsensor', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_nonworkingsensor_id'), table_name='nonworkingsensor')
    op.drop_table('nonworkingsensor')
    op.drop_index(op.f('ix_sensordata_id'), table_name='sensordata')
    op.drop_table('sensordata')
    # ### end Alembic commands ###
