// mobile/src/components/CandidateSelection.tsx

import {
    Image,
    Pressable,
    StyleSheet,
    Text,
    useWindowDimensions,
    View,
} from 'react-native';

import {
    colors,
    radius,
    shadow,
    spacing,
} from '@/constants/theme';

import {
    RecognitionCandidate,
    UncertainRecognitionResult,
} from '@/types/recognition';


type CandidateSelectionProps = {
  result:
    UncertainRecognitionResult;

  originalImageUri: string;

  onSelect:
    (
      candidate:
        RecognitionCandidate,
    ) => void;

  onReset: () => void;
};


export function CandidateSelection({
  result,
  originalImageUri,
  onSelect,
  onReset,
}: CandidateSelectionProps) {

  const { width } =
    useWindowDimensions();

  const isWideScreen =
    width >= 800;


  return (
    <View style={styles.container}>

      {/* ============================================
          STATUS
          ============================================ */}

      <View style={styles.statusBadge}>

        <View style={styles.statusDot}>
          <Text style={styles.statusSymbol}>
            ?
          </Text>
        </View>

        <Text style={styles.statusText}>
          Erkennung nicht eindeutig
        </Text>

      </View>


      {/* ============================================
          TITEL
          ============================================ */}

      <View style={styles.header}>

        <Text style={styles.stepLabel}>
          DEINE HILFE WIRD GEBRAUCHT
        </Text>

        <Text style={styles.title}>
          Welche Karte ist es?
        </Text>

        <Text style={styles.description}>
          Mehrere Karten sehen für unsere
          Erkennung sehr ähnlich aus.
          Wähle einfach den passenden Treffer.
        </Text>

      </View>


      {/* ============================================
          KANDIDATEN
          ============================================ */}

      <View
        style={[
          styles.candidateGrid,

          isWideScreen &&
            styles.candidateGridWide,
        ]}
      >

        {result.candidates.map(
          (
            candidate,
            index,
          ) => {

            const similarity =
              `${(
                candidate
                  .recognition
                  .similarity *
                100
              ).toFixed(1)} %`;


            return (
              <Pressable
                key={
                  candidate
                    .card
                    .card_id
                }

                accessibilityRole="button"

                accessibilityLabel={
                  `${candidate.card.name}, ${candidate.card.set_name}, Karte ${candidate.card.number}, auswählen`
                }

                onPress={() =>
                  onSelect(
                    candidate,
                  )
                }

                style={({
                  pressed,
                }) => [
                  styles.candidateCard,

                  pressed &&
                    styles.candidateCardPressed,
                ]}
              >

                {/* Rang */}

                <View style={styles.rankBadge}>

                  <Text style={styles.rankText}>
                    #{index + 1}
                  </Text>

                </View>


                {/* Kartenbild */}

                <View style={styles.imageFrame}>

                  <Image
                    source={{
                      uri:
                        candidate
                          .card
                          .image_url ??
                        originalImageUri,
                    }}

                    style={styles.cardImage}

                    resizeMode="contain"

                    accessibilityLabel={
                      candidate
                        .card
                        .name
                    }
                  />

                </View>


                {/* Daten */}

                <View style={styles.cardContent}>

                  <Text
                    style={styles.setName}

                    numberOfLines={1}
                  >
                    {
                      candidate
                        .card
                        .set_name
                    }
                  </Text>


                  <Text
                    style={styles.cardName}

                    numberOfLines={2}
                  >
                    {
                      candidate
                        .card
                        .name
                    }
                  </Text>


                  <Text style={styles.cardNumber}>
                    Karte #
                    {
                      candidate
                        .card
                        .number
                    }
                  </Text>


                  {/* Badges */}

                  <View style={styles.badges}>

                    {candidate
                      .card
                      .rarity && (

                      <View
                        style={[
                          styles.badge,
                          styles.blueBadge,
                        ]}
                      >

                        <Text
                          style={
                            styles.badgeText
                          }
                        >
                          {
                            candidate
                              .card
                              .rarity
                          }
                        </Text>

                      </View>

                    )}


                    {candidate
                      .card
                      .types
                      .slice(
                        0,
                        1,
                      )
                      .map(
                        (type) => (

                          <View
                            key={type}

                            style={[
                              styles.badge,
                              styles.mintBadge,
                            ]}
                          >

                            <Text
                              style={
                                styles.badgeText
                              }
                            >
                              {type}
                            </Text>

                          </View>

                        ),
                      )}

                  </View>


                  {/* Similarity */}

                  <View style={styles.similarityBox}>

                    <Text style={styles.similarityLabel}>
                      Bildähnlichkeit
                    </Text>

                    <Text style={styles.similarityValue}>
                      {similarity}
                    </Text>

                  </View>


                  {/* Button */}

                  <View style={styles.selectButton}>

                    <Text style={styles.selectButtonText}>
                      Diese Karte auswählen
                    </Text>

                    <Text style={styles.selectArrow}>
                      →
                    </Text>

                  </View>

                </View>

              </Pressable>
            );
          },
        )}

      </View>


      {/* ============================================
          RESET
          ============================================ */}

      <Pressable
        accessibilityRole="button"

        onPress={onReset}

        style={({ pressed }) => [
          styles.resetButton,

          pressed &&
            styles.resetButtonPressed,
        ]}
      >

        <Text style={styles.resetButtonText}>
          Lieber ein anderes Bild versuchen
        </Text>

      </Pressable>

    </View>
  );
}


const styles = StyleSheet.create({

  container: {
    width: '100%',
    maxWidth: 920,

    alignSelf: 'center',

    padding: 20,

    backgroundColor:
      'rgba(255,255,255,0.93)',

    borderWidth: 1.5,

    borderColor:
      'rgba(255,255,255,0.96)',

    borderTopLeftRadius: 40,
    borderTopRightRadius: 48,
    borderBottomLeftRadius: 46,
    borderBottomRightRadius: 36,

    ...shadow.card,
  },


  /* ======================================================
     STATUS
     ====================================================== */

  statusBadge: {
    alignSelf: 'flex-start',

    flexDirection: 'row',
    alignItems: 'center',

    gap: 7,

    paddingHorizontal: 12,
    paddingVertical: 7,

    borderRadius:
      radius.pill,

    backgroundColor:
      colors.blue,
  },

  statusDot: {
    width: 22,
    height: 22,

    alignItems: 'center',
    justifyContent: 'center',

    borderRadius:
      radius.pill,

    backgroundColor:
      'rgba(94,168,212,0.16)',
  },

  statusSymbol: {
    color:
      colors.blueStrong,

    fontSize: 14,
    fontWeight: '800',
  },

  statusText: {
    color:
      colors.blueStrong,

    fontSize: 13,
    fontWeight: '800',
  },


  /* ======================================================
     HEADER
     ====================================================== */

  header: {
    marginTop:
      spacing.lg,

    alignItems: 'center',
  },

  stepLabel: {
    color:
      colors.lavenderStrong,

    fontSize: 11,
    fontWeight: '800',

    letterSpacing: 1.1,

    textAlign: 'center',
  },

  title: {
    marginTop: 5,

    color:
      colors.text,

    fontSize: 32,
    lineHeight: 37,

    fontWeight: '800',

    letterSpacing: -1.1,

    textAlign: 'center',
  },

  description: {
    maxWidth: 560,

    marginTop: 9,

    color:
      colors.textSoft,

    fontSize: 14,
    lineHeight: 21,

    textAlign: 'center',
  },


  /* ======================================================
     GRID
     ====================================================== */

  candidateGrid: {
    width: '100%',

    gap: 13,

    marginTop:
      spacing.lg,
  },

  candidateGridWide: {
    flexDirection: 'row',

    alignItems: 'stretch',
  },


  /* ======================================================
     KANDIDAT
     ====================================================== */

  candidateCard: {
    position: 'relative',

    flex: 1,

    padding: 13,

    backgroundColor:
      'rgba(255,255,255,0.78)',

    borderWidth: 2,

    borderColor:
      'rgba(130,98,207,0.10)',

    borderTopLeftRadius: 31,
    borderTopRightRadius: 38,
    borderBottomLeftRadius: 39,
    borderBottomRightRadius: 27,

    ...shadow.card,
  },

  candidateCardPressed: {
    opacity: 0.82,

    transform: [
      {
        scale: 0.985,
      },
    ],

    borderColor:
      colors.lavenderStrong,
  },


  /* ======================================================
     RANG
     ====================================================== */

  rankBadge: {
    position: 'absolute',

    top: 22,
    left: 22,

    zIndex: 5,

    minWidth: 38,
    height: 30,

    paddingHorizontal: 9,

    alignItems: 'center',
    justifyContent: 'center',

    backgroundColor:
      colors.lavenderStrong,

    borderRadius:
      radius.pill,

    ...shadow.button,
  },

  rankText: {
    color: '#FFFFFF',

    fontSize: 12,
    fontWeight: '800',
  },


  /* ======================================================
     BILD
     ====================================================== */

  imageFrame: {
    width: '100%',

    aspectRatio: 0.88,

    padding: 9,

    alignItems: 'center',
    justifyContent: 'center',

    backgroundColor:
      colors.lavender,

    borderTopLeftRadius: 25,
    borderTopRightRadius: 31,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 22,

    overflow: 'hidden',
  },

  cardImage: {
    width: '100%',
    height: '100%',

    borderRadius: 18,

    backgroundColor:
      'rgba(255,255,255,0.70)',
  },


  /* ======================================================
     CARD CONTENT
     ====================================================== */

  cardContent: {
    paddingTop: 14,
  },

  setName: {
    color:
      colors.lavenderStrong,

    fontSize: 11,
    fontWeight: '800',
  },

  cardName: {
    minHeight: 28,

    marginTop: 3,

    color:
      colors.text,

    fontSize: 20,
    lineHeight: 23,

    fontWeight: '800',

    letterSpacing: -0.6,
  },

  cardNumber: {
    marginTop: 3,

    color:
      colors.textSoft,

    fontSize: 11,
  },


  /* ======================================================
     BADGES
     ====================================================== */

  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',

    gap: 6,

    marginTop: 11,
  },

  badge: {
    paddingHorizontal: 9,
    paddingVertical: 5,

    borderRadius:
      radius.pill,
  },

  blueBadge: {
    backgroundColor:
      colors.blue,
  },

  mintBadge: {
    backgroundColor:
      colors.mint,
  },

  badgeText: {
    color:
      colors.text,

    fontSize: 10,
    fontWeight: '700',
  },


  /* ======================================================
     SIMILARITY
     ====================================================== */

  similarityBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',

    gap: 8,

    marginTop: 13,

    paddingHorizontal: 12,
    paddingVertical: 10,

    backgroundColor:
      'rgba(223,204,255,0.48)',

    borderRadius: 17,
  },

  similarityLabel: {
    color:
      colors.textSoft,

    fontSize: 10,
  },

  similarityValue: {
    color:
      colors.text,

    fontSize: 13,
    fontWeight: '800',
  },


  /* ======================================================
     AUSWAHLBUTTON
     ====================================================== */

  selectButton: {
    minHeight: 45,

    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',

    gap: 7,

    marginTop: 12,

    paddingHorizontal: 12,

    backgroundColor:
      colors.lavenderStrong,

    borderTopLeftRadius: 22,
    borderTopRightRadius: 26,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 19,

    ...shadow.button,
  },

  selectButtonText: {
    color: '#FFFFFF',

    fontSize: 11,
    fontWeight: '800',

    textAlign: 'center',
  },

  selectArrow: {
    color: '#FFFFFF',

    fontSize: 17,
    fontWeight: '800',
  },


  /* ======================================================
     RESET
     ====================================================== */

  resetButton: {
    minHeight: 52,

    marginTop: 20,

    alignItems: 'center',
    justifyContent: 'center',

    paddingHorizontal: 18,

    borderWidth: 1,

    borderColor:
      colors.border,

    borderRadius: 28,

    backgroundColor:
      'rgba(255,255,255,0.72)',
  },

  resetButtonPressed: {
    opacity: 0.78,

    transform: [
      {
        scale: 0.99,
      },
    ],
  },

  resetButtonText: {
    color:
      colors.textSoft,

    fontSize: 13,
    fontWeight: '700',

    textAlign: 'center',
  },

});