// mobile/src/types/recognition.ts

export type CardVariant =
  | 'normal'
  | 'holo'
  | 'reverse_holo';


export type PokemonCard = {
  card_id: string;
  name: string;

  set_id: string;
  set_name: string;

  number: string;
  rarity: string;

  supertype: string;

  subtypes: string[];
  types: string[];

  artist: string;
  release_date: string;

  image_url?: string | null;
};


export type RecognitionInfo = {
  similarity: number;
  margin: number;
};


/*
 * ========================================================
 * EINDEUTIGER TREFFER
 * ========================================================
 */

export type RecognitionResult = {
  status: 'success';

  card: PokemonCard;

  recognition: RecognitionInfo;

  variants: CardVariant[];
};


/*
 * ========================================================
 * UNSICHERER TREFFER
 * ========================================================
 */

export type RecognitionCandidate = {
  card: PokemonCard;

  recognition: RecognitionInfo;

  variants: CardVariant[];
};


export type UncertainRecognitionResult = {
  status: 'uncertain';

  candidates: RecognitionCandidate[];
};


/*
 * ========================================================
 * KEIN TREFFER
 * ========================================================
 */

export type NotFoundReason =
  | 'no_card_detected'
  | 'no_matching_card';


export type NotFoundRecognitionResult = {
  status: 'not_found';

  reason?: NotFoundReason;

  message?: string;
};


/*
 * ========================================================
 * GESAMTE ERKENNUNGSANTWORT
 * ========================================================
 */

export type RecognitionResponse =
  | RecognitionResult
  | UncertainRecognitionResult
  | NotFoundRecognitionResult;


/*
 * ========================================================
 * PREIS
 * ========================================================
 */

export type CardPrice = {
  card_id: string;

  variant: CardVariant;

  price: number;

  currency: 'EUR';

  updated_at: string;
};