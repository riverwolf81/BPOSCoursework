#include <SDL.h>
#include <SDL_ttf.h>
#include <dirent.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define W 640
#define H 480
#define LINE 22
#define MAX_FILES 1024

char cwd[512] = "/";

typedef struct {
    char *names[MAX_FILES];
    int count;
} DirList;

void draw_text(SDL_Renderer *r, TTF_Font *f, int x, int y, const char *txt, SDL_Color c) {
    SDL_Surface *s = TTF_RenderText_Solid(f, txt, c);
    if (!s) return;
    SDL_Texture *t = SDL_CreateTextureFromSurface(r, s);
    if (!t) { SDL_FreeSurface(s); return; }
    SDL_Rect rc = {x, y, s->w, s->h};
    SDL_RenderCopy(r, t, NULL, &rc);
    SDL_FreeSurface(s);
    SDL_DestroyTexture(t);
}

void load_dir(DirList *dl, const char *path) {
    for(int i=0;i<MAX_FILES;i++){
        free(dl->names[i]);
        dl->names[i]=NULL;
    }
    dl->count = 0;

    DIR *d = opendir(path);
    if (!d) {
        fprintf(stderr, "Failed to open directory: %s\n", path);
        return;
    }

    struct dirent *ent;
    while ((ent = readdir(d)) && dl->count < MAX_FILES) {
        dl->names[dl->count] = strdup(ent->d_name);
        dl->count++;
    }
    closedir(d);
}

void free_dirlist(DirList *dl) {
    for (int i=0;i<dl->count;i++) free(dl->names[i]);
    dl->count = 0;
}

int main() {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        return 1;
    }

    if (TTF_Init() < 0) {
        fprintf(stderr, "TTF_Init failed: %s\n", TTF_GetError());
        SDL_Quit();
        return 1;
    }

    // Try primary font
    TTF_Font *f = TTF_OpenFont("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16);
    if (!f) {
        fprintf(stderr, "Primary font not found, trying fallback: %s\n", TTF_GetError());
        f = TTF_OpenFont("/usr/share/fonts/FreeSans.ttf", 16);
    }
    if (!f) {
        fprintf(stderr, "No usable font found, exiting.\n");
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    SDL_Window *w = SDL_CreateWindow("File Manager",
        SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, W, H, 0);
    if (!w) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    SDL_Renderer *r = SDL_CreateRenderer(w, -1, SDL_RENDERER_SOFTWARE);
    if (!r) {
        fprintf(stderr, "SDL_CreateRenderer failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(w);
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    DirList dl;
    load_dir(&dl, cwd);
    int selected = 0;
    int scroll = 0;
    int max_visible = (H - 20) / LINE;

    int running = 1;
    SDL_Event e;

    while (running) {
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) running = 0;
            if (e.type == SDL_KEYDOWN) {
                switch (e.key.keysym.sym) {
                    case SDLK_ESCAPE: running = 0; break;
                    case SDLK_UP:
                        if (selected > 0) selected--;
                        if (selected < scroll) scroll--;
                        break;
                    case SDLK_DOWN:
                        if (selected < dl.count - 1) selected++;
                        if (selected >= scroll + max_visible) scroll++;
                        break;
                    case SDLK_RETURN: {
                        char next[512];
                        snprintf(next, sizeof(next), "%s/%s", cwd, dl.names[selected]);
                        DIR *d = opendir(next);
                        if (d) { // it's a directory
                            closedir(d);
                            strncpy(cwd, next, sizeof(cwd));
                            load_dir(&dl, cwd);
                            selected = 0;
                            scroll = 0;
                        }
                        break;
                    }
                    case SDLK_BACKSPACE: {
                        if (strcmp(cwd, "/") != 0) {
                            char *last = strrchr(cwd, '/');
                            if (last == cwd) *(last+1) = '\0'; // go to root
                            else *last = '\0';
                            load_dir(&dl, cwd);
                            selected = 0;
                            scroll = 0;
                        }
                        break;
                    }
                }
            }
        }

        SDL_SetRenderDrawColor(r, 0, 0, 0, 255);
        SDL_RenderClear(r);

        int y = 10;
        SDL_Color white = {255,255,255};
        SDL_Color yellow = {255,255,0};
        draw_text(r, f, 10, y, cwd, white);
        y += LINE;

        for (int i = scroll; i < dl.count && y < H; i++) {
            SDL_Color c = (i == selected) ? yellow : white;
            draw_text(r, f, 20, y, dl.names[i], c);
            y += LINE;
        }

        SDL_RenderPresent(r);
        SDL_Delay(50);
    }

    free_dirlist(&dl);
    TTF_CloseFont(f);
    TTF_Quit();
    SDL_DestroyRenderer(r);
    SDL_DestroyWindow(w);
    SDL_Quit();

    return 0;
}

