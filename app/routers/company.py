import urllib.parse

from fastapi import APIRouter, Query, Depends, HTTPException
from app.utils.database import get_db, compare

from app.utils.jwt_handler import get_current_user

router = APIRouter(
    prefix="/company",
    tags=["all endpoints for company"]
)

@router.get("/projects/")
async def show_projects():
    try:
        db = get_db()
        project_collection = db['projects']
        projects = await project_collection.find({'status': 'current'}, {'_id': 0}).to_list(length=None)
        for project in projects:
            project_id = project['id']
            project_id = urllib.parse.unquote(project_id)
            task_collection = db['tasks']
            tasks = await task_collection.find({'project': project_id},{'_id': 0,'id': 1}).to_list(length=None)
            task_count = len(tasks)
            task_completed = await task_collection.find({'project': project_id, 'status': 'completed'},{'_id': 0,'id': 1}).to_list(length=None)
            task_completed_count = len(task_completed)
            print(type(project))
            project["task_count"] = task_count
            print(type(project))
            project["task_completed_count"] = task_completed_count
        return projects
    except Exception as error:
        return "ups"
    
@router.get("/projects_tasks/{project_id}")
async def show_tasks(project_id: str):
    project_id = urllib.parse.unquote(project_id)
    compared_lst = await compare(project_id, "projects")
    da_ili_net = False
    for id in compared_lst:
        if id['id'] == project_id:
            da_ili_net = True
            break
    if da_ili_net:
        db = get_db()
        task_collection = db['tasks']
        tasks = await task_collection.find({'project': 'project_id'},{'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'members': 1, 'project': 1, 'deadline': 1, 'created_at': 1, 'commets': 1, 'type': 1, 'status': 1,'time_completed': 1,'archive_deadline': 1}).to_list(length=None)
        for task in tasks:
            task_id = task['id']
            task_id = urllib.parse.unquote(task_id)
            post_collection = db['post']
            posts = await post_collection.find({'task': task_id},{'_id': 0,'id': 1}).to_list(length=None)
            post_count = len(posts)
            post_completed = await post_collection.find({'task': task_id, 'status': 'completed'},{'_id': 0,'id': 1}).to_list(length=None)
            post_completed_count = len(post_completed)
            print(type(task))
            task["post_count"] = post_count
            print(type(task))
            task["post_completed_count"] = post_completed_count
        return tasks
    else: 
        raise HTTPException(status_code=404, detail="Project not found")

@router.get("/task_posts/{task_id}")
async def show_posts(task_id: str):
    task_id = urllib.parse.unquote(task_id)
    compared_lst = await compare(task_id, "tasks")
    da_ili_net = False
    for id in compared_lst:
        if id['id'] == task_id:
            da_ili_net = True
            break
    if da_ili_net:
        db = get_db()
        post_collection = db['posts']
        posts = await post_collection.find({'task': task_id},{'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'member': 1, 'task': 1, 'created_at': 1,'time_completed': 1, 'type': 1, 'status': 1,'deadline': 1}).to_list(length=None)
        return posts
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    


@router.get("/completed_projects/")
async def show_completed_projects(start: int = Query(default=0, ge=0), end: int = Query(default=2000000000, le=2000000000), current_user: str = Depends(get_current_user)):
    try:
        db = get_db()   
        project_collection = db['projects']
        completed_project_lst = await project_collection.find({"time_completed":{"$gte": start, "$lte": end}, 'status': 'completed'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'members': 1, 'deadline': 1, 'created_at': 1, 'commets': 1, 'type': 1, 'status': 1, 'time_completed': 1}).to_list(length=None)
        return completed_project_lst
    except Exception as error: 
        return "something wrong"
    
