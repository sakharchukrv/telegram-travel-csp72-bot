
"""
Модели базы данных
"""
from datetime import datetime
from typing import List
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger, String, DateTime, Boolean, Text, JSON, Integer,
    ForeignKey, Enum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Базовый класс для моделей"""
    pass


class UserStatus(PyEnum):
    """Статусы пользователя"""
    PENDING = "pending"  # Ожидает одобрения
    APPROVED = "approved"  # Одобрен
    REJECTED = "rejected"  # Отклонен
    REVOKED = "revoked"  # Доступ отозван


class ApplicationStatus(PyEnum):
    """Статусы заявки"""
    DRAFT = "draft"  # Черновик
    SUBMITTED = "submitted"  # Отправлена
    PROCESSING = "processing"  # В обработке
    APPROVED = "approved"  # Одобрена
    REJECTED = "rejected"  # Отклонена


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(500), nullable=True)  # ФИО пользователя
    organization: Mapped[str] = mapped_column(String(500), nullable=True)  # Организация
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )
    drafts: Mapped[List["Draft"]] = relationship(
        "Draft", back_populates="user", cascade="all, delete-orphan"
    )


class Application(Base):
    """Модель заявки"""
    __tablename__ = "applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    
    # Основные поля
    sport_type: Mapped[str] = mapped_column(String(255))  # Вид спорта
    event_rank: Mapped[str] = mapped_column(String(255))  # Ранг мероприятия
    country: Mapped[str] = mapped_column(String(255))  # Страна
    city: Mapped[str] = mapped_column(String(255))  # Город
    
    # Данные об участниках (JSON)
    participants_data: Mapped[dict] = mapped_column(JSON)
    
    # Статус
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.SUBMITTED,
        nullable=False
    )
    
    # Файлы и отправка
    excel_file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    participants: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="application", cascade="all, delete-orphan"
    )


class Participant(Base):
    """Модель участника поездки"""
    __tablename__ = "participants"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"))
    
    full_name: Mapped[str] = mapped_column(String(500))  # ФИО
    date_from: Mapped[str] = mapped_column(String(20))  # Дата начала (ДД.ММ.ГГГГ)
    date_to: Mapped[str] = mapped_column(String(20))  # Дата окончания (ДД.ММ.ГГГГ)
    order_num: Mapped[int] = mapped_column(Integer)  # Порядковый номер
    
    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="participants"
    )


class Draft(Base):
    """Модель черновика заявки"""
    __tablename__ = "drafts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    
    # Данные черновика (JSON)
    draft_data: Mapped[dict] = mapped_column(JSON)
    
    # Название черновика
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="drafts")
