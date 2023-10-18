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
        return projects
    except Exception as error:
        return "ups"
    
@router.get("/projects_tasks/{project_name}")
async def show_tasks(project_name: str):
    project_name = urllib.parse.unquote(project_name)
    compared_lst = await compare(project_name, "projects")
    da_ili_net = False
    for name in compared_lst:
        if name['name'] == project_name:
            da_ili_net = True
            break
    if da_ili_net:
        db = get_db()
        task_collection = db['tasks']
        tasks = await task_collection.find({'project': project_name},{'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'members': 1, 'project': 1, 'deadline': 1, 'created_at': 1, 'commets': 1, 'type': 1, 'status': 1}).to_list(length=None)
        return tasks
    else: 
        raise HTTPException(status_code=404, detail="Project not found")

    
@router.get("/completed_projects/")
async def show_completed_projects(start: int = Query(default=0, ge=0), end: int = Query(default=2000000000, le=2000000000), current_user: str = Depends(get_current_user)):
    try:
        db = get_db()
        project_collection = db['projects']
        completed_project_lst = await project_collection.find({"created_at":{"$gte": start, "$lte": end}, 'status': 'completed'}, {'_id': 0, 'id': 1, 'name': 1, 'description': 1, 'members': 1, 'deadline': 1, 'created_at': 1, 'commets': 1, 'type': 1, 'status': 1, 'time_completed': 1}).to_list(length=None)
        return completed_project_lst
    except Exception as error: 
        return "something wrong"