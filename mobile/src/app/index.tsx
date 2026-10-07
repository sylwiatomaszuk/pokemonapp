import { useState } from 'react';

import {
  Alert,
  Image,
  Linking,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from 'react-native';

import * as ImagePicker from 'expo-image-picker';

import { CardResult } from '@/components/CardResult';
import { PsyduckMascot } from '@/components/PsyduckMascot';

import {
  colors,
  radius,
  shadow,
  spacing,
} from '@/constants/theme';

import {
  recognizeCard,
} from '@/services/recognitionService';

import {
  RecognitionResult,
} from '@/types/recognition';


export default function HomeScreen() {
  const { width } = useWindowDimensions();

  const isWideScreen = width >= 800;


  /* ======================================================
     STATES
     ====================================================== */

  const [selectedImage, setSelectedImage] =
    useState<string | null>(null);

  const [imageSource, setImageSource] =
    useState<'camera' | 'gallery' | null>(null);

  const [
    isAnalyzing,
    setIsAnalyzing,
  ] = useState(false);

  const [
    recognitionResult,
    setRecognitionResult,
  ] = useState<RecognitionResult | null>(
    null,
  );

  const [
    analysisStep,
    setAnalysisStep,
  ] = useState(0);


  /* ======================================================
     KAMERA
     ====================================================== */

  const openCamera = async () => {
    try {
      /*
       * Auf Android/iOS fragen wir explizit
       * nach der Kameraberechtigung.
       */
      if (Platform.OS !== 'web') {
        const permission =
          await ImagePicker.requestCameraPermissionsAsync();

        if (!permission.granted) {
          if (!permission.canAskAgain) {
            Alert.alert(
              'Kamerazugriff deaktiviert',
              'Bitte erlaube den Kamerazugriff in den Einstellungen, damit du Karten fotografieren kannst.',
              [
                {
                  text: 'Abbrechen',
                  style: 'cancel',
                },
                {
                  text: 'Einstellungen öffnen',
                  onPress: () => {
                    Linking.openSettings();
                  },
                },
              ],
            );
          } else {
            Alert.alert(
              'Kamerazugriff benötigt',
              'Ohne Kamerazugriff können wir keine Karte fotografieren.',
            );
          }

          return;
        }
      }


      const result =
        await ImagePicker.launchCameraAsync({
          mediaTypes: ['images'],

          /*
           * Kein Crop.
           *
           * Später soll YOLO die Karte selbst
           * im vollständigen Foto finden.
           */
          allowsEditing: false,

          quality: 1,
        });


      if (result.canceled) {
        return;
      }


      const image = result.assets[0];

      if (!image?.uri) {
        Alert.alert(
          'Foto konnte nicht geladen werden',
          'Bitte versuche es noch einmal.',
        );

        return;
      }


      setSelectedImage(image.uri);
      setImageSource('camera');

      setRecognitionResult(null);
      setAnalysisStep(0);
    } catch (error) {
      console.error(
        'Fehler beim Öffnen der Kamera:',
        error,
      );

      Alert.alert(
        'Kamera konnte nicht geöffnet werden',
        'Bitte versuche es erneut.',
      );
    }
  };


  /* ======================================================
     GALERIE
     ====================================================== */

  const openGallery = async () => {
    try {
      const result =
        await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ['images'],

          /*
           * Auch hier kein Crop.
           *
           * Das Originalbild soll später
           * an unsere KI-Pipeline gehen.
           */
          allowsEditing: false,

          quality: 1,
        });


      if (result.canceled) {
        return;
      }


      const image = result.assets[0];

      if (!image?.uri) {
        Alert.alert(
          'Bild konnte nicht geladen werden',
          'Bitte wähle ein anderes Bild aus.',
        );

        return;
      }


      setSelectedImage(image.uri);
      setImageSource('gallery');

      setRecognitionResult(null);
      setAnalysisStep(0);
    } catch (error) {
      console.error(
        'Fehler beim Öffnen der Galerie:',
        error,
      );

      Alert.alert(
        'Galerie konnte nicht geöffnet werden',
        'Bitte versuche es erneut.',
      );
    }
  };


  /* ======================================================
     AUSGEWÄHLTES BILD VERWERFEN
     ====================================================== */

  const resetImage = () => {
    setSelectedImage(null);
    setImageSource(null);

    setRecognitionResult(null);
    setAnalysisStep(0);
    setIsAnalyzing(false);
  };


  /* ======================================================
     MOCK-KARTENERKENNUNG
     ====================================================== */

  const startRecognition = async () => {
    if (!selectedImage) {
      return;
    }


    let stepOne:
      ReturnType<typeof setTimeout> | undefined;

    let stepTwo:
      ReturnType<typeof setTimeout> | undefined;


    try {
      setIsAnalyzing(true);

      setRecognitionResult(null);

      setAnalysisStep(0);


      /*
       * Diese Schritte simulieren momentan
       * den Ablauf unserer späteren Pipeline.
       *
       * 1. YOLO
       * 2. OpenCV
       * 3. ResNet / Referenzvergleich
       */

      stepOne = setTimeout(
        () => {
          setAnalysisStep(1);
        },
        650,
      );


      stepTwo = setTimeout(
        () => {
          setAnalysisStep(2);
        },
        1450,
      );


      /*
       * Aktuell kommt das Ergebnis noch
       * aus recognitionService.ts als Mock.
       *
       * Später wird dort FastAPI aufgerufen.
       */

      const result =
        await recognizeCard(
          selectedImage,
        );


      setAnalysisStep(3);

      setRecognitionResult(
        result,
      );
    } catch (error) {
      console.error(
        'Recognition failed:',
        error,
      );


      Alert.alert(
        'Karte konnte nicht erkannt werden',
        'Bitte versuche es mit einem anderen Bild.',
      );
    } finally {
      if (stepOne) {
        clearTimeout(stepOne);
      }

      if (stepTwo) {
        clearTimeout(stepTwo);
      }

      setIsAnalyzing(false);
    }
  };


  return (
    <SafeAreaView style={styles.safeArea}>

      {/* ==================================================
          HINTERGRUND
          ================================================== */}

      <View
        pointerEvents="none"
        style={styles.background}
      >
        <View
          style={[
            styles.backgroundBubble,
            styles.bubblePink,
          ]}
        />

        <View
          style={[
            styles.backgroundBubble,
            styles.bubbleLavender,
          ]}
        />

        <View
          style={[
            styles.backgroundBubble,
            styles.bubbleMint,
          ]}
        />
      </View>


      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,

          isWideScreen &&
            styles.scrollContentWide,
        ]}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >

        {/* ==================================================
            HEADER
            ================================================== */}

        <View style={styles.header}>

          <View style={styles.brand}>

            <View style={styles.brandIcon}>
              <Text style={styles.brandIconText}>
                ✦
              </Text>
            </View>

            <Text style={styles.brandText}>
              Card Scanner
            </Text>

          </View>


          {isWideScreen && (
            <View style={styles.projectBadge}>

              <Text style={styles.projectBadgeText}>
                Studienprojekt
              </Text>

            </View>
          )}

        </View>


        {/* ==================================================
            HERO
            ================================================== */}

        <View style={styles.hero}>

          <Text style={styles.eyebrow}>
            POKÉMON-KARTENERKENNUNG
          </Text>

          <Text style={styles.title}>
            Welche Karte hast du?
          </Text>

          <Text style={styles.description}>
            Fotografiere deine Karte oder wähle
            ein Bild aus. Wir suchen die passende
            Karte und zeigen dir anschließend
            ihre wichtigsten Informationen.
          </Text>


          <PsyduckMascot
            message={
              isAnalyzing
                ? 'Hmm … einen Moment. Ich vergleiche deine Karte gerade.'
                : recognitionResult
                  ? 'Ich glaube, die habe ich gefunden!'
                  : selectedImage
                    ? 'Sieht gut aus! Wenn die ganze Karte zu sehen ist, können wir loslegen.'
                    : 'Zeig mir deine Karte – ich schau sie mir an!'
            }
          />

        </View>


        {/* ==================================================
            SCANNER
            ================================================== */}

        {!recognitionResult && (
          <View style={styles.scannerCard}>

            <View style={styles.sectionHeader}>

              <Text style={styles.stepLabel}>
                SCHRITT 1
              </Text>

              <Text style={styles.sectionTitle}>
                {isAnalyzing
                  ? 'Karte analysieren'
                  : selectedImage
                    ? 'Karte prüfen'
                    : 'Karte hinzufügen'}
              </Text>

            </View>


            {/* ==============================================
                KEIN BILD AUSGEWÄHLT
                ============================================== */}

            {!selectedImage && !isAnalyzing && (
              <>
                <View style={styles.scannerArea}>

                  <View style={styles.scannerIcon}>
                    <Text style={styles.scannerIconText}>
                      ✦
                    </Text>
                  </View>

                  <Text style={styles.scannerTitle}>
                    Bereit zum Scannen
                  </Text>

                  <Text style={styles.scannerDescription}>
                    Achte darauf, dass die gesamte
                    Karte gut sichtbar und möglichst
                    scharf ist.
                  </Text>

                </View>


                <View
                  style={[
                    styles.actions,

                    isWideScreen &&
                      styles.actionsWide,
                  ]}
                >

                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Kamera öffnen"

                    onPress={openCamera}

                    style={({ pressed }) => [
                      styles.button,
                      styles.primaryButton,

                      pressed &&
                        styles.buttonPressed,
                    ]}
                  >

                    <Text style={styles.primaryButtonIcon}>
                      📷
                    </Text>

                    <Text style={styles.primaryButtonText}>
                      Kamera öffnen
                    </Text>

                  </Pressable>


                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Bild aus Galerie auswählen"

                    onPress={openGallery}

                    style={({ pressed }) => [
                      styles.button,
                      styles.secondaryButton,

                      pressed &&
                        styles.buttonPressed,
                    ]}
                  >

                    <Text style={styles.secondaryButtonIcon}>
                      ♡
                    </Text>

                    <Text style={styles.secondaryButtonText}>
                      Bild auswählen
                    </Text>

                  </Pressable>

                </View>
              </>
            )}


            {/* ==============================================
                BILD AUSGEWÄHLT
                ============================================== */}

            {selectedImage &&
              !isAnalyzing &&
              !recognitionResult && (

                <View>

                  <View style={styles.previewFrame}>

                    <Image
                      source={{
                        uri: selectedImage,
                      }}

                      style={styles.previewImage}

                      resizeMode="contain"

                      accessibilityLabel="Vorschau der ausgewählten Pokémon-Karte"
                    />

                  </View>


                  <View style={styles.previewInfo}>

                    <View style={styles.previewStatus}>

                      <View style={styles.previewStatusDot} />

                      <Text style={styles.previewStatusText}>
                        {imageSource === 'camera'
                          ? 'Foto aufgenommen'
                          : 'Bild ausgewählt'}
                      </Text>

                    </View>


                    <Text style={styles.previewTitle}>
                      Sieht die Karte gut aus?
                    </Text>

                    <Text style={styles.previewDescription}>
                      Die gesamte Karte sollte sichtbar
                      und möglichst scharf sein.
                      Hintergrund und Perspektive sind
                      kein Problem – darum kümmert sich
                      später unsere Erkennung.
                    </Text>

                  </View>


                  <View style={styles.previewActions}>

                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel="Karte erkennen"

                      onPress={startRecognition}

                      style={({ pressed }) => [
                        styles.button,
                        styles.primaryButton,
                        styles.fullWidthButton,

                        pressed &&
                          styles.buttonPressed,
                      ]}
                    >

                      <Text style={styles.primaryButtonText}>
                        Karte erkennen
                      </Text>

                      <Text style={styles.forwardIcon}>
                        →
                      </Text>

                    </Pressable>


                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel="Anderes Bild auswählen"

                      onPress={resetImage}

                      style={({ pressed }) => [
                        styles.button,
                        styles.changeImageButton,
                        styles.fullWidthButton,

                        pressed &&
                          styles.buttonPressed,
                      ]}
                    >

                      <Text style={styles.changeImageButtonText}>
                        Anderes Bild wählen
                      </Text>

                    </Pressable>

                  </View>

                </View>
              )}


            {/* ==============================================
                ANALYSE
                ============================================== */}

            {isAnalyzing && (
              <View style={styles.analysisContainer}>

                <View style={styles.loadingDots}>

                  <View
                    style={[
                      styles.loadingDot,
                      styles.loadingDotPurple,
                    ]}
                  />

                  <View
                    style={[
                      styles.loadingDot,
                      styles.loadingDotPink,
                    ]}
                  />

                  <View
                    style={[
                      styles.loadingDot,
                      styles.loadingDotMint,
                    ]}
                  />

                </View>


                <Text style={styles.analysisTitle}>
                  Wir schauen uns deine Karte an …
                </Text>

                <Text style={styles.analysisDescription}>
                  Das dauert normalerweise nur
                  einen Augenblick.
                </Text>


                <View style={styles.analysisSteps}>

                  <View
                    style={[
                      styles.analysisStep,

                      analysisStep === 0 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >= 0 &&
                          styles.analysisDotActive,

                        analysisStep > 0 &&
                          styles.analysisDotComplete,
                      ]}
                    />

                    <Text style={styles.analysisStepText}>
                      Karte finden
                    </Text>

                  </View>


                  <View
                    style={[
                      styles.analysisStep,

                      analysisStep === 1 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >= 1 &&
                          styles.analysisDotActive,

                        analysisStep > 1 &&
                          styles.analysisDotComplete,
                      ]}
                    />

                    <Text style={styles.analysisStepText}>
                      Bild aufbereiten
                    </Text>

                  </View>


                  <View
                    style={[
                      styles.analysisStep,

                      analysisStep >= 2 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >= 2 &&
                          styles.analysisDotActive,
                      ]}
                    />

                    <Text style={styles.analysisStepText}>
                      Referenzkarten vergleichen
                    </Text>

                  </View>

                </View>

              </View>
            )}

          </View>
        )}


        {/* ==================================================
            ERGEBNIS
            ================================================== */}

        {recognitionResult &&
          selectedImage && (

            <CardResult
              result={recognitionResult}

              originalImageUri={selectedImage}

              onReset={resetImage}
            />

          )}


        {/* ==================================================
            FOOTER
            ================================================== */}

        <Text style={styles.footer}>
          Studienprojekt zur optischen
          Pokémon-Kartenerkennung
        </Text>

      </ScrollView>

    </SafeAreaView>
  );
}


const styles = StyleSheet.create({

  /* ======================================================
     BASIS
     ====================================================== */

  safeArea: {
    flex: 1,

    backgroundColor:
      colors.background,
  },


  /* ======================================================
     HINTERGRUND
     ====================================================== */

  background: {
    position: 'absolute',

    top: 0,
    right: 0,
    bottom: 0,
    left: 0,

    overflow: 'hidden',
  },

  backgroundBubble: {
    position: 'absolute',

    borderRadius: radius.pill,

    opacity: 0.72,
  },

  bubblePink: {
    width: 290,
    height: 290,

    top: -145,
    right: -115,

    backgroundColor:
      colors.pink,
  },

  bubbleLavender: {
    width: 240,
    height: 240,

    left: -150,
    top: '42%',

    backgroundColor:
      colors.lavender,
  },

  bubbleMint: {
    width: 230,
    height: 230,

    right: -135,
    bottom: -110,

    backgroundColor:
      colors.mint,
  },


  /* ======================================================
     LAYOUT
     ====================================================== */

  scrollContent: {
    width: '100%',

    paddingHorizontal:
      spacing.md,

    paddingBottom:
      spacing.xl,

    alignSelf: 'center',
  },

  scrollContentWide: {
    maxWidth: 1000,
  },


  /* ======================================================
     HEADER
     ====================================================== */

  header: {
    minHeight: 72,

    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',

    paddingTop: spacing.sm,
  },

  brand: {
    flexDirection: 'row',
    alignItems: 'center',

    gap: 10,
  },

  brandIcon: {
    width: 42,
    height: 42,

    alignItems: 'center',
    justifyContent: 'center',

    backgroundColor:
      colors.pink,

    borderTopLeftRadius: 22,
    borderTopRightRadius: 18,
    borderBottomLeftRadius: 17,
    borderBottomRightRadius: 24,

    ...shadow.button,
  },

  brandIconText: {
    color: colors.text,

    fontSize: 18,
    fontWeight: '800',
  },

  brandText: {
    color: colors.text,

    fontSize: 17,
    fontWeight: '800',

    letterSpacing: -0.4,
  },

  projectBadge: {
    paddingHorizontal: 15,
    paddingVertical: 8,

    borderRadius: radius.pill,

    backgroundColor:
      colors.whiteTransparent,

    borderWidth: 1,
    borderColor: colors.border,
  },

  projectBadgeText: {
    color: colors.textSoft,

    fontSize: 12,
    fontWeight: '700',
  },


  /* ======================================================
     HERO
     ====================================================== */

  hero: {
    width: '100%',
    maxWidth: 680,

    alignSelf: 'center',

    alignItems: 'center',

    paddingTop:
      spacing.xl,

    paddingBottom:
      spacing.xl,
  },

  eyebrow: {
    color:
      colors.lavenderStrong,

    fontSize: 12,
    fontWeight: '800',

    letterSpacing: 1.2,

    textAlign: 'center',
  },

  title: {
    maxWidth: 650,

    marginTop: 7,

    color: colors.text,

    fontSize: 44,
    lineHeight: 47,

    fontWeight: '800',

    letterSpacing: -1.8,

    textAlign: 'center',
  },

  description: {
    maxWidth: 550,

    marginTop: 17,

    color:
      colors.textSoft,

    fontSize: 16,
    lineHeight: 24,

    textAlign: 'center',
  },


  /* ======================================================
     SCANNER CARD
     ====================================================== */

  scannerCard: {
    width: '100%',
    maxWidth: 820,

    alignSelf: 'center',

    padding: 20,

    backgroundColor:
      'rgba(255,255,255,0.91)',

    borderWidth: 1.5,
    borderColor:
      'rgba(255,255,255,0.95)',

    borderTopLeftRadius: 40,
    borderTopRightRadius: 48,
    borderBottomLeftRadius: 46,
    borderBottomRightRadius: 36,

    ...shadow.card,
  },

  sectionHeader: {
    marginBottom:
      spacing.md,
  },

  stepLabel: {
    color:
      colors.lavenderStrong,

    fontSize: 11,
    fontWeight: '800',

    letterSpacing: 1.1,

    marginBottom: 3,
  },

  sectionTitle: {
    color:
      colors.text,

    fontSize: 26,
    lineHeight: 31,

    fontWeight: '800',

    letterSpacing: -0.9,
  },


  /* ======================================================
     SCANNER START
     ====================================================== */

  scannerArea: {
    minHeight: 275,

    alignItems: 'center',
    justifyContent: 'center',

    padding:
      spacing.lg,

    borderWidth: 2,
    borderStyle: 'dashed',

    borderColor:
      'rgba(130,98,207,0.28)',

    backgroundColor:
      'rgba(233,214,255,0.48)',

    borderTopLeftRadius: 36,
    borderTopRightRadius: 46,
    borderBottomLeftRadius: 48,
    borderBottomRightRadius: 34,
  },

  scannerIcon: {
    width: 72,
    height: 72,

    alignItems: 'center',
    justifyContent: 'center',

    marginBottom: 14,

    backgroundColor:
      colors.pink,

    borderTopLeftRadius: 38,
    borderTopRightRadius: 31,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 42,

    ...shadow.button,
  },

  scannerIconText: {
    color:
      colors.text,

    fontSize: 26,
  },

  scannerTitle: {
    color:
      colors.text,

    fontSize: 21,
    fontWeight: '800',

    textAlign: 'center',
  },

  scannerDescription: {
    maxWidth: 390,

    marginTop: 5,

    color:
      colors.textSoft,

    fontSize: 14,
    lineHeight: 21,

    textAlign: 'center',
  },


  /* ======================================================
     BUTTONS
     ====================================================== */

  actions: {
    width: '100%',

    gap: 10,

    marginTop: 16,
  },

  actionsWide: {
    flexDirection: 'row',
    justifyContent: 'center',
  },

  button: {
    minHeight: 54,

    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',

    gap: 8,

    paddingHorizontal: 22,

    borderTopLeftRadius: 27,
    borderTopRightRadius: 32,
    borderBottomLeftRadius: 31,
    borderBottomRightRadius: 24,
  },

  primaryButton: {
    backgroundColor:
      colors.lavenderStrong,

    ...shadow.button,
  },

  secondaryButton: {
    backgroundColor:
      colors.pink,

    ...shadow.button,
  },

  changeImageButton: {
    backgroundColor:
      'rgba(255,255,255,0.82)',

    borderWidth: 1,
    borderColor:
      colors.border,
  },

  fullWidthButton: {
    width: '100%',
  },

  buttonPressed: {
    opacity: 0.82,

    transform: [
      {
        scale: 0.985,
      },
    ],
  },

  primaryButtonIcon: {
    fontSize: 17,
  },

  primaryButtonText: {
    color: '#FFFFFF',

    fontSize: 15,
    fontWeight: '800',
  },

  secondaryButtonIcon: {
    color:
      colors.text,

    fontSize: 18,
  },

  secondaryButtonText: {
    color:
      colors.text,

    fontSize: 15,
    fontWeight: '800',
  },

  changeImageButtonText: {
    color:
      colors.textSoft,

    fontSize: 14,
    fontWeight: '700',
  },

  forwardIcon: {
    color: '#FFFFFF',

    fontSize: 19,
    fontWeight: '800',
  },


  /* ======================================================
     BILDVORSCHAU
     ====================================================== */

  previewFrame: {
    width: '100%',

    minHeight: 330,
    maxHeight: 520,

    padding: 14,

    alignItems: 'center',
    justifyContent: 'center',

    backgroundColor:
      'rgba(223,204,255,0.62)',

    borderTopLeftRadius: 36,
    borderTopRightRadius: 46,
    borderBottomLeftRadius: 47,
    borderBottomRightRadius: 34,

    overflow: 'hidden',
  },

  previewImage: {
    width: '100%',
    height: 440,

    borderTopLeftRadius: 25,
    borderTopRightRadius: 29,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 22,

    backgroundColor:
      'rgba(255,255,255,0.62)',
  },

  previewInfo: {
    marginTop: 18,

    alignItems: 'center',
  },

  previewStatus: {
    flexDirection: 'row',
    alignItems: 'center',

    gap: 7,

    paddingHorizontal: 12,
    paddingVertical: 7,

    marginBottom: 13,

    borderRadius:
      radius.pill,

    backgroundColor:
      colors.mint,
  },

  previewStatusDot: {
    width: 8,
    height: 8,

    borderRadius:
      radius.pill,

    backgroundColor:
      colors.success,
  },

  previewStatusText: {
    color:
      colors.success,

    fontSize: 12,
    fontWeight: '800',
  },

  previewTitle: {
    color:
      colors.text,

    fontSize: 22,
    fontWeight: '800',

    textAlign: 'center',
  },

  previewDescription: {
    maxWidth: 520,

    marginTop: 7,

    color:
      colors.textSoft,

    fontSize: 14,
    lineHeight: 21,

    textAlign: 'center',
  },

  previewActions: {
    width: '100%',

    gap: 10,

    marginTop: 20,
  },


  /* ======================================================
     ANALYSE
     ====================================================== */

  analysisContainer: {
    minHeight: 330,

    alignItems: 'center',
    justifyContent: 'center',

    paddingVertical: 24,
  },

  loadingDots: {
    flexDirection: 'row',

    gap: 9,

    marginBottom: 20,
  },

  loadingDot: {
    width: 15,
    height: 15,

    borderRadius:
      radius.pill,
  },

  loadingDotPurple: {
    backgroundColor:
      colors.lavenderStrong,
  },

  loadingDotPink: {
    backgroundColor:
      colors.pinkStrong,
  },

  loadingDotMint: {
    backgroundColor:
      colors.mintStrong,
  },

  analysisTitle: {
    color:
      colors.text,

    fontSize: 22,
    fontWeight: '800',

    textAlign: 'center',
  },

  analysisDescription: {
    marginTop: 5,

    color:
      colors.textSoft,

    fontSize: 14,

    textAlign: 'center',
  },

  analysisSteps: {
    width: '100%',
    maxWidth: 460,

    gap: 9,

    marginTop: 24,
  },

  analysisStep: {
    minHeight: 50,

    flexDirection: 'row',
    alignItems: 'center',

    gap: 11,

    paddingHorizontal: 16,

    backgroundColor:
      'rgba(255,255,255,0.75)',

    borderRadius: 20,

    borderWidth: 1,

    borderColor:
      colors.border,
  },

  analysisStepActive: {
    backgroundColor:
      'rgba(223,204,255,0.72)',
  },

  analysisDot: {
    width: 11,
    height: 11,

    borderRadius:
      radius.pill,

    backgroundColor:
      '#D8D1DD',
  },

  analysisDotActive: {
    backgroundColor:
      colors.lavenderStrong,
  },

  analysisDotComplete: {
    backgroundColor:
      colors.success,
  },

  analysisStepText: {
    color:
      colors.textSoft,

    fontSize: 13,
    fontWeight: '700',
  },


  /* ======================================================
     FOOTER
     ====================================================== */

  footer: {
    marginTop:
      spacing.xl,

    color:
      colors.textFaint,

    fontSize: 12,

    textAlign: 'center',
  },

});