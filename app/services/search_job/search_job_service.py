from app.core.database import SessionLocal

from app.models.search_job import SearchJob



def create_search_job():

    db = SessionLocal()

    job = SearchJob()

    db.add(job)

    db.commit()

    db.refresh(job)

    db.close()

    return job


def get_search_job(job_id):

    db = SessionLocal()

    job = db.query(SearchJob).filter(SearchJob.id == job_id).first() 
    
    db.close()

    return job


def update_job( job_id, status, progress, current_step ):

    db = SessionLocal()

    job = db.query(SearchJob).filter(SearchJob.id == job_id).first() 

    if job:
        job.status = status
        job.progress = progress
        job.current_step = current_step

        db.commit()

    db.close()