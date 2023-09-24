from database.schema import Person as DBType
from database.schema import Contact

from datetime import date
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from schema import Person as Type
from schema import PersonContacts#, Types



async def create(datas: Type, session: Session) -> Type:
    datas = DBType(**dict(datas))
    session.add(datas)
    session.commit()
    session.refresh(datas)
    return datas

async def reads(skip: int, limit: int, session: Session) -> List[Type]:
    results: List[Type] = []
    result = session.query(DBType).offset(skip).limit(limit).all()
    for r in result:
        result = Type.model_validate(r)
        results.append(result)
    return results

async def read(pid: int, session: Session) -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        return  Type.model_validate(_datas)
    return None

async def update(pid: int, datas: Type, session: Session) -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        _datas.first_name   = datas.first_name  if datas.first_name else _datas.first_name
        _datas.last_name    = datas.last_name   if datas.last_name  else _datas.last_name
        _datas.born_date    = datas.born_date   if datas.born_date  else _datas.born_date
        session.commit()
        session.refresh(_datas)
        return Type.model_validate(_datas)
    return None

async def delete(pid: int, session: Session)  -> Type|None:
    _datas = session.query(DBType).filter(DBType.id == pid).first()
    if _datas:
        session.delete(_datas)
        session.commit()
        session.refresh(_datas)
    return _datas

async def reads_persons_by_birthday(days: int, session: Session) -> List[PersonContacts]:
    result = session.query(DBType)\
                .join(DBType.contacts)\
                .filter(func.days_to_birthday(DBType.born_date, date.today()) <= days).all()
    persons:List[PersonContacts] = []
    for r in result:
        person = PersonContacts.model_validate(r)
        persons.append(person)
    return persons

async def reads_persons(first_name: str, last_name: str, session: Session) -> List[PersonContacts]:
    if first_name and last_name:
        result = session.query(DBType)\
                    .join(DBType.contacts)\
                    .filter(
                        and_(
                            DBType.first_name.like('%' + first_name + '%'),
                            DBType.last_name.like('%' + last_name + '%')
                        )
                    ).all()
    elif first_name:
        result = session.query(DBType)\
                    .join(DBType.contacts)\
                    .filter(DBType.first_name.like('%' + first_name + '%'))\
                    .all()
    elif last_name:
        result = session.query(DBType)\
                    .join(DBType.contacts)\
                    .filter(DBType.last_name.like('%' + first_name + '%'))\
                    .all()
    else:
        result = session.query(DBType)\
                    .join(DBType.contacts)
    persons:List[PersonContacts] = []
    for r in result:
        person = PersonContacts.model_validate(r)
        persons.append(person)
    return persons

async def reads_contacts(value: str, session: Session) -> List[PersonContacts]:
    result = session.query(DBType).join(DBType.contacts).filter(Contact.value.like('%' + value + '%')).all()
    contacts = []
    for r in result:
        contact = PersonContacts.model_validate(r)
        contacts.append(contact)
    return contacts

async def read_contacts(pid: int, session: Session) -> List[PersonContacts]:
    result = session.query(DBType).join(DBType.contacts).filter(DBType.id == pid).all()
    contacts = []
    for r in result:
        contact = PersonContacts.model_validate(r)
        contacts.append(contact)
    return contacts
