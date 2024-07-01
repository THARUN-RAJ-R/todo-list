from fastapi import FastAPI, Depends,Response,HTTPException
from. import schemas, models
from.database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#doubt
def get_db2(id: int):
    db = SessionLocal()
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return db

@app.post("/blog",status_code=201)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.delete("/blog/{id}",status_code=204)
def destroy(id, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return "DELETED"


#doubt
@app.put('/blog/{id}', status_code=202)
def update(id: int, request: schemas.Blog, db: Session = Depends(get_db2)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    blog.title = request.title
    blog.body = request.body
    db.commit()
    return "updated"

@app.get("/blog")
def all(db: Session = Depends(get_db)):
    blogs= db.query(models.Blog).all()
    return blogs


@app.get("/blog/{id}",status_code=200)
def show(id,response:Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
        #response.status_code = 404
        #return {"message": "Not found"}
    return blog