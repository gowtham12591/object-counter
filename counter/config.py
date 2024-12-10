import os
from dotenv import load_dotenv
# from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.count_repo_psql import CountPostgresDBRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects
from logger_config import logger
# Load environment variables from .env file
load_dotenv()


# For postgres db
def dev_count_action() -> CountDetectedObjects:
    
    # SQLite URL for development
    db_url = os.environ.get('DEV_DB_URL', 'sqlite:///dev_counter.db')               # using sqlite for inmemory
    # Log the loaded configuration (you can replace this with your logger)
    logger.info(f"Loaded the sqlite database for storing the details inmemory")

    return CountDetectedObjects(
        FakeObjectDetector(),                                                       # In the dev mode, you can use FakeObjectDetector
        CountPostgresDBRepo(db_url)                                                 # Uses the PostgreSQL (or SQLite) repository
    )


def prod_count_action() -> CountDetectedObjects:
    try:
        # TensorFlow Serving details
        tfs_host = os.getenv('TFS_HOST', 'localhost')
        tfs_port = int(os.getenv('TFS_PORT', 8503))

        # PostgreSQL-related environment variables
        postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        postgres_port = int(os.getenv('POSTGRES_PORT', 5434))
        postgres_db = os.getenv('POSTGRES_DB', '')  # Add your postgres DB name
        postgres_user = os.getenv('POSTGRES_USER', '')  # Add your postgres user
        postgres_password = os.getenv('POSTGRES_PASSWORD', '')  # Add your postgres password

        # Log the loaded configuration (you can replace this with your logger)
        logger.info(f"Loaded the postgres database for updating/getting the details")

        # PostgreSQL connection URL (for SQLAlchemy)
        db_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

        # Return a configured CountDetectedObjects instance
        return CountDetectedObjects(
            TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
            CountPostgresDBRepo(db_url)  # Uses PostgreSQL repository for production
        )
    except Exception as e:
        logger.error(f"Failed to configure CountDetectedObjects: {e}")
        raise


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()
