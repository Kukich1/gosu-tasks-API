from motor import motor_asyncio

from werkzeug.security import check_password_hash

from app.utils.config import BD_CONNECTION

def get_db():
    client = motor_asyncio.AsyncIOMotorClient(BD_CONNECTION)
    db = client['gosu-tasks']
    return db

db = get_db()

async def add_new_post(data: dict):
    db = get_db()
    posts_collection = db['posts']
    result = posts_collection.insert_one(data)
    return result

async def register_new_user(data: dict):
    db = get_db()
    users_collection = db['users']
    result = await users_collection.insert_one(data)
    return result

async def authenticate_user(username: str, password: str):
    db = get_db()
    users_collection = db['users']
    user = await users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return user
    
async def compare(data, type):
    db = get_db()
    data_collection = db[type]
    lst = await data_collection.find({"id": data},{'_id': 0, 'id': 1, 'name': 1, 'members': 1}).to_list(length=None)
    return lst
  
async def check_complete_task(project_name):
    db = get_db()
    task_collection = db['tasks']
    tasks = await task_collection.find({'project': project_name}, {'_id': 0, 'status': 1}).to_list(length=None)
    return tasks