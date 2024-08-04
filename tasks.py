from utils import scrape_url
from models import Result, Task
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func


def store_result(task_id, result, db: Session):
    db_result = Result(task_id=task_id, **result)
    try:
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
    except:
        return 'error'


def get_results(task_id, db: Session):
    return db.query(Result).filter(Result.task_id == task_id).all()


def get_distinct_urls(page, page_size, db: Session):
    offset = (page - 1) * page_size
    urls_query = db.execute(select(func.count(Result.url.distinct())))
    total_urls = urls_query.scalar()
    total_pages = (total_urls + page_size - 1) // page_size

    if page > total_pages or page < 1:
        urls = []
    else:
        urls = db.query(Result.url).distinct(
            Result.url).offset(offset).limit(page_size)

    urls = [tup[0] for tup in urls]
    return {
        "urls": urls,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_urls": total_urls
        }
    }


def crawl_urls(urls, task_id, db: Session):
    from main import summarizer
    for url in urls:
        try:
            result = scrape_url(url, summarizer)
            result['url'] = url
            store_result(task_id, result, db)
        except Exception as e:
            error_message = str(e)
            store_task(task_id, db, status="error",
                       error_message=error_message)
            # Store an empty result indicating an error
            store_result(task_id, {"url": url, "title": "",
                         "summary": "", "links": []}, db)
            continue

    # Update task status to complete after processing all URLs
    store_task(task_id, db, status="complete")


def store_task(task_id, db: Session, status="in progress", error_message=None):
    task = db.query(Task).filter(Task.task_id == task_id,
                                 Task.status == 'in progress').first()
    if task:
        task.status = status
        if status == 'error':
            task.error_message = error_message
    else:
        db_task = Task(task_id=task_id, status=status,
                       error_message=error_message)
        db.add(db_task)
    db.commit()
