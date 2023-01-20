from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse 

import pandas as pd

import uvicorn
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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
                global_record[name] = {"通关次数":1,"最短用时(min)":eval(used_time)/60/1000,"道具总使用数":15-eval(item_remained)}
            else:
                global_record[name]["通关次数"] += 1
                global_record[name]["最短用时(min)"] = min(global_record[name]["最短用时(min)"],eval(used_time)/60/1000)
                global_record[name]["道具总使用数"] += 15-eval(item_remained)
    print(pd.DataFrame.from_dict(global_record,orient="index"))

@app.get("/")
def serve_home():
    return FileResponse('static/index.html')

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
    df = df.sort_values(by=["最短用时(min)","通关次数","道具使用数"],ascending=[True,False,True])
    df["排名"] = pd.Series(range(1,len(df)+1),index=df.index)
    htmlstr =  f'''
    <html>
<head>
<style> 
  table, th, td{{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:center;}}
  th, td {{padding: 5px;}}
.center{{
      display:table;
      margin:0 auto;
      border:1px solid red;
  }}
</style>
</head>
<body>
<div class="center">

{
  df.to_html()
}
</div>

</body>
</html>
    '''
    return HTMLResponse(content=htmlstr, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app="server:app",host="0.0.0.0",port=9000,reload=True)