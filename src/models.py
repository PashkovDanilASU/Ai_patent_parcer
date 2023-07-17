from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class WebsiteParsingConfig(Base):
    __tablename__ = 'website_parsing_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    publication_date_selector_value = Column(String(255), nullable=False)
    patent_title_selector_value = Column(String(255), nullable=False)
    document_number_selector_value = Column(String(255), nullable=False)
    patent_owner_selector_value = Column(String(255), nullable=False)
    applicant_selector_value = Column(String(255), nullable=False)
    international_patent_classification_selector_value = Column(String(255), nullable=False)
    country_selector_value = Column(String(255), nullable=False)


# class Authors(Base):
#     __tablename__ = 'authors'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     first_name = Column(String(255), nullable=False)
#     last_name = Column(String(255), nullable=False)


class Patents(Base):
    __tablename__ = 'patents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_date = Column(Date, nullable=False)
    patent_title = Column(String(255), nullable=False)
    document_number = Column(String(255), unique=True)
    patent_owner = Column(ARRAY(String(255)))
    applicant = Column(ARRAY(String(255)))
    international_patent_classification = Column(ARRAY(String(255)), nullable=False)
    country = Column(String(32))

    # authors = relationship('Authors', secondary='patents_authors')


class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parsed_patents_count = Column(Integer, nullable=False)
    missed_patents_count = Column(Integer, nullable=False)
    status = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    # parsing_info_id = Column(Integer, ForeignKey('parsing_information.id'))


# class PatentsAuthors(Base):
#     __tablename__ = 'patents_authors'
#
#     patent_id = Column(Integer, ForeignKey('patents.id'), primary_key=True)
#     author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)
