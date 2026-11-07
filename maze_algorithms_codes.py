import heapq
import itertools
import time
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches


# =============================================================================
# 1. DỮ LIỆU BA MÊ CUNG
# =============================================================================
# h_walls (r, c): tường giữa (r, c) và (r + 1, c)
# v_walls (r, c): tường giữa (r, c) và (r, c + 1)
# =============================================================================

MAZES = {
    "Maze 1": {
        "size": 7,
        "center": (3, 3),
        "flags": {
            1: (6, 5),
            2: (0, 0),
            3: (0, 2),
        },
        "h_walls": [
            (0, 0), (0, 5),
            (1, 1), (1, 3), (1, 4), (1, 5),
            (2, 1), (2, 2), (2, 4),
            (3, 0), (3, 1), (3, 3), (3, 4), (3, 5),
            (4, 3), (4, 4),
            (5, 2), (5, 4), (5, 5),
        ],
        "v_walls": [
            (0, 1), (0, 3),
            (1, 1), (1, 2), (1, 4),
            (2, 0), (2, 5),
            (3, 2), (3, 3), (3, 5),
            (4, 1), (4, 2), (4, 5),
            (5, 0), (5, 2), (5, 5),
        ],
    },

    "Maze 2": {
        "size": 7,
        "center": (3, 3),
        "flags": {
            1: (6, 6),
            2: (5, 0),
            3: (0, 2),
        },
        "h_walls": [
            (0, 0), (0, 6),
            (1, 1), (1, 2), (1, 3),
            (2, 1), (2, 2),
            (3, 2), (3, 3), (3, 6),
            (4, 2), (4, 4), (4, 5),
            (5, 3),
        ],
        "v_walls": [
            (0, 1), (0, 3),
            (1, 1), (1, 4),
            (2, 3), (2, 4),
            (3, 0), (3, 3), (3, 4), (3, 5),
            (4, 3), (4, 4),
            (5, 0), (5, 4),
            (6, 1), (6, 5),
        ],
    },

    "Maze 3": {
        "size": 7,
        "center": (3, 3),
        "flags": {
            1: (1, 6),
            2: (0, 0),
            3: (6, 6),
        },
        "h_walls": [
            (0, 1), (0, 2), (0, 5),
            (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 2), (2, 5),
            (3, 1), (3, 4), (3, 5),
            (4, 0), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
            (5, 1),
        ],
        "v_walls": [
            (0, 3), (0, 5),
            (1, 0), (1, 3), (1, 5),
            (2, 0), (2, 3), (2, 5),
            (3, 0), (3, 2), (3, 3),
            (5, 1), (5, 3), (5, 5),
            (6, 2), (6, 4),
        ],
    },
}

# Thứ tự ưu tiên: Lên -> Phải -> Xuống -> Trái
DIRECTIONS = [
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1),
]


# =============================================================================
# 2. GIÁ TRỊ TRÊN SLIDE ĐỂ ĐỐI CHIẾU
# =============================================================================
# Runtime được lưu riêng như số liệu tham khảo trên slide, không phải thời gian
# đo được khi chạy chương trình này.
# =============================================================================

SLIDE_RESULTS = {
    ("Maze 1", "BFS"): {
        "exit": 3, "L": 4, "visited": 10, "max_open": 3,
        "efficiency": "40%", "nearest": "Yes", "runtime_ms": 0.0620,
    },
    ("Maze 1", "DFS"): {
        "exit": 3, "L": 4, "visited": 9, "max_open": 2,
        "efficiency": "44.44%", "nearest": "Yes", "runtime_ms": 0.0166,
    },
    ("Maze 1", "GBFS"): {
        "exit": 3, "L": 4, "visited": 5, "max_open": 3,
        "efficiency": "80%", "nearest": "Yes", "runtime_ms": 0.0225,
    },

    ("Maze 2", "BFS"): {
        "exit": 2, "L": 5, "visited": 21, "max_open": 6,
        "efficiency": "23,8%", "nearest": "Yes", "runtime_ms": 0.1597,
    },
    ("Maze 2", "DFS"): {
        "exit": 3, "L": 26, "visited": 37, "max_open": 10,
        "efficiency": "70.27%", "nearest": "No", "runtime_ms": 0.0465,
    },
    ("Maze 2", "GBFS"): {
        "exit": 2, "L": 5, "visited": 10, "max_open": 6,
        "efficiency": "50%", "nearest": "Yes", "runtime_ms": 0.0495,
    },

    ("Maze 3", "BFS"): {
        "exit": 1, "L": 7, "visited": 30, "max_open": 5,
        "efficiency": "23,33%", "nearest": "Yes", "runtime_ms": 0.1068,
    },
    ("Maze 3", "DFS"): {
        "exit": 2, "L": 10, "visited": 11, "max_open": 2,
        "efficiency": "90.91%", "nearest": "No", "runtime_ms": 0.0287,
    },
    ("Maze 3", "GBFS"): {
        "exit": 2, "L": 10, "visited": 11, "max_open": 2,
        "efficiency": "90.91%", "nearest": "No", "runtime_ms": 0.0514,
    },
}


# =============================================================================
# 3. CÁC HÀM XỬ LÝ MÊ CUNG
# =============================================================================

def build_blocked(cfg):
    """Tạo tập các cạnh bị tường chặn."""
    blocked = set()

    for r, c in cfg["h_walls"]:
        a = (r, c)
        b = (r + 1, c)
        blocked.add((a, b))
        blocked.add((b, a))

    for r, c in cfg["v_walls"]:
        a = (r, c)
        b = (r, c + 1)
        blocked.add((a, b))
        blocked.add((b, a))

    return blocked


def get_neighbors(cfg, blocked, cell):
    """Lấy các ô hợp lệ theo thứ tự Up -> Right -> Down -> Left."""
    r, c = cell
    neighbors = []

    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        neighbor = (nr, nc)

        if (
            0 <= nr < cfg["size"]
            and 0 <= nc < cfg["size"]
            and (cell, neighbor) not in blocked
        ):
            neighbors.append(neighbor)

    return neighbors


def reconstruct_path(parent, goal):
    """Truy vết đường đi từ Start đến Goal."""
    if goal is None:
        return []

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    return path[::-1]


def is_valid_path(cfg, blocked, path):
    """Kiểm tra đường đi có hợp lệ không."""
    if not path:
        return False

    if path[0] != cfg["center"]:
        return False

    if path[-1] not in cfg["flags"].values():
        return False

    if len(path) != len(set(path)):
        return False

    for a, b in zip(path, path[1:]):
        distance = abs(a[0] - b[0]) + abs(a[1] - b[1])

        if distance != 1 or (a, b) in blocked:
            return False

    return True


# =============================================================================
# 4. CÀI ĐẶT BFS, DFS, GBFS
# =============================================================================

def run_bfs(cfg, blocked):
    start = cfg["center"]
    goals = set(cfg["flags"].values())

    queue = deque([start])
    discovered = {start}
    discovered_order = [start]
    explored = []
    parent = {start: None}

    max_open = 1
    found_goal = None

    while queue:
        current = queue.popleft()
        explored.append(current)

        if current in goals:
            found_goal = current
            break

        for neighbor in get_neighbors(cfg, blocked, current):
            if neighbor not in discovered:
                discovered.add(neighbor)
                discovered_order.append(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

        max_open = max(max_open, len(queue))

    return {
        "algorithm": "BFS",
        "goal": found_goal,
        "path": reconstruct_path(parent, found_goal),
        "explored": explored,
        "discovered": discovered_order,

        # Theo cách đếm dùng trong bảng slide 14–17.
        "visited_cells": discovered_order,
        "max_open": max_open,
    }


def run_dfs(cfg, blocked):
    start = cfg["center"]
    goals = set(cfg["flags"].values())

    stack = [start]
    visited = set()
    explored = []
    parent = {start: None}

    max_open = 1
    found_goal = None

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        explored.append(current)

        if current in goals:
            found_goal = current
            break

        # Đẩy ngược để ưu tiên Up -> Right -> Down -> Left.
        for neighbor in reversed(get_neighbors(cfg, blocked, current)):
            if neighbor not in visited:
                parent[neighbor] = current
                stack.append(neighbor)

        max_open = max(max_open, len(stack))

    return {
        "algorithm": "DFS",
        "goal": found_goal,
        "path": reconstruct_path(parent, found_goal),
        "explored": explored,
        "visited_cells": explored,
        "max_open": max_open,
    }


def run_gbfs(cfg, blocked):
    start = cfg["center"]
    goals = set(cfg["flags"].values())

    def heuristic(cell):
        r, c = cell
        return min(
            abs(r - gr) + abs(c - gc)
            for gr, gc in goals
        )

    counter = itertools.count()
    frontier = [(heuristic(start), next(counter), start)]

    discovered = {start}
    discovered_order = [start]
    explored = []
    parent = {start: None}

    max_open = 1
    found_goal = None

    while frontier:
        _, _, current = heapq.heappop(frontier)
        explored.append(current)

        if current in goals:
            found_goal = current
            break

        for neighbor in get_neighbors(cfg, blocked, current):
            if neighbor not in discovered:
                discovered.add(neighbor)
                discovered_order.append(neighbor)
                parent[neighbor] = current

                heapq.heappush(
                    frontier,
                    (heuristic(neighbor), next(counter), neighbor),
                )

        max_open = max(max_open, len(frontier))

    return {
        "algorithm": "GBFS",
        "goal": found_goal,
        "path": reconstruct_path(parent, found_goal),
        "explored": explored,
        "discovered": discovered_order,
        "visited_cells": explored,
        "max_open": max_open,
    }


ALGORITHMS = [
    ("BFS", run_bfs),
    ("DFS", run_dfs),
    ("GBFS", run_gbfs),
]


# =============================================================================
# 5. ĐO VÀ ĐỐI CHIẾU KẾT QUẢ
# =============================================================================

def measure_runtime_ms(algo_func, cfg, blocked, repeats=2000):
    """Đo thời gian trung bình; không tính thời gian vẽ hoặc tạo tập tường."""
    if repeats <= 0:
        raise ValueError("repeats phải lớn hơn 0")

    algo_func(cfg, blocked)  # Warm-up

    start_time = time.perf_counter()

    for _ in range(repeats):
        algo_func(cfg, blocked)

    elapsed = time.perf_counter() - start_time
    return elapsed * 1000 / repeats


def efficiency_as_slide(maze_name, algo_name, length, visited_count):
    """
    Định dạng hiệu suất như slide.

    Riêng Maze 2/BFS dùng một chữ số thập phân và dấu phẩy.
    Maze 3/BFS dùng hai chữ số thập phân và dấu phẩy.
    """
    if length is None or visited_count == 0:
        return "N/A"

    value = 100 * length / visited_count

    if maze_name == "Maze 2" and algo_name == "BFS":
        return f"{value:.1f}".replace(".", ",") + "%"

    if maze_name == "Maze 3" and algo_name == "BFS":
        return f"{value:.2f}".replace(".", ",") + "%"

    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value))}%"

    return f"{value:.2f}%"


def prepare_result(maze_name, cfg, blocked, raw, shortest_length, runtime_ms):
    path = raw["path"]
    goal = raw["goal"]

    flag_by_position = {
        position: flag_id
        for flag_id, position in cfg["flags"].items()
    }

    flag_id = flag_by_position.get(goal)
    length = len(path) - 1 if path else None
    visited_count = len(raw["visited_cells"])

    nearest = (
        "Yes"
        if length is not None and length == shortest_length
        else "No"
    )

    return {
        **raw,
        "maze": maze_name,
        "exit_id": flag_id,
        "L": length,
        "visited_count": visited_count,
        "efficiency": efficiency_as_slide(
            maze_name,
            raw["algorithm"],
            length,
            visited_count,
        ),
        "nearest": nearest,
        "runtime_ms": runtime_ms,
        "valid": is_valid_path(cfg, blocked, path),
    }


def compare_with_slide(result):
    """So sánh các chỉ số cố định với bảng slide, không so sánh runtime."""
    key = (result["maze"], result["algorithm"])
    slide = SLIDE_RESULTS[key]

    actual = {
        "exit": result["exit_id"],
        "L": result["L"],
        "visited": result["visited_count"],
        "max_open": result["max_open"],
        "efficiency": result["efficiency"],
        "nearest": result["nearest"],
    }

    differences = []

    for field, value in actual.items():
        if value != slide[field]:
            differences.append(
                f"{field}: code={value}, slide={slide[field]}"
            )

    return differences


def print_result(result):
    key = (result["maze"], result["algorithm"])
    slide = SLIDE_RESULTS[key]

    print(f"\n--- {result['algorithm']} ---")
    print(f"Goal Reached       : Exit {result['exit_id']} {result['goal']}")
    print(f"Path Length        : {result['L']}")
    print(f"Visited Nodes      : {result['visited_count']}")
    print(f"Max Open           : {result['max_open']}")
    print(f"Efficiency         : {result['efficiency']}")
    print(f"Nearest Goal       : {result['nearest']}")
    print(f"Path Valid         : {result['valid']}")

    print(f"Runtime đo (ms)    : {result['runtime_ms']:.4f}")
    print(f"Runtime slide (ms) : {slide['runtime_ms']:.4f} [tham khảo]")

    print(f"Đường đi           : {result['path']}")
    print(f"Thứ tự explored    : {result['explored']}")

    if result["algorithm"] == "BFS":
        print(
            "BFS discovered     : "
            f"{len(result['discovered'])} ô"
        )
        print(
            "BFS explored       : "
            f"{len(result['explored'])} ô"
        )

    


# =============================================================================
# 6. VẼ MÊ CUNG
# =============================================================================

def render_maze(ax, cfg, path=None, visited=None, title=None):
    size = cfg["size"]
    path = path or []
    visited = visited or []

    path_set = set(path)
    flag_positions = set(cfg["flags"].values())

    ax.set_facecolor("#ffffff")
    ax.set_xlim(-0.1, size + 0.1)
    ax.set_ylim(size + 0.1, -0.1)
    ax.set_aspect("equal")
    ax.axis("off")

    # Lưới nền.
    for i in range(size + 1):
        ax.axhline(i, color="#f2f4f5", linewidth=1, zorder=1)
        ax.axvline(i, color="#f2f4f5", linewidth=1, zorder=1)

    # Các ô đã duyệt.
    for r, c in visited:
        if (
            (r, c) != cfg["center"]
            and (r, c) not in flag_positions
            and (r, c) not in path_set
        ):
            ax.add_patch(
                patches.Rectangle(
                    (c, r), 1, 1,
                    facecolor="#bce6ff",
                    edgecolor="none",
                    zorder=2,
                )
            )

    # Đường đi.
    for r, c in path:
        if (r, c) != cfg["center"] and (r, c) not in flag_positions:
            ax.add_patch(
                patches.Rectangle(
                    (c, r), 1, 1,
                    facecolor="#007acc",
                    edgecolor="none",
                    zorder=2,
                )
            )

            ax.plot(
                c + 0.5, r + 0.5,
                marker="o",
                markersize=6.5,
                color="#dce6f2",
                zorder=6,
            )

        elif (r, c) == cfg["center"]:
            ax.plot(
                c + 0.72, r + 0.5,
                marker="o",
                markersize=6.5,
                color="#dce6f2",
                zorder=6,
            )

        elif (r, c) in flag_positions:
            ax.plot(
                c + 0.65, r + 0.52,
                marker="o",
                markersize=6.5,
                color="#dce6f2",
                zorder=6,
            )

    # Các cờ.
    for flag_id, (r, c) in cfg["flags"].items():
        ax.add_patch(
            patches.Rectangle(
                (c, r), 1, 1,
                facecolor="#00b87c",
                edgecolor="none",
                zorder=3,
            )
        )

        fx = c + 0.42
        fy = r + 0.25

        ax.plot(
            [fx, fx],
            [fy, fy + 0.25],
            color="#a3f7d6",
            linewidth=1.8,
            zorder=4,
        )

        ax.add_patch(
            patches.Polygon(
                [
                    [fx, fy],
                    [fx + 0.2, fy + 0.07],
                    [fx, fy + 0.15],
                ],
                closed=True,
                edgecolor="#a3f7d6",
                facecolor="none",
                linewidth=1.5,
                zorder=4,
            )
        )

        ax.text(
            c + 0.5,
            r + 0.72,
            str(flag_id),
            color="white",
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=4,
        )

    # Ô Start.
    r, c = cfg["center"]

    ax.add_patch(
        patches.Rectangle(
            (c, r), 1, 1,
            facecolor="#132226",
            edgecolor="none",
            zorder=3,
        )
    )

    cx, cy = c + 0.5, r + 0.5

    ax.plot(
        [cx, cx],
        [cy - 0.18, cy + 0.06],
        color="white",
        linewidth=2,
        solid_capstyle="round",
        zorder=4,
    )

    ax.plot(
        [cx - 0.08, cx, cx + 0.08],
        [cy - 0.02, cy + 0.06, cy - 0.02],
        color="white",
        linewidth=2,
        solid_capstyle="round",
        zorder=4,
    )

    ax.plot(
        [cx - 0.14, cx - 0.14, cx + 0.14, cx + 0.14],
        [cy + 0.04, cy + 0.14, cy + 0.14, cy + 0.04],
        color="white",
        linewidth=2,
        solid_capstyle="round",
        zorder=4,
    )

    # Vách tường.
    wall_color = "#223135"
    gap = 0.06

    def draw_segment(x1, y1, x2, y2, linewidth=3.5):
        if x1 == x2:
            y_start = min(y1, y2) + gap
            y_end = max(y1, y2) - gap

            ax.plot(
                [x1, x2],
                [y_start, y_end],
                color=wall_color,
                linewidth=linewidth,
                solid_capstyle="round",
                zorder=5,
            )
        else:
            x_start = min(x1, x2) + gap
            x_end = max(x1, x2) - gap

            ax.plot(
                [x_start, x_end],
                [y1, y2],
                color=wall_color,
                linewidth=linewidth,
                solid_capstyle="round",
                zorder=5,
            )

    # Khung ngoài.
    for i in range(size):
        draw_segment(i, 0, i + 1, 0, linewidth=2.5)
        draw_segment(i, size, i + 1, size, linewidth=2.5)
        draw_segment(0, i, 0, i + 1, linewidth=2.5)
        draw_segment(size, i, size, i + 1, linewidth=2.5)

    # Tường bên trong.
    for r, c in cfg["h_walls"]:
        draw_segment(c, r + 1, c + 1, r + 1)

    for r, c in cfg["v_walls"]:
        draw_segment(c + 1, r, c + 1, r + 1)

    if title:
        ax.set_title(
            title,
            fontsize=11,
            fontweight="bold",
            color="#132226",
            pad=10,
        )


def show_figure(fig, show=True):
    """Chỉ hiển thị hình, không lưu thành file."""
    fig.tight_layout()

    if show:
        plt.show()

    plt.close(fig)


def draw_original_maze(maze_name, cfg, show=True):
    """Hiển thị mê cung mẫu, không lưu ảnh."""
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    fig.patch.set_facecolor("#ffffff")

    render_maze(
        ax,
        cfg,
        title=f"Mê cung mẫu — {maze_name}",
    )

    show_figure(fig, show)


def draw_solved_mazes(maze_name, cfg, results, show=True):
    """Hiển thị ba kết quả BFS, DFS, GBFS cạnh nhau, không lưu ảnh."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))
    fig.patch.set_facecolor("#ffffff")

    for ax, result in zip(axes, results):
        title = (
            f"{result['algorithm']} — {maze_name}\n"
            f"Exit {result['exit_id']} | L={result['L']} | "
            f"Visited={result['visited_count']}\n"
            f"Max Open={result['max_open']} | "
            f"Efficiency={result['efficiency']}"
        )

        render_maze(
            ax,
            cfg,
            path=result["path"],
            visited=result["visited_cells"],
            title=title,
        )

    # Đã bỏ fig.suptitle(...)
    show_figure(fig, show)


# =============================================================================
# 7. CHƯƠNG TRÌNH CHÍNH
# =============================================================================

def main(show_plots=True, repeats=2000):
    for maze_name, cfg in MAZES.items():
        print("\n" + "=" * 80)
        print(maze_name.upper())
        print("=" * 80)

        blocked = build_blocked(cfg)

        # BƯỚC 1: MÊ CUNG MẪU
        print("\nBƯỚC 1: MÊ CUNG MẪU")

        draw_original_maze(
            maze_name,
            cfg,
            show=show_plots,
        )

        # BƯỚC 2: CHẠY BA THUẬT TOÁN
        print("\nBƯỚC 2: GIẢI BẰNG BFS, DFS VÀ GBFS")

        bfs_reference = run_bfs(cfg, blocked)
        shortest_length = (
            len(bfs_reference["path"]) - 1
            if bfs_reference["path"]
            else None
        )

        solved_results = []

        for _, algo_func in ALGORITHMS:
            raw_result = algo_func(cfg, blocked)

            runtime_ms = measure_runtime_ms(
                algo_func,
                cfg,
                blocked,
                repeats=repeats,
            )

            result = prepare_result(
                maze_name,
                cfg,
                blocked,
                raw_result,
                shortest_length,
                runtime_ms,
            )

            solved_results.append(result)
            print_result(result)

        # BƯỚC 3: HIỂN THỊ MÊ CUNG ĐÃ GIẢI
        print("\nBƯỚC 3: MÊ CUNG ĐÃ GIẢI")

        draw_solved_mazes(
            maze_name,
            cfg,
            solved_results,
            show=show_plots,
        )

    print("\n" + "=" * 80)
    print("Hoàn tất.")
    print("=" * 80)


if __name__ == "__main__":
    main(
        show_plots=True,
        repeats=2000,
    )



    