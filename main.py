import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances
from database import get_db
from database import engine
from tasks import crawl_urls, get_results, get_distinct_urls, store_task, store_result
from utils import scrape_url
from models import Base, Task, Result
from schemas import URLInput, URLListInput, ResultOutput

Base.metadata.create_all(bind=engine)

app = FastAPI()

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
model = SentenceTransformer('all-MiniLM-L6-v2')


@app.post("/scrape/", response_model=ResultOutput, response_model_exclude_none=True)
async def url_scrape(input: URLInput, db: Session = Depends(get_db)):
    result = db.query(Result).filter(Result.url == input.url).first()
    if result is None:
        result = scrape_url(input.url, summarizer)
        result['url'] = input.url
        store_result('manual task', result, db)
        result['info'] = None
    return result


@app.post("/bulk-scrape/")
async def bulk_scrape(input: URLListInput, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    store_task(task_id, db)
    background_tasks.add_task(crawl_urls, input.urls, task_id, db)
    return {"task_id": task_id}


@app.get("/bulk-scrape/status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == "in progress":
        return {"status": "in progress"}
    elif task.status == "error":
        return {"status": "error", "error_message": task.error_message}
    else:
        results = get_results(task_id, db)
        return {"status": "complete", "results": results}


@app.get("/report/")
async def get_report(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    return get_distinct_urls(page, page_size, db)


@app.get("/vectorize/")
async def get_vector_matrix(task_id: str, db: Session = Depends(get_db)):
    texts = db.query(Result.summary).filter(Result.task_id == task_id).all()

    embeddings = model.encode([text[0] for text in texts])
    distance_matrix = cosine_distances(embeddings)

    return {"distance_matrix": distance_matrix.tolist()}
