from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ParsingInformation(Base):
    __tablename__ = 'parsing_information'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    selector_type = Column(String(255), nullable=False)
    element_selector_value = Column(String(255), nullable=False)
    selectors_value = Column(ARRAY(String(255)), nullable=False)


class Authors(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)


class Patents(Base):
    __tablename__ = 'patents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_date = Column(Date, nullable=False)
    patent_title = Column(String(255), nullable=False)
    document_number = Column(String(255))
    patent_owner = Column(ARRAY(String(255)))
    applicant = Column(ARRAY(String(255)))
    international_patent_classification = Column(ARRAY(String(255)), nullable=False)

    authors = relationship('Authors', secondary='patents_authors')


class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(255))
    status = Column(String(255), nullable=False)
    message = Column(Text)
    timestamp = Column(TIMESTAMP, nullable=False)
    parsing_info_id = Column(Integer, ForeignKey('parsing_information.id'))


class PatentsAuthors(Base):
    __tablename__ = 'patents_authors'

    patent_id = Column(Integer, ForeignKey('patents.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)