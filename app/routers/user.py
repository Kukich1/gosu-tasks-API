from datetime import datetime
from uuid import uuid4
from bson import ObjectId

import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.models import Post, Updated_post, TYPE, Comment
from app.utils.jwt_handler import get_current_user
from app.utils.database import get_db, compare

router = APIRouter(
    prefix="/user",
    tags=["User и возможности"]
)

@router.get("/get_tasks&posts/")
async def get_user_posts(current_user: str = Depends(get_current_user)):
    db = get_db()
    posts_collection = db['posts']
    task_collection = db['tasks']
    project_collection = db['projects']
    user_posts = await posts_collection.find({"member": current_user, 'status': 'current'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'task': 1, 'deadline': 1,'created_at': 1, 'type': 1, 'status': 1}).to_list(length=None)
    user_tasks = await task_collection.find({"members": current_user, 'status': 'current'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'project': 1, 'deadline': 1, 'created_at': 1, 'comments': 1, 'type': 1, 'status': 1}).to_list(length=None)
    
    for user_task in user_tasks:
        project_id = user_task['project']
        project_id = urllib.parse.unquote(project_id)
        project_name = await project_collection.find_one({'id': project_id}, {'name': 1})
        user_task["project_name"] = project_name['name'] if project_name else "Неизвестный проект"
        user_task["project"] = str(project_id)  # Преобразование ObjectId в строку
    
    for user_post in user_posts:
        task_id = user_post['task']
        task_id = urllib.parse.unquote(task_id)
        task_name = await task_collection.find_one({'id': task_id}, {'name': 1})
        user_post["task_name"] = task_name['name'] if task_name else "Неизвестная задача"
        user_post["task"] = str(task_id)  # Преобразование ObjectId в строку
    
    completed_lst = user_posts + user_tasks
    completed_lst = user_posts + user_tasks
    return completed_lst

@router.get("/get_completed_tasks&posts/")
async def show_completed_taskpost(start: int = Query(default=0, ge=0), end: int = Query(default=2000000000, le=2000000000), current_user: str = Depends(get_current_user)):
    db = get_db()
    posts_collection = db['posts']
    task_collection = db['tasks']
    project_collection = db['projects']
    
    user_posts = await posts_collection.find({"created_at":{"$gte": start, "$lte": end}, "member": current_user, 'status': 'completed'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'task': 1,'deadline': 1, 'created_at': 1, 'type': 1, 'status': 1, 'time_completed': 1}).to_list(length=None)
    user_tasks = await task_collection.find({"created_at":{"$gte": start, "$lte": end}, "members": current_user, 'status': 'completed'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'project': 1, 'deadline': 1, 'created_at': 1, 'comments': 1, 'type': 1, 'status': 1, 'members': 1,'time_completed': 1}).to_list(length=None)
    
    for user_task in user_tasks:
        project_id = user_task['project']
        project_id = urllib.parse.unquote(project_id)
        project_name = await project_collection.find_one({'id': project_id}, {'name': 1})
        user_task["project_name"] = project_name['name'] if project_name else "Неизвестный проект"
        user_task["project"] = str(project_id)  # Преобразование ObjectId в строку
    
    for user_post in user_posts:
        task_id = user_post['task']
        task_id = urllib.parse.unquote(task_id)
        task_name = await task_collection.find_one({'id': task_id}, {'name': 1})
        user_post["task_name"] = task_name['name'] if task_name else "Неизвестная задача"
        user_post["task"] = str(task_id)  # Преобразование ObjectId в строку
    
    completed_lst = user_posts + user_tasks
    return completed_lst

@router.post("/create_post/")
async def create_new_post(post: Post, current_user: str = Depends(get_current_user)):
    db = get_db()
    post_collection = db['posts']
    task_collection = db['tasks']
    task_name = await task_collection.find_one({'id': post.task},{'_id': 0,'name': 1})
  
    post_dict = post.dict()
    post_dict['id'] = str(uuid4())
    post_dict['type'] = "post"
    post_dict['status'] = 'current'
    post_dict['member'] = current_user
    timestamp = datetime.now().timestamp()
    timestamp_without_ms = round(timestamp)
    post_dict['created_at'] = timestamp_without_ms
    compared_lst = await compare(post_dict['task'], "tasks")

    project_found = False

    print(compared_lst)
    for id in compared_lst:
        if id['id'] == post_dict['task']:
            if current_user in id['members']:
                project_found = True
                break

    if project_found:
        new_task = await post_collection.insert_one(post_dict)
        if new_task:
            return {"message": "New post is created"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    
@router.put("/change_post/{post_id}")
async def change_post(post_id: str, post: Post, current_user: str = Depends(get_current_user)):
    db = get_db()
    post_collection = db['posts']
    updated_dict = post.dict()
    updated_dict['id'] = str(uuid4())
    updated_dict['type'] = "post"
    updated_dict['status'] = 'current'
    updated_dict['member'] = current_user
    timestamp = datetime.now().timestamp()
    timestamp_without_ms = round(timestamp)
    updated_dict['created_at'] = timestamp_without_ms
    result = await post_collection.update_one({'id':  post_id}, {'$set': updated_dict})
    if result:
        return {"message": "Post changed"}
    
@router.patch("/complete_post/{post_id}")
async def complete_post(post_id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    post_collection = db['posts']
    result = await post_collection.update_one({'id': post_id}, {'$set': {'status': 'completed'}})
    if result.matched_count == 1:
        updated_post = await post_collection.find_one({"id": post_id},{'_id': 0})
        timestamp = datetime.now().timestamp()
        timestamp_without_ms = round(timestamp)
        updated_post['time_completed'] = timestamp_without_ms
        return updated_post
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    
@router.patch("/complete_task/{task_id}")
async def complete_task(task_id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    task_collection = db['tasks']
    result = await task_collection.update_one({'id': task_id}, {'$set': {'status': 'completed'}})
    if result.matched_count == 1:
        updated_task = await task_collection.find_one({'id': task_id},{'_id': 0})
        timestamp = datetime.now().timestamp()
        timestamp_without_ms = round(timestamp)
        updated_task['time_completed'] = timestamp_without_ms
        return updated_task
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    

@router.delete("delete_post/{post_id}")
async def delete_post(post_id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    post_collection = db['posts']
    result = post_collection.delete_one({'id': post_id})
    if result:
        return {"message": "Post deleted "}

    
