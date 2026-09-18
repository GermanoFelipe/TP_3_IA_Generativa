import sys

NEIGHBORS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)

def read_grid(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return [line.replace("\r", "").replace("\n", "") for line in f]

def step(alive, rows, cols):
    candidates = set(alive)
    for r, c in alive:
        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                candidates.add((nr, nc))

    result = set()
    for r, c in candidates:
        neighbors = 0
        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) in alive:
                neighbors += 1

        if (r, c) in alive:
            if neighbors == 2 or neighbors == 3:
                result.add((r, c))
        else:
            if neighbors == 3:
                result.add((r, c))

    return result

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 vida.py <archivo_estado_inicial> <generaciones>")

    try:
        generations = int(sys.argv[2])
    except ValueError:
        sys.exit("Error: <generaciones> must be an integer")

    if generations < 0:
        sys.exit("Error: <generaciones> must be non-negative")

    grid = read_grid(sys.argv[1])
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    if generations == 0:
        output = grid
    else:
        alive = set()
        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch == "#":
                    alive.add((r, c))

        for _ in range(generations):
            if not alive:
                break
            new_alive = step(alive, rows, cols)
            if new_alive == alive:
                alive = new_alive
                break
            alive = new_alive

        output = []
        for r in range(rows):
            output.append("".join("#" if (r, c) in alive else "." for c in range(cols)))

    out = "\n".join(output)
    if output:
        out += "\n"
    sys.stdout.buffer.write(out.encode("ascii"))

if __name__ == "__main__":
    main()
