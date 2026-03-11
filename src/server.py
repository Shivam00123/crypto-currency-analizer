from fastapi import FastAPI,Query
from .client.rq_client import queue
from .queues.worker import helper_function

app = FastAPI()


@app.post("/user-query")
def process_user_query(query:str = Query(...,description="User Query")):
    job = queue.enqueue(helper_function,query)
    return {"status":"query added in queue","Job Id":job.id}

@app.get("/job-result")
def get_job_result(job_id:str = Query(...,description="Job id")):
    print("=======" * 30,job_id)
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    print(result)
    return {"status":"result","result":result}