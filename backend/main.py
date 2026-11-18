import logging
import mimetypes
import os
import tempfile

from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from starlette.concurrency import (
    run_in_threadpool,
)

from backend.providers import (
    create_recognition_provider,
)

from backend.providers.base import (
    RecognitionInputError,
    RecognitionProviderUnavailable,
)

from backend.schemas import (
    HealthResponse,
    RecognitionResponse,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(
    "pokemon-recognition-api"
)


# ============================================================
# KONFIGURATION
# ============================================================

API_CONTRACT_VERSION = "1"


MAX_UPLOAD_BYTES = int(
    os.getenv(
        "MAX_UPLOAD_BYTES",
        str(
            25
            * 1024
            * 1024
        ),
    )
)


UPLOAD_CHUNK_SIZE = (
    1024
    * 1024
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/octet-stream",
}


# ============================================================
# PROVIDER
# ============================================================

provider = (
    create_recognition_provider()
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title=(
        "Pokemon Card Recognition API"
    ),

    version="0.1.0",

    description=(
        "Stabile API-Schnittstelle zwischen "
        "Frontend und Kartenerkennung."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    # Für unsere lokale Entwicklung
    # zunächst bewusst offen.
    allow_origins=[
        "*",
    ],

    allow_credentials=False,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/api/health",

    response_model=HealthResponse,
)
async def health(
) -> HealthResponse:

    ready = (
        provider.is_ready()
    )


    return HealthResponse(
        status=(
            "ok"
            if ready
            else "degraded"
        ),

        service=(
            "pokemon-recognition-api"
        ),

        api_contract_version=(
            API_CONTRACT_VERSION
        ),

        provider=(
            provider.name
        ),

        provider_ready=(
            ready
        ),
    )


# ============================================================
# DATEIENDUNG ERMITTELN
# ============================================================

def determine_suffix(
    upload: UploadFile,
) -> str:

    filename = (
        upload.filename
        or ""
    )


    suffix = (
        Path(
            filename
        )
        .suffix
        .lower()
    )


    allowed_suffixes = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".heic",
        ".heif",
    }


    if suffix in allowed_suffixes:

        return suffix


    if upload.content_type:

        guessed = (
            mimetypes
            .guess_extension(
                upload.content_type
            )
        )


        if (
            guessed
            in allowed_suffixes
        ):

            return guessed


    return ".jpg"


# ============================================================
# UPLOAD TEMPORÄR SPEICHERN
# ============================================================

async def save_upload(
    upload: UploadFile,
    destination: Path,
) -> int:
    """
    Speichert den Upload in kleinen Blöcken.

    Dadurch muss ein großes Kamerafoto
    nicht vollständig gleichzeitig in den RAM.
    """

    total_bytes = 0


    with destination.open(
        "wb"
    ) as output_file:

        while True:

            chunk = await upload.read(
                UPLOAD_CHUNK_SIZE
            )


            if not chunk:
                break


            total_bytes += len(
                chunk
            )


            if (
                total_bytes
                > MAX_UPLOAD_BYTES
            ):

                raise HTTPException(
                    status_code=413,

                    detail=(
                        "Die Bilddatei ist zu groß."
                    ),
                )


            output_file.write(
                chunk
            )


    if total_bytes <= 0:

        raise HTTPException(
            status_code=400,

            detail=(
                "Die hochgeladene Bilddatei ist leer."
            ),
        )


    return total_bytes


# ============================================================
# RECOGNITION
# ============================================================

@app.post(
    "/api/recognize",

    response_model=RecognitionResponse,
)
async def recognize_card(
    file: UploadFile = File(...),
) -> RecognitionResponse:

    content_type = (
        file.content_type
        or "application/octet-stream"
    )


    if (
        content_type
        not in ALLOWED_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=415,

            detail=(
                "Die hochgeladene Datei "
                "ist kein unterstütztes Bild."
            ),
        )


    if not provider.is_ready():

        raise HTTPException(
            status_code=503,

            detail=(
                "Die Kartenerkennung "
                "ist momentan nicht verfügbar."
            ),
        )


    suffix = determine_suffix(
        file
    )


    try:

        with tempfile.TemporaryDirectory(
            prefix=(
                "pokemon-recognition-"
            )
        ) as temp_directory:

            image_path = (
                Path(
                    temp_directory
                )
                / (
                    "query"
                    + suffix
                )
            )


            file_size = await save_upload(
                file,
                image_path,
            )


            logger.info(
                (
                    "Recognition request: "
                    "filename=%s "
                    "content_type=%s "
                    "bytes=%s "
                    "provider=%s"
                ),

                file.filename,

                content_type,

                file_size,

                provider.name,
            )


            # Provider bewusst synchron.
            #
            # ML-Arbeit kann später CPU-/GPU-intensiv sein.
            # Deshalb wird sie außerhalb des normalen
            # Async-Eventloops ausgeführt.

            result = await run_in_threadpool(
                provider.recognize,
                image_path,
            )


            logger.info(
                (
                    "Recognition result: "
                    "status=%s "
                    "provider=%s"
                ),

                result.status,

                provider.name,
            )


            return result


    except RecognitionInputError as error:

        logger.warning(
            "Recognition input error: %s",
            error,
        )


        raise HTTPException(
            status_code=422,

            detail=str(
                error
            ),
        ) from error


    except RecognitionProviderUnavailable as error:

        logger.warning(
            (
                "Recognition provider "
                "unavailable: %s"
            ),
            error,
        )


        raise HTTPException(
            status_code=503,

            detail=str(
                error
            ),
        ) from error


    except HTTPException:

        raise


    except Exception as error:

        logger.exception(
            "Unexpected recognition error"
        )


        raise HTTPException(
            status_code=500,

            detail=(
                "Bei der Kartenerkennung "
                "ist ein interner Fehler aufgetreten."
            ),
        ) from error


    finally:

        await file.close()