#ifndef AUDIO_PLAYER_H
#define AUDIO_PLAYER_H

#include <SLES/OpenSLES.h>
#include <SLES/OpenSLES_Android.h>
#include <stdbool.h>

typedef struct {
  SLObjectItf engineObject;
  SLEngineItf engineEngine;

  SLObjectItf outputMixObject;

  SLObjectItf playerObject;
  SLPlayItf playerPlay;
  SLSeekItf playerSeek;
  SLMuteSoloItf playerMuteSolo;
  SLVolumeItf playerVolume;

  bool isPlaying;
  bool isPrepared;
  bool finished;
} AudioPlayer;

// Inisialisasi audio player
AudioPlayer *createAudioPlayer(const char *filePath);

// Setup player untuk URI
void setupUriAudioPlayer(AudioPlayer *player, const char *filePath);

// Mulai pemutaran
void playAudio(AudioPlayer *player);

// Jeda pemutaran
void pauseAudio(AudioPlayer *player);

// Hentikan pemutaran
void stopAudio(AudioPlayer *player);

// Set looping
void setLooping(AudioPlayer *player, bool loop);

// Dapatkan status pemutaran
bool isAudioPlaying(AudioPlayer *player);

// Bersihkan resources
void destroyAudioPlayer(AudioPlayer *player);

// Callback untuk pemutaran selesai
void SLAPIENTRY playbackCallback(SLPlayItf caller, void *context,
                                 SLuint32 event);

#endif // AUDIO_PLAYER_H
