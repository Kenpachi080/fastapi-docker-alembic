from typing import Optional, List, Union
from fastapi import FastAPI, Cookie, Body, Header, status, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError  # дочитать попозже "ОБРАБОТКА ОШИБОК"
from fastapi.security import OAuth2PasswordBearer
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
import requests
from bs4 import BeautifulSoup

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)]) зависимость КО ВСЕМУ ПРИЛОЖЕНИЮ


class Image(BaseModel):
    url: str = Field(..., example="donate")
    name: str = Field(..., example="li")


class Item(BaseModel):
    name: Optional[str] = Field(..., example="John")
    description: Optional[str] = Field(None, title="The description of the item", max_length=300)
    price: float = Field(None, gt=0, example="3.1", description="The price must be greater than zero")
    tax: float = 3.1
    tags: List[str] = Field(None)
    image: Optional[Image] = None


class ItemVali(BaseModel):
    description: Optional[str] = Field(None, title="The description of the item", max_length=300)
    price: float = Field(None, gt=0, example="3.1", description="The price must be greater than zero")
    tax: float = 3.1
    tags: List[str] = Field(None)
    image: Optional[Image] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class ModelName(Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Config(BaseModel):
    schema_extra = {
        "example": {
            "name": "foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        }
    }


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

model = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = 'car'


class PlaneItem(BaseItem):
    type = 'plane'


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


class CreateParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


def fake_decode_token(token):
    return User(
        username=token + "fakecode", fullname="john marston"
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"OOps! {exc.name} did something. There goes a rainbow..."
        }
    )


async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/tokens/")
async def read_tockens(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/dependoperation/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def dependOperation():
    return [{"item": "Foo"}, {"item": "Bar"}]


@app.post('/depend/')
async def depent(
        commons: CreateParams = Depends()
):
    return {"commons": commons}


@app.post('/exceptions/')
async def exceptions(
        item_id: str
):
    if item_id not in items:
        # raise HTTPException(status_code=404, detail='item is not found', headers={"X-Error": "There goes my error"})
        raise UnicornException(name=item_id)
    return {"item": items[item_id]}


@app.post('/files/')
async def create_file(
        file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type
    }


@app.post('/file/')
async def create_files(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post('/uploadfile/')
async def create_upload_file(files: UploadFile = File(...)):
    return {"file_size": len(files)}


@app.get("/forms/")
async def forms(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}


@app.get("/model/{model_id}", response_model=Union[PlaneItem, CarItem], status_code=status.HTTP_201_CREATED)
async def models(model_id: str):
    return model[model_id]


@app.get("/items/", response_model=Item, response_model_exclude_unset=True, response_model_exclude={"name"}, )
# response_model = Модель, которую будет возврощать, unset = убрать все Null из callback, exclude = убирает поле для
# вывода, iclude добовляет
async def items_response(item_id: str):
    return items[item_id]


@app.get("/")
async def home(user_agent: Optional[List[str]] = Header(None,
                                                        convert_underscores=True)):  # convert_underscores = False что бы не изменять text-style
    return {'User-Agent': user_agent}


@app.put("/items/{item_id}")
async def update_item(item_id: int,
                      item: Item = Body(
                          ...,
                          examples={
                              "normal": {
                                  "summary": "A normal example",
                                  "description": "A **normal** item works correctly.",
                                  "value": {
                                      "name": "Foo",
                                      "description": "A very nice Item",
                                      "price": 35.4,
                                      "tax": 3.2,
                                  },
                              },
                              "converted": {
                                  "summary": "An example with converted data",
                                  "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                                  "value": {
                                      "name": "Bar",
                                      "price": "35.4",
                                  },
                              },
                              "invalid": {
                                  "summary": "Invalid data is rejected with an error",
                                  "value": {
                                      "name": "Baz",
                                      "price": "thirty five point four",
                                  },
                              },
                          },
                      ),
                      # user: User = Body(
                      #     ...,
                      #     example={
                      #         "username": "ya",
                      #         "full_name": "neya",
                      #     }),
                      # importance: int = Query(...)
                      ):
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/login/")
async def authorization(ads_id: Optional[str] = Cookie(None), login: Optional[str] = None,
                        password: Optional[str] = None):
    login_info = {
        'user': login,
        'password': password
    }
    url = 'https://tou.edu.kz/student_cabinet/'
    session = requests.Session()
    schedulePage = session.post(url, data=login_info)
    soup = BeautifulSoup(schedulePage.content, 'html.parser')
    lessons = soup.find('div', {'class': 'login-background'})
    if lessons is not None:
        return {"code": 404}
    else:
        return session.cookies.get_dict()


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Hello alexnet"}

    if model_name == ModelName.lenet:
        return {"model_name": model_name, "mesasge": "Hello Lenet"}

    return {"model_name": model_name, "message": "Have Some redus"}


@app.get("/{pk}")
def get_item(pk: int, q: str = None):
    return {'key': pk, "q": q}


@app.post("/item/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/profile/")
async def profile():
    return "privet"


@app.get("/schedule/")
async def schedule(login: Optional[str] = None, password: Optional[str] = None):
    if login:
        login_info = {
            'user': login,
            'password': password
        }
        url = 'https://tou.edu.kz/student_cabinet/'
        session = requests.Session()
        session.post(url, data=login_info)
        schedulePage = session.get(url + '?lang=rus&mod=rasp')
        soup = BeautifulSoup(schedulePage.content, 'html.parser')

        parsedLessons = {}
        day = ''
        lessons = soup.find('table', {'class': 'schedule-table'})
        if lessons is not None:
            rows = lessons.findAll('tr')

            # Remove table heading
            rows.pop(0)

            for row in rows:
                td = [td for td in row.stripped_strings]
                isNewDay = not td[0].isnumeric()

                if isNewDay:
                    day = td[0]
                    parsedLessons[day] = [{
                        'row': td[1],
                        'time': td[2],
                        'name': td[3],
                    }]
                else:
                    parsedLessons[day].append({
                        'row': td[0],
                        'time': td[1],
                        'name': td[2],
                    })
            return parsedLessons
        else:
            return {"code": 404, "text": "Not found user"}
    else:
        return {"code": 404, "text": "Not found user"}
