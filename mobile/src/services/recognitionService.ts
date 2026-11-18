// mobile/src/services/recognitionService.ts

import {
  CardPrice,
  CardVariant,
  RecognitionResponse,
} from '@/types/recognition';


/*
 * ========================================================
 * MOCK-SERVICE
 * ========================================================
 *
 * Für den aktuellen Test verwenden wir absichtlich
 * den Unsicherheitsfall.
 *
 * Später wird diese Datei durch die echte
 * FastAPI-Kommunikation ersetzt.
 */


/*
 * Zum Testen:
 *
 * 'uncertain'
 * → Top-3-Auswahl
 *
 * 'success'
 * → direkter Treffer
 */
const MOCK_RECOGNITION_MODE: string =
  'uncertain';


const wait = (
  milliseconds: number,
) =>
  new Promise<void>((resolve) => {
    setTimeout(
      resolve,
      milliseconds,
    );
  });


export async function recognizeCard(
  imageUri: string,
): Promise<RecognitionResponse> {

  console.log(
    'Mock recognition for:',
    imageUri,
  );


  /*
   * Simuliert:
   *
   * YOLO
   * OpenCV
   * ResNet18
   * Embedding Search
   */

  await wait(2800);


  /* ======================================================
     EINDEUTIGER TREFFER
     ====================================================== */

  if (
    MOCK_RECOGNITION_MODE ===
    'success'
  ) {
    return {
      status: 'success',

      card: {
        card_id: 'swsh8-1',

        name: 'Caterpie',

        set_id: 'swsh8',
        set_name: 'Fusion Strike',

        number: '1',
        rarity: 'Common',

        supertype: 'Pokémon',

        subtypes: [
          'Basic',
        ],

        types: [
          'Grass',
        ],

        artist: 'Mitsuhiro Arita',

        release_date:
          '2021-11-12',

        image_url:
          'https://images.pokemontcg.io/swsh8/1_hires.png',
      },

      recognition: {
        similarity: 0.963,
        margin: 0.087,
      },

      variants: [
        'normal',
        'holo',
        'reverse_holo',
      ],
    };
  }


  /* ======================================================
     UNSICHERER TREFFER
     ====================================================== */

  return {
    status: 'uncertain',

    candidates: [

      {
        card: {
          card_id: 'swsh8-1',

          name: 'Caterpie',

          set_id: 'swsh8',
          set_name:
            'Fusion Strike',

          number: '1',
          rarity: 'Common',

          supertype:
            'Pokémon',

          subtypes: [
            'Basic',
          ],

          types: [
            'Grass',
          ],

          artist:
            'Mitsuhiro Arita',

          release_date:
            '2021-11-12',

          image_url:
            'https://images.pokemontcg.io/swsh8/1_hires.png',
        },

        recognition: {
          similarity: 0.914,
          margin: 0.008,
        },

        variants: [
          'normal',
          'holo',
          'reverse_holo',
        ],
      },


      {
        card: {
          card_id: 'swsh8-2',

          name: 'Metapod',

          set_id: 'swsh8',
          set_name:
            'Fusion Strike',

          number: '2',
          rarity: 'Uncommon',

          supertype:
            'Pokémon',

          subtypes: [
            'Stage 1',
          ],

          types: [
            'Grass',
          ],

          artist:
            'Miki Tanaka',

          release_date:
            '2021-11-12',

          image_url:
            'https://images.pokemontcg.io/swsh8/2_hires.png',
        },

        recognition: {
          similarity: 0.906,
          margin: 0.006,
        },

        variants: [
          'normal',
          'holo',
          'reverse_holo',
        ],
      },


      {
        card: {
          card_id: 'swsh8-3',

          name: 'Butterfree',

          set_id: 'swsh8',
          set_name:
            'Fusion Strike',

          number: '3',
          rarity: 'Rare',

          supertype:
            'Pokémon',

          subtypes: [
            'Stage 2',
          ],

          types: [
            'Grass',
          ],

          artist:
            'Pokémon Card Artist',

          release_date:
            '2021-11-12',

          image_url:
            'https://images.pokemontcg.io/swsh8/3_hires.png',
        },

        recognition: {
          similarity: 0.897,
          margin: 0.005,
        },

        variants: [
          'normal',
          'holo',
          'reverse_holo',
        ],
      },

    ],
  };
}


/* ========================================================
   PREISSERVICE
   ======================================================== */

export async function getCardPrice(
  cardId: string,
  variant: CardVariant,
): Promise<CardPrice> {

  await wait(800);


  const prices:
    Record<
      CardVariant,
      number
    > = {

      normal: 1.29,

      holo: 4.89,

      reverse_holo: 2.79,
    };


  return {
    card_id: cardId,

    variant,

    price:
      prices[variant],

    currency: 'EUR',

    updated_at:
      new Date().toISOString(),
  };
}