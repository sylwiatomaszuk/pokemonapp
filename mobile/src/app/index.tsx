// mobile/src/app/index.tsx

import {
  useEffect,
  useRef,
  useState,
} from 'react';

import {
  ActivityIndicator,
  Alert,
  Image,
  Linking,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from 'react-native';

import type {
  ScrollViewInstance,
} from 'react-native';

import {
  SafeAreaView,
} from 'react-native-safe-area-context';

import {
  CameraView,
  useCameraPermissions,
} from 'expo-camera';

import * as ImagePicker from 'expo-image-picker';

import {
  CandidateSelection,
} from '@/components/CandidateSelection';

import {
  CardResult,
} from '@/components/CardResult';

import {
  NotFoundResult,
} from '@/components/NotFoundResult';

import {
  PsyduckMascot,
} from '@/components/PsyduckMascot';

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
  RecognitionCandidate,
  RecognitionResponse,
} from '@/types/recognition';


export default function HomeScreen() {

  const { width } =
    useWindowDimensions();

  const isWideScreen =
    width >= 800;

  const isMobile =
    width < 600;


  /* ======================================================
     SCROLL
     ====================================================== */

  const scrollViewRef =
    useRef<ScrollViewInstance>(
      null,
    );


  /* ======================================================
     BILD / ERKENNUNG
     ====================================================== */

  const [
    selectedImage,
    setSelectedImage,
  ] =
    useState<string | null>(
      null,
    );


  const [
    imageSource,
    setImageSource,
  ] =
    useState<
      'camera' |
      'gallery' |
      null
    >(
      null,
    );


  const [
    isAnalyzing,
    setIsAnalyzing,
  ] =
    useState(
      false,
    );


  const [
    recognitionResult,
    setRecognitionResult,
  ] =
    useState<
      RecognitionResponse |
      null
    >(
      null,
    );


  const [
    analysisStep,
    setAnalysisStep,
  ] =
    useState(
      0,
    );


  /* ======================================================
     IN-APP-KAMERA
     ====================================================== */

  const [
    cameraVisible,
    setCameraVisible,
  ] =
    useState(
      false,
    );


  const [
    cameraReady,
    setCameraReady,
  ] =
    useState(
      false,
    );


  const [
    cameraBusy,
    setCameraBusy,
  ] =
    useState(
      false,
    );


  const [
    cameraPermission,
    requestCameraPermission,
  ] =
    useCameraPermissions();


  const cameraRef =
    useRef<CameraView | null>(
      null,
    );


  /* ======================================================
     AKTUELLER SCREEN
     ====================================================== */

  const currentScreen =
    recognitionResult?.status ===
    'uncertain'
      ? 'uncertain'

      : recognitionResult?.status ===
        'success'
        ? 'success'

        : recognitionResult?.status ===
          'not_found'
          ? 'not_found'

          : isAnalyzing
            ? 'analyzing'

            : selectedImage
              ? 'preview'

              : 'start';


  /* ======================================================
     BEI SCREENWECHSEL NACH OBEN
     ====================================================== */

  useEffect(
    () => {

      const frame =
        requestAnimationFrame(
          () => {

            scrollViewRef
              .current
              ?.scrollTo({
                y: 0,
                animated: false,
              });

          },
        );


      return () => {

        cancelAnimationFrame(
          frame,
        );

      };

    },
    [
      currentScreen,
    ],
  );


  /* ======================================================
     KAMERA ÖFFNEN
     ====================================================== */

  const openCamera =
    async () => {

      try {

        let granted =
          cameraPermission
            ?.granted ??
          false;


        if (
          !granted
        ) {

          const permission =
            await requestCameraPermission();


          granted =
            permission.granted;


          if (
            !granted
          ) {

            if (
              !permission
                .canAskAgain
            ) {

              Alert.alert(
                'Kamerazugriff deaktiviert',

                'Bitte erlaube den Kamerazugriff in den Einstellungen, damit du Karten fotografieren kannst.',

                [
                  {
                    text:
                      'Abbrechen',

                    style:
                      'cancel',
                  },

                  {
                    text:
                      'Einstellungen öffnen',

                    onPress:
                      () => {

                        Linking
                          .openSettings();

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


        setCameraReady(
          false,
        );


        setCameraBusy(
          false,
        );


        setCameraVisible(
          true,
        );

      } catch (error) {

        console.error(
          'Kamera konnte nicht geöffnet werden:',
          error,
        );


        Alert.alert(
          'Kamera konnte nicht geöffnet werden',

          'Bitte versuche es erneut.',
        );

      }

    };


  /* ======================================================
     FOTO MIT IN-APP-KAMERA AUFNEHMEN
     ====================================================== */

  const takePhoto =
    async () => {

      if (
        !cameraRef.current ||
        !cameraReady ||
        cameraBusy
      ) {
        return;
      }


      try {

        setCameraBusy(
          true,
        );


        const picture =
          await cameraRef
            .current
            .takePictureAsync({

              quality:
                1,

              skipProcessing:
                false,

              shutterSound:
                true,

            });


        if (
          !picture?.uri
        ) {

          throw new Error(
            'Kein Kamerabild erhalten.',
          );

        }


        setSelectedImage(
          picture.uri,
        );


        setImageSource(
          'camera',
        );


        setRecognitionResult(
          null,
        );


        setAnalysisStep(
          0,
        );


        setCameraVisible(
          false,
        );


        setCameraReady(
          false,
        );

      } catch (error) {

        console.error(
          'Foto konnte nicht aufgenommen werden:',
          error,
        );


        Alert.alert(
          'Foto konnte nicht aufgenommen werden',

          'Bitte versuche es erneut.',
        );

      } finally {

        setCameraBusy(
          false,
        );

      }

    };


  /* ======================================================
     KAMERA SCHLIESSEN
     ====================================================== */

  const closeCamera =
    () => {

      if (
        cameraBusy
      ) {
        return;
      }


      setCameraVisible(
        false,
      );


      setCameraReady(
        false,
      );

    };


  /* ======================================================
     GALERIE
     ====================================================== */

  const openGallery =
    async () => {

      try {

        const result =
          await ImagePicker
            .launchImageLibraryAsync({

              mediaTypes: [
                'images',
              ],

              allowsEditing:
                false,

              quality:
                1,

            });


        if (
          result.canceled
        ) {
          return;
        }


        const image =
          result.assets[0];


        if (
          !image?.uri
        ) {

          Alert.alert(
            'Bild konnte nicht geladen werden',

            'Bitte wähle ein anderes Bild aus.',
          );

          return;

        }


        setSelectedImage(
          image.uri,
        );


        setImageSource(
          'gallery',
        );


        setRecognitionResult(
          null,
        );


        setAnalysisStep(
          0,
        );

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
     RESET
     ====================================================== */

  const resetImage =
    () => {

      setSelectedImage(
        null,
      );


      setImageSource(
        null,
      );


      setRecognitionResult(
        null,
      );


      setAnalysisStep(
        0,
      );


      setIsAnalyzing(
        false,
      );

    };


  /* ======================================================
     ERKENNUNG STARTEN
     ====================================================== */

  const startRecognition =
    async () => {

      if (
        !selectedImage
      ) {
        return;
      }


      let stepOne:
        ReturnType<
          typeof setTimeout
        > |
        undefined;


      let stepTwo:
        ReturnType<
          typeof setTimeout
        > |
        undefined;


      try {

        setIsAnalyzing(
          true,
        );


        setRecognitionResult(
          null,
        );


        setAnalysisStep(
          0,
        );


        stepOne =
          setTimeout(
            () => {

              setAnalysisStep(
                1,
              );

            },

            650,
          );


        stepTwo =
          setTimeout(
            () => {

              setAnalysisStep(
                2,
              );

            },

            1450,
          );


        /*
         * Die Analyseanzeige bleibt mindestens
         * 2,5 Sekunden sichtbar.
         *
         * Wenn das echte Backend später länger
         * braucht, warten wir automatisch länger.
         *
         * Beispiel:
         *
         * Backend = 0,4 Sekunden
         * → Anzeige = 2,5 Sekunden
         *
         * Backend = 4 Sekunden
         * → Anzeige = 4 Sekunden
         */

        const [
          result,
        ] =
          await Promise.all([

            recognizeCard(
              selectedImage,
            ),

            new Promise<void>(
              (resolve) => {

                setTimeout(
                  resolve,
                  2500,
                );

              },
            ),

          ]);


        setAnalysisStep(
          3,
        );


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

        if (
          stepOne
        ) {

          clearTimeout(
            stepOne,
          );

        }


        if (
          stepTwo
        ) {

          clearTimeout(
            stepTwo,
          );

        }


        setIsAnalyzing(
          false,
        );

      }

    };


  /* ======================================================
     KANDIDAT AUSWÄHLEN
     ====================================================== */

  const selectCandidate =
    (
      candidate:
        RecognitionCandidate,
    ) => {

      setRecognitionResult({

        status:
          'success',

        card:
          candidate.card,

        recognition:
          candidate.recognition,

        variants:
          candidate.variants,

      });

    };


  /* ======================================================
     ENTON-ZUSTAND
     ====================================================== */

  const isUncertain =
    recognitionResult?.status ===
    'uncertain';


  const isNotFound =
    recognitionResult?.status ===
    'not_found';


  const psyduckMessage =
    isAnalyzing
      ? 'Hmm … einen Moment. Ich vergleiche deine Karte gerade.'

      : isNotFound
        ? recognitionResult.reason ===
          'no_card_detected'
          ? 'Hmm … ich kann auf dem Bild keine Karte erkennen. Versuch es einfach noch einmal.'
          : 'Oh je … ich finde leider keine passende Karte in meinen Referenzen.'

        : isUncertain
          ? 'Oh je … bei diesen Karten bin ich mir nicht ganz sicher. Hilfst du mir?'

          : recognitionResult?.status ===
            'success'
            ? 'Ich glaube, die habe ich gefunden!'

            : selectedImage
              ? 'Sieht gut aus! Wenn die ganze Karte zu sehen ist, können wir loslegen.'

              : 'Zeig mir deine Karte – ich schau sie mir an!';


  return (

    <SafeAreaView
      style={
        styles.safeArea
      }

      edges={[
        'top',
        'left',
        'right',
      ]}
    >

      <View
        pointerEvents="none"

        style={
          styles.background
        }
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
        ref={
          scrollViewRef
        }

        contentContainerStyle={[
          styles.scrollContent,

          isWideScreen &&
            styles.scrollContentWide,

          isMobile &&
            styles.scrollContentMobile,
        ]}

        showsVerticalScrollIndicator={
          false
        }

        keyboardShouldPersistTaps="handled"
      >

        <View style={styles.header}>

          <Pressable
            accessibilityRole="button"

            accessibilityLabel="Zur Startseite"

            onPress={
              resetImage
            }

            style={({
              pressed,
            }) => [

              styles.brand,

              pressed &&
                styles.brandPressed,

            ]}
          >

            <View style={styles.brandIcon}>

              <Text style={styles.brandIconText}>
                ✦
              </Text>

            </View>


            <Text style={styles.brandText}>
              Card Scanner
            </Text>

          </Pressable>


          {isWideScreen && (

            <View style={styles.projectBadge}>

              <Text style={styles.projectBadgeText}>
                Studienprojekt
              </Text>

            </View>

          )}

        </View>


        <View
          style={[
            styles.hero,

            isMobile &&
              styles.heroMobile,
          ]}
        >

          <Text style={styles.eyebrow}>
            POKÉMON-KARTENERKENNUNG
          </Text>


          <Text
            numberOfLines={
              1
            }

            adjustsFontSizeToFit

            minimumFontScale={
              0.75
            }

            style={[
              styles.title,

              isMobile &&
                styles.titleMobile,
            ]}
          >
            Welche Karte hast du?
          </Text>


          {!recognitionResult && (

            <Text
              style={[
                styles.description,

                isMobile &&
                  styles.descriptionMobile,
              ]}
            >
              Fotografiere deine Karte oder wähle
              ein Bild aus. Wir suchen die passende
              Karte und zeigen dir anschließend
              ihre wichtigsten Informationen.
            </Text>

          )}


          <PsyduckMascot
            message={
              psyduckMessage
            }

            mood={
              isNotFound
                ? 'confused'

                : isUncertain
                  ? 'sad'

                  : 'default'
            }
          />

        </View>


        {!recognitionResult && (

          <View style={styles.scannerCard}>

            <View style={styles.sectionHeader}>

              <Text style={styles.stepLabel}>
                SCHRITT 1
              </Text>


              <Text style={styles.sectionTitle}>

                {
                  isAnalyzing
                    ? 'Karte analysieren'

                    : selectedImage
                      ? 'Karte prüfen'

                      : 'Karte hinzufügen'
                }

              </Text>

            </View>


            {!selectedImage &&
              !isAnalyzing && (

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

                    onPress={
                      openCamera
                    }

                    style={({
                      pressed,
                    }) => [

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

                    onPress={
                      openGallery
                    }

                    style={({
                      pressed,
                    }) => [

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


            {selectedImage &&
              !isAnalyzing &&
              !recognitionResult && (

              <View>

                <View style={styles.previewFrame}>

                  <Image
                    source={{
                      uri:
                        selectedImage,
                    }}

                    style={
                      styles.previewImage
                    }

                    resizeMode="contain"

                    accessibilityLabel="Vorschau der ausgewählten Pokémon-Karte"
                  />

                </View>


                <View style={styles.previewInfo}>

                  <View style={styles.previewStatus}>

                    <View style={styles.previewStatusDot} />


                    <Text style={styles.previewStatusText}>

                      {
                        imageSource ===
                        'camera'

                          ? 'Foto aufgenommen'

                          : 'Bild ausgewählt'
                      }

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

                    onPress={
                      startRecognition
                    }

                    style={({
                      pressed,
                    }) => [

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

                    onPress={
                      resetImage
                    }

                    style={({
                      pressed,
                    }) => [

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

                      analysisStep ===
                        0 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >=
                          0 &&
                          styles.analysisDotActive,

                        analysisStep >
                          0 &&
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

                      analysisStep ===
                        1 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >=
                          1 &&
                          styles.analysisDotActive,

                        analysisStep >
                          1 &&
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

                      analysisStep >=
                        2 &&
                        styles.analysisStepActive,
                    ]}
                  >

                    <View
                      style={[
                        styles.analysisDot,

                        analysisStep >=
                          2 &&
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


        {recognitionResult?.status ===
          'not_found' &&
          selectedImage && (

          <NotFoundResult
            result={
              recognitionResult
            }

            originalImageUri={
              selectedImage
            }

            onCamera={
              openCamera
            }

            onGallery={
              openGallery
            }

            onReset={
              resetImage
            }
          />

        )}


        {recognitionResult?.status ===
          'uncertain' &&
          selectedImage && (

          <CandidateSelection
            result={
              recognitionResult
            }

            originalImageUri={
              selectedImage
            }

            onSelect={
              selectCandidate
            }

            onReset={
              resetImage
            }
          />

        )}


        {recognitionResult?.status ===
          'success' &&
          selectedImage && (

          <CardResult
            result={
              recognitionResult
            }

            originalImageUri={
              selectedImage
            }

            onReset={
              resetImage
            }
          />

        )}


        <Text style={styles.footer}>
          Studienprojekt zur optischen
          Pokémon-Kartenerkennung
        </Text>

      </ScrollView>


      <Modal
        visible={
          cameraVisible
        }

        animationType="fade"

        presentationStyle="fullScreen"

        statusBarTranslucent

        onRequestClose={
          closeCamera
        }
      >

        <View style={styles.cameraScreen}>

          <CameraView
            ref={
              cameraRef
            }

            style={
              StyleSheet.absoluteFill
            }

            facing="back"

            onCameraReady={() => {

              setCameraReady(
                true,
              );

            }}

            onMountError={(error) => {

              console.error(
                'Camera mount error:',
                error,
              );


              setCameraVisible(
                false,
              );


              setCameraReady(
                false,
              );


              Alert.alert(
                'Kamerafehler',

                'Die Kamera konnte nicht gestartet werden.',
              );

            }}
          />


          <SafeAreaView
            style={
              styles.cameraOverlay
            }

            edges={[
              'top',
              'bottom',
              'left',
              'right',
            ]}
          >

            <View style={styles.cameraTopBar}>

              <Pressable
                accessibilityRole="button"

                accessibilityLabel="Kamera schließen"

                disabled={
                  cameraBusy
                }

                onPress={
                  closeCamera
                }

                style={({
                  pressed,
                }) => [

                  styles.cameraCloseButton,

                  pressed &&
                    !cameraBusy &&
                    styles.cameraButtonPressed,

                ]}
              >

                <Text style={styles.cameraCloseText}>
                  ×
                </Text>

              </Pressable>


              <Text
                numberOfLines={
                  1
                }

                style={
                  styles.cameraTitle
                }
              >
                Pokémon-Karte fotografieren
              </Text>


              <View style={styles.cameraTopSpacer} />

            </View>


            <View style={styles.cameraBottomBar}>

              <Text style={styles.cameraHint}>
                Halte die gesamte Karte möglichst
                gut sichtbar ins Bild.
              </Text>


              <Pressable
                accessibilityRole="button"

                accessibilityLabel="Foto aufnehmen"

                disabled={
                  !cameraReady ||
                  cameraBusy
                }

                onPress={
                  takePhoto
                }

                style={({
                  pressed,
                }) => [

                  styles.shutterOuter,

                  (
                    !cameraReady ||
                    cameraBusy
                  ) &&
                    styles.shutterDisabled,

                  pressed &&
                    cameraReady &&
                    !cameraBusy &&
                    styles.shutterPressed,

                ]}
              >

                {cameraBusy ? (

                  <ActivityIndicator
                    size="large"

                    color="#FFFFFF"
                  />

                ) : (

                  <View style={styles.shutterInner} />

                )}

              </Pressable>

            </View>

          </SafeAreaView>

        </View>

      </Modal>

    </SafeAreaView>

  );

}


const styles =
  StyleSheet.create({

    safeArea: {
      flex:
        1,

      backgroundColor:
        colors.background,
    },


    background: {
      position:
        'absolute',

      top:
        0,

      right:
        0,

      bottom:
        0,

      left:
        0,

      overflow:
        'hidden',
    },


    backgroundBubble: {
      position:
        'absolute',

      borderRadius:
        radius.pill,

      opacity:
        0.72,
    },


    bubblePink: {
      width:
        290,

      height:
        290,

      top:
        -145,

      right:
        -115,

      backgroundColor:
        colors.pink,
    },


    bubbleLavender: {
      width:
        240,

      height:
        240,

      left:
        -150,

      top:
        '42%',

      backgroundColor:
        colors.lavender,
    },


    bubbleMint: {
      width:
        230,

      height:
        230,

      right:
        -135,

      bottom:
        -110,

      backgroundColor:
        colors.mint,
    },


    scrollContent: {
      width:
        '100%',

      paddingHorizontal:
        spacing.md,

      paddingBottom:
        spacing.xl,

      alignSelf:
        'center',
    },


    scrollContentWide: {
      maxWidth:
        1000,
    },


    scrollContentMobile: {
      paddingBottom:
        spacing.lg,
    },


    header: {
      minHeight:
        72,

      flexDirection:
        'row',

      alignItems:
        'center',

      justifyContent:
        'space-between',

      paddingTop:
        spacing.sm,
    },


    brand: {
      flexDirection:
        'row',

      alignItems:
        'center',

      gap:
        10,
    },


    brandPressed: {
      opacity:
        0.72,

      transform: [
        {
          scale:
            0.98,
        },
      ],
    },


    brandIcon: {
      width:
        42,

      height:
        42,

      alignItems:
        'center',

      justifyContent:
        'center',

      backgroundColor:
        colors.pink,

      borderTopLeftRadius:
        22,

      borderTopRightRadius:
        18,

      borderBottomLeftRadius:
        17,

      borderBottomRightRadius:
        24,

      ...shadow.button,
    },


    brandIconText: {
      color:
        colors.text,

      fontSize:
        18,

      fontWeight:
        '800',
    },


    brandText: {
      color:
        colors.text,

      fontSize:
        17,

      fontWeight:
        '800',

      letterSpacing:
        -0.4,
    },


    projectBadge: {
      paddingHorizontal:
        15,

      paddingVertical:
        8,

      borderRadius:
        radius.pill,

      backgroundColor:
        colors.whiteTransparent,

      borderWidth:
        1,

      borderColor:
        colors.border,
    },


    projectBadgeText: {
      color:
        colors.textSoft,

      fontSize:
        12,

      fontWeight:
        '700',
    },


    hero: {
      width:
        '100%',

      maxWidth:
        680,

      alignSelf:
        'center',

      alignItems:
        'center',

      paddingTop:
        spacing.xl,

      paddingBottom:
        spacing.xl,
    },


    heroMobile: {
      paddingTop:
        18,

      paddingBottom:
        14,
    },


    eyebrow: {
      color:
        colors.lavenderStrong,

      fontSize:
        12,

      fontWeight:
        '800',

      letterSpacing:
        1.2,

      textAlign:
        'center',
    },


    title: {
      maxWidth:
        650,

      marginTop:
        7,

      color:
        colors.text,

      fontSize:
        44,

      lineHeight:
        47,

      fontWeight:
        '800',

      letterSpacing:
        -1.8,

      textAlign:
        'center',
    },


    titleMobile: {
      width:
        '100%',

      fontSize:
        31,

      lineHeight:
        36,

      letterSpacing:
        -1.1,

      marginTop:
        5,
    },


    description: {
      maxWidth:
        550,

      marginTop:
        17,

      color:
        colors.textSoft,

      fontSize:
        16,

      lineHeight:
        24,

      textAlign:
        'center',
    },


    descriptionMobile: {
      marginTop:
        10,

      fontSize:
        14,

      lineHeight:
        20,
    },


    scannerCard: {
      width:
        '100%',

      maxWidth:
        820,

      alignSelf:
        'center',

      padding:
        20,

      backgroundColor:
        'rgba(255,255,255,0.91)',

      borderWidth:
        1.5,

      borderColor:
        'rgba(255,255,255,0.95)',

      borderTopLeftRadius:
        40,

      borderTopRightRadius:
        48,

      borderBottomLeftRadius:
        46,

      borderBottomRightRadius:
        36,

      ...shadow.card,
    },


    sectionHeader: {
      marginBottom:
        spacing.md,
    },


    stepLabel: {
      color:
        colors.lavenderStrong,

      fontSize:
        11,

      fontWeight:
        '800',

      letterSpacing:
        1.1,

      marginBottom:
        3,
    },


    sectionTitle: {
      color:
        colors.text,

      fontSize:
        26,

      lineHeight:
        31,

      fontWeight:
        '800',

      letterSpacing:
        -0.9,
    },


    scannerArea: {
      minHeight:
        275,

      alignItems:
        'center',

      justifyContent:
        'center',

      padding:
        spacing.lg,

      borderWidth:
        2,

      borderStyle:
        'dashed',

      borderColor:
        'rgba(130,98,207,0.28)',

      backgroundColor:
        'rgba(233,214,255,0.48)',

      borderTopLeftRadius:
        36,

      borderTopRightRadius:
        46,

      borderBottomLeftRadius:
        48,

      borderBottomRightRadius:
        34,
    },


    scannerIcon: {
      width:
        72,

      height:
        72,

      alignItems:
        'center',

      justifyContent:
        'center',

      marginBottom:
        14,

      backgroundColor:
        colors.pink,

      borderTopLeftRadius:
        38,

      borderTopRightRadius:
        31,

      borderBottomLeftRadius:
        30,

      borderBottomRightRadius:
        42,

      ...shadow.button,
    },


    scannerIconText: {
      color:
        colors.text,

      fontSize:
        26,
    },


    scannerTitle: {
      color:
        colors.text,

      fontSize:
        21,

      fontWeight:
        '800',

      textAlign:
        'center',
    },


    scannerDescription: {
      maxWidth:
        390,

      marginTop:
        5,

      color:
        colors.textSoft,

      fontSize:
        14,

      lineHeight:
        21,

      textAlign:
        'center',
    },


    actions: {
      width:
        '100%',

      gap:
        10,

      marginTop:
        16,
    },


    actionsWide: {
      flexDirection:
        'row',

      justifyContent:
        'center',
    },


    button: {
      minHeight:
        54,

      flexDirection:
        'row',

      alignItems:
        'center',

      justifyContent:
        'center',

      gap:
        8,

      paddingHorizontal:
        22,

      borderTopLeftRadius:
        27,

      borderTopRightRadius:
        32,

      borderBottomLeftRadius:
        31,

      borderBottomRightRadius:
        24,
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

      borderWidth:
        1,

      borderColor:
        colors.border,
    },


    fullWidthButton: {
      width:
        '100%',
    },


    buttonPressed: {
      opacity:
        0.82,

      transform: [
        {
          scale:
            0.985,
        },
      ],
    },


    primaryButtonIcon: {
      fontSize:
        17,
    },


    primaryButtonText: {
      color:
        '#FFFFFF',

      fontSize:
        15,

      fontWeight:
        '800',
    },


    secondaryButtonIcon: {
      color:
        colors.text,

      fontSize:
        18,
    },


    secondaryButtonText: {
      color:
        colors.text,

      fontSize:
        15,

      fontWeight:
        '800',
    },


    changeImageButtonText: {
      color:
        colors.textSoft,

      fontSize:
        14,

      fontWeight:
        '700',
    },


    forwardIcon: {
      color:
        '#FFFFFF',

      fontSize:
        19,

      fontWeight:
        '800',
    },


    previewFrame: {
      width:
        '100%',

      minHeight:
        330,

      maxHeight:
        520,

      padding:
        14,

      alignItems:
        'center',

      justifyContent:
        'center',

      backgroundColor:
        'rgba(223,204,255,0.62)',

      borderTopLeftRadius:
        36,

      borderTopRightRadius:
        46,

      borderBottomLeftRadius:
        47,

      borderBottomRightRadius:
        34,

      overflow:
        'hidden',
    },


    previewImage: {
      width:
        '100%',

      height:
        440,

      borderTopLeftRadius:
        25,

      borderTopRightRadius:
        29,

      borderBottomLeftRadius:
        30,

      borderBottomRightRadius:
        22,

      backgroundColor:
        'rgba(255,255,255,0.62)',
    },


    previewInfo: {
      marginTop:
        18,

      alignItems:
        'center',
    },


    previewStatus: {
      flexDirection:
        'row',

      alignItems:
        'center',

      gap:
        7,

      paddingHorizontal:
        12,

      paddingVertical:
        7,

      marginBottom:
        13,

      borderRadius:
        radius.pill,

      backgroundColor:
        colors.mint,
    },


    previewStatusDot: {
      width:
        8,

      height:
        8,

      borderRadius:
        radius.pill,

      backgroundColor:
        colors.success,
    },


    previewStatusText: {
      color:
        colors.success,

      fontSize:
        12,

      fontWeight:
        '800',
    },


    previewTitle: {
      color:
        colors.text,

      fontSize:
        22,

      fontWeight:
        '800',

      textAlign:
        'center',
    },


    previewDescription: {
      maxWidth:
        520,

      marginTop:
        7,

      color:
        colors.textSoft,

      fontSize:
        14,

      lineHeight:
        21,

      textAlign:
        'center',
    },


    previewActions: {
      width:
        '100%',

      gap:
        10,

      marginTop:
        20,
    },


    analysisContainer: {
      minHeight:
        330,

      alignItems:
        'center',

      justifyContent:
        'center',

      paddingVertical:
        24,
    },


    loadingDots: {
      flexDirection:
        'row',

      gap:
        9,

      marginBottom:
        20,
    },


    loadingDot: {
      width:
        15,

      height:
        15,

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

      fontSize:
        22,

      fontWeight:
        '800',

      textAlign:
        'center',
    },


    analysisDescription: {
      marginTop:
        5,

      color:
        colors.textSoft,

      fontSize:
        14,

      textAlign:
        'center',
    },


    analysisSteps: {
      width:
        '100%',

      maxWidth:
        460,

      gap:
        9,

      marginTop:
        24,
    },


    analysisStep: {
      minHeight:
        50,

      flexDirection:
        'row',

      alignItems:
        'center',

      gap:
        11,

      paddingHorizontal:
        16,

      backgroundColor:
        'rgba(255,255,255,0.75)',

      borderRadius:
        20,

      borderWidth:
        1,

      borderColor:
        colors.border,
    },


    analysisStepActive: {
      backgroundColor:
        'rgba(223,204,255,0.72)',
    },


    analysisDot: {
      width:
        11,

      height:
        11,

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

      fontSize:
        13,

      fontWeight:
        '700',
    },


    cameraScreen: {
      flex:
        1,

      backgroundColor:
        '#000000',
    },


    cameraOverlay: {
      flex:
        1,

      justifyContent:
        'space-between',

      backgroundColor:
        'transparent',
    },


    cameraTopBar: {
      minHeight:
        66,

      flexDirection:
        'row',

      alignItems:
        'center',

      justifyContent:
        'space-between',

      paddingHorizontal:
        14,

      paddingVertical:
        8,

      backgroundColor:
        'rgba(0,0,0,0.28)',
    },


    cameraCloseButton: {
      width:
        44,

      height:
        44,

      alignItems:
        'center',

      justifyContent:
        'center',

      borderRadius:
        22,

      backgroundColor:
        'rgba(0,0,0,0.38)',
    },


    cameraCloseText: {
      color:
        '#FFFFFF',

      fontSize:
        32,

      lineHeight:
        34,

      fontWeight:
        '400',
    },


    cameraTitle: {
      flex:
        1,

      paddingHorizontal:
        8,

      color:
        '#FFFFFF',

      fontSize:
        15,

      fontWeight:
        '700',

      textAlign:
        'center',
    },


    cameraTopSpacer: {
      width:
        44,
    },


    cameraBottomBar: {
      alignItems:
        'center',

      paddingHorizontal:
        20,

      paddingTop:
        18,

      paddingBottom:
        24,

      backgroundColor:
        'rgba(0,0,0,0.30)',
    },


    cameraHint: {
      maxWidth:
        340,

      marginBottom:
        17,

      color:
        '#FFFFFF',

      fontSize:
        13,

      lineHeight:
        18,

      textAlign:
        'center',

      textShadowColor:
        'rgba(0,0,0,0.75)',

      textShadowOffset: {
        width:
          0,

        height:
          1,
      },

      textShadowRadius:
        3,
    },


    cameraButtonPressed: {
      opacity:
        0.70,
    },


    shutterOuter: {
      width:
        78,

      height:
        78,

      alignItems:
        'center',

      justifyContent:
        'center',

      borderRadius:
        39,

      borderWidth:
        4,

      borderColor:
        '#FFFFFF',

      backgroundColor:
        'rgba(0,0,0,0.12)',
    },


    shutterInner: {
      width:
        60,

      height:
        60,

      borderRadius:
        30,

      backgroundColor:
        '#FFFFFF',
    },


    shutterDisabled: {
      opacity:
        0.45,
    },


    shutterPressed: {
      transform: [
        {
          scale:
            0.94,
        },
      ],
    },


    footer: {
      marginTop:
        spacing.xl,

      color:
        colors.textFaint,

      fontSize:
        12,

      textAlign:
        'center',
    },

  });