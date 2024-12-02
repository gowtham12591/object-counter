from typing import List                                         # Importing List for type hinting in method arguments and return values
from sqlalchemy import create_engine, Column, Integer, String   # Importing SQLAlchemy components for ORM
from sqlalchemy.ext.declarative import declarative_base         # Importing a base class for model definitions
from sqlalchemy.orm import sessionmaker                         # Importing session maker for database session management
from counter.domain.models import ObjectCount                   # Importing the ObjectCount domain model
from counter.domain.ports import ObjectCountRepo                # Importing the ObjectCountRepo interface/port
from logger_config import logger                                # Importing logger from logger_config

# Creating a base class for SQLAlchemy models
Base = declarative_base()

# Defining the Counter table as a SQLAlchemy model
class Counter(Base):
    __tablename__ = 'counter'                                   # Specifies the name of the table in the database
    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key column with auto-increment
    object_class = Column(String, unique=True, nullable=False)  # Column for object class, must be unique and non-null
    count = Column(Integer, nullable=False)                     # Column for count, must be non-null

# Repository implementation for interacting with PostgreSQL
class CountPostgresDBRepo(ObjectCountRepo):
    def __init__(self, db_url: str):
        try:
            logger.info("Initializing CountPostgresDBRepo with DB URL.")
            # Create a database engine using the provided database URL
            self.engine = create_engine(db_url)
            # Create the database tables defined by the models (if they don't already exist)
            Base.metadata.create_all(self.engine)
            # Create a session factory bound to the engine for session management
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database engine and session successfully initialized.")
        except Exception as e:
            logger.error(f"Error initializing database connection: {e}")
            raise e

    # Private method to create a new database session
    def __get_session(self):
        logger.debug("Creating a new database session.")
        return self.Session()

    # Method to read values from the database
    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        session = self.__get_session()  # Create a new session
        try:
            logger.info("Reading values from the database.")
            if object_classes:
                # Query specific object classes using a filter
                logger.debug(f"Filtering values for object classes: {object_classes}")
                counters = session.query(Counter).filter(Counter.object_class.in_(object_classes)).all()
            else:
                # Query all rows from the Counter table
                logger.debug("Fetching all rows from the Counter table.")
                counters = session.query(Counter).all()

            # Convert the Counter table rows into a list of ObjectCount domain models
            result = [ObjectCount(counter.object_class, counter.count) for counter in counters]
            logger.info(f"Read {len(result)} rows from the database.")
            return result
        except Exception as e:
            logger.error(f"Error reading values from the database: {e}")
            raise e
        finally:
            session.close()  # Ensure the session is closed after the operation
            logger.debug("Database session closed.")

    # Method to update values in the database
    def update_values(self, new_values: List[ObjectCount]):
        session = self.__get_session()                                  # Create a new session
        try:
            logger.info("Updating values in the database.")
            for value in new_values:
                logger.debug(f"Processing value: {value}")
                # Check if a record exists for the given object_class
                counter = session.query(Counter).filter_by(object_class=value.object_class).first()
                if counter:
                    # If the record exists, update its count
                    logger.debug(f"Updating count for object class {value.object_class}.")
                    counter.count += value.count
                else:
                    # If the record doesn't exist, create a new one
                    logger.debug(f"Creating new record for object class {value.object_class}.")
                    counter = Counter(object_class=value.object_class, count=value.count)
                    session.add(counter)                                # Add the new record to the session
            session.commit()                                            # Commit all changes to the database
            logger.info("Database update committed successfully.")
        except Exception as e:
            session.rollback()                                          # Roll back the transaction in case of an error
            logger.error(f"Error updating values in the database: {e}")
            raise e                                                     # Re-raise the exception after rolling back
        finally:
            session.close()                                             # Ensure the session is closed after the operation
            logger.debug("Database session closed.")