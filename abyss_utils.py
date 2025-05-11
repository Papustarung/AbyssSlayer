

def circle_rect_collision(circle_center, radius, rect):
    cx, cy = circle_center

    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))

    dx = cx - closest_x
    dy = cy - closest_y

    return dx * dx + dy * dy <= radius * radius
