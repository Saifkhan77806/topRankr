from app.core.database import SessionLocal

from app.models.search_job import SearchJob


def get_all_jobs():

    db = SessionLocal()

    try:

        jobs = (
            db.query(
                SearchJob
            )
            .order_by(
                SearchJob.id.desc()
            )
            .all()
        )

        return [

            {
                "id":
                    job.id,

                "status":
                    job.status,

                "progress":
                    job.progress,

                "current_step":
                    job.current_step,

                "created_at":
                    job.created_at
            }

            for job in jobs
        ]

    finally:
        db.close()


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