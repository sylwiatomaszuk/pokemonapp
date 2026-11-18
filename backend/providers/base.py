from pathlib import Path
from typing import Protocol

from backend.schemas import RecognitionResponse


# ============================================================
# PROVIDER-FEHLER
# ============================================================

class RecognitionProviderError(
    Exception
):
    """
    Basisklasse für erwartbare Fehler innerhalb
    eines RecognitionProviders.
    """


class RecognitionInputError(
    RecognitionProviderError
):
    """
    Das übergebene Bild kann nicht verarbeitet werden.
    """


class RecognitionProviderUnavailable(
    RecognitionProviderError
):
    """
    Die eigentliche Erkennung ist momentan
    nicht einsatzbereit.

    Beispiele:

    - Modell fehlt
    - Embeddings fehlen
    - Referenzdaten fehlen
    - Pipeline konnte nicht geladen werden
    """


# ============================================================
# PROVIDER-SCHNITTSTELLE
# ============================================================

class RecognitionProvider(
    Protocol
):
    """
    Gemeinsame Schnittstelle für jede Form
    der Pokémon-Kartenerkennung.

    FastAPI kennt ausschließlich diese Schnittstelle.

    Dahinter können später beliebige Technologien laufen:

    - YOLO
    - OpenCV
    - ResNet18
    - NumPy
    - PyTorch
    - Embeddings
    - Cosine Similarity
    - andere Modelle

    Die API muss davon nichts wissen.
    """

    name: str


    def is_ready(
        self,
    ) -> bool:
        """
        Gibt zurück, ob der Provider momentan
        Anfragen verarbeiten kann.
        """

        ...


    def recognize(
        self,
        image_path: Path,
    ) -> RecognitionResponse:
        """
        Erkennt eine Pokémon-Karte anhand
        eines lokalen Bildpfades.

        Das ist später der einzige notwendige
        Kontaktpunkt zwischen FastAPI und
        Sylwis Recognition-Pipeline.
        """

        ...