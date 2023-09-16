# import sqlalchemy.orm as orm
from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

Base = declarative_base()



class Person(Base):
    __tablename__ = "persons"
    id          = Column("id"           , Integer       , primary_key = True)
    first_name  = Column("first_name"   , String(128)   , nullable=False)
    last_name   = Column("last_name"    , String(128)   , nullable=False)
    born_date   = Column("born_date"    , DateTime      , nullable=True)
    __table_args__ = (UniqueConstraint("first_name", "last_name", name = "uc_groups"), )

    contacts = relationship("Contact"   , back_populates="person")



class Type(Base):
    __tablename__ = "types"
    id      = Column("id"   , Integer       , primary_key = True)
    name    = Column("name" , String(64)    , nullable=False, unique=True)
    
    contacts = relationship("Contact"   , back_populates="type")



class Contact(Base):
    __tablename__ = "contacts"
    id          = Column("id"           , Integer       , primary_key=True)
    value       = Column("value"        , String(128)   , nullable=False, unique=True)
    type_id     = Column("type_id"      , Integer       , ForeignKey('types.id'     , onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    contact_id  = Column("person_id"    , Integer       , ForeignKey('persons.id'   , onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    person = relationship("Person"      , back_populates="contacts")
    type   = relationship("Type"        , back_populates="contacts")



metadata = MetaData()
# target_metadata = Base.metadata