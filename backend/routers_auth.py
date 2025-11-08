from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import get_db
from . import models, schemas
from .utils_auth import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_owner(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.Owner:
    """Get current authenticated owner from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    owner_id = payload.get("sub")
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    owner = db.get(models.Owner, owner_id)
    if not owner or not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Owner not found or inactive",
        )
    return owner


@router.post("/register", response_model=schemas.TokenResponse)
def register_owner(payload: schemas.OwnerRegister, db: Session = Depends(get_db)):
    """Register a new owner/businessman."""
    # Input validation
    errors = []
    
    # Password validation
    if len(payload.password) < 6:
        errors.append("Password must be at least 6 characters long")
    if len(payload.password) > 72:
        errors.append("Password cannot be longer than 72 characters")
    
    # PAN card validation (10 characters, alphanumeric)
    pan_clean = payload.pan_card.upper().strip()
    if len(pan_clean) != 10:
        errors.append("PAN card must be exactly 10 characters (e.g., ABCDE1234F)")
    elif not pan_clean[:5].isalpha() or not pan_clean[5:9].isdigit() or not pan_clean[9].isalpha():
        errors.append("PAN card format invalid. Use format: ABCDE1234F (5 letters, 4 digits, 1 letter)")
    else:
        payload.pan_card = pan_clean
    
    # Contact validation (10 digits)
    contact_clean = payload.contact.strip().replace(" ", "").replace("-", "")
    if not contact_clean.isdigit():
        errors.append("Contact number must contain only digits")
    elif len(contact_clean) != 10:
        errors.append("Contact number must be exactly 10 digits")
    else:
        payload.contact = contact_clean
    
    # Aadhar validation (12 digits if provided)
    if payload.aadhar_number:
        aadhar_clean = payload.aadhar_number.strip().replace(" ", "").replace("-", "")
        if not aadhar_clean.isdigit():
            errors.append("Aadhar number must contain only digits")
        elif len(aadhar_clean) != 12:
            errors.append("Aadhar number must be exactly 12 digits")
        else:
            payload.aadhar_number = aadhar_clean
    
    # IFSC validation (11 characters if provided)
    if payload.ifsc_code:
        ifsc_clean = payload.ifsc_code.upper().strip()
        if len(ifsc_clean) != 11:
            errors.append("IFSC code must be exactly 11 characters (e.g., SBIN0001234)")
        elif not ifsc_clean[:4].isalpha() or not ifsc_clean[4:].isdigit():
            errors.append("IFSC code format invalid. Use format: ABCD0123456 (4 letters, 7 digits)")
        else:
            payload.ifsc_code = ifsc_clean
    
    # GST validation (15 characters if provided)
    if payload.gst_number:
        gst_clean = payload.gst_number.upper().strip()
        if len(gst_clean) != 15:
            errors.append("GST number must be exactly 15 characters")
        else:
            payload.gst_number = gst_clean
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors),
        )
    
    # Check if email already exists
    existing = db.execute(
        select(models.Owner).where(models.Owner.email == payload.email)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if PAN card already exists
    existing_pan = db.execute(
        select(models.Owner).where(models.Owner.pan_card == payload.pan_card)
    ).scalar_one_or_none()
    if existing_pan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PAN card already registered",
        )

    # Create new owner
    owner = models.Owner(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        pan_card=payload.pan_card.upper(),
        contact=payload.contact,
        business_name=payload.business_name,
        business_address=payload.business_address,
        gst_number=payload.gst_number,
        aadhar_number=payload.aadhar_number,
        bank_account=payload.bank_account,
        ifsc_code=payload.ifsc_code,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    # Generate token
    access_token = create_access_token(data={"sub": owner.id, "email": owner.email})

    return schemas.TokenResponse(
        access_token=access_token,
        owner=schemas.OwnerOut.model_validate(owner),
    )


@router.post("/login", response_model=schemas.TokenResponse)
def login_owner(payload: schemas.OwnerLogin, db: Session = Depends(get_db)):
    """Login owner and return JWT token."""
    owner = db.execute(
        select(models.Owner).where(models.Owner.email == payload.email)
    ).scalar_one_or_none()

    if not owner or not verify_password(payload.password, owner.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Generate token
    access_token = create_access_token(data={"sub": owner.id, "email": owner.email})

    return schemas.TokenResponse(
        access_token=access_token,
        owner=schemas.OwnerOut.model_validate(owner),
    )


@router.get("/me", response_model=schemas.OwnerOut)
def get_current_user_info(owner: models.Owner = Depends(get_current_owner)):
    """Get current authenticated owner's information."""
    return schemas.OwnerOut.model_validate(owner)

