import scipy.ndimage.interpolation as i

rotations = [
    (270 , (2, 1)),
    (180 , (1, 0)),
]

def rotate(movie, rot_enum):
    print 'ROTATE', rotations[rot_enum]
    angle, axes = rotations[rot_enum]
    return i.rotate(movie, angle, axes=axes, mode='nearest')
    # return movie

def imgbuf(rot_enum, tex_size, win):
    from psychopy.visual import ImageStim
    x, y = win.size
    size = (
        (x, tex_size)
            if rot_enum is 1 else
        (tex_size, y)
    )
    return ImageStim(
        win = win,
        size = size,
        units = 'pix',
    )
