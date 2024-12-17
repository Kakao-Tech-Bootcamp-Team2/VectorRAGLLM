from fastapi import FastAPI
from app.route.route import router
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI()
app.include_router(router)