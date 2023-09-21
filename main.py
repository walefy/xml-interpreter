from fastapi import FastAPI, UploadFile, Header, HTTPException
import xmltodict

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/xmltest')
async def xml_test(upload_file: UploadFile = None, api_key: str = Header(None)):
    if api_key != "123456":
        raise HTTPException(status_code=401, detail="api-key header invalid!")
    if upload_file is None:
        raise HTTPException(status_code=400, detail="xml file not found!")
    if upload_file.filename.endswith('.xml'):
        doc = xmltodict.parse(upload_file.file.read())
        return doc
    else:
        raise HTTPException(status_code=400, detail="xml file not found!")
