from fastapi import FastAPI, Depends, Request, HTTPException,Form
from typing import List
from . import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="blog")

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db1(id):
    int_check(id)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db2(id):
    int_check(id)
    db = SessionLocal()
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return db


@app.post("/blog", status_code=201, response_model=schemas.Blog)
def create(request: Request, form_data: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=form_data.title, body=form_data.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.delete("/blog/{id}", status_code=204)
def destroy(id, db: Session = Depends(get_db1)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return "DELETED"

def int_check(id):
    try:
        id = int(id) 
        return id
    except ValueError:
        raise HTTPException(status_code=400, detail="ID must be an integer")
    

@app.put("/blog/{id}", status_code=202)
def update(id,request: schemas.Blog, db: Session = Depends(get_db2)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    blog.title = request.title
    blog.body = request.body
    
    db.commit()
    return "updated"


@app.get("/blog")
def all(request:Request,db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return templates.TemplateResponse("homepage.html", {"request": request , "blogs" : blogs})

@app.get("/blog/{id}", status_code=200, response_model=schemas.ShowBlog)
def show(id,request:Request, db: Session = Depends(get_db1)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    title=blog.title
    body=blog.body
    if not blog:
        raise HTTPException(
            status_code=404,
            detail=f"Blog with id {id} not found",
            headers={"xerror": "not found"},
        )
    return templates.TemplateResponse("homepage.html", {"request": request, "title":title,"body":body})
