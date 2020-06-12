from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

from auth.auth_utils import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user
from clients.routes import clients_router
from database.mongodb_utilites import connect_to_mongo, disconnect_from_mongo
from auth.model import Token
from history_loans.routes import history_loans_router
from loans.routes import loans_router
from users.model import UserResponse
from users.routes import users_router

app = FastAPI(title="LoansAnalyzerAPI ", description="леха привет")

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", disconnect_from_mongo)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    loans_router,
    prefix="/loans",
    tags=["loans"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    clients_router,
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    history_loans_router,
    prefix="/history_loans",
    tags=["history_loans"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# current_user: UserResponse = Depends(get_current_active_user)
