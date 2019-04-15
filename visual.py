import numpy as np
import cv2

from utils import Directions

p_up = np.array([
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,1,0,0,0,1],
    [1,0,0,1,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1]
])

patches = {
    Directions.UP: p_up,
    Directions.DOWN: p_up[::-1, :],
    Directions.RIGHT: p_up.transpose()[:, ::-1],
    Directions.LEFT: p_up.transpose(),
    Directions.NONE: np.zeros_like(p_up)
}


def save_dir_map(dir_map, tick):
    img = np.zeros((600, 600))
    for i in range(len(dir_map)):
        for j in range(len(dir_map[i])):
            img[i*10:i*10 + 10, j*10:j*10 + 10] = patches[dir_map[i, j]] * 255
    cv2.imwrite('out/{}.jpg'.format(tick), img)


def save_speed_map(speed_map, dir_map, tick):
    img = np.zeros((600, 600))
    for i in range(len(speed_map)):
        for j in range(len(speed_map[i])):
            img[i*10:i*10 + 10, j*10:j*10 + 10] = patches[dir_map[i, j]] * 255 / 3 * speed_map[i, j]
    cv2.imwrite('out/{}.jpg'.format(tick), img)


def save_poss_dir_map(dir_map):
    img = np.zeros((600, 600))
    for i in range(len(dir_map)):
        for j in range(len(dir_map[i])):
            patch = patches[Directions.NONE]
            for d in dir_map[i, j]:
                patch = np.logical_or(patch, patches[d])
            img[i*10:i*10 + 10, j*10:j*10 + 10] = patch * 255
    cv2.imwrite('out/poss.jpg', img)
