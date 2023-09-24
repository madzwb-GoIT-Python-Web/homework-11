from datetime import date
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from typing import List

from database.schema import Contact
from database.schema import Person as DBType
# from schema import Person as Type
from schema import PersonContacts as Type



async def reads_persons_by_birthday(days: int, session: Session) -> List[Type]:
    result = session.query(DBType)\
                .join(DBType.contacts)\
                .filter(func.days_to_birthday(DBType.born_date, date.today()) <= days).all()
    persons:List[Type] = []
    for r in result:
        person = Type.model_validate(r)
        persons.append(person)
    return persons

async def reads_persons(first_name: str, last_name: str, session: Session) -> List[Type]:
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
    persons:List[Type] = []
    for r in result:
        person = Type.model_validate(r)
        persons.append(person)
    return persons

async def reads_contacts(value: str, session: Session) -> List[Type]:
    result = session.query(DBType).join(DBType.contacts).filter(Contact.value.like('%' + value + '%')).all()
    contacts = []
    for r in result:
        contact = Type.model_validate(r)
        contacts.append(contact)
    return contacts

async def read_contacts(pid: int, session: Session) -> List[Type]:
    result = session.query(DBType).join(DBType.contacts).filter(DBType.id == pid).all()
    contacts = []
    for r in result:
        contact = Type.model_validate(r)
        contacts.append(contact)
    return contacts
