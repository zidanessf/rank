from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import HTMLResponse
import pandas as pd

import uvicorn
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Record(BaseModel):
    name: str
    used_time: int
    item_remained:int

global_record = dict()

def update_rank():
    global global_record
    global_record = dict()
    with open("log.txt","r",encoding='utf-8') as f:
        for r in f.readlines():
            _,name,used_time,item_remained = r.split("    ")
            if name not in global_record:
                global_record[name] = {"通关次数":1,"总用时(min)":eval(used_time)//60,"道具使用数":15-eval(item_remained)}
            else:
                global_record[name]["通关次数"] += 1
                global_record[name]["总用时(min)"] += eval(used_time)//60
                global_record[name]["道具使用数"] += 15-eval(item_remained)
    print(pd.DataFrame.from_dict(global_record,orient="index"))

@app.post("/rank")
async def rank(record:Record):
    with open("log.txt","a",encoding='utf-8') as f:
        name = record.name
        f.write(f"{datetime.now()}    {name}    {record.used_time}    {record.item_remained}\n")
    update_rank()
    return
@app.get("/rankboard")
def rankboard():
    update_rank()
    df = pd.DataFrame.from_dict(global_record,orient="index")
    print(df)
    df = df.sort_values(by=["通关次数","总用时(min)","道具使用数"],ascending=[False,True,True])
    return HTMLResponse(content=df.to_html(), status_code=200)

@app.get("/login")
def login():
    return HTMLResponse(content=df.to_html(), status_code=200)

if __name__ == "__main__":
    uvicorn.run(app="server:app",host="0.0.0.0",port=9000,reload=True)