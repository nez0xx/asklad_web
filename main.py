from fastapi import FastAPI, APIRouter
from auth import router as auth_router
import uvicorn

app = FastAPI()
app.include_router(auth_router)

from fastapi import Depends

def sir(a,b):
    return {"a":a, "b":b}

@app.get("/test")
def func(params = Depends(sir)):
    return {"params":params}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)