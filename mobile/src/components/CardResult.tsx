import {
  useRef,
  useState,
} from 'react';

import {
  ActivityIndicator,
  Animated,
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
  CardPrice,
  CardVariant,
  RecognitionResult,
} from '@/types/recognition';

import {
  getCardPrice,
} from '@/services/recognitionService';


type CardResultProps = {
  result: RecognitionResult;

  originalImageUri: string;

  onReset: () => void;
};


const variantLabels: Record<
  CardVariant,
  {
    title: string;
    description: string;
    symbol: string;
  }
> = {

  normal: {
    title: 'Normal',
    description: 'Standardkarte',
    symbol: '○',
  },

  holo: {
    title: 'Holo',
    description: 'Holografischer Bildbereich',
    symbol: '✦',
  },

  reverse_holo: {
    title: 'Reverse Holo',
    description: 'Holografischer Kartenbereich',
    symbol: '✧',
  },

};


export function CardResult({
  result,
  originalImageUri,
  onReset,
}: CardResultProps) {

  const { width } =
    useWindowDimensions();

  const isWideScreen =
    width >= 800;


  /* ======================================================
     VARIANTENAUSWAHL
     ====================================================== */

  const [
    selectedVariant,
    setSelectedVariant,
  ] = useState<CardVariant | null>(
    null,
  );


  /*
   * Zusätzlicher Ref:
   *
   * Falls der Benutzer während des Ladens
   * die Variante wechselt, wissen wir nach
   * dem Laden trotzdem sofort, welche Variante
   * aktuell ausgewählt ist.
   */

  const selectedVariantRef =
    useRef<CardVariant | null>(
      null,
    );


  /* ======================================================
     PREISE
     ====================================================== */

  /*
   * Statt nur EINEN Preis zu speichern,
   * speichern wir jetzt alle bereits
   * geladenen Preise.
   *
   * Beispiel:
   *
   * {
   *   normal: {...},
   *   holo: {...},
   *   reverse_holo: {...}
   * }
   */

  const [
    prices,
    setPrices,
  ] = useState<
    Partial<
      Record<
        CardVariant,
        CardPrice
      >
    >
  >({});


  /*
   * Steuert, ob die Preisbox
   * aktuell sichtbar ist.
   */

  const [
    isPriceVisible,
    setIsPriceVisible,
  ] = useState(false);


  /*
   * Diese Variante wird tatsächlich
   * gerade in der Preisbox angezeigt.
   *
   * Sie ist bewusst getrennt von
   * selectedVariant, damit wir beim
   * Wechsel eine kurze Animation
   * durchführen können.
   */

  const [
    displayedVariant,
    setDisplayedVariant,
  ] = useState<CardVariant | null>(
    null,
  );


  const [
    isLoadingPrices,
    setIsLoadingPrices,
  ] = useState(false);


  const [
    isRefreshingPrice,
    setIsRefreshingPrice,
  ] = useState(false);


  /* ======================================================
     PREIS-ANIMATION
     ====================================================== */

  const priceOpacity =
    useRef(
      new Animated.Value(1),
    ).current;


  const priceScale =
    useRef(
      new Animated.Value(1),
    ).current;


  const refreshRotation =
    useRef(
      new Animated.Value(0),
    ).current;


  /*
   * Mit dieser ID verhindern wir,
   * dass eine alte Animation noch
   * einen neueren Variantenwechsel
   * überschreibt.
   */

  const animationIdRef =
    useRef(0);


  const refreshRotationStyle =
    refreshRotation.interpolate({
      inputRange: [
        0,
        1,
      ],

      outputRange: [
        '0deg',
        '360deg',
      ],
    });


  /* ======================================================
     KARTENDATEN
     ====================================================== */

  const card =
    result.card;


  const similarity =
    `${(
      result.recognition.similarity * 100
    ).toFixed(1)} %`;


  const formattedReleaseDate =
    new Intl.DateTimeFormat(
      'de-DE',
    ).format(
      new Date(
        card.release_date,
      ),
    );


  /* ======================================================
     AKTUELL ANGEZEIGTER PREIS
     ====================================================== */

  const displayedPrice =
    displayedVariant
      ? prices[displayedVariant]
      : undefined;


  /* ======================================================
     KURZE REFRESH-ANIMATION
     ====================================================== */

  const animatePriceChange = (
    nextVariant: CardVariant,
  ) => {

    const animationId =
      ++animationIdRef.current;


    setIsRefreshingPrice(true);


    /*
     * Falls noch eine vorherige Animation
     * läuft, wird sie beendet.
     */

    priceOpacity.stopAnimation();

    priceScale.stopAnimation();

    refreshRotation.stopAnimation();


    /*
     * Ausgangswerte des Refresh-Symbols.
     */

    refreshRotation.setValue(0);


    /*
     * Phase 1:
     * alter Preis blendet ganz kurz aus.
     */

    Animated.parallel([
      Animated.timing(
        priceOpacity,
        {
          toValue: 0.28,
          duration: 90,
          useNativeDriver: true,
        },
      ),

      Animated.timing(
        priceScale,
        {
          toValue: 0.985,
          duration: 90,
          useNativeDriver: true,
        },
      ),
    ]).start(() => {

      /*
       * Falls inzwischen schon eine
       * neuere Animation gestartet wurde,
       * machen wir hier nichts mehr.
       */

      if (
        animationId !==
        animationIdRef.current
      ) {
        return;
      }


      /*
       * Genau zwischen Aus- und Einblenden
       * wird der angezeigte Preis gewechselt.
       */

      setDisplayedVariant(
        nextVariant,
      );


      /*
       * Phase 2:
       * neuer Preis erscheint wieder.
       */

      Animated.parallel([
        Animated.timing(
          priceOpacity,
          {
            toValue: 1,
            duration: 150,
            useNativeDriver: true,
          },
        ),

        Animated.timing(
          priceScale,
          {
            toValue: 1,
            duration: 150,
            useNativeDriver: true,
          },
        ),

        Animated.timing(
          refreshRotation,
          {
            toValue: 1,
            duration: 240,
            useNativeDriver: true,
          },
        ),
      ]).start(() => {

        if (
          animationId ===
          animationIdRef.current
        ) {
          setIsRefreshingPrice(
            false,
          );
        }

      });

    });

  };


  /* ======================================================
     VARIANTE AUSWÄHLEN
     ====================================================== */

  const selectVariant = (
    variant: CardVariant,
  ) => {

    /*
     * Nichts machen, wenn dieselbe
     * Variante nochmals gedrückt wird.
     */

    if (
      selectedVariant ===
      variant
    ) {
      return;
    }


    setSelectedVariant(
      variant,
    );


    selectedVariantRef.current =
      variant;


    /*
     * Falls der Marktwert gerade sichtbar ist,
     * wechseln wir direkt zum Preis der
     * neuen Variante.
     *
     * Alle Preise wurden beim ersten Klick
     * bereits geladen.
     */

    if (
      isPriceVisible &&
      prices[variant]
    ) {
      animatePriceChange(
        variant,
      );
    }

  };


  /* ======================================================
     ALLE PREISE LADEN
     ====================================================== */

  const loadAllPrices =
    async () => {

      /*
       * Prüfen, ob wirklich alle Varianten
       * bereits im Cache liegen.
       */

      const allPricesAlreadyLoaded =
        result.variants.every(
          (variant) =>
            Boolean(
              prices[variant],
            ),
        );


      if (
        allPricesAlreadyLoaded
      ) {
        return prices;
      }


      setIsLoadingPrices(
        true,
      );


      try {

        /*
         * WICHTIG:
         *
         * Promise.all bedeutet:
         *
         * Normal
         * Holo
         * Reverse Holo
         *
         * werden gleichzeitig geladen
         * und nicht nacheinander.
         */

        const loadedPrices =
          await Promise.all(
            result.variants.map(
              (variant) =>
                getCardPrice(
                  card.card_id,
                  variant,
                ),
            ),
          );


        const newPrices:
          Partial<
            Record<
              CardVariant,
              CardPrice
            >
          > = {
            ...prices,
          };


        loadedPrices.forEach(
          (price) => {

            newPrices[
              price.variant
            ] = price;

          },
        );


        setPrices(
          newPrices,
        );


        return newPrices;

      } finally {

        setIsLoadingPrices(
          false,
        );

      }

    };


  /* ======================================================
     MARKTWERT ANZEIGEN / AUSBLENDEN
     ====================================================== */

  const togglePrice =
    async () => {

      if (
        !selectedVariant
      ) {
        return;
      }


      /*
       * Preis ist bereits sichtbar:
       * einfach ausblenden.
       *
       * Die Preise bleiben trotzdem
       * im Speicher.
       */

      if (
        isPriceVisible
      ) {

        setIsPriceVisible(
          false,
        );

        setIsRefreshingPrice(
          false,
        );

        return;
      }


      /*
       * Beim ersten Anzeigen laden wir
       * sofort ALLE Preise.
       */

      const loadedPrices =
        await loadAllPrices();


      /*
       * Während des Ladens könnte der
       * Benutzer die Variante gewechselt
       * haben.
       *
       * Deshalb nehmen wir hier die
       * aktuellste Auswahl.
       */

      const currentVariant =
        selectedVariantRef.current ??
        selectedVariant;


      if (
        !currentVariant
      ) {
        return;
      }


      if (
        !loadedPrices[
          currentVariant
        ]
      ) {
        return;
      }


      /*
       * Richtigen Preis setzen.
       */

      setDisplayedVariant(
        currentVariant,
      );


      /*
       * Anfangszustand für eine sehr
       * kurze Einblendanimation.
       */

      priceOpacity.setValue(
        0.45,
      );

      priceScale.setValue(
        0.985,
      );

      refreshRotation.setValue(
        0,
      );


      setIsPriceVisible(
        true,
      );


      Animated.parallel([
        Animated.timing(
          priceOpacity,
          {
            toValue: 1,
            duration: 170,
            useNativeDriver: true,
          },
        ),

        Animated.timing(
          priceScale,
          {
            toValue: 1,
            duration: 170,
            useNativeDriver: true,
          },
        ),
      ]).start();

    };


  return (
    <View style={styles.container}>

      {/* ============================================
          SUCCESS
          ============================================ */}

      <View style={styles.successBadge}>

        <View style={styles.successDot}>
          <Text style={styles.successCheck}>
            ✓
          </Text>
        </View>

        <Text style={styles.successText}>
          Karte erkannt
        </Text>

      </View>


      {/* ============================================
          KARTE
          ============================================ */}

      <View
        style={[
          styles.cardLayout,

          isWideScreen &&
            styles.cardLayoutWide,
        ]}
      >

        <View
          style={[
            styles.imageColumn,

            isWideScreen &&
              styles.imageColumnWide,
          ]}
        >

          <View style={styles.imageFrame}>

            <Image
              source={{
                uri:
                  card.image_url ??
                  originalImageUri,
              }}

              style={styles.cardImage}

              resizeMode="contain"

              accessibilityLabel={
                `Erkannte Pokémon-Karte ${card.name}`
              }
            />

          </View>

        </View>


        {/* ============================================
            INFORMATIONEN
            ============================================ */}

        <View style={styles.infoColumn}>

          <Text style={styles.setName}>
            {card.set_name}
          </Text>

          <Text style={styles.cardName}>
            {card.name}
          </Text>

          <Text style={styles.cardNumber}>
            Karte #{card.number}
          </Text>


          {/* Badges */}

          <View style={styles.badges}>

            {card.rarity && (
              <View
                style={[
                  styles.badge,
                  styles.blueBadge,
                ]}
              >
                <Text style={styles.badgeText}>
                  {card.rarity}
                </Text>
              </View>
            )}


            {card.types.map(
              (type) => (
                <View
                  key={type}

                  style={[
                    styles.badge,
                    styles.mintBadge,
                  ]}
                >
                  <Text style={styles.badgeText}>
                    {type}
                  </Text>
                </View>
              ),
            )}


            {card.subtypes.map(
              (subtype) => (
                <View
                  key={subtype}

                  style={[
                    styles.badge,
                    styles.butterBadge,
                  ]}
                >
                  <Text style={styles.badgeText}>
                    {subtype}
                  </Text>
                </View>
              ),
            )}

          </View>


          {/* Metadaten */}

          <View style={styles.metadataGrid}>

            <View style={styles.metadataItem}>

              <Text style={styles.metadataLabel}>
                ILLUSTRATOR
              </Text>

              <Text style={styles.metadataValue}>
                {card.artist || '–'}
              </Text>

            </View>


            <View style={styles.metadataItem}>

              <Text style={styles.metadataLabel}>
                VERÖFFENTLICHUNG
              </Text>

              <Text style={styles.metadataValue}>
                {formattedReleaseDate}
              </Text>

            </View>


            <View style={styles.metadataItem}>

              <Text style={styles.metadataLabel}>
                SET
              </Text>

              <Text style={styles.metadataValue}>
                {card.set_name}
              </Text>

            </View>


            <View style={styles.metadataItem}>

              <Text style={styles.metadataLabel}>
                SELTENHEIT
              </Text>

              <Text style={styles.metadataValue}>
                {card.rarity || '–'}
              </Text>

            </View>

          </View>


          {/* Similarity */}

          <View style={styles.similarityBox}>

            <View style={styles.similarityRow}>

              <Text style={styles.similarityLabel}>
                Bildähnlichkeit
              </Text>

              <Text style={styles.similarityValue}>
                {similarity}
              </Text>

            </View>

            <Text style={styles.similarityDescription}>
              Der Wert beschreibt die visuelle
              Übereinstimmung mit der Referenzkarte.
            </Text>

          </View>

        </View>

      </View>


      {/* ============================================
          VARIANTE
          ============================================ */}

      <View style={styles.variantSection}>

        <Text style={styles.stepLabel}>
          SCHRITT 2
        </Text>

        <Text style={styles.sectionTitle}>
          Welche Variante hast du?
        </Text>


        <View
          style={[
            styles.variantGrid,

            isWideScreen &&
              styles.variantGridWide,
          ]}
        >

          {result.variants.map(
            (variant) => {

              const option =
                variantLabels[variant];

              const isSelected =
                selectedVariant ===
                variant;


              return (
                <Pressable
                  key={variant}

                  accessibilityRole="radio"

                  accessibilityState={{
                    selected:
                      isSelected,
                  }}

                  onPress={() =>
                    selectVariant(
                      variant,
                    )
                  }

                  style={({ pressed }) => [
                    styles.variantButton,

                    isSelected &&
                      styles.variantButtonSelected,

                    pressed &&
                      styles.variantButtonPressed,
                  ]}
                >

                  <View style={styles.variantIcon}>

                    <Text
                      style={
                        styles.variantIconText
                      }
                    >
                      {option.symbol}
                    </Text>

                  </View>


                  <View style={styles.variantText}>

                    <Text style={styles.variantTitle}>
                      {option.title}
                    </Text>

                    <Text
                      style={
                        styles.variantDescription
                      }
                    >
                      {option.description}
                    </Text>

                  </View>

                </Pressable>
              );
            },
          )}

        </View>


        {/* ============================================
            MARKTWERT BUTTON
            ============================================ */}

        <Pressable
          accessibilityRole="button"

          disabled={
            !selectedVariant ||
            isLoadingPrices
          }

          onPress={
            togglePrice
          }

          style={({ pressed }) => [
            styles.priceButton,

            (
              !selectedVariant ||
              isLoadingPrices
            ) &&
              styles.priceButtonDisabled,

            pressed &&
              selectedVariant &&
              !isLoadingPrices &&
              styles.buttonPressed,
          ]}
        >

          {isLoadingPrices ? (

            <View style={styles.loadingPriceRow}>

              <ActivityIndicator
                color="#FFFFFF"
                size="small"
              />

              <Text style={styles.priceButtonText}>
                Marktwerte laden …
              </Text>

            </View>

          ) : (

            <Text style={styles.priceButtonText}>
              {isPriceVisible
                ? 'Marktwert ausblenden'
                : 'Marktwert anzeigen'}
            </Text>

          )}

        </Pressable>

      </View>


      {/* ============================================
          PREIS
          ============================================ */}

      {isPriceVisible &&
        displayedVariant &&
        displayedPrice && (

          <Animated.View
            style={[
              styles.priceCard,

              {
                opacity:
                  priceOpacity,

                transform: [
                  {
                    scale:
                      priceScale,
                  },
                ],
              },
            ]}
          >

            {/* Kurzer Refresh-Indikator */}

            <View style={styles.priceRefreshRow}>

              <Animated.Text
                style={[
                  styles.priceRefreshIcon,

                  {
                    opacity:
                      isRefreshingPrice
                        ? 1
                        : 0,

                    transform: [
                      {
                        rotate:
                          refreshRotationStyle,
                      },
                    ],
                  },
                ]}
              >
                ↻
              </Animated.Text>

            </View>


            <Text style={styles.priceLabel}>
              Geschätzter Marktwert
            </Text>

            <Text style={styles.priceValue}>
              {new Intl.NumberFormat(
                'de-DE',
                {
                  style: 'currency',

                  currency:
                    displayedPrice.currency,
                },
              ).format(
                displayedPrice.price,
              )}
            </Text>

            <Text style={styles.priceMeta}>
              {
                variantLabels[
                  displayedVariant
                ].title
              }
              {' · '}
              zuletzt aktualisiert{' '}
              {new Intl.DateTimeFormat(
                'de-DE',
              ).format(
                new Date(
                  displayedPrice.updated_at,
                ),
              )}
            </Text>

          </Animated.View>

        )}


      {/* ============================================
          RESET
          ============================================ */}

      <Pressable
        accessibilityRole="button"

        onPress={onReset}

        style={({ pressed }) => [
          styles.resetButton,

          pressed &&
            styles.buttonPressed,
        ]}
      >

        <Text style={styles.resetButtonText}>
          Neue Karte scannen
        </Text>

      </Pressable>

    </View>
  );
}


const styles = StyleSheet.create({

  container: {
    width: '100%',

    maxWidth: 820,

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
     SUCCESS
     ====================================================== */

  successBadge: {
    alignSelf: 'flex-start',

    flexDirection: 'row',
    alignItems: 'center',

    gap: 7,

    paddingHorizontal: 12,
    paddingVertical: 7,

    borderRadius:
      radius.pill,

    backgroundColor:
      colors.mint,
  },

  successDot: {
    width: 22,
    height: 22,

    alignItems: 'center',
    justifyContent: 'center',

    borderRadius:
      radius.pill,

    backgroundColor:
      'rgba(67,155,106,0.15)',
  },

  successCheck: {
    color:
      colors.success,

    fontWeight: '800',
  },

  successText: {
    color:
      colors.success,

    fontSize: 13,
    fontWeight: '800',
  },


  /* ======================================================
     KARTEN-LAYOUT
     ====================================================== */

  cardLayout: {
    marginTop:
      spacing.xl,

    gap: 24,
  },

  cardLayoutWide: {
    flexDirection: 'row',

    alignItems: 'flex-start',
  },


  imageColumn: {
    width: '78%',
    maxWidth: 290,

    alignSelf: 'center',
  },

  imageColumnWide: {
    width: 280,

    flexShrink: 0,
  },

  imageFrame: {
    width: '100%',

    padding: 12,

    backgroundColor:
      colors.lavender,

    borderTopLeftRadius: 34,
    borderTopRightRadius: 42,
    borderBottomLeftRadius: 44,
    borderBottomRightRadius: 31,

    ...shadow.card,
  },

  cardImage: {
    width: '100%',

    aspectRatio: 0.72,

    borderRadius: 24,

    backgroundColor:
      'rgba(255,255,255,0.72)',
  },


  /* ======================================================
     INFORMATIONEN
     ====================================================== */

  infoColumn: {
    flex: 1,
  },

  setName: {
    color:
      colors.lavenderStrong,

    fontSize: 15,
    fontWeight: '800',
  },

  cardName: {
    marginTop: 2,

    color:
      colors.text,

    fontSize: 36,
    lineHeight: 40,

    fontWeight: '800',

    letterSpacing: -1.3,
  },

  cardNumber: {
    marginTop: 6,

    color:
      colors.textSoft,

    fontSize: 14,
  },


  /* ======================================================
     BADGES
     ====================================================== */

  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',

    gap: 7,

    marginTop: 16,
    marginBottom: 16,
  },

  badge: {
    paddingHorizontal: 11,
    paddingVertical: 6,

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

  butterBadge: {
    backgroundColor:
      colors.butter,
  },

  badgeText: {
    color:
      colors.text,

    fontSize: 12,
    fontWeight: '700',
  },


  /* ======================================================
     METADATEN
     ====================================================== */

  metadataGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',

    gap: 8,
  },

  metadataItem: {
    width: '48%',

    minWidth: 130,

    flexGrow: 1,

    padding: 12,

    backgroundColor:
      'rgba(255,255,255,0.76)',

    borderWidth: 1,

    borderColor:
      colors.border,

    borderRadius: 20,
  },

  metadataLabel: {
    color:
      colors.textFaint,

    fontSize: 9,
    fontWeight: '800',

    letterSpacing: 0.7,
  },

  metadataValue: {
    marginTop: 3,

    color:
      colors.text,

    fontSize: 13,
    fontWeight: '700',
  },


  /* ======================================================
     SIMILARITY
     ====================================================== */

  similarityBox: {
    marginTop: 12,

    padding: 14,

    borderRadius: 22,

    backgroundColor:
      'rgba(223,204,255,0.55)',
  },

  similarityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',

    gap: 12,
  },

  similarityLabel: {
    color:
      colors.textSoft,

    fontSize: 13,
  },

  similarityValue: {
    color:
      colors.text,

    fontSize: 16,
    fontWeight: '800',
  },

  similarityDescription: {
    marginTop: 5,

    color:
      colors.textSoft,

    fontSize: 11,
    lineHeight: 16,
  },


  /* ======================================================
     VARIANTEN
     ====================================================== */

  variantSection: {
    marginTop: 30,

    paddingTop: 24,

    borderTopWidth: 1,

    borderTopColor:
      colors.border,
  },

  stepLabel: {
    color:
      colors.lavenderStrong,

    fontSize: 11,
    fontWeight: '800',

    letterSpacing: 1.1,
  },

  sectionTitle: {
    marginTop: 3,
    marginBottom: 14,

    color:
      colors.text,

    fontSize: 24,
    fontWeight: '800',

    letterSpacing: -0.8,
  },


  variantGrid: {
    gap: 9,
  },

  variantGridWide: {
    flexDirection: 'row',
  },

  variantButton: {
    flex: 1,

    minHeight: 86,

    flexDirection: 'row',
    alignItems: 'center',

    gap: 10,

    padding: 13,

    backgroundColor:
      'rgba(255,255,255,0.78)',

    borderWidth: 2,

    borderColor:
      'transparent',

    borderTopLeftRadius: 25,
    borderTopRightRadius: 30,
    borderBottomLeftRadius: 29,
    borderBottomRightRadius: 22,
  },

  variantButtonSelected: {
    backgroundColor:
      colors.lavender,

    borderColor:
      colors.lavenderStrong,
  },

  variantButtonPressed: {
    opacity: 0.83,

    transform: [
      {
        scale: 0.985,
      },
    ],
  },

  variantIcon: {
    width: 40,
    height: 40,

    alignItems: 'center',
    justifyContent: 'center',

    borderRadius:
      radius.pill,

    backgroundColor:
      'rgba(255,255,255,0.78)',
  },

  variantIconText: {
    color:
      colors.text,

    fontSize: 19,
  },

  variantText: {
    flex: 1,
  },

  variantTitle: {
    color:
      colors.text,

    fontSize: 14,
    fontWeight: '800',
  },

  variantDescription: {
    marginTop: 2,

    color:
      colors.textSoft,

    fontSize: 10,
    lineHeight: 14,
  },


  /* ======================================================
     MARKTWERT-BUTTON
     ====================================================== */

  priceButton: {
    minHeight: 54,

    marginTop: 15,

    alignItems: 'center',
    justifyContent: 'center',

    borderTopLeftRadius: 27,
    borderTopRightRadius: 32,
    borderBottomLeftRadius: 31,
    borderBottomRightRadius: 24,

    backgroundColor:
      colors.lavenderStrong,

    ...shadow.button,
  },

  priceButtonDisabled: {
    opacity: 0.42,
  },

  priceButtonText: {
    color: '#FFFFFF',

    fontSize: 15,
    fontWeight: '800',
  },

  loadingPriceRow: {
    flexDirection: 'row',
    alignItems: 'center',

    gap: 9,
  },


  /* ======================================================
     PREIS
     ====================================================== */

  priceCard: {
    position: 'relative',

    marginTop: 18,

    padding: 24,

    alignItems: 'center',

    backgroundColor:
      colors.butter,

    borderTopLeftRadius: 34,
    borderTopRightRadius: 43,
    borderBottomLeftRadius: 45,
    borderBottomRightRadius: 31,

    ...shadow.card,
  },

  priceRefreshRow: {
    position: 'absolute',

    top: 12,
    right: 15,

    width: 24,
    height: 24,

    alignItems: 'center',
    justifyContent: 'center',
  },

  priceRefreshIcon: {
    color:
      colors.butterStrong,

    fontSize: 20,
    fontWeight: '800',
  },

  priceLabel: {
    color:
      colors.textSoft,

    fontSize: 14,
    fontWeight: '700',
  },

  priceValue: {
    marginTop: 5,

    color:
      colors.text,

    fontSize: 46,
    lineHeight: 52,

    fontWeight: '800',

    letterSpacing: -1.7,
  },

  priceMeta: {
    marginTop: 7,

    color:
      colors.textSoft,

    fontSize: 11,

    textAlign: 'center',
  },


  /* ======================================================
     RESET
     ====================================================== */

  resetButton: {
    minHeight: 52,

    marginTop: 18,

    alignItems: 'center',
    justifyContent: 'center',

    borderWidth: 1,

    borderColor:
      colors.border,

    borderRadius: 28,

    backgroundColor:
      'rgba(255,255,255,0.72)',
  },

  resetButtonText: {
    color:
      colors.textSoft,

    fontSize: 14,
    fontWeight: '700',
  },

  buttonPressed: {
    opacity: 0.82,

    transform: [
      {
        scale: 0.985,
      },
    ],
  },

});