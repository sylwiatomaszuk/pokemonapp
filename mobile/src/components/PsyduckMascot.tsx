// mobile/src/components/PsyduckMascot.tsx

import {
  StyleSheet,
  Text,
  View,
} from 'react-native';

import {
  colors,
  radius,
  shadow,
} from '@/constants/theme';


type PsyduckMood =
  | 'default'
  | 'sad';


type PsyduckMascotProps = {
  message?: string;
  mood?: PsyduckMood;
};


export function PsyduckMascot({
  message =
    'Zeig mir deine Karte – ich schau sie mir an!',

  mood = 'default',
}: PsyduckMascotProps) {

  const isSad =
    mood === 'sad';


  return (
    <View style={styles.wrapper}>

      <View
        style={styles.characterWrapper}

        accessible

        accessibilityLabel={
          isSad
            ? 'Enton ist sich bei der Kartenerkennung nicht sicher'
            : 'Enton, das Maskottchen der App'
        }
      >

        <View
          style={[
            styles.psyduck,

            isSad &&
              styles.psyduckSad,
          ]}
        >

          <View
            style={[
              styles.hair,
              styles.hairLeft,

              isSad &&
                styles.hairLeftSad,
            ]}
          />

          <View
            style={[
              styles.hair,
              styles.hairCenter,

              isSad &&
                styles.hairCenterSad,
            ]}
          />

          <View
            style={[
              styles.hair,
              styles.hairRight,

              isSad &&
                styles.hairRightSad,
            ]}
          />


          <View
            style={[
              styles.eye,
              styles.eyeLeft,

              isSad &&
                styles.eyeSad,

              isSad &&
                styles.eyeLeftSad,
            ]}
          />

          <View
            style={[
              styles.eye,
              styles.eyeRight,

              isSad &&
                styles.eyeSad,

              isSad &&
                styles.eyeRightSad,
            ]}
          />


          {isSad && (
            <View style={styles.tear} />
          )}


          <View
            style={[
              styles.beak,

              isSad &&
                styles.beakSad,
            ]}
          >

            <View
              style={[
                styles.beakLine,

                isSad &&
                  styles.beakLineSad,
              ]}
            />

          </View>

        </View>


        <View
          style={[
            styles.yellowBubble,

            isSad &&
              styles.yellowBubbleSad,
          ]}
        />

      </View>


      <View
        style={[
          styles.speechBubble,

          isSad &&
            styles.speechBubbleSad,
        ]}
      >

        <View
          style={[
            styles.speechPointer,

            isSad &&
              styles.speechPointerSad,
          ]}
        />

        <Text style={styles.speechTitle}>

          {isSad
            ? 'Enton ist unsicher'
            : 'Enton hilft mit'}

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

    marginTop: 12,
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

    backgroundColor:
      'rgba(255, 227, 106, 0.22)',

    borderRadius:
      radius.bubble,

    transform: [
      {
        scaleX: 1.15,
      },
    ],

    zIndex: -1,
  },

  yellowBubbleSad: {
    backgroundColor:
      'rgba(207, 238, 255, 0.40)',
  },


  psyduck: {
    position: 'relative',

    width: 88,
    height: 82,

    backgroundColor:
      colors.psyduckYellow,

    borderTopLeftRadius: 47,
    borderTopRightRadius: 42,
    borderBottomLeftRadius: 38,
    borderBottomRightRadius: 48,

    alignItems: 'center',

    ...shadow.card,
  },

  psyduckSad: {
    transform: [
      {
        rotate: '-4deg',
      },
    ],
  },


  hair: {
    position: 'absolute',

    top: -15,

    width: 4,
    height: 27,

    borderRadius:
      radius.pill,

    backgroundColor:
      colors.text,
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


  hairLeftSad: {
    transform: [
      {
        rotate: '-35deg',
      },
    ],
  },

  hairCenterSad: {
    transform: [
      {
        rotate: '-8deg',
      },
    ],
  },

  hairRightSad: {
    transform: [
      {
        rotate: '12deg',
      },
    ],
  },


  eye: {
    position: 'absolute',

    top: 30,

    width: 8,
    height: 12,

    backgroundColor:
      colors.text,

    borderRadius:
      radius.pill,
  },

  eyeLeft: {
    left: 25,
  },

  eyeRight: {
    right: 25,
  },


  eyeSad: {
    width: 11,
    height: 5,

    top: 31,

    borderRadius: 5,
  },

  eyeLeftSad: {
    transform: [
      {
        rotate: '16deg',
      },
    ],
  },

  eyeRightSad: {
    transform: [
      {
        rotate: '-16deg',
      },
    ],
  },


  tear: {
    position: 'absolute',

    top: 41,
    right: 19,

    width: 7,
    height: 11,

    backgroundColor:
      colors.blueStrong,

    borderTopLeftRadius: 6,
    borderTopRightRadius: 6,
    borderBottomLeftRadius: 7,
    borderBottomRightRadius: 2,

    transform: [
      {
        rotate: '12deg',
      },
    ],

    opacity: 0.8,
  },


  beak: {
    position: 'absolute',

    width: 48,
    height: 26,

    bottom: 9,

    borderRadius: 22,

    backgroundColor:
      colors.psyduckBeak,

    alignItems: 'center',
    justifyContent: 'center',
  },

  beakSad: {
    bottom: 7,

    transform: [
      {
        rotate: '-3deg',
      },
    ],
  },


  beakLine: {
    width: 28,
    height: 1.5,

    marginTop: 5,

    borderRadius:
      radius.pill,

    backgroundColor:
      'rgba(92, 62, 42, 0.25)',
  },

  beakLineSad: {
    width: 23,

    marginTop: 2,

    transform: [
      {
        rotate: '-5deg',
      },
    ],
  },


  speechBubble: {
    position: 'relative',

    flex: 1,
    maxWidth: 280,

    paddingHorizontal: 18,
    paddingVertical: 14,

    borderRadius: 28,

    backgroundColor:
      '#FFF2B8',

    ...shadow.card,
  },

  speechBubbleSad: {
    backgroundColor:
      '#E8F4FF',
  },


  speechPointer: {
    position: 'absolute',

    left: -7,
    top: 29,

    width: 18,
    height: 18,

    backgroundColor:
      '#FFF2B8',

    transform: [
      {
        rotate: '45deg',
      },
    ],
  },

  speechPointerSad: {
    backgroundColor:
      '#E8F4FF',
  },


  speechTitle: {
    color:
      colors.text,

    fontSize: 14,
    fontWeight: '800',

    marginBottom: 2,
  },

  speechText: {
    color:
      colors.textSoft,

    fontSize: 13,
    lineHeight: 18,
  },

});