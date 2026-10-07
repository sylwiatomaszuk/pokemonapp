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

  /*
   * Das Backend wird später niemals einen lokalen
   * Windows-Pfad wie C:\Users\... zurückgeben.
   *
   * Stattdessen kommt hier eine HTTP-URL hinein.
   */
  image_url?: string | null;
};


export type RecognitionInfo = {
  similarity: number;
  margin: number;
};


export type RecognitionResult = {
  status: 'success';

  card: PokemonCard;

  recognition: RecognitionInfo;

  variants: CardVariant[];
};


export type CardPrice = {
  card_id: string;
  variant: CardVariant;

  price: number;
  currency: 'EUR';

  updated_at: string;
};