from fastapi import FastAPI, UploadFile
import shutil
import os

from graph import app as workflow

api = FastAPI()

# common function for single pdf processing
async def process_pdf(file: UploadFile):

    os.makedirs("temp", exist_ok=True)

    path = "temp/" + file.filename


    # save pdf locally
    with open(path, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    # call langgraph
    result = workflow.invoke(
        {
            "file_path": path
        }
    )


    return result["final"]




@api.get("/health")
def health():

    return {
        "status": "ok"
    }




# single pdf extraction
@api.post("/extract")
async def extract(
    file: UploadFile
):

    result = await process_pdf(file)

    return result




# multiple pdf extraction
@api.post("/batch")
async def batch(
    files: list[UploadFile]
):

    results = []


    for file in files:

        result = await process_pdf(file)

        results.append(result)


    return results