
prefix = """
if __name__ == "__main__":
    import os
    prefix = os.path.splitext(os.path.basename(__file__))[0]
else:
    prefix = __name__

def key(key):
    return f'{prefix}:{str(key)}'

"""

repository = prefix + """
async def create(datas: Type, session: Session, cache: Cache|None = None) -> Type:
    model = datas.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    pk = [c.name for c in DBType.metadata.tables[DBType.__tablename__].primary_key.columns]
    model = {k: v for k, v in model.items() if k not in pk}
    record = DBType(**model)
    session.add(record)
    session.commit()
    session.refresh(record)
    model = Type.model_validate(record)
    if cache is not None:
        cache.set(key(record.id), pickle.dumps(model))
    return model

async def reads(skip: int, limit: int, session: Session, cache: Cache|None = None) -> List[Type]:
    models: List[Type] = []
    records = session.query(DBType).offset(skip).limit(limit).all()
    for record in records:
        model = Type.model_validate(record)
        models.append(model)
        if cache is not None:
            cache.set(key(record.id), pickle.dumps(model))
    return models

async def read(pid: int, session: Session) -> Type|None:
    if cache is not None:
        model = cache.get(key(record.id))
    else:
        model = None
    if model is None:
        record = session.query(DBType).filter(DBType.id == pid).first()
        if record:
            model = Type.model_validate(record)
            if cache is not None:
                cache.set(key(record.id), pickle.dumps(model))
    else:
        model = pickle.loads(model)
    return model

async def update(pid: int, datas: Type, session: Session, cache: Cache|None = None) -> Type|None:
    record = session.query(DBType).filter(DBType.id == pid).first()
    if record:
        values = datas.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
        for name, value in values.items():
            if hasattr(record, name):
                setattr(record, name, value)
        else:
            session.commit()
            session.refresh(record)
        model = Type.model_validate(record)
        if cache is not None:
            cache.set(key(record.id), pickle.dumps(model))
    return None

async def delete(pid: int, session: Session, cache: Cache|None = None)  -> Type|None:
    record = session.query(DBType).filter(DBType.id == pid).first()
    if record:
        if cache is not None:
            cache.delete(key(record.id))
        session.delete(record)
        session.commit()
        session.refresh(record)
    return record
"""
