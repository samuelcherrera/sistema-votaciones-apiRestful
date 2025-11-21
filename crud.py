from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas

# ======================
#   CRUD VOTERS
# ======================

def create_voter(db: Session, voter: schemas.VoterCreate):
    # Verificar que no sea candidato
    candidate_exists = db.query(models.Candidate).filter(
        models.Candidate.name.ilike(voter.name)
    ).first()
    if candidate_exists:
        raise HTTPException(
            status_code=400,
            detail=f"El nombre '{voter.name}' ya está registrado como candidato y no puede ser votante."
        )

    db_voter = models.Voter(name=voter.name, email=voter.email)
    db.add(db_voter)
    db.commit()
    db.refresh(db_voter)
    return db_voter


def get_voters(db: Session):
    return db.query(models.Voter).all()


def get_voter(db: Session, voter_id: int):
    return db.query(models.Voter).filter(models.Voter.id == voter_id).first()


def delete_voter(db: Session, voter_id: int):
    voter = get_voter(db, voter_id)
    if not voter:
        return False
    db.delete(voter)
    db.commit()
    return True


# ======================
#   CRUD CANDIDATES
# ======================

def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    # Verificar que no sea votante
    voter_exists = db.query(models.Voter).filter(
        models.Voter.name.ilike(candidate.name)
    ).first()
    if voter_exists:
        raise HTTPException(
            status_code=400,
            detail=f"El nombre '{candidate.name}' ya está registrado como votante y no puede ser candidato."
        )

    db_candidate = models.Candidate(name=candidate.name, party=candidate.party)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def get_candidates(db: Session):
    return db.query(models.Candidate).all()


def get_candidate(db: Session, candidate_id: int):
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()


def delete_candidate(db: Session, candidate_id: int):
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return False
    db.delete(candidate)
    db.commit()
    return True


# ======================
#   CRUD VOTES
# ======================

def create_vote(db: Session, vote: schemas.VoteCreate):
    voter = db.query(models.Voter).filter(models.Voter.id == vote.voter_id).first()
    candidate = db.query(models.Candidate).filter(models.Candidate.id == vote.candidate_id).first()

    if not voter:
        raise HTTPException(status_code=404, detail="Votante no encontrado.")

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidato no encontrado.")

    if voter.has_voted:
        raise HTTPException(status_code=400, detail="El votante ya realizó su voto anteriormente.")

    # Registrar voto
    db_vote = models.Vote(voter_id=vote.voter_id, candidate_id=vote.candidate_id)
    voter.has_voted = True
    candidate.votes += 1

    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


def get_votes(db: Session):
    return db.query(models.Vote).all()


# ======================
#   STATISTICS
# ======================

def get_statistics(db: Session):
    candidates = db.query(models.Candidate).all()
    total_votes = sum(c.votes for c in candidates)

    results = []
    for c in candidates:
        percentage = (c.votes / total_votes * 100) if total_votes > 0 else 0
        results.append(
            schemas.VoteStatistics(
                candidate_id=c.id,
                candidate_name=c.name,
                votes=c.votes,
                percentage=round(percentage, 2),
            )
        )

    total_voters_voted = db.query(models.Voter).filter(models.Voter.has_voted == True).count()

    return schemas.VotingSummary(
        results=results,
        total_votes=total_votes,
        total_voters_voted=total_voters_voted
    )
