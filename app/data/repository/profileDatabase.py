
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, Float, Integer, UniqueConstraint, Index, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from config import DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW

logger = logging.getLogger(__name__)

Base = declarative_base()


engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    echo=False,
    pool_pre_ping=True
)

print(f"DEBUG: DATABASE_URL value is: {DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ProfileModel(Base):

    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    gender = Column(String(10), nullable=False, index=True)
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String(20), nullable=False, index=True)
    country_id = Column(String(5), nullable=False, index=True)
    country_probability = Column(Float, nullable=False)
    created_at = Column(String(30), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('name', name='uq_profiles_name'),
        Index('idx_gender', 'gender'),
        Index('idx_country_id', 'country_id'),
        Index('idx_age_group', 'age_group'),
        Index('idx_created_at', 'created_at'),
    )


async def init_db():

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise RuntimeError(f"Failed to initialize database: {str(e)}")


async def close_db():

    try:
        engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")


async def check_db_connection():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.debug("Database connection check passed")
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        raise


@contextmanager
def get_session():

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def create_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:

    try:
        with get_session() as session:
            profile = ProfileModel(
                id=profile_data['id'],
                name=profile_data['name'],
                gender=profile_data['gender'],
                gender_probability=profile_data['gender_probability'],
                sample_size=profile_data['sample_size'],
                age=profile_data['age'],
                age_group=profile_data['age_group'],
                country_id=profile_data['country_id'],
                country_probability=profile_data['country_probability'],
                created_at=profile_data['created_at']
            )
            session.add(profile)
            session.commit()

            logger.info(f"Profile created: {profile_data['id']} (name: {profile_data['name']})")
            return profile_data
    except Exception as e:
        logger.error(f"Failed to create profile: {str(e)}")
        raise


async def get_profile_by_id(profile_id: str) -> Optional[Dict[str, Any]]:

    try:
        with get_session() as session:
            profile = session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()

            if profile is None:
                logger.debug(f"Profile not found: {profile_id}")
                return None

            result = {
                'id': profile.id,
                'name': profile.name,
                'gender': profile.gender,
                'gender_probability': profile.gender_probability,
                'sample_size': profile.sample_size,
                'age': profile.age,
                'age_group': profile.age_group,
                'country_id': profile.country_id,
                'country_probability': profile.country_probability,
                'created_at': profile.created_at
            }

            logger.debug(f"Profile retrieved: {profile_id}")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve profile by ID: {str(e)}")
        raise


async def get_profile_by_name(name: str) -> Optional[Dict[str, Any]]:

    try:
        with get_session() as session:
            profile = session.query(ProfileModel).filter(
                ProfileModel.name.ilike(name)
            ).first()

            if profile is None:
                logger.debug(f"Profile not found for name: {name}")
                return None

            result = {
                'id': profile.id,
                'name': profile.name,
                'gender': profile.gender,
                'gender_probability': profile.gender_probability,
                'sample_size': profile.sample_size,
                'age': profile.age,
                'age_group': profile.age_group,
                'country_id': profile.country_id,
                'country_probability': profile.country_probability,
                'created_at': profile.created_at
            }

            logger.debug(f"Profile retrieved for name: {name}")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve profile by name: {str(e)}")
        raise


async def get_profiles(
        gender: Optional[str] = None,
        country_id: Optional[str] = None,
        age_group: Optional[str] = None
) -> List[Dict[str, Any]]:

    try:
        with get_session() as session:
            query = session.query(ProfileModel)

            if gender:
                query = query.filter(ProfileModel.gender.ilike(gender))

            if country_id:
                query = query.filter(ProfileModel.country_id.ilike(country_id))

            if age_group:
                query = query.filter(ProfileModel.age_group.ilike(age_group))

            profiles = query.all()

            results = [
                {
                    'id': p.id,
                    'name': p.name,
                    'gender': p.gender,
                    'gender_probability': p.gender_probability,
                    'sample_size': p.sample_size,
                    'age': p.age,
                    'age_group': p.age_group,
                    'country_id': p.country_id,
                    'country_probability': p.country_probability,
                    'created_at': p.created_at
                }
                for p in profiles
            ]

            logger.info(
                f"Retrieved {len(results)} profiles (filters: gender={gender}, country={country_id}, age_group={age_group})")
            return results
    except Exception as e:
        logger.error(f"Failed to retrieve profiles: {str(e)}")
        raise


async def delete_profile(profile_id: str) -> bool:

    try:
        with get_session() as session:
            profile = session.query(ProfileModel).filter(ProfileModel.id == profile_id).first()

            if profile is None:
                logger.warning(f"Profile not found for deletion: {profile_id}")
                return False

            session.delete(profile)
            session.commit()

            logger.info(f"Profile deleted: {profile_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to delete profile: {str(e)}")
        raise