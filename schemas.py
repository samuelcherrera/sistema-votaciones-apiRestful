from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ======================================
# AUTENTICACIÓN
# ======================================

class Token(BaseModel):
    access_token: str
    token_type: str


# ======================================
# VOTERS
# ======================================

class VoterCreate(BaseModel):
    name: str
    email: EmailStr


class VoterResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    has_voted: bool

    class Config:
        from_attributes = True


# ======================================
# CANDIDATES
# ======================================

class CandidateCreate(BaseModel):
    name: str
    party: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    name: str
    party: Optional[str]
    votes: int

    class Config:
        from_attributes = True


# ======================================
# VOTES
# ======================================

class VoteCreate(BaseModel):
    voter_id: int
    candidate_id: int


class VoteResponse(BaseModel):
    id: int
    voter_id: int
    candidate_id: int

    class Config:
        from_attributes = True


# ======================================
# STATISTICS
# ======================================

class VoteStatistics(BaseModel):
    candidate_id: int
    candidate_name: str
    votes: int
    percentage: float


class VotingSummary(BaseModel):
    total_votes: int
    total_voters_voted: int
    results: List[VoteStatistics]