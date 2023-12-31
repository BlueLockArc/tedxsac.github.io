from datetime import datetime
import json
import os
import re
import time
import traceback

import pymysql
import uvicorn
from databases import Database
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Constants
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
NAME_PATTERN = r"^[a-zA-Z\-\.' ]*$"
PHONE_PATTERN = r"^\+\d{1,3}\d{1,14}$"
UPI_REF_PATTERN = r"^\d{12}$"

# Database connection
database = Database(
    "mysql+aiomysql://u293549859_tedxsac:4&Xa=kGQ3@auth-db198.hstgr.io:3306/u293549859_tedxsac"
)

"""Database Schema
CREATE TABLE `attendees` (
    `email` VARCHAR(200) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `wa_num` VARCHAR(20) NOT NULL,
    `ph_num` VARCHAR(20),
    `aloy` BOOLEAN NOT NULL,
    `payment_type` VARCHAR(20) NOT NULL,
    `paid` BOOLEAN,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`email`),
    INDEX `idx_email` (`email`)
);

CREATE TABLE `aloy` (
    `email` VARCHAR(200) NOT NULL UNIQUE,
    `regno` VARCHAR(10) NOT NULL UNIQUE,
    PRIMARY KEY (`email`),
    INDEX `idx_regno` (`regno`),
    FOREIGN KEY (`email`) REFERENCES `attendees`(`email`) ON DELETE CASCADE
);

CREATE TABLE `partial` (
    `email` VARCHAR(200) NOT NULL UNIQUE,
    `first_ref` VARCHAR(12) NOT NULL UNIQUE,
    `first_date_paid` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    `first_status` VARCHAR(20) NOT NULL,
    `second_ref` VARCHAR(12) UNIQUE,
    `second_date_paid` TIMESTAMP, 
    `second_status` VARCHAR(20),
    PRIMARY KEY (`email`),
    INDEX `idx_first_ref` (`first_ref`),
    INDEX `idx_second_ref` (`second_ref`),
    FOREIGN KEY (`email`) REFERENCES `attendees`(`email`) ON DELETE CASCADE
);


CREATE TABLE `full` (
    `email` VARCHAR(200) NOT NULL UNIQUE,
    `ref` VARCHAR(12) NOT NULL UNIQUE,
    `date_paid` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) NOT NULL,
    PRIMARY KEY (`email`),
    INDEX `idx_ref` (`ref`),
    FOREIGN KEY (`email`) REFERENCES `attendees`(`email`) ON DELETE CASCADE
);
CREATE TABLE `admin` (
    `token` VARCHAR(16) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`token`),
    INDEX `idx_name` (`token`)
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


def is_valid(value, pattern):
    return bool(re.match(pattern, value))


async def is_email_exists(email):
    query = "SELECT 1 FROM attendees WHERE `email` = :email"
    values = {"email": email}
    result = await database.fetch_one(query=query, values=values)
    return bool(result)


@app.post("/display")
async def display(request: Request):
    data = await request.json()
    if not data.get("token", "") == "tedxsac":
        return send_json({"msg": "Error 1: Token Must be a 4 digit number"}, 520)
    query = """SELECT a.email, a.name, a.wa_num, a.ph_num,
    CASE
        WHEN a.aloy = 1 THEN al.regno 
        ELSE NULL
    END AS regno,
    CASE
        WHEN a.payment_type = 'partial' AND p.second_status = 'pending' THEN 'Second'
        WHEN a.payment_type = 'partial' AND p.first_status = 'pending' THEN 'First'
        ELSE 'Full'
    END AS payment_type,
    CASE
        WHEN a.payment_type = 'partial' AND p.second_status = 'pending' THEN p.second_ref
        WHEN a.payment_type = 'partial' AND p.first_status = 'pending' THEN p.first_ref
        ELSE f.ref
    END AS upi_ref,
    CASE
        WHEN a.payment_type = 'partial' AND p.second_status = 'pending' THEN p.second_date_paid
        WHEN a.payment_type = 'partial' AND p.first_status = 'pending' THEN p.first_date_paid
        ELSE f.date_paid
    END AS date_paid
    FROM attendees AS a
    LEFT JOIN aloy AS al ON a.email = al.email
    LEFT JOIN partial AS p ON a.email = p.email
    LEFT JOIN full AS f ON a.email = f.email;
"""  # email, name, wa_num, ph_num, regno, payment_type, upi_ref, date_paid
    result = await database.fetch_all(query=query)
    result = list(map(list, result))
    return result


async def get_payment_type(email):
    query = "SELECT `payment_type` FROM attendees WHERE `email` = :email"
    values = {"email": email}
    result = await database.fetch_one(query=query, values=values)
    return result[0]


async def is_payment_done(email):
    query = "SELECT `paid` FROM attendees WHERE `email` = :email"
    values = {"email": email}
    result = await database.fetch_one(query=query, values=values)
    return bool(result[0])


@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        if data.get("token", "") == "tedxsac":
            return send_json({"msg": "Success"}, 200)
        else:
            return send_json({"msg": "Error: Token Must be a 4 digit number"}, 520)
    except Exception as e:
        print(traceback.format_exc())
        return send_json({"msg": "Eror: Token must be 4 digit number"}, 520)

@app.post("/approve")
async def approve(request: Request):
    try:
        data = await request.json()
        try:
            token, email = (
                data.get(key, "").strip() for key in ["token", "email"]
            )
        except AttributeError as e:
            return send_json({"msg": "Error Request"}, 520)
        email = email.lower()

        if not all([token, email]):
            return send_json({"msg": "Invalid Request"}, 520)

        if not is_valid(email, EMAIL_PATTERN):
            return send_json({"msg": "Invalid Email"}, 520)

        #check token
        query = "SELECT 1 FROM admin WHERE `token` = :token"
        values = {"token": token}
        result = await database.fetch_one(query=query, values=values)
        if not bool(result):
            return send_json({"msg": "Invalid Token"}, 520)
        print(result)
        name = result[0]
        if payment_type == "partial":
            query = "UPDATE `partial` SET `first_status` = :status WHERE `email` = :email"
            values = {"email": email, "status": "verified"}
        elif payment_type == "full":
            query = "UPDATE `full` SET `status` = :status WHERE `email` = :email"
            values = {"email": email, "status": "verified"}
        await database.execute(query=query, values=values)
        return send_json({"msg": "Success"}, 200)

    except Exception as e:
        print(traceback.format_exc())
        return send_json({"msg": "Internal Error: a.2\nContact Developer"}, 520)

@app.get("/check/{email}")
async def check(email: str):
    try:
        email = email.strip().lower()
        if not is_valid(email, EMAIL_PATTERN):  # invalid
            return send_json({"msg": "Invalid Email"}, 520)
        elif await is_email_exists(email):  # email exists
            if await is_payment_done(email):  # payment status is true
                return send_json({"msg": "Payment Done"}, 222)
            else:
                payment_type = await get_payment_type(email)
                if payment_type == "full":  # payment type is full
                    query = "SELECT `status` FROM `full` WHERE `email` = :email"
                    values = {"email": email}
                    result = await database.fetch_one(query=query, values=values)
                    return send_json({"msg": result[0]}, 310)
                elif payment_type == "partial":  # payment type is partial
                    query = """SELECT p.first_status, p.second_status, ( SELECT a.name FROM attendees AS a WHERE a.email = :email )
                    AS name FROM partial AS p WHERE p.email = :email;"""
                    values = {"email": email}
                    result = await database.fetch_one(query=query, values=values)

                    # second payment can be null,pending, verified and first payment can be pending, verified

                    if (
                        result[1] == "pending" or result[0] == "pending"
                    ):  # second pending
                        return send_json({"msg": "pending"}, 310)
                    elif result[0] == "verified":  # first verified
                        return send_json({"msg": "verified", "name": result[2]}, 310)
                else:  # payment type is not set
                    return send_json(
                        {
                            "msg": "Payment Type not set\nError Code:1-2 Contact Developer"
                        },
                        520,
                    )
        else:  # email does not exist
            return send_json({}, 200)
    except Exception as e:
        print(traceback.format_exc())
        return send_json({"msg": "Internal Error: c-2x\nContact Developer"}, 520)


@app.post("/register")
async def register(request: Request):
    try:
        data = await request.json()
        try:
            email, name, wa_number, ph_number = (
                data.get(key, "").strip()
                for key in ["email", "name", "wa_number", "ph_number"]
            )
            aloy, regno, payment_type, upi_ref_no = (
                data.get(key, "").strip()
                for key in ["aloy", "regno", "payment_type", "upi_ref_no"]
            )
        except AttributeError as e:
            return send_json({"msg": "Error Request"}, 520)

        aloy = int(aloy)
        email = email.lower()
        name = name.title()

        if not all([email, name, wa_number, payment_type, upi_ref_no]) or (
            aloy and not regno
        ):
            return send_json({"msg": "Invalid Request"}, 520)
        if (
            len(email) > 200
            or len(name) > 100
            or len(wa_number) > 20
            or len(ph_number) > 20
            or len(regno) > 10
        ):
            return send_json({"msg": "Input value exceeds maximum allowed length"}, 520)

        if not all(
            is_valid(value, pattern)
            for value, pattern in zip(
                [email, name, wa_number, upi_ref_no],
                [EMAIL_PATTERN, NAME_PATTERN, PHONE_PATTERN, UPI_REF_PATTERN],
            )
        ):
            return send_json({"msg": "Invalid Input"}, 520)
        if not is_valid(wa_number, PHONE_PATTERN):
            return send_json({"msg": "Invalid Whatsapp Number"}, 520)
        if ph_number and not is_valid(ph_number, PHONE_PATTERN):
            return send_json({"msg": "Invalid Phone Number"}, 520)

        if payment_type not in ["partial", "full"]:
            return send_json({"msg": "Invalid Payment Type"}, 520)

        if await is_email_exists(email):
            return send_json({"msg": "Email already registered"}, 520)

        transaction = await database.transaction()
        try:
            query = "INSERT INTO attendees (`email`, `name`, `wa_num`,`ph_num`, `aloy`, `payment_type`) VALUES (:email, :name, :wa_number, :ph_number, :aloy, :payment_type)"
            values = {
                "name": name,
                "email": email,
                "wa_number": wa_number,
                "ph_number": ph_number,
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
            return send_json({"msg": "Success"}, 200)

        except pymysql.err.IntegrityError as e:
            print(email, e)
            await transaction.rollback()
            return send_json({"msg": str(e)}, 520)

        except Exception as e:
            print(email, traceback.format_exc())
            await transaction.rollback()
            return send_json({"msg": "Internal Error: 2-4\nContact Developer"}, 520)

    except Exception as e:
        print(traceback.format_exc())
        return send_json({"msg": "Internal Error: 4-6x\nContact Developer"}, 520)


@app.post("/second")
async def second(request: Request):
    try:
        data = await request.json()
        try:
            email, upi_ref_no = (
                data.get(key, "").strip() for key in ["email", "upi_ref_no"]
            )
        except AttributeError as e:
            return send_json({"msg": "Error Request"}, 520)
        email = email.lower()

        if not all([email, upi_ref_no]):
            return send_json({"msg": "Invalid request"}, 520)

        if not all(
            is_valid(value, pattern)
            for value, pattern in zip(
                [email, upi_ref_no],
                [EMAIL_PATTERN, UPI_REF_PATTERN],
            )
        ):
            return send_json({"msg": "Invalid Input"}, 520)

        if not await is_email_exists(email):
            return send_json({"msg": "Not registered"}, 520)

        payment_type = await get_payment_type(email)
        if payment_type == "full":
            return send_json({"msg": "Invalid Payment Type\nNot allowed"}, 520)
        elif payment_type == "partial":  # payment type is partial
            query = "SELECT `first_status`,`second_status` FROM `partial` WHERE `email` = :email"
            values = {"email": email}
            result = await database.fetch_one(query=query, values=values)
            if result[0] != "verified" and result[1]:  # first verified
                return send_json({"msg": "Invalid Payment Type\nNot allowed"}, 520)
        transaction = await database.transaction()
        try:
            query = "UPDATE `partial` SET `second_ref` = :ref, `second_status` = :status WHERE `email` = :email"
            values = {"email": email, "ref": upi_ref_no, "status": "pending"}
            await database.execute(query=query, values=values)
            await transaction.commit()
            return send_json({"msg": "Success"}, 200)

        except pymysql.err.IntegrityError as e:
            print(email, e)
            await transaction.rollback()
            return send_json({"msg": str(e)}, 520)

        except Exception as e:
            print(email, traceback.format_exc())
            await transaction.rollback()
            return send_json({"msg": "Internal Error: 3-4\nContact Developer"}, 520)

    except Exception as e:
        print(traceback.format_exc())
        return send_json({"msg": "Internal Error: 5-6x\nContact Developer"}, 520)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", default=5000)),
        reload=True,
        workers=5,
    )
