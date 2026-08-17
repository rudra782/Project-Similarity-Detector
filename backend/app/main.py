import io, os, zipfile
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session
from pypdf import PdfReader
from .database import Base, SessionLocal, engine, get_db
from .models import Analysis, Project, SimilarityResult
from .seed import seed
from .similarity import compare_projects

MAX_REPORT=10*1024*1024; MAX_SOURCE=5*1024*1024
CODE_EXT={".py",".js",".jsx",".ts",".tsx",".java",".cpp",".c",".h",".cs"}
class ProjectIn(BaseModel):
    title:str=Field(min_length=3,max_length=240); abstract:str=Field(min_length=20); description:str=""; keywords:list[str]=[]; category:str="Other"; academic_year:str=""; team_name:str=""; report_text:str=""; source_code:str=""
class ProjectOut(ProjectIn):
    model_config=ConfigDict(from_attributes=True)
    id:int; created_at:object

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db: seed(db,Project)
    yield
app=FastAPI(title="Project Similarity Detection API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("CORS_ORIGINS","http://localhost:5173").split(","),allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"healthy","service":"similarity-engine"}
@app.get("/api/algorithms")
def algorithms(): return {"algorithms":[{"name":"TF-IDF + cosine","purpose":"Semantic vocabulary weighting"},{"name":"Jaccard","purpose":"Keyword/token overlap"},{"name":"MinHash + LSH","purpose":"Approximate candidate retrieval"},{"name":"Code tokens","purpose":"Normalized structural comparison"}]}
@app.get("/api/projects",response_model=list[ProjectOut])
def projects(db:Session=Depends(get_db),search:str="",category:str="",year:str="",sort:str=Query("newest",pattern="^(newest|oldest|title)$")):
    q=db.query(Project)
    if search:q=q.filter(or_(Project.title.ilike(f"%{search}%"),Project.abstract.ilike(f"%{search}%")))
    if category:q=q.filter(Project.category==category)
    if year:q=q.filter(Project.academic_year==year)
    q=q.order_by(Project.title if sort=="title" else (Project.created_at.asc() if sort=="oldest" else Project.created_at.desc()))
    return q.all()
@app.post("/api/projects",response_model=ProjectOut,status_code=201)
def add_project(data:ProjectIn,db:Session=Depends(get_db)):
    item=Project(**data.model_dump());db.add(item);db.commit();db.refresh(item);return item
@app.get("/api/projects/{project_id}",response_model=ProjectOut)
def project(project_id:int,db:Session=Depends(get_db)):
    item=db.get(Project,project_id)
    if not item:raise HTTPException(404,"Project not found")
    return item
@app.delete("/api/projects/{project_id}",status_code=204)
def delete_project(project_id:int,db:Session=Depends(get_db)):
    item=db.get(Project,project_id)
    if not item:raise HTTPException(404,"Project not found")
    db.delete(item);db.commit()

async def read_report(file):
    if not file:return ""
    data=await file.read()
    if not data or len(data)>MAX_REPORT: raise HTTPException(400,"Report is empty or exceeds 10 MB")
    ext=os.path.splitext(file.filename or "")[1].lower()
    if ext==".txt":return data.decode("utf-8",errors="replace")
    if ext==".pdf":
        try:return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        except Exception:raise HTTPException(400,"The PDF could not be parsed")
    raise HTTPException(400,"Report must be PDF or TXT")
async def read_source(file):
    if not file:return ""
    data=await file.read()
    if not data or len(data)>MAX_SOURCE:raise HTTPException(400,"Source is empty or exceeds 5 MB")
    ext=os.path.splitext(file.filename or "")[1].lower()
    if ext in CODE_EXT:return data.decode("utf-8",errors="replace")
    if ext==".zip":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                safe=[x for x in z.infolist() if not x.is_dir() and os.path.splitext(x.filename)[1].lower() in CODE_EXT and x.file_size<1_000_000]
                return "\n".join(z.read(x).decode("utf-8",errors="replace") for x in safe[:50])
        except zipfile.BadZipFile:raise HTTPException(400,"The ZIP archive is malformed")
    raise HTTPException(400,"Source must be ZIP or a supported source file")

@app.post("/api/analysis",status_code=201)
async def analyze(title:Annotated[str,Form(min_length=3)],abstract:Annotated[str,Form(min_length=20)],keywords:Annotated[str,Form()]="",description:Annotated[str,Form()]="",category:Annotated[str,Form()]="Other",academic_year:Annotated[str,Form()]="",team_name:Annotated[str,Form()]="",report:UploadFile|None=File(None),source:UploadFile|None=File(None),db:Session=Depends(get_db)):
    report_text=await read_report(report); source_code=await read_source(source)
    query={"title":title,"abstract":abstract,"description":description,"keywords":[x.strip() for x in keywords.split(",") if x.strip()],"report_text":report_text,"source_code":source_code}
    ranked=[]
    for candidate in db.query(Project).all(): ranked.append((candidate,compare_projects(query,candidate)))
    ranked.sort(key=lambda x:x[1]["score"],reverse=True); ranked=ranked[:10]
    top=ranked[0][1] if ranked else {"score":0,"classification":"Low Similarity"}
    analysis=Analysis(title=title,category=category,academic_year=academic_year,team_name=team_name,overall_score=top["score"],classification=top["classification"]);db.add(analysis);db.flush()
    for rank,(candidate,result) in enumerate(ranked,1):db.add(SimilarityResult(analysis_id=analysis.id,project_id=candidate.id,rank=rank,**result))
    db.commit();return {"id":analysis.id,"status":"complete","overall_score":top["score"],"classification":top["classification"]}
def analysis_payload(item,db):
    results=[]
    for r in db.query(SimilarityResult).filter_by(analysis_id=item.id).order_by(SimilarityResult.rank).all():
        p=db.get(Project,r.project_id);results.append({"rank":r.rank,"score":r.score,"classification":r.classification,"components":r.components,"shared_keywords":r.shared_keywords,"evidence":r.evidence,"project":{"id":p.id,"title":p.title,"category":p.category,"academic_year":p.academic_year,"abstract":p.abstract}})
    return {"id":item.id,"title":item.title,"category":item.category,"academic_year":item.academic_year,"team_name":item.team_name,"overall_score":item.overall_score,"classification":item.classification,"created_at":item.created_at,"results":results}
@app.get("/api/analysis/{analysis_id}")
@app.get("/api/analysis/{analysis_id}/results")
def get_analysis(analysis_id:int,db:Session=Depends(get_db)):
    item=db.get(Analysis,analysis_id)
    if not item:raise HTTPException(404,"Analysis not found")
    return analysis_payload(item,db)
