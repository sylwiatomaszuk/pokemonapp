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
 * Eindeutiger Treffer.
 */
export type RecognitionResult = {
  status: 'success';

  card: PokemonCard;

  recognition: RecognitionInfo;

  variants: CardVariant[];
};


/*
 * Einzelner Kandidat bei einer
 * unsicheren Erkennung.
 */
export type RecognitionCandidate = {
  card: PokemonCard;

  recognition: RecognitionInfo;

  variants: CardVariant[];
};


/*
 * Mehrere mögliche Treffer.
 */
export type UncertainRecognitionResult = {
  status: 'uncertain';

  candidates: RecognitionCandidate[];
};


/*
 * Das ist die Antwort, die unsere
 * Erkennung insgesamt liefern kann.
 */
export type RecognitionResponse =
  | RecognitionResult
  | UncertainRecognitionResult;


export type CardPrice = {
  card_id: string;
  variant: CardVariant;

  price: number;
  currency: 'EUR';

  updated_at: string;
};