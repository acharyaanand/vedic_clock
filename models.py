"""
AETHERIS — Data Models
Pydantic request/response models and SQLAlchemy DB models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BirthDetails(BaseModel):
    name: str = "Native"
    year: int = Field(..., ge=1800, le=2400)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    second: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "Asia/Kolkata"
    ayanamsa: str = "lahiri"
    house_system: str = "whole_sign"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Test Native",
                "year": 1990,
                "month": 1,
                "day": 15,
                "hour": 10,
                "minute": 30,
                "second": 0,
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone": "Asia/Kolkata",
                "ayanamsa": "lahiri",
                "house_system": "whole_sign"
            }
        }


class VedicChartRequest(BaseModel):
    birth_details: BirthDetails
    include_panchanga: bool = True
    include_muhurta: bool = True
    target_month_offset: int = Field(1, ge=0, le=24)

    class Config:
        json_schema_extra = {
            "example": {
                "birth_details": {
                    "name": "Test Native",
                    "year": 1990,
                    "month": 1,
                    "day": 15,
                    "hour": 10,
                    "minute": 30,
                    "second": 0,
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata",
                    "ayanamsa": "lahiri",
                    "house_system": "whole_sign"
                },
                "include_panchanga": True,
                "include_muhurta": True,
                "target_month_offset": 1
            }
        }


class UserChart(Base):
    __tablename__ = "user_charts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chart_id = Column(String(100), unique=True, index=True, nullable=False)
    user_name = Column(String(200), nullable=True)
    birth_details_json = Column(JSON, nullable=True)
    chart_data_json = Column(JSON, nullable=True)
    yogas_json = Column(JSON, nullable=True)
    doshas_json = Column(JSON, nullable=True)
    panchanga_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
