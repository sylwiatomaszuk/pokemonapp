// mobile/src/components/NotFoundResult.tsx

import {
    Image,
    Pressable,
    StyleSheet,
    Text,
    View,
} from 'react-native';

import {
    colors,
    radius,
    shadow,
    spacing,
} from '@/constants/theme';

import {
    NotFoundRecognitionResult,
} from '@/types/recognition';


type NotFoundResultProps = {
  result:
    NotFoundRecognitionResult;

  originalImageUri:
    string;

  onCamera:
    () => void;

  onGallery:
    () => void;

  onReset:
    () => void;
};


export function NotFoundResult({
  result,
  originalImageUri,
  onCamera,
  onGallery,
  onReset,
}: NotFoundResultProps) {

  const isNoCardDetected =
    result.reason ===
    'no_card_detected';


  const title =
    isNoCardDetected
      ? 'Ich sehe keine Karte.'
      : 'Diese Karte kenne ich noch nicht.';


  const description =
    isNoCardDetected
      ? 'Auf dem Bild konnte keine Pokémon-Karte sicher gefunden werden. Versuch es noch einmal und achte darauf, dass die ganze Karte sichtbar ist.'
      : 'Leider wurde keine ausreichend passende Karte in unseren Referenzen gefunden. Ein neues oder etwas schärferes Bild kann helfen.';


  return (
    <View style={styles.container}>

      <View style={styles.statusBadge}>

        <View style={styles.statusDot}>

          <Text style={styles.statusSymbol}>
            ?
          </Text>

        </View>

        <Text style={styles.statusText}>
          Keine Karte gefunden
        </Text>

      </View>


      <View style={styles.content}>

        <View style={styles.imageFrame}>

          <Image
            source={{
              uri:
                originalImageUri,
            }}

            style={
              styles.image
            }

            resizeMode="contain"

            accessibilityLabel="Nicht erkannte Pokémon-Karte"
          />

        </View>


        <Text style={styles.stepLabel}>
          NOCH EIN VERSUCH
        </Text>


        <Text style={styles.title}>
          {title}
        </Text>


        <Text style={styles.description}>
          {description}
        </Text>


        <View style={styles.actions}>

          <Pressable
            accessibilityRole="button"

            accessibilityLabel="Neues Foto aufnehmen"

            onPress={
              onCamera
            }

            style={({
              pressed,
            }) => [
              styles.actionButton,
              styles.cameraButton,

              pressed &&
                styles.buttonPressed,
            ]}
          >

            <Text style={styles.actionIcon}>
              📷
            </Text>

            <Text style={styles.cameraButtonText}>
              Kamera
            </Text>

          </Pressable>


          <Pressable
            accessibilityRole="button"

            accessibilityLabel="Anderes Bild aus der Galerie auswählen"

            onPress={
              onGallery
            }

            style={({
              pressed,
            }) => [
              styles.actionButton,
              styles.galleryButton,

              pressed &&
                styles.buttonPressed,
            ]}
          >

            <Text style={styles.galleryIcon}>
              ♡
            </Text>

            <Text style={styles.galleryButtonText}>
              Galerie
            </Text>

          </Pressable>

        </View>


        <Pressable
          accessibilityRole="button"

          accessibilityLabel="Zur Startseite"

          onPress={
            onReset
          }

          style={({
            pressed,
          }) => [
            styles.resetButton,

            pressed &&
              styles.resetButtonPressed,
          ]}
        >

          <Text style={styles.resetButtonText}>
            Zurück zur Startseite
          </Text>

        </Pressable>

      </View>

    </View>
  );
}


const styles =
  StyleSheet.create({

    container: {
      width:
        '100%',

      maxWidth:
        820,

      alignSelf:
        'center',

      padding:
        18,

      backgroundColor:
        'rgba(255,255,255,0.93)',

      borderWidth:
        1.5,

      borderColor:
        'rgba(255,255,255,0.96)',

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


    statusBadge: {
      alignSelf:
        'flex-start',

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

      borderRadius:
        radius.pill,

      backgroundColor:
        colors.pink,
    },


    statusDot: {
      width:
        22,

      height:
        22,

      alignItems:
        'center',

      justifyContent:
        'center',

      borderRadius:
        radius.pill,

      backgroundColor:
        'rgba(201,81,115,0.10)',
    },


    statusSymbol: {
      color:
        colors.danger,

      fontSize:
        14,

      fontWeight:
        '800',
    },


    statusText: {
      color:
        colors.danger,

      fontSize:
        13,

      fontWeight:
        '800',
    },


    content: {
      width:
        '100%',

      maxWidth:
        560,

      alignSelf:
        'center',

      alignItems:
        'center',

      paddingTop:
        spacing.md,
    },


    imageFrame: {
      width:
        118,

      height:
        150,

      padding:
        7,

      marginBottom:
        13,

      alignItems:
        'center',

      justifyContent:
        'center',

      backgroundColor:
        colors.blue,

      borderTopLeftRadius:
        25,

      borderTopRightRadius:
        30,

      borderBottomLeftRadius:
        31,

      borderBottomRightRadius:
        22,

      ...shadow.card,
    },


    image: {
      width:
        '100%',

      height:
        '100%',

      borderRadius:
        17,

      backgroundColor:
        'rgba(255,255,255,0.70)',
    },


    stepLabel: {
      color:
        colors.lavenderStrong,

      fontSize:
        10,

      fontWeight:
        '800',

      letterSpacing:
        1.05,

      textAlign:
        'center',
    },


    title: {
      marginTop:
        4,

      color:
        colors.text,

      fontSize:
        27,

      lineHeight:
        32,

      fontWeight:
        '800',

      letterSpacing:
        -0.9,

      textAlign:
        'center',
    },


    description: {
      maxWidth:
        480,

      marginTop:
        8,

      color:
        colors.textSoft,

      fontSize:
        13,

      lineHeight:
        19,

      textAlign:
        'center',
    },


    actions: {
      width:
        '100%',

      flexDirection:
        'row',

      gap:
        9,

      marginTop:
        17,
    },


    actionButton: {
      minHeight:
        50,

      flex:
        1,

      flexDirection:
        'row',

      alignItems:
        'center',

      justifyContent:
        'center',

      gap:
        7,

      paddingHorizontal:
        10,

      borderTopLeftRadius:
        24,

      borderTopRightRadius:
        28,

      borderBottomLeftRadius:
        27,

      borderBottomRightRadius:
        21,

      ...shadow.button,
    },


    cameraButton: {
      backgroundColor:
        colors.lavenderStrong,
    },


    galleryButton: {
      backgroundColor:
        colors.pink,
    },


    actionIcon: {
      fontSize:
        15,
    },


    galleryIcon: {
      color:
        colors.text,

      fontSize:
        17,
    },


    cameraButtonText: {
      color:
        '#FFFFFF',

      fontSize:
        13,

      fontWeight:
        '800',
    },


    galleryButtonText: {
      color:
        colors.text,

      fontSize:
        13,

      fontWeight:
        '800',
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


    resetButton: {
      minHeight:
        44,

      marginTop:
        10,

      paddingHorizontal:
        20,

      alignItems:
        'center',

      justifyContent:
        'center',
    },


    resetButtonPressed: {
      opacity:
        0.65,
    },


    resetButtonText: {
      color:
        colors.textSoft,

      fontSize:
        12,

      fontWeight:
        '700',

      textAlign:
        'center',
    },

  });