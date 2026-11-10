        if curplayer == 0:
            tiles[curplayer][i].Rect.x = 50 * i
        else:
            tiles[curplayer][i].Rect.x = screen.width - (50 * i) - 60
        tiles[curplayer][i].Rect.y = racky
