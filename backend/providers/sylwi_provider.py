from pathlib import Path

from backend.providers.base import (
    RecognitionProviderUnavailable,
)

from backend.schemas import (
    RecognitionResponse,
)


class SylwiRecognitionProvider:
    """
    Adapter zwischen Sylwis ML-Pipeline
    und unserer stabilen API-Schnittstelle.


    WICHTIG:

    Sylwis bestehender ML-Code soll später
    möglichst NICHT für FastAPI umgebaut werden.

    Dieser Adapter übernimmt stattdessen:

    1. Bildpfad an Sylwis Pipeline übergeben
    2. Ergebnis empfangen
    3. Ergebnis ins gemeinsame API-Format übersetzen


    Die ML-Pipeline darf intern weiterhin
    vollkommen unabhängig arbeiten.
    """


    name = "sylwi"


    def __init__(
        self,
    ):
        # Noch wird absichtlich keine ML-Pipeline geladen.
        #
        # Später könnte hier beispielsweise stehen:
        #
        # self.pipeline = PokemonRecognitionPipeline(...)
        #
        # Modell, Embeddings und Referenzdaten würden dann
        # EINMAL beim Backend-Start geladen und nicht
        # bei jeder einzelnen Anfrage neu.

        self._ready = False


    def is_ready(
        self,
    ) -> bool:

        return self._ready


    def recognize(
        self,
        image_path: Path,
    ) -> RecognitionResponse:

        raise RecognitionProviderUnavailable(
            (
                "Sylwis Recognition-Pipeline ist "
                "noch nicht an den API-Adapter gekoppelt."
            )
        )