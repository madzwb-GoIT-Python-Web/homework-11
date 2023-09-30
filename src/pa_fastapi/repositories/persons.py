from datetime import date

from redis          import Redis as Cache
from sqlalchemy     import func, and_, true
from sqlalchemy.orm import Session

from typing import List

from pa_fastapi.database.schema import Contact
from pa_fastapi.database.schema import Person as DBType
# from pa_fastapi.schema import Person as Type
from pa_fastapi.schema import PersonContacts as Type



async def reads_persons_by_birthday(days: int, session: Session, user_id: int = 0) -> List[Type]:
    result = session.query(DBType)\
                .join(DBType.contacts, isouter=True)\
                .filter(
                    and_(
                        DBType.born_date != None,
                        func.days_to_birthday(DBType.born_date, date.today()) <= days
                    )
                ).all()
    persons:List[Type] = []
    for r in result:
        person = Type.model_validate(r)
        persons.append(person)
    return persons

async def reads_persons(first_name: str, last_name: str, session: Session, user_id: int = 0) -> List[Type]:
    if first_name and last_name:
        result = session.query(DBType)\
                    .join(DBType.contacts, isouter=True)\
                    .filter(
                        and_(
                            DBType.user_id == user_id if user_id else any_(DBType.user_id),
                            DBType.first_name.like('%' + first_name + '%'),
                            DBType.last_name.like('%' + last_name + '%')
                        )
                    ).all()
    elif first_name:
        result = session.query(DBType)\
                    .join(DBType.contacts, isouter=True)\
                    .filter(
                        and_(
                            DBType.user_id == user_id if user_id else any_(DBType.user_id),
                            DBType.first_name.like('%' + first_name + '%')
                        )
                    ).all()
    elif last_name:
        result = session.query(DBType)\
                    .join(DBType.contacts, isouter=True)\
                    .filter(
                        and_(
                            DBType.user_id == user_id if user_id else any_(DBType.user_id),
                            DBType.last_name.like('%' + first_name + '%')
                        )
                    ).all()
    else:
        if user_id:
            criterion = DBType.user_id == user_id
        else:
            criterion = False
        result = session.query(DBType)\
                    .join(DBType.contacts, isouter=True )\
                    .filter(criterion if id(criterion) != id(False) else true()).all()
    persons:List[Type] = []
    for r in result:
        person = Type.model_validate(r)
        persons.append(person)
    return persons

async def reads_contacts(value: str, session: Session, user_id: int = 0) -> List[Type]:
    result = session.query(DBType)\
                .join(DBType.contacts, isouter=True)\
                .filter(
                    and_(
                        DBType.user_id == user_id if user_id else any_(DBType.user_id),
                        Contact.value.like('%' + value + '%')
                    )
                ).all()
    contacts = []
    for r in result:
        contact = Type.model_validate(r)
        contacts.append(contact)
    return contacts

async def read_contacts(pid: int, session: Session, user_id: int = 0) -> List[Type]:
    result = session.query(DBType)\
                .join(DBType.contacts, isouter=True)\
                .filter(
                    and_(
                        DBType.user_id  == user_id if user_id else any_(DBType.user_id),
                        DBType.id       == pid
                    )
                ).all()
    contacts = []
    for r in result:
        contact = Type.model_validate(r)
        contacts.append(contact)
    return contacts
