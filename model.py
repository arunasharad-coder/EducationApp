
from datetime import datetime, time
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Time,
    ForeignKey,
    Boolean,
    Enum as SQLAEnum,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ReminderType(str, Enum):
    EVENT = "event"
    ASSIGNMENT = "assignment"
    DAILY_INSPIRATION = "daily_inspiration"
    SOCIAL_CURFEW_NOTIFICATION = "social_curfew_notification"


class ActivityType(str, Enum):
    ATTENDANCE = "attendance"
    ASSIGNMENT_SUBMISSION = "assignment_submission"
    QUIZ_PARTICIPATION = "quiz_participation"
    COMMUNITY_VOLUNTEERING = "community_volunteering"
    FORUM_ENGAGEMENT = "forum_engagement"


class SocialPostVisibility(str, Enum):
    PUBLIC = "public"
    GROUP_ONLY = "group_only"
    PRIVATE = "private"


class Event(Base):
    """
    Represents an event such as workshop, class session, seminar, etc.
    Related to Reminders via event linkage.
    """
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Backrefs (reminders referencing this event) defined from Reminder model


class Reminder(Base):
    """
    Personalized or global reminders for students.
    Can relate to Events or standalone reminders.
    """

    __tablename__ = "reminders"

    reminder_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    reminder_type = Column(SQLAEnum(ReminderType), nullable=False, index=True)
    reminder_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Linkage: Reminder may be linked to a student (personalized) or be global (admin managed)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True, index=True)  # nullable = global reminders
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=True, index=True)

    # User controls:
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    is_dismissed = Column(Boolean, default=False, nullable=False, index=True)

    # Allows user to modify notification time:
    modified_reminder_time = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="reminders", foreign_keys=[student_id])
    event = relationship("Event", backref="reminders", foreign_keys=[event_id])


class ReviewSubmission(Base):
    """
    Represents a submission for assignments or quizzes that can be reviewed.
    Implicitly relevant for points awarding and review tracking.
    """
    __tablename__ = "review_submissions"

    submission_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    assignment_id = Column(Integer, nullable=True, index=True)  # Assuming assignments are tracked elsewhere; FK to assignments table if exists
    quiz_id = Column(Integer, nullable=True, index=True)  # Optional: FK to quiz table if exists

    submitted_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_comments = Column(Text, nullable=True)

    # Status like 'pending', 'approved', 'rejected' might be needed for real world, but spec doesn't state:

    # Points awarded can be tracked elsewhere in PointsTransaction for transparency.

    student = relationship("Student", back_populates="review_submissions")


class GamificationProfile(Base):
    """
    Stores aggregated gamification data per student including points total,
    levels, badges (planned for future extensions).
    """

    __tablename__ = "gamification_profiles"

    student_id = Column(Integer, ForeignKey("students.student_id"), primary_key=True)
    total_points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    badges = Column(Text, nullable=True)  # JSON-encoded string or comma separated badge names or IDs for future extensibility

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="gamification_profile")


class SocialPost(Base):
    """
    Represents a social post made by students on portal social features.
    Tracks content, visibility, timestamps.
    """

    __tablename__ = "social_posts"

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    visibility = Column(SQLAEnum(SocialPostVisibility), nullable=False, default=SocialPostVisibility.PUBLIC)

    is_active = Column(Boolean, nullable=False, default=True)  # Whether post is visible/active

    student = relationship("Student", back_populates="social_posts")


# --- Additional core models referenced above but minimal to support FK constraints --- #

class Student(Base):
    """
    Minimal Student model to support FK relations as per spec.
    """
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    profile_data = Column(Text, nullable=True)  # JSON-encoded profile data or similar

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    reminders = relationship("Reminder", back_populates="student", cascade="all, delete-orphan")
    review_submissions = relationship("ReviewSubmission", back_populates="student", cascade="all, delete-orphan")
    gamification_profile = relationship("GamificationProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    social_posts = relationship("SocialPost", back_populates="student", cascade="all, delete-orphan")
    
class Syllabus(Base):
    """
    Tracks course content and student completion.
    """
    __tablename__ = "syllabus_topics"

    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0) # To keep chapters in order
    is_completed = Column(Boolean, default=False)
    
    # Link it to a student if you want individual progress
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True)

class CourseCalendar(Base):
    """
    Specific class dates for students to follow.
    """
    __tablename__ = "course_calendar"

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    category = Column(String(100)) # e.g., 'Upanishad', 'Gita', 'Meditation'
