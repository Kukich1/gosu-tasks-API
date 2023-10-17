from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import user
from app.routers import admin
from app.routers import refresh
from app.routers import company


app = FastAPI(title="Gosu-tasks")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Просто проверка 
@app.get("/", tags=["Тест"])
def privet():
    return {"Hello": "World!"}

app.include_router(auth.router)
app.include_router(company.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(refresh.router)
