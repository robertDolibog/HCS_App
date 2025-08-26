from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from extensions import db  

class FileLocation(db.Model):
    __tablename__ = 'file_locations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(UUID(as_uuid=True),
                     ForeignKey('files.id', ondelete='CASCADE'),
                     nullable=False)
    location = Column(String, nullable=False)

    file = relationship('File', back_populates='locations')