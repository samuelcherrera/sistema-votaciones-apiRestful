from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

import models, schemas, crud, auth
from database import SessionLocal, engine

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Votaciones API")


# ===========================
# DB Session Dependency
# ===========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/",include_in_schema=False)
def root():
    return {"message": "API del Sistema de Votaciones funcionando correctamente, para probar los endpoints dirígete a localhost:8000/docs"}
# ===========================
# AUTENTICACIÓN
# ===========================

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtener token JWT con credenciales hardcodeadas.
    Username: admin
    Password: admin123
    """
    if form_data.username != auth.ADMIN_USERNAME or form_data.password != auth.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": "admin"}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ===========================
# VOTERS (Protegidos)
# ===========================

@app.post("/voters", response_model=schemas.VoterResponse)
def create_voter(voter: schemas.VoterCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.create_voter(db, voter)


@app.get("/voters", response_model=List[schemas.VoterResponse])
def get_voters(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.get_voters(db)


@app.get("/voters/{voter_id}", response_model=schemas.VoterResponse)
def get_voter(voter_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    voter = crud.get_voter(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Votante no encontrado.")
    return voter


@app.delete("/voters/{voter_id}")
def delete_voter(voter_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    deleted = crud.delete_voter(db, voter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Votante no encontrado.")
    return {"message": "Votante eliminado correctamente."}


# ===========================
# CANDIDATES (Protegidos)
# ===========================

@app.post("/candidates", response_model=schemas.CandidateResponse)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.create_candidate(db, candidate)


@app.get("/candidates", response_model=List[schemas.CandidateResponse])
def get_candidates(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.get_candidates(db)


@app.get("/candidates/{candidate_id}", response_model=schemas.CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    candidate = crud.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidato no encontrado.")
    return candidate


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    deleted = crud.delete_candidate(db, candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Candidato no encontrado.")
    return {"message": "Candidato eliminado correctamente."}


# ===========================
# VOTES (Públicos)
# ===========================

@app.post("/votes", response_model=schemas.VoteResponse)
def create_vote(vote: schemas.VoteCreate, db: Session = Depends(get_db)):
    return crud.create_vote(db, vote)


@app.get("/votes", response_model=List[schemas.VoteResponse])
def get_votes(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.get_votes(db)


@app.get("/votes/statistics", response_model=schemas.VotingSummary)
def get_statistics(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return crud.get_statistics(db)