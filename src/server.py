from fastapi import FastAPI,Query
from .client.rq_client import queue
from .queues.worker import helper_function

app = FastAPI()


@app.post("/user-query")
def process_user_query(query:str = Query(...,description="User Query")):
    job = queue.enqueue(helper_function,query)
    return {"status":"query added in queue","Job Id":job.id}

@app.get("/job-result")
def get_job_result(job_id: str = Query(...)):
    job = queue.fetch_job(job_id)

    if not job:
        return {
            "status": "error",
            "message": "Job not found"
        }

    if job.is_finished:
        return {
            "status": "finished",
            "result": job.return_value
        }

    if job.is_failed:
        return {
            "status": "failed",
            "error": str(job.exc_info)
        }

    return {
        "status": "in_progress"
    }