


import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque


# ====================================================================
# 1. DU LIEU ME CUNG (lay nguyen tu file cua Duy)
#    h_walls (r,c): tuong giua o (r,c) va (r+1,c)
#    v_walls (r,c): tuong giua o (r,c) va (r,c+1)
# ====================================================================
MAZES = {
    2: {
        'size': 7, 'center': (3, 3),
        'flags': {1: (6, 6), 2: (5, 0), 3: (0, 2)},
        'h_walls': [(0, 0), (0, 6), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 2), (3, 3), (3, 6), (4, 2), (4, 4), (4, 5), (5, 3)],
        'v_walls': [(0, 1), (0, 3), (1, 1), (1, 4), (2, 3), (2, 4), (3, 0), (3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (5, 0), (5, 4), (6, 1), (6, 5)],
    },
    3: {
        'size': 7, 'center': (3, 3),
        'flags': {1: (1, 6), 2: (0, 0), 3: (6, 6)},
        'h_walls': [(0, 1), (0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 5), (3, 1), (3, 4), (3, 5), (4, 0), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, 1)],
        'v_walls': [(0, 3), (0, 5), (1, 0), (1, 3), (1, 5), (2, 0), (2, 3), (2, 5), (3, 0), (3, 2), (3, 3), (5, 1), (5, 3), (5, 5), (6, 2), (6, 4)],
    },
    4: {
        'size': 7, 'center': (3, 3),
        'flags': {1: (6, 5), 2: (0, 0), 3: (0, 2)},
        'h_walls': [(0, 0), (0, 5), (1, 1), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2), (2, 4), (3, 0), (3, 1), (3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (5, 2), (5, 4), (5, 5)],
        'v_walls': [(0, 1), (0, 3), (1, 1), (1, 2), (1, 4), (2, 0), (2, 5), (3, 2), (3, 3), (3, 5), (4, 1), (4, 2), (4, 5), (5, 0), (5, 2), (5, 5)],
    },
}


# Thu tu uu tien xet o lan can: Tren -> Phai -> Duoi -> Trai
DIRECTIONS = [(-1, 0, "Up"), (0, 1, "Right"), (1, 0, "Down"), (0, -1, "Left")]




def build_blocked(cfg):
    blocked = set()
    for r, c in cfg["h_walls"]:
        blocked.add(((r, c), (r + 1, c))); blocked.add(((r + 1, c), (r, c)))
    for r, c in cfg["v_walls"]:
        blocked.add(((r, c), (r, c + 1))); blocked.add(((r, c + 1), (r, c)))
    return blocked




def get_neighbors(cfg, blocked, r, c):
    
    res = []
    for dr, dc, _ in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < cfg["size"] and 0 <= nc < cfg["size"] and ((r, c), (nr, nc)) not in blocked:
            res.append((nr, nc))
    return res




# ====================================================================
# 2. THUAT TOAN DFS
# ====================================================================
def dfs(cfg):
    blocked = build_blocked(cfg)
    start = cfg["center"]
    goals = set(cfg["flags"].values())
    stack = [start]                 # Open: ngan xep (LIFO)
    parent = {start: None}          # truy vet duong di
    visited = set()                 # tap da duyet (da lay ra khoi stack)
    explored = []                   # thu tu cac o duoc lay ra khoi stack
    max_open = 1                    # so o toi da trong stack tai mot thoi diem
    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        explored.append(cur)
        if cur in goals:            # toi mot la co bat ky -> dung
            path = []
            while cur is not None:
                path.append(cur); cur = parent[cur]
            return path[::-1], explored, max_open
        # day nguoc de o dau tien trong thu tu uu tien (Tren) duoc lay ra truoc
        for nb in reversed(get_neighbors(cfg, blocked, *cur)):
            if nb not in visited:
                parent[nb] = cur    # ghi de de luu dung nut cha cua ban duoc pop
                stack.append(nb)
        max_open = max(max_open, len(stack))
    return None, explored, max_open




def bfs_shortest(cfg):
   
    blocked = build_blocked(cfg)
    start = cfg["center"]
    dist = {start: 0}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nb in get_neighbors(cfg, blocked, *cur):
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                q.append(nb)
    return {n: dist.get(pos) for n, pos in cfg["flags"].items()}




def is_valid(cfg, path):
    blocked = build_blocked(cfg)
    if not path or path[0] != cfg["center"] or path[-1] not in cfg["flags"].values():
        return False
    if len(set(path)) != len(path):
        return False
    return all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 and (a, b) not in blocked
               for a, b in zip(path, path[1:]))




def evaluate(num, cfg, repeats=2000):
    path, explored, max_open = dfs(cfg)
    t0 = time.perf_counter()
    for _ in range(repeats):
        dfs(cfg)
    ms = (time.perf_counter() - t0) / repeats * 1000
    flag_of = {pos: n for n, pos in cfg["flags"].items()}
    shortest = bfs_shortest(cfg)
    L = len(path) - 1
    best = min(d for d in shortest.values() if d is not None)
    return {
        "maze": num, "path": path, "explored": explored,
        "flag": flag_of[path[-1]], "goal": path[-1], "L": L,
        "visited": len(explored), "max_open": max_open,
        "ratio": 100.0 * L / len(explored), "nearest": "Co" if L == best else "Khong",
        "best": best, "shortest": shortest, "ms": ms, "valid": is_valid(cfg, path),
    }




# ====================================================================
# 3. VE ME CUNG (dung nguyen format va mau sac goc cua Duy)
# ====================================================================
def draw_maze(cfg, path=None, visited=None, title=None, out=None):
    size = cfg["size"]
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')


    ax.set_xlim(-0.1, size + 0.1)
    ax.set_ylim(size + 0.1, -0.1)
    ax.set_aspect('equal')
    ax.axis('off')


    # 1. Luoi nen mo
    for i in range(size + 1):
        ax.axhline(i, color='#f2f4f5', linewidth=1, zorder=1)
        ax.axvline(i, color='#f2f4f5', linewidth=1, zorder=1)


    path_set = set(path) if path else set()
    flag_values = set(cfg["flags"].values())


    # 2. To mau xanh nhat (#bce6ff) cho cac o da duyet
    if visited:
        for (vr, vc) in visited:
            if (vr, vc) != cfg["center"] and (vr, vc) not in flag_values and (vr, vc) not in path_set:
                rect = patches.Rectangle((vc, vr), 1, 1, facecolor='#bce6ff', edgecolor='none', zorder=2)
                ax.add_patch(rect)


    # 3. To mau xanh dam (#007acc) va cham tron cho duong di
    if path:
        for (pr, pc) in path:
            if (pr, pc) != cfg["center"] and (pr, pc) not in flag_values:
                rect = patches.Rectangle((pc, pr), 1, 1, facecolor='#007acc', edgecolor='none', zorder=2)
                ax.add_patch(rect)
                ax.plot(pc + 0.5, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) == cfg["center"]:
                ax.plot(pc + 0.72, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) in flag_values:
                ax.plot(pc + 0.65, pr + 0.52, marker='o', markersize=6.5, color='#dce6f2', zorder=6)


    # 4. Ve cac o Co mau xanh la (Flags 1, 2, 3)
    for flag_num, (fr, fc) in cfg["flags"].items():
        rect = patches.Rectangle((fc, fr), 1, 1, facecolor='#00b87c', edgecolor='none', zorder=3)
        ax.add_patch(rect)
        fx, fy = fc + 0.42, fr + 0.25
        ax.plot([fx, fx], [fy, fy + 0.25], color='#a3f7d6', linewidth=1.8, zorder=4)
        flag_poly = patches.Polygon([[fx, fy], [fx + 0.2, fy + 0.07], [fx, fy + 0.15]],
                                    closed=True, edgecolor='#a3f7d6', facecolor='none', linewidth=1.5, zorder=4)
        ax.add_patch(flag_poly)
        ax.text(fc + 0.5, fr + 0.72, str(flag_num), color='white', fontsize=11,
                fontweight='bold', ha='center', va='center', zorder=4)


    # 5. Ve o Trung tam mau den (Center node)
    cr, cc = cfg["center"]
    center_rect = patches.Rectangle((cc, cr), 1, 1, facecolor='#132226', edgecolor='none', zorder=3)
    ax.add_patch(center_rect)


    cx, cy = cc + 0.5, cr + 0.5
    ax.plot([cx, cx], [cy - 0.18, cy + 0.06], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.08, cx, cx + 0.08], [cy - 0.02, cy + 0.06, cy - 0.02], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.14, cx - 0.14, cx + 0.14, cx + 0.14],
            [cy + 0.04, cy + 0.14, cy + 0.14, cy + 0.04], color='white', linewidth=2, solid_capstyle='round', zorder=4)


    # 6. Ve cac vach tuong
    wall_color = '#223135'
    wall_width = 3.5
    gap = 0.06


    def draw_segment(x1, y1, x2, y2, lw=wall_width):
        if x1 == x2:
            y_start, y_end = min(y1, y2) + gap, max(y1, y2) - gap
            ax.plot([x1, x2], [y_start, y_end], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)
        else:
            x_start, x_end = min(x1, x2) + gap, max(x1, x2) - gap
            ax.plot([x_start, x_end], [y1, y2], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)


    for i in range(size):
        draw_segment(i, 0, i + 1, 0, lw=2.5)
        draw_segment(i, size, i + 1, size, lw=2.5)
        draw_segment(0, i, 0, i + 1, lw=2.5)
        draw_segment(size, i, size, i + 1, lw=2.5)


    for r, c in cfg["h_walls"]:
        draw_segment(c, r + 1, c + 1, r + 1)
    for r, c in cfg["v_walls"]:
        draw_segment(c + 1, r, c + 1, r + 1)


    if title:
        plt.title(title, fontsize=14, fontweight='bold', pad=12, color='#132226')
    plt.tight_layout()
    if out:
        fig.savefig(out)
    plt.show()




# ====================================================================
# 4. CHAY VA GHI KET QUA (in theo cung khuon voi code GBFS cua Vinh)
#    Ten me cung theo muc trong file cua Duy: 1.1 = me cung 4, 1.2 = me cung 2, 1.3 = me cung 3
# ====================================================================
MAZE_NAMES = {"Maze 1.1": 4, "Maze 1.2": 2, "Maze 1.3": 3}




def nhan_xet(r):
    if r["nearest"] == "Có":
        return ("DFS tìm được đường đi ngắn nhất (do đường tới đích gần nhất là duy nhất "
                "trong vùng nhánh dạng cây, dù vẫn duyệt nhầm vào nhánh cụt 4 ô trước).")
    return (f"DFS không tối ưu: ra Cờ {r['flag']} sau {r['L']} bước, "
            f"trong khi cờ gần nhất chỉ cách {r['best']} bước.")




if __name__ == "__main__":
    for name, num in MAZE_NAMES.items():
        if num not in MAZES:
            continue
        r = evaluate(num, MAZES[num])
        r["nearest"] = "Có" if r["nearest"] == "Co" else "Không"
        print(f"========== {name} ==========")
        print(f"Maze: {name}")
        print("Thuật toán: DFS")
        print(f"Đích tìm được: {r['flag']} {r['goal']}")
        print(f"Path Length: {r['L']}")
        print(f"Visited: {r['visited']}")
        print(f"Max Open: {r['max_open']}")
        print(f"Efficiency (%): {round(r['ratio'], 2)}")
        print(f"Nearest Goal: {r['nearest']}")
        print(f"Runtime (ms): {r['ms']:.4f}")
        print(f"Nhận xét: {nhan_xet(r)}")
        print(f"Đường đi: {r['path']}")
        print(f"Thứ tự duyệt: {r['explored']}")
        print()
        draw_maze(MAZES[num], r["path"], r["explored"],
                  f"DFS - {name}: Cờ {r['flag']}, L={r['L']}, Visited={r['visited']}",
                  f"dfs_{name.replace(' ', '_').replace('.', '_')}.png")

import heapq
import itertools
import time
from collections import deque
def gbfs(config, get_neighbors):

    start_time = time.perf_counter()

    # 1. Khởi tạo
    start = config["center"]
    exits = set(config["flags"].values())

    frontier = []
    visited = []
    parent = {}

    counter = itertools.count()

    def heuristic(position):
        x, y = position
        return min(
            abs(x - ex) + abs(y - ey)
            for ex, ey in exits
        )

    # 2. Đưa Start vào Priority Queue
    heapq.heappush(
        frontier,
        (heuristic(start), next(counter), start)
    )

    discovered = {start}
    parent[start] = None

    max_open = len(frontier)
    found_goal = None

    # 3. Vòng lặp tìm kiếm
    while frontier:

        _, _, current = heapq.heappop(frontier)
        visited.append(current)

        if current in exits:
            found_goal = current
            break

        for neighbor, move_name in get_neighbors(*current):

            if neighbor in discovered:
                continue

            discovered.add(neighbor)
            parent[neighbor] = current

            heapq.heappush(
                frontier,
                (heuristic(neighbor), next(counter), neighbor)
            )

        max_open = max(max_open, len(frontier))

    # 4. Truy vết đường đi
    path = []

    if found_goal is not None:
        current = found_goal

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()

    # 5. Tính thời gian
    runtime_ms = (time.perf_counter() - start_time) * 1000

    return {
        "path": path,
        "explored": visited,
        "exit": found_goal,
        "max_open": max_open,
        "runtime_ms": runtime_ms
    }

import matplotlib.pyplot as plt
import matplotlib.patches as patches


# =====================================================================
# 1. CẤU HÌNH DỮ LIỆU MÊ CUNG 7x7 SỐ 1 & LUẬT DI CHUYỂN
# =====================================================================

MAZE_1_CONFIG = {
    "size": 7,
    "center": (3, 3),  # Ô màu đen ở giữa (Mở lối đi phía trên sang ô (2, 3))
    "flags": {
        1: (6, 5),     # Cờ 1 (Hàng 6, Cột 5)
        2: (0, 0),     # Cờ 2 (Hàng 0, Cột 0)
        3: (0, 2)      # Cờ 3 (Hàng 0, Cột 2)
    },
    # Tường ngang: ngăn cách giữa ô (r, c) và (r + 1, c)
    "h_walls": [
        (0, 0), (0, 5),
        (1, 1), (1, 3), (1, 4), (1, 5),
        (2, 1), (2, 2), (2, 4),
        (3, 0), (3, 1), (3, 3), (3, 4), (3, 5),
        (4, 3), (4, 4),
        (5, 2), (5, 4), (5, 5)
    ],
    # Tường dọc: ngăn cách giữa ô (r, c) và (r, c + 1)
    "v_walls": [
        (0, 1), (0, 3),
        (1, 1), (1, 2), (1, 4),
        (2, 0), (2, 5),
        (3, 2), (3, 3), (3, 5),
        (4, 1), (4, 2), (4, 5),
        (5, 0), (5, 2), (5, 5)
    ]
}

# Khởi tạo tập hợp tra cứu tường nhanh O(1)
BLOCKED_EDGES_1 = set()
for r, c in MAZE_1_CONFIG["h_walls"]:
    BLOCKED_EDGES_1.add(((r, c), (r + 1, c)))
    BLOCKED_EDGES_1.add(((r + 1, c), (r, c)))
for r, c in MAZE_1_CONFIG["v_walls"]:
    BLOCKED_EDGES_1.add(((r, c), (r, c + 1)))
    BLOCKED_EDGES_1.add(((r, c + 1), (r, c)))

# Thứ tự ưu tiên xét ô lân cận: Lên -> Phải -> Xuống -> Trái
DIRECTIONS = [
    (-1, 0, "Up"),
    (0, 1, "Right"),
    (1, 0, "Down"),
    (0, -1, "Left")
]

def get_neighbors_maze4(r, c):
    """Hàm chuẩn lấy danh sách các ô lân cận hợp lệ theo thứ tự ưu tiên."""
    size = MAZE_1_CONFIG["size"]
    neighbors = []
    for dr, dc, move_name in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            if ((r, c), (nr, nc)) not in BLOCKED_EDGES_1:
                neighbors.append(((nr, nc), move_name))
    return neighbors


# =====================================================================
# 2. HÀM VẼ ĐỒ HỌA MÊ CUNG GỐC SỐ 4
# =====================================================================

def draw_maze_1(path=None, visited=None, title=None):
    """
    Hàm vẽ mê cung 7x7 số 1:
    - Mặc định gọi draw_maze_1() chỉ hiển thị mê cung gốc trắng tinh (chưa giải).
    - Hỗ trợ truyền `visited` và `path` để vẽ màu xanh nhạt/xanh đậm và chấm tròn.
    """
    size = MAZE_1_CONFIG["size"]
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Đảo trục Y để hàng 0 ở trên cùng, hàng 6 ở dưới cùng
    ax.set_xlim(-0.1, size + 0.1)
    ax.set_ylim(size + 0.1, -0.1)
    ax.set_aspect('equal')
    ax.axis('off')

    # 1. Vẽ lưới nền mờ (Grid lines)
    for i in range(size + 1):
        ax.axhline(i, color='#f2f4f5', linewidth=1, zorder=1)
        ax.axvline(i, color='#f2f4f5', linewidth=1, zorder=1)

    path_set = set(path) if path else set()

    # 2. Tô màu xanh nhạt (#bce6ff) cho các ô đã duyệt (nếu truyền vào)
    if visited:
        for (vr, vc) in visited:
            if (vr, vc) != MAZE_1_CONFIG["center"] and (vr, vc) not in MAZE_1_CONFIG["flags"].values() and (vr, vc) not in path_set:
                rect = patches.Rectangle((vc, vr), 1, 1, facecolor='#bce6ff', edgecolor='none', zorder=2)
                ax.add_patch(rect)

    # 3. Tô màu xanh đậm (#007acc) và chấm tròn cho đường đi (nếu truyền vào)
    if path:
        for (pr, pc) in path:
            if (pr, pc) != MAZE_1_CONFIG["center"] and (pr, pc) not in MAZE_1_CONFIG["flags"].values():
                rect = patches.Rectangle((pc, pr), 1, 1, facecolor='#007acc', edgecolor='none', zorder=2)
                ax.add_patch(rect)
                ax.plot(pc + 0.5, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) == MAZE_1_CONFIG["center"]:
                ax.plot(pc + 0.72, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) in MAZE_1_CONFIG["flags"].values():
                ax.plot(pc + 0.65, pr + 0.52, marker='o', markersize=6.5, color='#dce6f2', zorder=6)

    # 4. Vẽ các ô Cờ màu xanh lá (Flags 1, 2, 3)
    for flag_num, (fr, fc) in MAZE_1_CONFIG["flags"].items():
        rect = patches.Rectangle((fc, fr), 1, 1, facecolor='#00b87c', edgecolor='none', zorder=3)
        ax.add_patch(rect)
        # Vẽ biểu tượng lá cờ
        fx, fy = fc + 0.42, fr + 0.25
        ax.plot([fx, fx], [fy, fy + 0.25], color='#a3f7d6', linewidth=1.8, zorder=4)
        flag_poly = patches.Polygon([[fx, fy], [fx + 0.2, fy + 0.07], [fx, fy + 0.15]], 
                                    closed=True, edgecolor='#a3f7d6', facecolor='none', linewidth=1.5, zorder=4)
        ax.add_patch(flag_poly)
        # Số thứ tự cờ
        ax.text(fc + 0.5, fr + 0.72, str(flag_num), color='white', fontsize=11, 
                fontweight='bold', ha='center', va='center', zorder=4)

    # 5. Vẽ ô Trung tâm màu đen (Center node)
    cr, cc = MAZE_1_CONFIG["center"]
    center_rect = patches.Rectangle((cc, cr), 1, 1, facecolor='#132226', edgecolor='none', zorder=3)
    ax.add_patch(center_rect)
    
    # Vẽ icon khay & mũi tên chỉ xuống
    cx, cy = cc + 0.5, cr + 0.5
    ax.plot([cx, cx], [cy - 0.18, cy + 0.06], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.08, cx, cx + 0.08], [cy - 0.02, cy + 0.06, cy - 0.02], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.14, cx - 0.14, cx + 0.14, cx + 0.14], 
            [cy + 0.04, cy + 0.14, cy + 0.14, cy + 0.04], color='white', linewidth=2, solid_capstyle='round', zorder=4)

    # 6. Vẽ các vách tường
    wall_color = '#223135'
    wall_width = 3.5
    gap = 0.06

    def draw_segment(x1, y1, x2, y2, lw=wall_width):
        if x1 == x2:  # Đoạn dọc
            y_start, y_end = min(y1, y2) + gap, max(y1, y2) - gap
            ax.plot([x1, x2], [y_start, y_end], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)
        else:         # Đoạn ngang
            x_start, x_end = min(x1, x2) + gap, max(x1, x2) - gap
            ax.plot([x_start, x_end], [y1, y2], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)

    # Vẽ khung viền ngoài cùng (Riêng cạnh trên của Cờ 2 và Cờ 3 không vẽ nét tường đậm theo đúng ảnh)
    for i in range(size):
        if i not in (0, 2):  # Cờ 2 (0,0) và Cờ 3 (0,2) chạm sát mép trên không có viền đen
            draw_segment(i, 0, i + 1, 0, lw=2.5)
        if i != 5:           # Cờ 1 (6,5) chạm sát mép dưới
            draw_segment(i, size, i + 1, size, lw=2.5)
        if i != 0:           # Cờ 2 (0,0) chạm sát mép trái
            draw_segment(0, i, 0, i + 1, lw=2.5)
        draw_segment(size, i, size, i + 1, lw=2.5)

    # Vẽ tường ngang và tường dọc bên trong
    for r, c in MAZE_1_CONFIG["h_walls"]:
        draw_segment(c, r + 1, c + 1, r + 1)

    for r, c in MAZE_1_CONFIG["v_walls"]:
        draw_segment(c + 1, r, c + 1, r + 1)

    if title:
        plt.title(title, fontsize=14, fontweight='bold', pad=12, color='#132226')
    plt.tight_layout()
    plt.show()


# =====================================================================
# 3. HIỂN THỊ MÊ CUNG GỐC SỐ 4 (CHƯA GIẢI)
# =====================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =====================================================================
# 1. CẤU HÌNH DỮ LIỆU MÊ CUNG 7x7 SỐ 2 & LUẬT DI CHUYỂN
# =====================================================================

MAZE_2_CONFIG = {
    "size": 7,
    "center": (3, 3),  # Ô màu đen ở giữa (Mở lối đi bên trái sang ô (3, 2))
    "flags": {
        1: (6, 6),     # Cờ 1 (Góc dưới cùng bên phải)
        2: (5, 0),     # Cờ 2 (Hàng 5, Cột 0)
        3: (0, 2)      # Cờ 3 (Hàng 0, Cột 2)
    },
    # Tường ngang: ngăn cách giữa ô (r, c) và (r + 1, c)
    "h_walls": [
        (0, 0), (0, 6),
        (1, 1), (1, 2), (1, 3),
        (2, 1), (2, 2),
        (3, 2), (3, 3), (3, 6),
        (4, 2), (4, 4), (4, 5),
        (5, 3)
    ],
    # Tường dọc: ngăn cách giữa ô (r, c) và (r, c + 1)
    "v_walls": [
        (0, 1), (0, 3),
        (1, 1), (1, 4),
        (2, 3), (2, 4),
        (3, 0), (3, 3), (3, 4), (3, 5),
        (4, 3), (4, 4),
        (5, 0), (5, 4),
        (6, 1), (6, 5)
    ]
}

# Khởi tạo tập hợp tra cứu tường nhanh O(1)
BLOCKED_EDGES_2 = set()
for r, c in MAZE_2_CONFIG["h_walls"]:
    BLOCKED_EDGES_2.add(((r, c), (r + 1, c)))
    BLOCKED_EDGES_2.add(((r + 1, c), (r, c)))
for r, c in MAZE_2_CONFIG["v_walls"]:
    BLOCKED_EDGES_2.add(((r, c), (r, c + 1)))
    BLOCKED_EDGES_2.add(((r, c + 1), (r, c)))

# Thứ tự ưu tiên xét ô lân cận: Lên -> Phải -> Xuống -> Trái
DIRECTIONS = [
    (-1, 0, "Up"),
    (0, 1, "Right"),
    (1, 0, "Down"),
    (0, -1, "Left")
]

def get_neighbors_maze2(r, c):
    """Hàm chuẩn lấy danh sách các ô lân cận hợp lệ theo thứ tự ưu tiên."""
    size = MAZE_2_CONFIG["size"]
    neighbors = []
    for dr, dc, move_name in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            if ((r, c), (nr, nc)) not in BLOCKED_EDGES_2:
                neighbors.append(((nr, nc), move_name))
    return neighbors


# =====================================================================
# 2. HÀM VẼ ĐỒ HỌA MÊ CUNG GỐC (KÈM STYLE XANH DƯƠNG KHI GIẢI)
# =====================================================================

def draw_maze_2(path=None, visited=None, title=None):
    """
    Hàm vẽ mê cung 7x7 số 2:
    - Mặc định gọi draw_maze_2() chỉ hiển thị mê cung gốc trắng tinh (chưa giải).
    - Nếu truyền `visited` và `path`, hàm sẽ tô màu xanh nhạt/xanh đậm và chấm tròn giống hệt ảnh.
    """
    size = MAZE_2_CONFIG["size"]
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Đảo trục Y để hàng 0 ở trên cùng, hàng 6 ở dưới cùng
    ax.set_xlim(-0.1, size + 0.1)
    ax.set_ylim(size + 0.1, -0.1)
    ax.set_aspect('equal')
    ax.axis('off')

    # 1. Vẽ lưới nền mờ (Grid lines)
    for i in range(size + 1):
        ax.axhline(i, color='#f2f4f5', linewidth=1, zorder=1)
        ax.axvline(i, color='#f2f4f5', linewidth=1, zorder=1)

    path_set = set(path) if path else set()

    # 2. Tô màu xanh nhạt (#bce6ff) cho các ô đã duyệt (nếu truyền vào)
    if visited:
        for (vr, vc) in visited:
            if (vr, vc) != MAZE_2_CONFIG["center"] and (vr, vc) not in MAZE_2_CONFIG["flags"].values() and (vr, vc) not in path_set:
                rect = patches.Rectangle((vc, vr), 1, 1, facecolor='#bce6ff', edgecolor='none', zorder=2)
                ax.add_patch(rect)

    # 3. Tô màu xanh đậm (#007acc) và chấm tròn cho đường đi (nếu truyền vào)
    if path:
        for (pr, pc) in path:
            if (pr, pc) != MAZE_2_CONFIG["center"] and (pr, pc) not in MAZE_2_CONFIG["flags"].values():
                rect = patches.Rectangle((pc, pr), 1, 1, facecolor='#007acc', edgecolor='none', zorder=2)
                ax.add_patch(rect)
                ax.plot(pc + 0.5, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) == MAZE_2_CONFIG["center"]:
                ax.plot(pc + 0.72, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) in MAZE_2_CONFIG["flags"].values():
                ax.plot(pc + 0.65, pr + 0.52, marker='o', markersize=6.5, color='#dce6f2', zorder=6)

    # 4. Vẽ các ô Cờ màu xanh lá (Flags 1, 2, 3)
    for flag_num, (fr, fc) in MAZE_2_CONFIG["flags"].items():
        rect = patches.Rectangle((fc, fr), 1, 1, facecolor='#00b87c', edgecolor='none', zorder=3)
        ax.add_patch(rect)
        # Vẽ biểu tượng lá cờ
        fx, fy = fc + 0.42, fr + 0.25
        ax.plot([fx, fx], [fy, fy + 0.25], color='#a3f7d6', linewidth=1.8, zorder=4)
        flag_poly = patches.Polygon([[fx, fy], [fx + 0.2, fy + 0.07], [fx, fy + 0.15]], 
                                    closed=True, edgecolor='#a3f7d6', facecolor='none', linewidth=1.5, zorder=4)
        ax.add_patch(flag_poly)
        # Số thứ tự cờ
        ax.text(fc + 0.5, fr + 0.72, str(flag_num), color='white', fontsize=11, 
                fontweight='bold', ha='center', va='center', zorder=4)

    # 5. Vẽ ô Trung tâm màu đen (Center node)
    cr, cc = MAZE_2_CONFIG["center"]
    center_rect = patches.Rectangle((cc, cr), 1, 1, facecolor='#132226', edgecolor='none', zorder=3)
    ax.add_patch(center_rect)
    
    # Vẽ icon khay & mũi tên chỉ xuống
    cx, cy = cc + 0.5, cr + 0.5
    ax.plot([cx, cx], [cy - 0.18, cy + 0.06], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.08, cx, cx + 0.08], [cy - 0.02, cy + 0.06, cy - 0.02], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.14, cx - 0.14, cx + 0.14, cx + 0.14], 
            [cy + 0.04, cy + 0.14, cy + 0.14, cy + 0.04], color='white', linewidth=2, solid_capstyle='round', zorder=4)

    # 6. Vẽ các vách tường
    wall_color = '#223135'
    wall_width = 3.5
    gap = 0.06

    def draw_segment(x1, y1, x2, y2, lw=wall_width):
        if x1 == x2:  # Đoạn dọc
            y_start, y_end = min(y1, y2) + gap, max(y1, y2) - gap
            ax.plot([x1, x2], [y_start, y_end], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)
        else:         # Đoạn ngang
            x_start, x_end = min(x1, x2) + gap, max(x1, x2) - gap
            ax.plot([x_start, x_end], [y1, y2], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)

    # Vẽ khung viền ngoài cùng
    for i in range(size):
        draw_segment(i, 0, i + 1, 0, lw=2.5)
        draw_segment(i, size, i + 1, size, lw=2.5)
        draw_segment(0, i, 0, i + 1, lw=2.5)
        draw_segment(size, i, size, i + 1, lw=2.5)

    # Vẽ tường ngang và tường dọc bên trong
    for r, c in MAZE_2_CONFIG["h_walls"]:
        draw_segment(c, r + 1, c + 1, r + 1)

    for r, c in MAZE_2_CONFIG["v_walls"]:
        draw_segment(c + 1, r, c + 1, r + 1)

    if title:
        plt.title(title, fontsize=14, fontweight='bold', pad=12, color='#132226')
    plt.tight_layout()
    plt.show()


# =====================================================================
# 3. HIỂN THỊ MÊ CUNG GỐC (CHƯA GIẢI)
# =====================================================================

if __name__ == "__main__":
    draw_maze_2()

# =====================================================================
# 1. CẤU HÌNH DỮ LIỆU MÊ CUNG 7x7 SỐ 3 & LUẬT DI CHUYỂN
# =====================================================================
MAZE_3_CONFIG = {
    "size": 7,
    "center": (3, 3),  # Ô màu đen ở giữa (Mở lối Lên sang (2, 3) và lối Xuống sang (4, 3))
    "flags": {
    1: (1, 6),     # Cờ 1 (Hàng 1, Cột 6) - Đích gần nhất theo đường đi (7 bước), chỉ BFS tìm được
    2: (0, 0),     # Cờ 2 (Hàng 0, Cột 0) - Đích mà GBFS/DFS chọn (10 bước; ngắn nhất tới cờ này là 8)
    3: (6, 6)      # Cờ 3 (Hàng 6, Cột 6) - Đích xa nhất (16 bước), góc dưới bên phải
},
    # Tường ngang: ngăn cách giữa ô (r, c) và (r + 1, c)
    "h_walls": [
        (0, 1), (0, 2), (0, 5),
        (1, 2), (1, 3), (1, 4),
        (2, 1), (2, 2), (2, 5),
        (3, 1), (3, 4), (3, 5),
        (4, 0), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
        (5, 1)
    ],
    # Tường dọc: ngăn cách giữa ô (r, c) và (r, c + 1)
    "v_walls": [
        (0, 3), (0, 5),
        (1, 0), (1, 3), (1, 5),
        (2, 0), (2, 3), (2, 5),
        (3, 0), (3, 2), (3, 3),
        (5, 1), (5, 3), (5, 5),
        (6, 2), (6, 4)
    ]
}
BLOCKED_EDGES_3 = set()
for r, c in MAZE_3_CONFIG["h_walls"]:
    BLOCKED_EDGES_3.add(((r, c), (r + 1, c)))
    BLOCKED_EDGES_3.add(((r + 1, c), (r, c)))
for r, c in MAZE_3_CONFIG["v_walls"]:
    BLOCKED_EDGES_3.add(((r, c), (r, c + 1)))
    BLOCKED_EDGES_3.add(((r, c + 1), (r, c)))


# Thứ tự ưu tiên xét ô lân cận: Lên -> Phải -> Xuống -> Trái
DIRECTIONS = [
    (-1, 0, "Up"),
    (0, 1, "Right"),
    (1, 0, "Down"),
    (0, -1, "Left")
]


def get_neighbors_maze3(r, c):
    """Hàm chuẩn lấy danh sách các ô lân cận hợp lệ theo thứ tự ưu tiên."""
    size = MAZE_3_CONFIG["size"]
    neighbors = []
    for dr, dc, move_name in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            if ((r, c), (nr, nc)) not in BLOCKED_EDGES_3:
                neighbors.append(((nr, nc), move_name))
    return neighbors


# =====================================================================
# 2. HÀM VẼ ĐỒ HỌA MÊ CUNG GỐC SỐ 3
# =====================================================================
def draw_maze_3(path=None, visited=None, title=None):
    """
    Hàm vẽ mê cung 7x7 số 3:
    - Mặc định gọi draw_maze_3() chỉ hiển thị mê cung gốc trắng tinh (chưa giải).
    - Hỗ trợ truyền `visited` và `path` để vẽ màu xanh nhạt/xanh đậm và chấm tròn.
    """
    size = MAZE_3_CONFIG["size"]
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
   
    # Đảo trục Y để hàng 0 ở trên cùng, hàng 6 ở dưới cùng
    ax.set_xlim(-0.1, size + 0.1)
    ax.set_ylim(size + 0.1, -0.1)
    ax.set_aspect('equal')
    ax.axis('off')
   
    # 1. Vẽ lưới nền mờ (Grid lines)
    for i in range(size + 1):
        ax.axhline(i, color='#f2f4f5', linewidth=1, zorder=1)
        ax.axvline(i, color='#f2f4f5', linewidth=1, zorder=1)
       
    path_set = set(path) if path else set()
   
    # 2. Tô màu xanh nhạt (#bce6ff) cho các ô đã duyệt (nếu truyền vào)
    if visited:
        for (vr, vc) in visited:
            if (vr, vc) != MAZE_3_CONFIG["center"] and (vr, vc) not in MAZE_3_CONFIG["flags"].values() and (vr, vc) not in path_set:
                rect = patches.Rectangle((vc, vr), 1, 1, facecolor='#bce6ff', edgecolor='none', zorder=2)
                ax.add_patch(rect)
               
    # 3. Tô màu xanh đậm (#007acc) và chấm tròn cho đường đi (nếu truyền vào)
    if path:
        for (pr, pc) in path:
            if (pr, pc) != MAZE_3_CONFIG["center"] and (pr, pc) not in MAZE_3_CONFIG["flags"].values():
                rect = patches.Rectangle((pc, pr), 1, 1, facecolor='#007acc', edgecolor='none', zorder=2)
                ax.add_patch(rect)
                ax.plot(pc + 0.5, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) == MAZE_3_CONFIG["center"]:
                ax.plot(pc + 0.72, pr + 0.5, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
            elif (pr, pc) in MAZE_3_CONFIG["flags"].values():
                ax.plot(pc + 0.65, pr + 0.52, marker='o', markersize=6.5, color='#dce6f2', zorder=6)
               
    # 4. Vẽ các ô Cờ màu xanh lá (Flags 1, 2, 3)
    for flag_num, (fr, fc) in MAZE_3_CONFIG["flags"].items():
        rect = patches.Rectangle((fc, fr), 1, 1, facecolor='#00b87c', edgecolor='none', zorder=3)
        ax.add_patch(rect)
        # Vẽ biểu tượng lá cờ
        fx, fy = fc + 0.42, fr + 0.25
        ax.plot([fx, fx], [fy, fy + 0.25], color='#a3f7d6', linewidth=1.8, zorder=4)
        flag_poly = patches.Polygon([[fx, fy], [fx + 0.2, fy + 0.07], [fx, fy + 0.15]],
                                    closed=True, edgecolor='#a3f7d6', facecolor='none', linewidth=1.5, zorder=4)
        ax.add_patch(flag_poly)
        # Số thứ tự cờ
        ax.text(fc + 0.5, fr + 0.72, str(flag_num), color='white', fontsize=11,
                fontweight='bold', ha='center', va='center', zorder=4)
               
    # 5. Vẽ ô Trung tâm màu đen (Center node)
    cr, cc = MAZE_3_CONFIG["center"]
    center_rect = patches.Rectangle((cc, cr), 1, 1, facecolor='#132226', edgecolor='none', zorder=3)
    ax.add_patch(center_rect)
   
    # Vẽ icon khay & mũi tên chỉ xuống
    cx, cy = cc + 0.5, cr + 0.5
    ax.plot([cx, cx], [cy - 0.18, cy + 0.06], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.08, cx, cx + 0.08], [cy - 0.02, cy + 0.06, cy - 0.02], color='white', linewidth=2, solid_capstyle='round', zorder=4)
    ax.plot([cx - 0.14, cx - 0.14, cx + 0.14, cx + 0.14],
            [cy + 0.04, cy + 0.14, cy + 0.14, cy + 0.04], color='white', linewidth=2, solid_capstyle='round', zorder=4)
           
    # 6. Vẽ các vách tường
    wall_color = '#223135'
    wall_width = 3.5
    gap = 0.06
    def draw_segment(x1, y1, x2, y2, lw=wall_width):
        if x1 == x2:  # Đoạn dọc
            y_start, y_end = min(y1, y2) + gap, max(y1, y2) - gap
            ax.plot([x1, x2], [y_start, y_end], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)
        else:         # Đoạn ngang
            x_start, x_end = min(x1, x2) + gap, max(x1, x2) - gap
            ax.plot([x_start, x_end], [y1, y2], color=wall_color, linewidth=lw, solid_capstyle='round', zorder=5)
           
    # Vẽ khung viền ngoài cùng
    for i in range(size):
        draw_segment(i, 0, i + 1, 0, lw=2.5)
        draw_segment(i, size, i + 1, size, lw=2.5)
        draw_segment(0, i, 0, i + 1, lw=2.5)
        draw_segment(size, i, size, i + 1, lw=2.5)
       
    # Vẽ tường ngang và tường dọc bên trong
    for r, c in MAZE_3_CONFIG["h_walls"]:
        draw_segment(c, r + 1, c + 1, r + 1)
    for r, c in MAZE_3_CONFIG["v_walls"]:
        draw_segment(c + 1, r, c + 1, r + 1)
       
    if title:
        plt.title(title, fontsize=14, fontweight='bold', pad=12, color='#132226')
    plt.tight_layout()
    plt.show()


# =====================================================================
# 3. HIỂN THỊ MÊ CUNG GỐC SỐ 3 (CHƯA GIẢI)
# =====================================================================
if __name__ == "__main__":
    draw_maze_3()

from collections import deque

def shortest_distance_to_flag(config, get_neighbors):

    start = config["center"]
    exits = set(config["flags"].values())

    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        current, distance = queue.popleft()

        if current in exits:
            return distance, current

        for neighbor, move_name in get_neighbors(*current):

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    return None, None
def record_data(maze_name, config, get_neighbors, result):

    # Chạy GBFS

    path = result["path"]
    goal = result["exit"]

    # Độ dài đường đi
    L = len(path) - 1 if path else None

    # Số ô đã duyệt
    visited_count = len(result["explored"])

    # Max Open
    max_open = result["max_open"]

    # Tỷ lệ hiệu quả
    efficiency = (
        L / visited_count * 100
        if L is not None and visited_count > 0
        else None
    )

    # Tìm lá cờ mà GBFS đã đến
    goal_name = next(
        (
            name for name, position in config["flags"].items()
            if position == goal
        ),
        "Không tìm thấy"
    )

    # Dùng BFS tìm khoảng cách ngắn nhất đến một lá cờ
    shortest_distance, nearest_goal = shortest_distance_to_flag(
        config, get_neighbors
    )

    # Kiểm tra GBFS có tìm được đích gần nhất không
    if L is None:
        nearest_check = "Không tìm được đích"
    elif L == shortest_distance:
        nearest_check = "Có"
    else:
        nearest_check = "Không"

    # Nhận xét hành vi
    if L is None:
        behavior = "Không tìm được đường đến lá cờ."
    elif nearest_check == "Có":
        behavior = "GBFS tìm được đường đi có độ dài ngắn nhất."
    else:
        behavior = "GBFS chọn đích chưa tối ưu về số bước."

    return {
        "Maze": maze_name,
        "Thuật toán": "GBFS",
        "Đích tìm được": f"{goal_name} {goal}" if goal else "Không tìm thấy",
        "Path Length": L,
        "Visited": visited_count,
        "Max Open": max_open,
        "Efficiency (%)": round(efficiency, 2) if efficiency is not None else None,
        "Nearest Goal": nearest_check,
        "Runtime (ms)": round(result["runtime_ms"], 4),
        "Nhận xét": behavior
    }
# ==============================
# RECORD DATA - GBFS
# ==============================

results = []

mazes = [
    ("Maze 1.1", MAZE_1_CONFIG, get_neighbors_maze4),
    ("Maze 1.2", MAZE_2_CONFIG, get_neighbors_maze2),
    ("Maze 1.3", MAZE_3_CONFIG, get_neighbors_maze3)
]

for name, config, get_neighbors in mazes:

    result = gbfs(config, get_neighbors)

    row = record_data(name, config, get_neighbors, result)
    results.append(row)

    print(f"\n========== {name} ==========")

    for key, value in row.items():
        print(f"{key}: {value}")

    print("Đường đi:", result["path"])
    print("Thứ tự duyệt:", result["explored"])


# ==========================================
# BFS - CHẠY VÀ GHI KẾT QUẢ 3 MAZE
# ==========================================

def bfs(config, get_neighbors):

    start_time = time.perf_counter()

    start = config["center"]
    goals = set(config["flags"].values())

    queue = deque([start])
    discovered = {start}
    parent = {start: None}

    explored = []
    max_open = 1
    found_goal = None

    while queue:

        current = queue.popleft()
        explored.append(current)

        if current in goals:
            found_goal = current
            break

        for neighbor, move_name in get_neighbors(*current):

            if neighbor not in discovered:
                discovered.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

        max_open = max(max_open, len(queue))

    # Truy vết đường đi
    path = []

    if found_goal is not None:
        current = found_goal

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()

    runtime_ms = (time.perf_counter() - start_time) * 1000

    return {
    "path": path,
    "explored": explored,
    "exit": found_goal,
    "max_open": max_open,
    "runtime_ms": runtime_ms,
    "discovered_count": len(discovered)
}


# ==========================================
# CHẠY BFS TRÊN 3 MAZE
# ==========================================



for name, config, get_neighbors in mazes:

    result = bfs(config, get_neighbors)

    path = result["path"]
    explored = result["explored"]
    goal = result["exit"]

    flag_name = next(
        (n for n, pos in config["flags"].items() if pos == goal),
        "Không tìm thấy"
    )

    L = len(path) - 1 if path else None
    visited_count = result["discovered_count"]

    efficiency = (
        L / visited_count * 100
        if L is not None and visited_count > 0
        else None
    )

    print(f"\n========== {name} ==========")
    print(f"Maze: {name}")
    print("Thuật toán: BFS")
    print(f"Đích tìm được: {flag_name} {goal}")
    print(f"Path Length: {L}")
    print(f"Visited: {visited_count}")
    print(f"Max Open: {result['max_open']}")
    print(f"Efficiency (%): {round(efficiency, 2) if efficiency is not None else None}")
    print("Nearest Goal: Có" if path else "Nearest Goal: Không tìm được đích")
    print(f"Runtime (ms): {result['runtime_ms']:.4f}")
    print("Đường đi:", path)
    print("Thứ tự duyệt:", explored)
