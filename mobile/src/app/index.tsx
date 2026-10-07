import {
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from 'react-native';

import { PsyduckMascot } from '@/components/PsyduckMascot';

import {
  colors,
  radius,
  shadow,
  spacing,
} from '@/constants/theme';


export default function HomeScreen() {
  const { width } = useWindowDimensions();

  const isWideScreen = width >= 800;

  return (
    <SafeAreaView style={styles.safeArea}>

      {/* Hintergrund-Bubbles */}

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
      >

        {/* ======================================
            HEADER
        ====================================== */}

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


        {/* ======================================
            HERO
        ====================================== */}

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


          <PsyduckMascot />

        </View>


        {/* ======================================
            SCANNER CARD
        ====================================== */}

        <View style={styles.scannerCard}>

          <View style={styles.sectionHeader}>

            <Text style={styles.stepLabel}>
              SCHRITT 1
            </Text>

            <Text style={styles.sectionTitle}>
              Karte hinzufügen
            </Text>

          </View>


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


          {/* Buttons */}

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

        </View>


        {/* ======================================
            FOOTER
        ====================================== */}

        <Text style={styles.footer}>
          Studienprojekt zur optischen
          Pokémon-Kartenerkennung
        </Text>

      </ScrollView>

    </SafeAreaView>
  );
}


const styles = StyleSheet.create({

  safeArea: {
    flex: 1,

    backgroundColor:
      colors.background,
  },


  /* Hintergrund */

  background: {
    ...StyleSheet.absoluteFill,

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


  /* Layout */

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


  /* Header */

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


  /* Hero */

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
    fontWeight: '900',

    letterSpacing: 1.2,

    textAlign: 'center',
  },

  title: {
    maxWidth: 650,

    marginTop: 7,

    color: colors.text,

    fontSize: 44,
    lineHeight: 47,

    fontWeight: '900',

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


  /* Scanner */

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
    fontWeight: '900',

    letterSpacing: 1.1,

    marginBottom: 3,
  },

  sectionTitle: {
    color:
      colors.text,

    fontSize: 26,
    lineHeight: 31,

    fontWeight: '900',

    letterSpacing: -0.9,
  },

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


  /* Buttons */

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


  /* Footer */

  footer: {
    marginTop:
      spacing.xl,

    color:
      colors.textFaint,

    fontSize: 12,

    textAlign: 'center',
  },

});