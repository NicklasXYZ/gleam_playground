from sqlalchemy import Text, String, Column
from database import Base

class Snippet(Base):
    __tablename__ = "snippet"
    code = Column(Text)
    snippetID = Column(String, primary_key = True)
