import json
import os
import re
from threading import Thread
import time
from fastapi.concurrency import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI, Request, Response
from databases import Database
from fastapi.middleware.cors import CORSMiddleware

database = Database("mysql+aiomysql://tedxtest:tedxtest@db4free.net:3306/tedxtest")

"""Database Schema
CREATE TABLE `attendees` (
	`email` varchar(200) NOT NULL,
	`name` varchar(100) NOT NULL,
	`phone` varchar(20) NOT NULL,
	`aloy` BOOLEAN NOT NULL,
	`payment_type` varchar(20) NOT NULL,
	`paid` BOOLEAN NOT NULL,
	PRIMARY KEY (`email`)
);

CREATE TABLE `aloy` (
	`email` varchar(200) NOT NULL,
	`regno` int(10) NOT NULL UNIQUE,
	PRIMARY KEY (`email`)
);

CREATE TABLE `partial` (
	`email` varchar(200) NOT NULL,
	`first_ref` int(13) NOT NULL UNIQUE,
	`first_status` varchar(20) NOT NULL,
	`second_ref` int(13) NOT NULL UNIQUE,
	`second_status` varchar(20) NOT NULL,
	PRIMARY KEY (`email`)
);

CREATE TABLE `full` (
	`email` varchar(200) NOT NULL,
	`ref` int(13) NOT NULL,
	`status` varchar(20) NOT NULL,
	PRIMARY KEY (`email`)
);
    """


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the actual origin of your frontend app
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return "Internal Error"


def send_json(data, code):
    return Response(json.dumps(data), status_code=code, media_type="application/json")


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return True
    else:
        return False


async def check_email_exists(email):
    email = email.strip()
    query = "SELECT * FROM attendees WHERE `email` = :email"
    values = {"email": email}
    result = await database.fetch_one(query=query, values=values)
    print(bool(result))  #
    if result:
        return True
    else:
        return False


@app.get("/display")
async def display():
    query = "SELECT * FROM attendees"
    result = await database.fetch_all(query=query)
    print(list(map(list, result)))
    return list(map(list, result))


@app.get("/check/{email}")
async def check(email):
    email = email.strip()
    if not is_valid_email(email):
        return send_json({"msg": "Invalid Email"}, 220)
    elif await check_email_exists(email):
        return send_json({}, 202)  # exists
    else:
        return send_json({}, 200)  # does not exist


@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data.get("email", None)
    name = data.get("name", None)
    phone = data.get("phone", None)
    aloy = int(data.get("aloy", None))
    if aloy:
        regno = int(data.get("regno", None))
    payment_type = data.get("payment_type", None)
    upi_ref_no = data.get("upi_ref_no", None)

    if not all([email, name, phone, payment_type, upi_ref_no]) or (aloy and not regno):
        return send_json({"msg": "Invalid Request"}, 520)

    if not is_valid_email(email):
        return send_json({"msg": "Invalid Email"}, 520)

    transaction = await database.transaction()
    try:
        query = "INSERT INTO attendees (`email`, `name`, `phone`, `aloy`, `payment_type`) VALUES (:email, :name,  :phone, :aloy,  :payment_type)"
        values = {
            "name": name,
            "email": email,
            "phone": phone,
            "aloy": aloy,
            "payment_type": payment_type,
        }
        await database.execute(query=query, values=values)

        if aloy:
            query = "INSERT INTO aloy (`email`, `regno`) VALUES (:email, :regno)"
            values = {"email": email, "regno": regno}
            await database.execute(query=query, values=values)

        values = {"email": email, "ref": upi_ref_no, "status": "pending"}
        if payment_type == "partial":
            query = "INSERT INTO partial (`email`, `first_ref`, `first_status`) VALUES (:email, :ref, :status)"
        elif payment_type == "full":
            query = "INSERT INTO `full` (`email`, `ref`, `status`) VALUES (:email, :ref, :status)"
        await database.execute(query=query, values=values)
        await transaction.commit()
        # If all queries are successful, commit the transaction
        return send_json({"msg": "Success"}, 200)
    except Exception as e:
        await transaction.rollback()
        # If any error occurs, rollback the transaction
        return send_json({"msg": str(e)}, 520)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", default=5000)),
        reload=True,
    )
