from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from extensions import db  

class File(db.Model):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    last_modified = Column(DateTime, nullable=False)
    sensitivity = Column(String, nullable=False)
    backup_count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False,
                        default=datetime.utcnow, onupdate=datetime.utcnow)

    locations = relationship(
        'FileLocation',
        back_populates='file',
        cascade='all, delete-orphan'
    )