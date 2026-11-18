// mobile/src/config/api.ts

export type RecognitionSource =
  | 'mock'
  | 'api';


export type MockRecognitionMode =
  | 'success'
  | 'uncertain'
  | 'not_found';


const recognitionSourceValue =
  process.env.EXPO_PUBLIC_RECOGNITION_SOURCE
    ?.trim()
    .toLowerCase();


const mockRecognitionModeValue =
  process.env.EXPO_PUBLIC_MOCK_RECOGNITION_MODE
    ?.trim()
    .toLowerCase();


export const recognitionSource:
  RecognitionSource =
    recognitionSourceValue ===
    'api'
      ? 'api'
      : 'mock';


export const mockRecognitionMode:
  MockRecognitionMode =
    mockRecognitionModeValue ===
    'uncertain'
      ? 'uncertain'

      : mockRecognitionModeValue ===
        'not_found'
        ? 'not_found'

        : 'success';


export const apiUrl =
  (
    process.env.EXPO_PUBLIC_API_URL ??
    ''
  )
    .trim()
    .replace(
      /\/+$/,
      '',
    );


export function requireApiUrl() {

  if (
    !apiUrl
  ) {

    throw new Error(
      'EXPO_PUBLIC_API_URL ist nicht gesetzt.',
    );

  }


  return apiUrl;
}