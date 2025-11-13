"""
Database Schemas for 3D Printing Service

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, Dict, List

class Printer(BaseModel):
    """Showcase item (a 3D printer or printed product)"""
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Short description")
    price: Optional[float] = Field(None, ge=0, description="Price (optional)")
    image_url: Optional[HttpUrl] = Field(None, description="Main image URL")
    specs: Optional[Dict[str, str]] = Field(default_factory=dict, description="Key-value specs")
    tags: Optional[List[str]] = Field(default_factory=list, description="Search tags")
    available: bool = Field(default=True, description="Visibility toggle")

class ContactMessage(BaseModel):
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    phone: Optional[str] = Field(None, description="Phone number")
    message: str = Field(..., min_length=5, description="Message body")
    status: str = Field(default="new", description="new|read|archived")

class SocialLink(BaseModel):
    platform: str = Field(..., description="e.g., Instagram, Facebook, LinkedIn")
    url: HttpUrl = Field(..., description="Profile URL")
    visible: bool = Field(default=True)
