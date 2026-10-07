import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, shadow } from '@/constants/theme';

type PsyduckMascotProps = {
  message?: string;
};

export function PsyduckMascot({
  message = 'Zeig mir deine Karte – ich schau sie mir an!',
}: PsyduckMascotProps) {
  return (
    <View style={styles.wrapper}>
      <View
        style={styles.characterWrapper}
        accessible
        accessibilityLabel="Enton, das Maskottchen der App"
      >
        <View style={styles.psyduck}>
          {/* Haare */}
          <View style={[styles.hair, styles.hairLeft]} />
          <View style={[styles.hair, styles.hairCenter]} />
          <View style={[styles.hair, styles.hairRight]} />

          {/* Augen */}
          <View style={[styles.eye, styles.eyeLeft]} />
          <View style={[styles.eye, styles.eyeRight]} />

          {/* Schnabel */}
          <View style={styles.beak}>
            <View style={styles.beakLine} />
          </View>
        </View>

        <View style={styles.yellowBubble} />
      </View>

      <View style={styles.speechBubble}>
        <View style={styles.speechPointer} />

        <Text style={styles.speechTitle}>
          Enton hilft mit
        </Text>

        <Text style={styles.speechText}>
          {message}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    width: '100%',

    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',

    gap: 12,

    marginTop: 22,
  },

  characterWrapper: {
    position: 'relative',

    width: 92,
    height: 100,

    alignItems: 'center',
    justifyContent: 'center',
  },

  yellowBubble: {
    position: 'absolute',

    width: 86,
    height: 45,

    bottom: 0,

    backgroundColor: 'rgba(255, 227, 106, 0.22)',

    borderRadius: radius.bubble,

    transform: [
      {
        scaleX: 1.15,
      },
    ],

    zIndex: -1,
  },

  psyduck: {
    position: 'relative',

    width: 88,
    height: 82,

    backgroundColor: colors.psyduckYellow,

    borderTopLeftRadius: 47,
    borderTopRightRadius: 42,
    borderBottomLeftRadius: 38,
    borderBottomRightRadius: 48,

    alignItems: 'center',

    ...shadow.card,
  },

  hair: {
    position: 'absolute',

    top: -15,

    width: 4,
    height: 27,

    borderRadius: radius.pill,

    backgroundColor: colors.text,
  },

  hairLeft: {
    left: 33,

    transform: [
      {
        rotate: '-21deg',
      },
    ],
  },

  hairCenter: {
    left: 43,

    height: 30,
  },

  hairRight: {
    left: 53,

    transform: [
      {
        rotate: '21deg',
      },
    ],
  },

  eye: {
    position: 'absolute',

    top: 30,

    width: 8,
    height: 12,

    backgroundColor: colors.text,

    borderRadius: radius.pill,
  },

  eyeLeft: {
    left: 25,
  },

  eyeRight: {
    right: 25,
  },

  beak: {
    position: 'absolute',

    width: 48,
    height: 26,

    bottom: 9,

    borderRadius: 22,

    backgroundColor: colors.psyduckBeak,

    alignItems: 'center',
    justifyContent: 'center',
  },

  beakLine: {
    width: 28,
    height: 1.5,

    marginTop: 5,

    borderRadius: radius.pill,

    backgroundColor: 'rgba(92, 62, 42, 0.25)',
  },

  speechBubble: {
    position: 'relative',

    flex: 1,
    maxWidth: 280,

    paddingHorizontal: 18,
    paddingVertical: 14,

    borderRadius: 28,

    backgroundColor: '#FFF2B8',

    ...shadow.card,
  },

  speechPointer: {
    position: 'absolute',

    left: -7,
    top: 29,

    width: 18,
    height: 18,

    backgroundColor: '#FFF2B8',

    transform: [
      {
        rotate: '45deg',
      },
    ],
  },

  speechTitle: {
    color: colors.text,

    fontSize: 14,
    fontWeight: '800',

    marginBottom: 2,
  },

  speechText: {
    color: colors.textSoft,

    fontSize: 13,
    lineHeight: 18,
  },
});