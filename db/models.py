from sqlalchemy import (
    Column, Integer, String, Text, Numeric, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Person(Base):
    __tablename__ = "person"
    id            = Column(Integer, primary_key=True)
    full_name     = Column(Text, nullable=False)
    first_name    = Column(Text)
    last_name     = Column(Text)
    current_title = Column(Text)
    location      = Column(Text)
    bio           = Column(Text)
    summary       = Column(Text)
    quality_score = Column(Numeric)
    embedding     = Column(Vector(768))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    emails        = relationship("Email",        cascade="all, delete-orphan")
    sources       = relationship("Source",       cascade="all, delete-orphan")
    affiliations  = relationship("Affiliation",  cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "email"
    id         = Column(Integer, primary_key=True)
    person_id  = Column(Integer, ForeignKey("person.id"))
    address    = Column(Text, unique=True, nullable=False)
    confidence = Column(Numeric, default=1)

class Organization(Base):
    __tablename__ = "organization"
    id      = Column(Integer, primary_key=True)
    name    = Column(Text, unique=True, nullable=False)
    org_type= Column(Text)
    country = Column(Text)

class Affiliation(Base):
    __tablename__ = "affiliation"
    person_id = Column(Integer, ForeignKey("person.id"), primary_key=True)
    org_id    = Column(Integer, ForeignKey("organization.id"), primary_key=True)
    role      = Column(Text, primary_key=True)

class Source(Base):
    __tablename__ = "source"
    id        = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    url       = Column(Text)
    snippet   = Column(Text)
    source_rank = Column(Integer)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

class Edge(Base):
    __tablename__ = "edge"
    from_id  = Column(Integer, ForeignKey("person.id"), primary_key=True)
    to_id    = Column(Integer, ForeignKey("person.id"), primary_key=True)
    rel_type = Column(Text, primary_key=True)
    weight   = Column(Numeric, default=1)
