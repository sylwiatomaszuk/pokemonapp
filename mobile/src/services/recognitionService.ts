// mobile/src/services/recognitionService.ts

import {
  Platform,
} from 'react-native';

import {
  fetch as expoFetch,
} from 'expo/fetch';

import {
  File,
} from 'expo-file-system';

import {
  mockRecognitionMode,
  recognitionSource,
  requireApiUrl,
} from '@/config/api';

import {
  CardPrice,
  CardVariant,
  RecognitionResponse,
} from '@/types/recognition';


/*
 * ========================================================
 * HILFSFUNKTIONEN
 * ========================================================
 */

const wait = (
  milliseconds: number,
) =>
  new Promise<void>((resolve) => {

    setTimeout(
      resolve,
      milliseconds,
    );

  });


function getFileName(
  imageUri: string,
) {

  const cleanUri =
    imageUri.split(
      '?',
    )[0];


  const lastPart =
    cleanUri
      .split('/')
      .pop();


  if (
    lastPart &&
    lastPart.includes('.')
  ) {
    return lastPart;
  }


  return 'pokemon-card.jpg';
}


/*
 * ========================================================
 * API-ANTWORT PRÜFEN
 * ========================================================
 */

function isRecognitionResponse(
  value: unknown,
): value is RecognitionResponse {

  if (
    !value ||
    typeof value !==
      'object'
  ) {
    return false;
  }


  const response =
    value as {
      status?: unknown;
    };


  return (
    response.status ===
      'success' ||

    response.status ===
      'uncertain' ||

    response.status ===
      'not_found'
  );
}


/*
 * ========================================================
 * FORM DATA
 * ========================================================
 */

async function createImageFormData(
  imageUri: string,
) {

  const formData =
    new FormData();


  /*
   * ======================================================
   * WEB
   * ======================================================
   *
   * Im Browser funktioniert der normale Blob-Weg.
   */

  if (
    Platform.OS ===
    'web'
  ) {

    const imageResponse =
      await fetch(
        imageUri,
      );


    if (
      !imageResponse.ok
    ) {

      throw new Error(
        'Das ausgewählte Bild konnte nicht gelesen werden.',
      );

    }


    const imageBlob =
      await imageResponse.blob();


    formData.append(
      'file',
      imageBlob,
      getFileName(
        imageUri,
      ),
    );


    return formData;

  }


  /*
   * ======================================================
   * ANDROID / IOS
   * ======================================================
   *
   * Expo SDK 58 verwendet eine WinterCG-kompatible
   * Fetch-/FormData-Implementierung.
   *
   * Deshalb KEIN altes React-Native-Objekt:
   *
   * {
   *   uri,
   *   name,
   *   type
   * }
   *
   * Stattdessen erzeugen wir eine echte Expo-File-
   * Instanz. File implementiert Blob und kann direkt
   * in FormData verwendet werden.
   */

  const imageFile =
    new File(
      imageUri,
    );


  formData.append(
    'file',
    imageFile,
  );


  return formData;
}


/*
 * ========================================================
 * ECHTE FASTAPI-ERKENNUNG
 * ========================================================
 */

async function recognizeCardViaApi(
  imageUri: string,
): Promise<RecognitionResponse> {

  const baseUrl =
    requireApiUrl();


  console.log(
    'Recognition API:',
    `${baseUrl}/api/recognize`,
  );


  console.log(
    'Uploading image:',
    imageUri,
  );


  const formData =
    await createImageFormData(
      imageUri,
    );


  /*
   * expoFetch verwenden wir bewusst.
   *
   * Damit arbeiten File + FormData auf Expo 58
   * über dieselbe moderne Implementierung.
   */

  const response =
    await expoFetch(
      `${baseUrl}/api/recognize`,
      {
        method:
          'POST',

        body:
          formData,
      },
    );


  const responseText =
    await response.text();


  if (
    !response.ok
  ) {

    throw new Error(
      `Recognition API Fehler ${response.status}: ${responseText}`,
    );

  }


  let responseData:
    unknown;


  try {

    responseData =
      JSON.parse(
        responseText,
      );

  } catch {

    throw new Error(
      'Die Recognition API hat keine gültige JSON-Antwort geliefert.',
    );

  }


  if (
    !isRecognitionResponse(
      responseData,
    )
  ) {

    throw new Error(
      'Die Recognition API hat ein unbekanntes Antwortformat geliefert.',
    );

  }


  console.log(
    'Recognition API response:',
    responseData,
  );


  return responseData;
}


/*
 * ========================================================
 * MOCK-ERKENNUNG
 * ========================================================
 */

async function recognizeCardWithMock(
  imageUri: string,
): Promise<RecognitionResponse> {

  console.log(
    'Mock recognition for:',
    imageUri,
  );


  console.log(
    'Mock recognition mode:',
    mockRecognitionMode,
  );


  await wait(
    2800,
  );


  /* ======================================================
     KEIN TREFFER
     ====================================================== */

  if (
    mockRecognitionMode ===
    'not_found'
  ) {

    return {
      status:
        'not_found',

      reason:
        'no_matching_card',

      message:
        'Für dieses Bild wurde keine ausreichend passende Referenzkarte gefunden.',
    };

  }


  /* ======================================================
     EINDEUTIGER TREFFER
     ====================================================== */

  if (
    mockRecognitionMode ===
    'success'
  ) {

    return {
      status:
        'success',

      card: {

        card_id:
          'swsh8-1',

        name:
          'Caterpie',

        set_id:
          'swsh8',

        set_name:
          'Fusion Strike',

        number:
          '1',

        rarity:
          'Common',

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

        similarity:
          0.963,

        margin:
          0.087,

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
    status:
      'uncertain',

    candidates: [

      {
        card: {

          card_id:
            'swsh8-1',

          name:
            'Caterpie',

          set_id:
            'swsh8',

          set_name:
            'Fusion Strike',

          number:
            '1',

          rarity:
            'Common',

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

          similarity:
            0.914,

          margin:
            0.008,

        },

        variants: [
          'normal',
          'holo',
          'reverse_holo',
        ],
      },


      {
        card: {

          card_id:
            'swsh8-2',

          name:
            'Metapod',

          set_id:
            'swsh8',

          set_name:
            'Fusion Strike',

          number:
            '2',

          rarity:
            'Uncommon',

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

          similarity:
            0.906,

          margin:
            0.006,

        },

        variants: [
          'normal',
          'holo',
          'reverse_holo',
        ],
      },


      {
        card: {

          card_id:
            'swsh8-3',

          name:
            'Butterfree',

          set_id:
            'swsh8',

          set_name:
            'Fusion Strike',

          number:
            '3',

          rarity:
            'Rare',

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

          similarity:
            0.897,

          margin:
            0.005,

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


/*
 * ========================================================
 * ÖFFENTLICHE ERKENNUNGSFUNKTION
 * ========================================================
 */

export async function recognizeCard(
  imageUri: string,
): Promise<RecognitionResponse> {

  console.log(
    'Recognition source:',
    recognitionSource,
  );


  if (
    recognitionSource ===
    'api'
  ) {

    return recognizeCardViaApi(
      imageUri,
    );

  }


  return recognizeCardWithMock(
    imageUri,
  );
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

  await wait(
    800,
  );


  const prices:
    Record<
      CardVariant,
      number
    > = {

      normal:
        1.29,

      holo:
        4.89,

      reverse_holo:
        2.79,
    };


  return {

    card_id:
      cardId,

    variant,

    price:
      prices[
        variant
      ],

    currency:
      'EUR',

    updated_at:
      new Date()
        .toISOString(),

  };

}