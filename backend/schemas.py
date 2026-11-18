from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# GEMEINSAME TYPEN
# ============================================================

CardVariant = Literal[
    "normal",
    "holo",
    "reverse_holo",
]


NotFoundReason = Literal[
    "no_card_detected",
    "no_matching_card",
]


# ============================================================
# KARTENDATEN
# ============================================================

class PokemonCard(BaseModel):
    """
    Einheitliches Kartenformat für das Frontend.

    Die eigentliche ML-Pipeline muss intern nicht
    mit diesem Format arbeiten.

    Der RecognitionProvider übersetzt lediglich
    das interne Ergebnis in dieses API-Format.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    card_id: str = Field(
        min_length=1,
    )

    name: str = Field(
        min_length=1,
    )

    set_id: str = Field(
        min_length=1,
    )

    set_name: str

    number: str = Field(
        min_length=1,
    )

    rarity: str

    supertype: str

    subtypes: list[str] = Field(
        default_factory=list,
    )

    types: list[str] = Field(
        default_factory=list,
    )

    artist: str

    release_date: str

    image_url: str | None = None


# ============================================================
# ERKENNUNGSWERTE
# ============================================================

class RecognitionInfo(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    similarity: float = Field(
        ge=-1.0,
        le=1.0,
    )

    margin: float = Field(
        ge=0.0,
        le=2.0,
    )


# ============================================================
# EINDEUTIGER TREFFER
# ============================================================

class SuccessRecognitionResult(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal[
        "success"
    ] = "success"

    card: PokemonCard

    recognition: RecognitionInfo

    variants: list[
        CardVariant
    ] = Field(
        default_factory=list,
    )


# ============================================================
# EINZELNER KANDIDAT
# ============================================================

class RecognitionCandidate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    card: PokemonCard

    recognition: RecognitionInfo

    variants: list[
        CardVariant
    ] = Field(
        default_factory=list,
    )


# ============================================================
# UNSICHERE ERKENNUNG
# ============================================================

class UncertainRecognitionResult(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal[
        "uncertain"
    ] = "uncertain"

    candidates: list[
        RecognitionCandidate
    ] = Field(
        min_length=1,
        max_length=3,
    )


# ============================================================
# KEIN TREFFER
# ============================================================

class NotFoundRecognitionResult(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal[
        "not_found"
    ] = "not_found"

    reason: NotFoundReason

    message: str | None = None


# ============================================================
# GEMEINSAME API-ANTWORT
# ============================================================

RecognitionResponse = Annotated[
    (
        SuccessRecognitionResult
        | UncertainRecognitionResult
        | NotFoundRecognitionResult
    ),
    Field(
        discriminator="status",
    ),
]


# ============================================================
# HEALTH CHECK
# ============================================================

class HealthResponse(BaseModel):

    status: Literal[
        "ok",
        "degraded",
    ]

    service: str

    api_contract_version: str

    provider: str

    provider_ready: bool