from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Guild(Base):
    __tablename__ = "guilds"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    prefix = Column(String(10), default="!")
    owner_id = Column(BigInteger)
    maintenance_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(100))
    discriminator = Column(String(10))
    avatar_url = Column(String(200))
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Economy(Base):
    __tablename__ = "economy"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    balance = Column(Integer, default=0)
    bank = Column(Integer, default=0)
    daily_last = Column(DateTime)
    weekly_last = Column(DateTime)
    work_last = Column(DateTime)

class Leveling(Base):
    __tablename__ = "leveling"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    last_xp_time = Column(DateTime)
    xp_multiplier = Column(Float, default=1.0)

class ModerationCase(Base):
    __tablename__ = "moderation_cases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    user_id = Column(BigInteger)
    moderator_id = Column(BigInteger)
    action = Column(String(50))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    user_id = Column(BigInteger)
    status = Column(String(20), default="open")
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomCommand(Base):
    __tablename__ = "custom_commands"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    name = Column(String(100))
    response = Column(Text)
    author_id = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    guild_id = Column(BigInteger)
    name = Column(String(100))
    description = Column(Text)
    earned_at = Column(DateTime, default=datetime.utcnow)
