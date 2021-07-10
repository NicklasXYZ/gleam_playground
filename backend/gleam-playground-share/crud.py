from typing import List, Dict
import uuid
from sqlalchemy.orm import Session
import models, schemas


def get_snippet(db: Session, snippet_id: str):
    return db.query(
        models.Snippet,
    ).filter(
        models.Snippet.snippetID == snippet_id,
    ).first()


def create_snippet(db: Session, snippet: schemas.BaseSnippet):
    db_snippet = models.Snippet(
        code = snippet.code,
        snippetID = str(uuid.uuid4()),
    )
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet