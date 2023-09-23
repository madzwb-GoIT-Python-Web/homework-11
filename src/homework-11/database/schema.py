# import sqlalchemy.orm as orm
from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
# from sqlalchemy.sql.functions import GenericFunction
# from sqlalchemy.ext.compiler import compiles

Base = declarative_base()

# class DaysToBirthday(GenericFunction):
#     name = "days_to_birthday"
#     type = Integer

# @compiles(DaysToBirthday, "postgresql")
# def compile_days_to_birthday(element, compiler, **kw):
#     args = list(element.clauses)
#     if len(args) != 2:
#             raise Exception(
#                 "Function 'array_get' expects two arguments (%d given)." %
#                 len(args)
#             )

#     if not hasattr(args[1], "value") or not isinstance(args[1].value, int):
#         raise Exception(
#             "Second argument should be an integer."
#         )
#     return "%s(%s)" % (element.name, compiler.process(element.clauses))

class Person(Base):
    __tablename__ = "persons"
    id          = Column("id"           , Integer       , primary_key = True)
    user_id     = Column("user_id"      , Integer       , ForeignKey("users.id" , onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    first_name  = Column("first_name"   , String(128)   , nullable=False)
    last_name   = Column("last_name"    , String(128)   , nullable=False)
    born_date   = Column("born_date"    , Date          , nullable=True)
    __table_args__ = (UniqueConstraint("user_id", "first_name", "last_name", name = "uc_persons"), )

    user        = relationship("User"      , back_populates="persons")
    contacts    = relationship("Contact"   , back_populates="person")



class Type(Base):
    __tablename__ = "types"
    id      = Column("id"   , Integer       , primary_key = True)
    name    = Column("name" , String(64)    , nullable=False, unique=True)
    
    contacts = relationship("Contact"   , back_populates="type")



class Contact(Base):
    __tablename__ = "contacts"
    id          = Column("id"           , Integer       , primary_key=True)
    value       = Column("value"        , String(128)   , nullable=False, unique=True)
    type_id     = Column("type_id"      , Integer       , ForeignKey("types.id"     , onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    person_id   = Column("person_id"    , Integer       , ForeignKey("persons.id"   , onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    person = relationship("Person"      , back_populates="contacts")
    type   = relationship("Type"        , back_populates="contacts")



class User(Base):
    __tablename__ = "users"
    id              = Column("id"           , Integer       , primary_key=True)
    login           = Column("login"        , String(50)    , nullable=False    , unique=True)
    password        = Column("password"     , String(255)   , nullable=False)
    email           = Column("email"        , String(250)   , nullable=False    , unique=True)
    created_at      = Column("created_at"   , DateTime      , nullable=False    , default=func.now())
    disabled        = Column("disabled"     , Boolean       , nullable=True     , default=False)
    # avatar          = Column("id"           , String(255)   , nullable=True)
    refresh_token   = Column("refresh_token", String(255)   , nullable=True)

    persons = relationship("Person"   , back_populates="user")

metadata = MetaData()
# target_metadata = Base.metadata