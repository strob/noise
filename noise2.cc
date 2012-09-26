// g++ -o noise2 noise2.cc -lSDL -lm

#include <SDL/SDL.h>
#include <stdio.h>
#include <math.h>

float freq = 200.0;             /* frequency */
float phase= 0.0;               /* phase */

float dist = 1.0;

void audio_out(void *udata, Uint8 *stream, int len) {

  /* We know that the stream _really_ is int16 */
  int16_t *real_stream;
  int real_len;

  real_stream = (int16_t*) stream;
  real_len = len / sizeof(int16_t);

  while(real_len--) {
    /* I didn't memorize eight digits of pi for nothing! */
    *real_stream++ += 16000 * \
      (sin( 2 * 3.1415926 * freq * phase / 44100.0 ) +                  \
       sin( (1.0+dist)*3.1415926 + 2 * 3.1415926 * freq * phase++ / 44100.0 ));
  }
}

int main(int argc, char *argv[]) {

  SDL_Event event;
  SDL_Surface *screen;
  SDL_AudioSpec desired;
  float old_freq;

  int cur_x;
  int cur_y;

  int antagonist_x = 100;
  int antagonist_y = 100;

  int n_w = 10;
  int n_h = 10;
  Uint32 sm_noise[n_w*n_h];
  for(int x=0; x<n_w; ++x) {
    for(int y=0; y<n_h; ++y) {
      sm_noise[x+y*n_w] = random();
    }
  }

  int nx_step = 640/n_w;
  int ny_step = 480/n_h;

  // interpolate into full rez
  Uint32 noise[640*480];
  float dx, dy;
  for(int x=0; x<640; ++x) {
    for(int y=0; y<480; ++y) {
      dx = (x % nx_step) / float(nx_step);
      dy = (y % ny_step) / float(ny_step);
      noise[x+y*640] = 0;

      int x_idx = (x/nx_step);
      int y_idx = (y/ny_step);
      int x1_idx = (x_idx + 1) % (n_w); /* wrap around */
      int y1_idx = (y_idx + 1) % (n_h);

      uint8_t* xy = (uint8_t*) &sm_noise[y_idx*n_w + x_idx];
      uint8_t* x1y = (uint8_t*) &sm_noise[y_idx*n_w + x1_idx];
      uint8_t* x1y1 = (uint8_t*) &sm_noise[y1_idx*n_w + x1_idx];
      uint8_t* xy1 = (uint8_t*) &sm_noise[y1_idx*n_w + x_idx];

      uint8_t* start = (uint8_t*) &noise[x+y*640];
      for(int i=0; i<4; ++i) {  /* colors */
        *start++ = (1.0-dx) * (1.0-dy) * xy[i] +                  \
          dx * (1.0-dy) * x1y[i] +                             \
          dx * dy * x1y1[i] +                                  \
          (1.0-dx) * dy * xy1[i];
      }
    }
  }

  // <boilerplate crap>
  if(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO) == -1) { 
    printf("no go sdl init: %s.\n", SDL_GetError());
    exit(1);
  }

  screen = SDL_SetVideoMode(640, 480, 32, 0);
  //screen = SDL_SetVideoMode(640, 480, 32, SDL_FULLSCREEN);

  if ( screen == NULL) {
    fprintf(stderr, "no go vid-e-o: %s\n", SDL_GetError());
    exit(1);
  }

  desired.freq = 44100;
  desired.format = AUDIO_S16;
  desired.channels = 2;
  desired.samples = 1024;
  desired.callback = audio_out;
  desired.userdata = NULL;

  if ( SDL_OpenAudio(&desired, NULL) < 0) {
    printf("i never get what i want");
    exit(1);
  }

  SDL_PauseAudio(0);

  // </boils>

  while( true ) {
  while ( SDL_PollEvent(&event) > 0 ) {
    switch (event.type) {
    case SDL_MOUSEMOTION: {
      cur_x = event.motion.x;
      cur_y = event.motion.y;

      dist = pow(pow((cur_x-antagonist_x)/640.0, 2) + \
                 pow((cur_y-antagonist_y)/480.0, 2),
                 0.5);
      break;
    }
    case SDL_KEYDOWN: {
      exit(0);
      break;
    }
    case SDL_QUIT: {
      exit(0);
      break;
    }
    }
  }
  antagonist_x = int(antagonist_x + pow(20*dist, 0.5)) % 640;

  SDL_LockSurface(screen);
  for(int sx=0; sx<640; ++sx) {
    for(int sy=0; sy<480; ++sy) {
      int x = (sx + cur_x) % 640;
      int y = (sy + cur_y) % 480;

      int ax = (sx + antagonist_x) % 640;
      int ay = (sy + antagonist_y) % 480;

      *((Uint32*) screen->pixels + sy*screen->w + sx) = noise[x+y*640] - noise[ax+ay*640];
    }
  }
  SDL_UnlockSurface(screen);
  SDL_UpdateRect(screen, 0, 0, 640, 480);
  }
}
