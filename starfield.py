# return the RGB value for a pixel in a starfield image
def starfield_pixel(x, y, t):
    """
    Generate a starfield pixel color based on position (x, y) and time t.
    Stars twinkle and move to create a dynamic starfield effect.
    """
    import math
    import random

    # Parameters for starfield
    num_stars = 100
    width, height = 200, 200  # Assuming a 200x200 pixel starfield

    # Initialize star positions and brightness
    stars = []
    random.seed(42)  # For reproducibility
    for _ in range(num_stars):
        star_x = random.randint(0, width - 1)
        star_y = random.randint(0, height - 1)
        brightness = random.uniform(0.5, 1.0)
        stars.append((star_x, star_y, brightness))

    # Calculate pixel color
    r, g, b = 0, 0, 0
    for star_x, star_y, brightness in stars:
        # Calculate distance from the pixel to the star
        dist = math.sqrt((x - star_x) ** 2 + (y - star_y) ** 2)
        if dist < 5:  # Star influence radius
            # Twinkle effect based on time
            twinkle = (math.sin(t + dist) + 1) / 2  # Normalize to [0, 1]
            intensity = brightness * twinkle * (1 - dist / 5)
            r += int(255 * intensity)
            g += int(255 * intensity)
            b += int(255 * intensity)

    # Clamp values to [0, 255]
    r = min(255, r)
    g = min(255, g)
    b = min(255, b)

    return (r, g, b)