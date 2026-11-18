import os
from pathlib import Path

from backend.providers.base import (
    RecognitionInputError,
)

from backend.schemas import (
    NotFoundRecognitionResult,
    PokemonCard,
    RecognitionCandidate,
    RecognitionInfo,
    RecognitionResponse,
    SuccessRecognitionResult,
    UncertainRecognitionResult,
)


class MockRecognitionProvider:

    name = "mock"


    def is_ready(
        self,
    ) -> bool:

        return True


    def recognize(
        self,
        image_path: Path,
    ) -> RecognitionResponse:

        if not image_path.exists():

            raise RecognitionInputError(
                f"Bild wurde nicht gefunden: {image_path}"
            )


        if image_path.stat().st_size <= 0:

            raise RecognitionInputError(
                "Das Bild ist leer."
            )


        mode = (
            os.getenv(
                "MOCK_RECOGNITION_MODE",
                "success",
            )
            .strip()
            .lower()
        )


        # ====================================================
        # KEIN TREFFER
        # ====================================================

        if mode == "not_found":

            return NotFoundRecognitionResult(
                reason="no_matching_card",

                message=(
                    "Für dieses Bild wurde keine "
                    "ausreichend passende Referenzkarte gefunden."
                ),
            )


        # ====================================================
        # TESTKARTEN
        # ====================================================

        caterpie = PokemonCard(
            card_id="swsh8-1",

            name="Caterpie",

            set_id="swsh8",

            set_name="Fusion Strike",

            number="1",

            rarity="Common",

            supertype="Pokémon",

            subtypes=[
                "Basic",
            ],

            types=[
                "Grass",
            ],

            artist="Mitsuhiro Arita",

            release_date="2021-11-12",

            image_url=(
                "https://images.pokemontcg.io/"
                "swsh8/1_hires.png"
            ),
        )


        metapod = PokemonCard(
            card_id="swsh8-2",

            name="Metapod",

            set_id="swsh8",

            set_name="Fusion Strike",

            number="2",

            rarity="Uncommon",

            supertype="Pokémon",

            subtypes=[
                "Stage 1",
            ],

            types=[
                "Grass",
            ],

            artist="Miki Tanaka",

            release_date="2021-11-12",

            image_url=(
                "https://images.pokemontcg.io/"
                "swsh8/2_hires.png"
            ),
        )


        butterfree = PokemonCard(
            card_id="swsh8-3",

            name="Butterfree",

            set_id="swsh8",

            set_name="Fusion Strike",

            number="3",

            rarity="Rare",

            supertype="Pokémon",

            subtypes=[
                "Stage 2",
            ],

            types=[
                "Grass",
            ],

            artist="",

            release_date="2021-11-12",

            image_url=(
                "https://images.pokemontcg.io/"
                "swsh8/3_hires.png"
            ),
        )


        # ====================================================
        # UNSICHER
        # ====================================================

        if mode == "uncertain":

            return UncertainRecognitionResult(
                candidates=[

                    RecognitionCandidate(
                        card=caterpie,

                        recognition=RecognitionInfo(
                            similarity=0.914,
                            margin=0.008,
                        ),

                        variants=[
                            "normal",
                            "holo",
                            "reverse_holo",
                        ],
                    ),

                    RecognitionCandidate(
                        card=metapod,

                        recognition=RecognitionInfo(
                            similarity=0.906,
                            margin=0.006,
                        ),

                        variants=[
                            "normal",
                            "holo",
                            "reverse_holo",
                        ],
                    ),

                    RecognitionCandidate(
                        card=butterfree,

                        recognition=RecognitionInfo(
                            similarity=0.897,
                            margin=0.005,
                        ),

                        variants=[
                            "normal",
                            "holo",
                            "reverse_holo",
                        ],
                    ),

                ],
            )


        # ====================================================
        # SUCCESS
        #
        # Auch bei unbekanntem Mock-Modus verwenden wir
        # absichtlich den sicheren Standard "success".
        # ====================================================

        return SuccessRecognitionResult(
            card=caterpie,

            recognition=RecognitionInfo(
                similarity=0.963,
                margin=0.087,
            ),

            variants=[
                "normal",
                "holo",
                "reverse_holo",
            ],
        )