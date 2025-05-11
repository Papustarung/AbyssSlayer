import heapq

class AStarPathfinder:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_walkable(self, x, y):
        return (
            0 <= x < self.cols and 0 <= y < self.rows
            and self.grid[y][x] != "1"
        )

    def heuristic(self, a, b):
        # Octile distance (used in Unity)
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return 14 * min(dx, dy) + 10 * abs(dx - dy)

    def find_path(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, 0, start))  # (fScore, hScore, node)
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)

                if not self.is_walkable(*neighbor):
                    continue

                # ✋ Prevent diagonal clipping through corners
                if dx != 0 and dy != 0:
                    if not self.is_walkable(current[0] + dx, current[1]) or \
                            not self.is_walkable(current[0], current[1] + dy):
                        continue  # One of the sides is blocked

                move_cost = 14 if dx != 0 and dy != 0 else 10
                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, self.heuristic(neighbor, goal), neighbor))

        return []

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
