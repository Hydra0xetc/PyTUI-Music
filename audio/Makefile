CC       = gcc
SRC      = audio_player.c 
CFLAGS   = -Wall -Wextra -O2 -fPIC
LD_FLAGS = -shared -L/system/lib64/ -llog -lOpenSLES -landroid
OUT      = libAndroPlayer.so

.PHONY: all build

all: build patch

build: $(OUT)

$(OUT): $(SRC)
	$(CC) -o $(OUT) $(SRC) $(CFLAGS) $(LD_FLAGS)

# patch for android
patch: build
	patchelf $(OUT) --set-rpath /system/lib64/

clean:
	rm -f $(OUT)

rebuild: clean build
