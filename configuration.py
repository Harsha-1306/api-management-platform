"""
Configuration Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON

from app.database import Base


class Configuration(Base):
    """Configuration model for storing application settings"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string", nullable=False)  # string, json, integer, boolean
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_sensitive = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    def get_typed_value(self):
        """Return the value converted to its proper type"""
        if self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.value_type == "json":
            import json
            return json.loads(self.value)
        return self.value
    
    def __repr__(self):
        return f"<Configuration(key={self.key}, type={self.value_type})>"
