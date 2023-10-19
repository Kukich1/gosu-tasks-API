from pydantic import BaseModel, validator

class User(BaseModel):
    id: str = None
    name: str 
    username: str
    password: str
    role: int


    @validator("role")
    def validate_is_active(cls, value):
        if value not in (0, 1):
            raise ValueError("Value must be 0 or 1")
        return value

class UserLogin(BaseModel):
    username: str
    password: str

class Project(BaseModel):
    id: str = None
    name: str
    description: str
    members: list[str]
    deadline: int
    created_at: int = None
    time_completed: int = None
    status: str = None

class Task(BaseModel):
    id: str = None
    name: str
    description: str
    members: list[str]
    project: str
    deadline: int
    created_at: int = None
    comments: list[str] = []
    time_completed: int = None
    type: str = None
    status: str = None

class Post(BaseModel):
    id: str = None
    name: str
    description: str
    member: str 
    task: str
    created_at: int = None
    time_completed: int = None
    type: str  = None
    status: str = None

class Updated_post(BaseModel):
    post_text: str

class Comment(BaseModel):
    comment: str

class TYPE(BaseModel):
    type: str

class DateRange(BaseModel):
    start: float = None
    end: float = None