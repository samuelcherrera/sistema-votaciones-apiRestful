from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    has_voted = Column(Boolean, default=False)

    # Relación 1 a 1 con Vote
    vote = relationship("Vote", back_populates="voter", uselist=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    party = Column(String(100), nullable=True)
    votes = Column(Integer, default=0)

    # Relación 1 a muchos (un candidato puede recibir muchos votos)
    received_votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(Integer, ForeignKey("voters.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    voter = relationship("Voter", back_populates="vote")
    candidate = relationship("Candidate", back_populates="received_votes")

    # Evita doble voto desde la base de datos
    __table_args__ = (
        UniqueConstraint('voter_id', name='uq_voter_vote'),
    )