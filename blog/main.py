from fastapi import FastAPI, Depends, Request, HTTPException,Form,status,Response
from . import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="blog/static"), name="static")

templates = Jinja2Templates(directory="blog")

models.Base.metadata.create_all(engine)


def get_db():
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

@app.get("/",status_code=200)
def all(request:Request,db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return templates.TemplateResponse("homepage.html", {"request": request , "blogs" : blogs})

@app.get("/blog",status_code=200)
def all(request:Request,db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return templates.TemplateResponse("homepage.html", {"request": request , "blogs" : blogs})
    
@app.post("/blog", status_code=201)
def create(request : Request, title: str = Form(...), body: str = Form(...), db: Session = Depends(get_db)):
    new_blog = models.Blog(title=title, body=body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    url=app.url_path_for("all")
    return RedirectResponse(url=url,status_code=status.HTTP_201_CREATED)

@app.delete("/blog/{id}", status_code=204)
def delete_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

def int_check(id):
    try:
        id = int(id) 
        return id
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID must be an integer")
    

@app.put("/blog/{id}", status_code=202)
def update_blog(request: Request,id: int, title: str = Form(...), body: str = Form(...), db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.title = title
    blog.body = body
    db.commit()
    db.refresh(blog)
    url = app.url_path_for("all")
    return RedirectResponse(url=url, status_code=status.HTTP_202_ACCEPTED)




@app.get("/blog/{id}", status_code=200, response_model=schemas.Blog)
def show(id, request: Request, db: Session = Depends(get_db2)):
    blogs = db.query(models.Blog).filter(models.Blog.id == id)
    if not blogs:
        raise HTTPException(
            status_code=404,
            detail=f"Blog with id {id} not found",
            headers={"xerror": "not found"},
        )
    return templates.TemplateResponse("homepage.html", {"request": request,"blogs":blogs})
