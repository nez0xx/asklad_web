from fastapi import FastAPI
from api_v1.auth import router as auth_router
from api_v1.orders import router as orders_router
import uvicorn

app = FastAPI()
app.include_router(auth_router)
app.include_router(orders_router)
from fastapi import Depends

def sir(a,b):
    return {"a":a, "b":b}

@app.get("/test")
def func(params = Depends(sir)):
    return {"params":params}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)