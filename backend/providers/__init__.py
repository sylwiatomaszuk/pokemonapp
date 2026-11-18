import os

from backend.providers.base import (
    RecognitionProvider,
)

from backend.providers.mock_provider import (
    MockRecognitionProvider,
)

from backend.providers.sylwi_provider import (
    SylwiRecognitionProvider,
)


def create_recognition_provider(
) -> RecognitionProvider:

    provider_name = (
        os.getenv(
            "RECOGNITION_PROVIDER",
            "mock",
        )
        .strip()
        .lower()
    )


    if provider_name == "mock":

        return MockRecognitionProvider()


    if provider_name == "sylwi":

        return SylwiRecognitionProvider()


    raise RuntimeError(
        (
            "Unbekannter RecognitionProvider: "
            f"{provider_name}"
        )
    )