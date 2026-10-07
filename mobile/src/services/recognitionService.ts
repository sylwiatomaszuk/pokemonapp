import {
  CardPrice,
  CardVariant,
  RecognitionResult,
} from '@/types/recognition';


/*
 * ========================================================
 * MOCK-SERVICE
 * ========================================================
 *
 * WICHTIG:
 *
 * Die UI kennt später nur diese Funktionen:
 *
 * recognizeCard(...)
 * getCardPrice(...)
 *
 * Sobald FastAPI fertig ist, ändern wir nur den Inhalt
 * dieser Datei.
 *
 * Die Screens und Komponenten können gleich bleiben.
 */


const wait = (milliseconds: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, milliseconds);
  });


export async function recognizeCard(
  imageUri: string,
): Promise<RecognitionResult> {

  /*
   * Noch wird das Bild nicht wirklich analysiert.
   *
   * Wir behalten imageUri als Parameter, weil später
   * genau dieses Bild an FastAPI geschickt wird.
   */

  console.log(
    'Mock recognition for:',
    imageUri,
  );


  /*
   * Simuliert die Zeit für:
   *
   * YOLO
   * OpenCV
   * ResNet18
   * Similarity Search
   */

  await wait(2800);


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

      release_date: '2021-11-12',

      image_url: null,
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


/*
 * ========================================================
 * PREISSERVICE
 * ========================================================
 */

export async function getCardPrice(
  cardId: string,
  variant: CardVariant,
): Promise<CardPrice> {

  await wait(800);


  /*
   * Nur temporäre Testpreise.
   *
   * Später:
   *
   * FastAPI
   *   ↓
   * Supabase / PriceService
   */

  const prices: Record<CardVariant, number> = {
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