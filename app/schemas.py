from pydantic import BaseModel
from typing import List, Optional
import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class RoleBase(BaseModel):
    name: str
    permissions: str

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    roles: List[Role] = []
    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    title: str
    company_name: str
    document_type: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    document_id: int
    uploaded_by: int
    created_at: datetime.datetime
    file_path: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
