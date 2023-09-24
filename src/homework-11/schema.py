import csv
# import pathlib
# import os

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict



class Type(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:     int = Field(default=0)
    name:   str = Field(max_length=64, default="")



class Value(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:     int = Field(default=0)
    value:  str = Field(max_length=128, default="")



class Contact(Value):
    person_id:  int = Field(default=0)
    type_id:    int = Field(default=0)


# TODO:
class Telegram(Value):
    @field_validator("value")
    def validator(cls, value: str):
        if not value.startswith('@'):
            raise ValueError("Invalid telegram account.")
        return value

class Email(Value):
    @field_validator("value")
    def validator(cls, value):
        if not "@" in value:
            raise ValueError("Invalid email.")
        return value

class PhoneValidator():
    mobile_codes = ["50", "63", "66", "67", "68", "73", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"]
    region_codes = []
    with open("data/region_codes_ua.csv", 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            codes = row[2].split('"')
            code = codes[0]
            try:
                int(code)
            except ValueError:
                continue
            region_codes.append(code)
    

class Phone(Value, PhoneValidator):
    @field_validator("value")
    def validator(cls, value):
        if len(value) != 10:
            raise ValueError("Invalid phone number.")
        if      value[2:8] not in cls.region_codes  \
            and value[2:7] not in cls.region_codes  \
            and value[2:6] not in cls.region_codes  \
            and value[2:5] not in cls.region_codes  \
            and value[2:4] not in cls.region_codes  \
            and value[2:4] not in cls.mobile_codes  \
        :
            raise ValueError("Invalid phone number.")
        return value



class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:         int = Field(default=0)
    user_id:    int = Field(default=0)
    first_name: str = Field(max_length=128, default="")
    last_name:  str = Field(max_length=128, default="")
    born_date:  date= Field(default=date.today())


class PersonContacts(Person):
    contacts: List[Contact]

# class Persons(BaseModel):
#     persons: List[Person]


class Login(BaseModel):
    login:      str = Field(min_length=5, max_length=16, default="")
    password:   str = Field(min_length=6, max_length=10, default="")
    email:      str = Field(max_length=250, default="")


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         int         = Field(default=0)
    login:      str         = Field(min_length=5, max_length=16, default="")
    email:      str         = Field(max_length=250, default="")
    password:   str         = Field(max_length=255, default="")
    created_at: datetime    = Field(default=datetime.now())
    disabled:   bool        = Field(default=False)
    # avatar: str


class LoginResponse(BaseModel):
    id:         int         = Field(default=0)
    login:      str         = Field(min_length=5, max_length=16, default="")
    email:      str         = Field(max_length=250, default="")
    created_at: datetime    = Field(default=datetime.now())
    disabled:   bool        = Field(default=False)


class Token(BaseModel):
    access_token:   str = ""
    refresh_token:  str = ""
    token_type:     str = "bearer"

class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:     int = Field(default=0)
    name:   str = Field(max_length=64, default="")