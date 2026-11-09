# -*- coding: utf-8 -*-
"""
TPC 服务器 · 地铁线路查询  图形化界面 (Tkinter)

直接复用「tpc服务器线路查询.py」里的线路数据与寻路算法：
    * 优先找同目录下的 tpc服务器线路查询.py
    * 其次找脚本同目录、上一级目录、桌面、下载夹里名字含「线路查询」的第一个 .py
    * 也可以在程序里「导入数据文件」，路径会记在 metro_gui.json 里

运行:
    python 地铁线路查询.pyw
    (双击也可以；带窗口的 pythonw 不会弹出黑框)

三个页签:
    路径查询   起点 / 终点，选每组返回条数，展开可看全程站序；点站名可设为起点或终点
    线路查询   输入 8 / 13B / 玉衡1号线 / 沼刷线 …… 查看站序与换乘信息
    线网概览   线路 / 车站 / 换乘站统计、换乘枢纽、全部线路目录
"""

import os
import sys
import json
import difflib
import threading
import traceback
import importlib.util

try:
    import tkinter as tk
    from tkinter import ttk, font as tkfont, filedialog, messagebox
except Exception:  # pragma: no cover - 没有 tk 时的兜底提示
    sys.stderr.write("需要带 Tk 的 Python 才能运行图形界面。\n")
    raise

APP_TITLE = "TPC服务器 · 地铁线路查询"
CONFIG_NAME = "metro_gui.json"

# 浅色主题
BG        = "#f3f5f9"
CARD      = "#ffffff"
BORDER    = "#dde3ec"
TEXT      = "#1f2937"
MUTED     = "#75808f"
ACCENT    = "#2f6df6"
ACCENT_DK = "#1f52c9"
ACCENT_LT = "#e8f0ff"
CHIP      = "#f6f8fb"

# 深色主题
DBG       = "#1b1e24"
DCARD     = "#23272f"
DBORDER   = "#343a45"
DTEXT     = "#e8eaed"
DMUTED    = "#9aa4b2"
DACCENT   = "#6d9bff"
DACCENT_LT = "#26324a"
DCHIP     = "#2b3039"

TRANSFER_SYM = "⟳"
ARROW = "→"
OTHER = "其他"


# ============================================================================
#  内置线路数据（由 metro_query.py 原样内嵌，单文件运行用）
# ============================================================================

LINES = {
    "L1": ["葵园村", "四威", "涵址", "暗东湖", "萝野", "月漓", "星流峡", "流旷", "浅池", "穹林", "泽汀", "绿野东", "绿野", "东滩", "林南大道", "金域北路", "盒原", "渥丘", "龙池", "神殿"],
    "L2": ["火药塔", "出生点", "刷铁机", "中途岛", "大平原", "正白高原", "妍星山", "火焰高原", "西南平原", "南砂", "河东走廊", "北砂", "全物品", "漠北", "绯阳半岛", "芳霰", "千风镇"],
    "L3N": ["雪崖", "朔漠", "环蓝村", "冰湾", "絮语", "冻港村", "刷冰机", "北西", "鞍村", "农林东路", "农业基地", "北林", "龙归", "亡村"],
    "L3S": ["划岗", "南石半岛", "卡岸", "界谷", "雪谷", "归墟", "未晞", "樱林六交", "樱园口", "下樱河谷"],
    "L4": ["江跳", "翠竹基地", "林场", "远望坡", "湖尾", "亚当村", "复兴桥", "中港码头", "中途岛", "庄桥", "中央商务区", "金域北路", "中林", "纺林", "定海", "农业基地", "喷泉广场"],
    "L5": ["黑子交易所", "花卉博览园", "萨瓦湖", "喀斯特", "翠竹基地", "书林", "月潭", "铜山公园", "正白高原", "滴水角", "守卫者农场", "上岸", "新屿", "东陆", "东林", "毒家村"],
    "L6": ["农林十字", "剡溪", "林泉", "寒川"],
    "L7": ["千风镇", "樱池", "湖景", "河滩岛", "档案馆", "农林十字", "农业基地", "通天竹", "袭击塔西", "东阴礁", "葫芦岛", "东陆湖", "绿野东"],
    "L8": ["竹邑", "清蘅", "跃金", "沉玉", "丹恒", "平芜", "阳关", "西港", "五溪", "风屿", "绯阳半岛", "瑞香", "江斜", "群芳", "龙归", "定海", "沧墟", "婉青", "铃芽岛", "梦樱", "云飞", "玥琳"],
    "L10": ["火药塔", "东滩", "林庙桥", "纺林", "亡村", "中河", "西林", "神殿", "赤漠", "南砂", "江心洲", "月潭", "湖尾", "划岗", "凤归", "奥力金字塔", "火药塔"],
    "L11": ["海上明珠", "电视台", "上岸", "火药塔", "出生点", "奥力樱花庄", "巨谷", "林塘东", "林塘西", "赤漠", "河东走廊", "铃芽交易所", "中砂矿山", "丹霞", "双沙", "西砂大裂谷", "流沙河", "黑子交易所"],
    "L12": ["林庙桥", "林南大道", "世纪大道东", "奥力樱花庄", "刷铁机", "守卫者农场", "凤归", "蘅芜", "腐竹山"],
    "L13": ["西南平原", "秀谷", "铜山公园", "亚当村", "复兴桥", "奥力金字塔", "上岸", "雨林岛", "绿野", "葫芦岛", "繁花岛", "向阳", "北萨瓦纳", "西寨", "东寨", "北桦", "溺尸塔", "蔡徐村", "上北泽"],
    "L13B": ["繁花岛", "铃芽岛"],
    "L14": ["松港村", "松港村南", "墟影", "苹桦", "梦樱", "北萨瓦纳", "明萤", "浦江", "林坡"],
    "L17": ["珊瑚工业园", "流沙河", "红霞林", "科奇诺温泉", "黄沙", "赤龙泾", "江心洲", "秀谷", "火焰高原", "林塘西", "龙池", "中河", "群芳", "档案馆", "玄武湖东", "杉各庄", "松吟"],
    "L19": ["刷铁机", "奥力樱花庄", "蒋沟", "通天竹"],
    "L20": ["樱落", "未晞", "归墟", "望风", "沧浪", "伪和平", "腐竹山", "小雪镇东", "雪沁", "茂林", "佳楠村", "欢乐谷", "松霜", "星荧", "延年路", "渊口", "天遒谷", "月漓", "华强南", "鹿蹊", "玥琳", "牧驿", "溺尸塔", "墟影", "刷冰机", "寒川", "松吟", "苍岭", "池湖", "湄洲", "荡谷", "生物头颅塔", "西港", "寥津", "丹霞", "千嶂", "科奇诺温泉", "萨瓦湖", "笋林", "四海界", "桃苑", "樱落"],
    # "L21": ["东阴礁", "繁花岛", "明萤", "金岚", "鹿蹊"],
    "L24": ["南砂", "末地要塞", "对川", "正白大道", "中港码头", "凤归", "海上明珠", "碎樱", "散岩", "东星港", "星荧东", "林光村"],
    "L25": ["海上明珠", "甘岸", "崖湾", "蘅芜", "雪谷", "望风", "星落", "棕原", "花源村", "中甸山", "花林终", "南樱雪", "南洲", "群系之海"],
    "L28": ["漠北", "西林", "江斜"],
    "LY1": ["幽府", "蜻莹湾", "景元", "赤垩", "中海", "仙舟大道", "昔涟", "沉沙", "观洲", "璜溪", "白马山"],
    "LY2": ["群系之海", "扶摇", "科技城", "北沥", "中海"],
    "LR1": ["蔡徐村", "海东村", "霞林村", "沼泽刷怪塔", "一线村", "水月村", "水月湾", "莹岛村", "芒夏村", "万界村", "刷花机"],
    "LR2": ["四海界", "樱谷村", "星落", "小雪镇", "刷沙机", "欢乐谷"],
    "LT1": ["中途岛南", "中途岛西", "北岛竹林", "刷铁机西", "仙人掌农场", "缘溪路", "领事馆", "出生点"],
    "LT3": ["农基码头", "瓜机", "镜泊", "林庙桥北", "林南大道东", "星枢之眼", "缘溪路", "地铁大厦"],
    "LT6": ["蛙明灯农场", "沼泽刷怪塔", "新沼泽怪塔"],
}

# 每条线路按当前营业站序保存相邻区间总里程。
# 暂缓开通车站两侧的原始区间按“数据求和”合并；0 是有效里程。

INTERVAL_LENGTHS = {
    "L1": [261.0, 236.0, 262.0, 252.0, 252.5, 184.5, 210.0, 262.5, 225.0, 295.5, 313.5, 196.0, 491.5, 387.5, 203.5, 204.0, 291.0, 256.5, 285.0],
    "L2": [230.5, 305.5, 192.0, 254.5, 247.5, 177.5, 203.0, 346.5, 259.5, 223.0, 271.5, 169.0, 177.0, 238.0, 251.0, 213.0],
    "L3N": [288.5, 286.0, 281.5, 293.0, 211.5, 287.5, 193.5, 335.0, 332.5, 261.0, 292.5, 176.5, 267.0],
    "L3S": [337.0, 224.5, 184.5, 174.5, 451.5, 403.0, 284.0, 257.0, 219.5],
    "L4": [157.0, 280.0, 383.0, 372.5, 286.5, 343.0, 217.0, 166.5, 190.0, 141.0, 139.5, 137.0, 198.0, 158.5, 352.0, 119.5],
    "L5": [390.5, 308.5, 385.0, 369.0, 439.0, 262.5, 297.0, 417.5, 299.0, 199.0, 633.0, 554.0, 356.0, 307.5, 195.0],
    "L6": [129.5, 428.5, 324.5],
    "L7": [196.5, 248.5, 226.0, 180.0, 178.0, 153.0, 212.0, 450.5, 334.0, 354.5, 205.0, 255.0],
    "L8": [368.0, 277.0, 431.0, 433.0, 412.0, 446.0, 459.0, 719.0, 296.0, 236.5, 213.5, 197.5, 311.5, 264.0, 219.0, 563.5, 876.5, 415.5, 454.5, 420.0, 569.5],
    "L10": [442.0, 413.5, 273.5, 229.0, 297.0, 424.0, 308.5, 336.5, 305.5, 392.0, 433.5, 344.5, 233.0, 272.5, 772.0, 360.0],
    "L11": [348.0, 598.0, 365.5, 301.0, 330.0, 363.0, 230.5, 246.5, 301.0, 240.0, 373.0, 239.0, 345.5, 245.0, 270.5, 202.5, 562.5],
    "L12": [208.0, 129.0, 140.5, 136.0, 263.0, 477.5, 824.5, 857.5],
    "L13": [308.0, 317.5, 265.5, 302.0, 644.0, 353.5, 600.0, 327.5, 325.0, 334.5, 297.0, 322.0, 303.5, 290.0, 454.0, 335.5, 426.0, 297.0],
    "L13B": [489.0],
    "L14": [234.5, 229.5, 149.0, 290.5, 150.0, 307.5, 634.5, 286.5],
    "L17": [327.5, 226.0, 300.0, 421.0, 316.5, 299.5, 319.5, 324.0, 386.5, 332.0, 444.5, 170.5, 434.5, 249.5, 340.5, 467.5],
    "L19": [140.0, 527.0, 537.5],
    "L20": [402.0, 403.5, 256.5, 143.5, 278.0, 407.5, 279.0, 610.5, 591.0, 617.0, 440.0, 357.0, 249.0, 220.0, 489.0, 501.0, 581.5, 480.0, 314.5, 430.0, 407.5, 655.0, 727.5, 1453.0, 266.5, 436.0, 247.5, 351.5, 425.0, 483.0, 730.0, 669.5, 580.0, 546.0, 281.0, 320.5, 371.5, 326.0, 380.5, 740.5, 423.0],
    "L24": [232.5, 404.0, 353.5, 238.0, 557.0, 864.5, 638.5, 524.0, 352.5, 1053.5, 759.0],
    "L25": [455.0, 200.0, 255.0, 474.5, 316.0, 181.5, 445.0, 321.0, 366.5, 451.5, 437.0, 900.0, 482.5],
    "L28": [304.0, 299.0],
    "LY1": [692.5, 431.0, 427.0, 297.5, 587.0, 342.0, 378.0, 316.0, 515.0, 540.0],
    "LY2": [574.0, 471.0, 402.5, 449.5],
    "LR1": [2477.0, 658.5, 1532.5, 855.5, 941.5, 728.0, 823.0, 676.5, 749.5, 803.5],
    "LR2": [1232.5, 1135.0, 797.0, 1851.5, 468.0],
    "LT1": [131.5, 56.5, 159.5, 103.5, 81.0, 80.5, 58.5],
    "LT3": [86.0, 238.0, 140.0, 178.5, 138.0, 192.0, 73.0],
    "LT6": [405.0, 190.0],
}

# 线路键 -> 显示名

NAMES = {
    "L1": "1号线",
    "L2": "2号线",
    "L3": "3号线",
    "L3N": "3号线北段",
    "L3S": "3号线南段",
    "L4": "4号线",
    "L5": "5号线",
    "L6": "6号线",
    "L7": "7号线",
    "L8": "8号线",
    "L10": "10号线",
    "L11": "11号线",
    "L12": "12号线",
    "L13": "13号线",
    "L13B": "13号线支线",
    "L14": "14号线",
    "L17": "17号线",
    "L19": "19号线",
    "L20": "20号线",
    # "L21": "21号线",  # 暂无里程数据，暂不参与查询
    "L24": "24号线",
    "L25": "25号线",
    "L28": "28号线",
    "LY1": "玉衡1号线",
    "LY2": "玉衡2号线",
    "LR1": "R1线",
    "LR2": "R2线",
    "LT1": "便民快线",
    "LT3": "有轨电车3号线",
    "LT6": "沼刷线",
}

LINE_GROUPS = {
    "L3": ("L3N", "L3S"),
}

DEFAULT_TRANSFER_WEIGHT = 100

SPECIAL_TRANSFER_WEIGHT = {
    "纺林": 300,
    "欢乐谷": 200,
    "梦樱": 200,
    "刷冰机": 200,
}

EMBEDDED_LINES = LINES
EMBEDDED_NAMES = NAMES
EMBEDDED_INTERVAL_LENGTHS = INTERVAL_LENGTHS
EMBEDDED_LINE_GROUPS = LINE_GROUPS
EMBEDDED_TRANSFER_WEIGHT = 100
EMBEDDED_SPECIAL_TRANSFER_WEIGHT = SPECIAL_TRANSFER_WEIGHT



# ============================================================================
#  第一部分：数据引擎（加载原脚本 + 补丁缓存版 k 短路）
# ============================================================================

class MetroData:
    """线路数据 + 寻路算法。

    两种数据来源：
      * path=None  -> 用内嵌数据（EMBEDDED_LINES），单文件/EXE 直接跑，不依赖外部文件
      * path=xxx.py -> 加载外部脚本（想换一份新的线路数据时用）

    两种计算方式（可在「关于」里切换）：
      * algo="weight" 新版：权重 = 总里程(m) + 换乘权重
      * algo="score"  旧版：得分 = 区间数 + 换乘数 x 2
    """

    def __init__(self, path=None, algo="weight"):
        if path:
            self.path = os.path.abspath(path)
            self.mod = self._load(self.path)
            self.source = os.path.basename(self.path)
        else:
            self.path = None
            self.mod = self._build_embedded_module()
            self.source = "内置数据"
        m = self.mod
        self.LINES = m.LINES
        self.NAMES = m.NAMES
        self.STATION_LINES = m.STATION_LINES
        self.RING = getattr(m, "RING_LINES", {k for k, v in self.LINES.items()
                                              if len(v) > 1 and v[0] == v[-1]})
        self.TRANSFER_COST = getattr(m, "TRANSFER_COST", 2)
        self.LINE_GROUPS = getattr(m, "LINE_GROUPS", {})
        self.search_mod = m
        self.set_algo(algo)

    # -- 切换计算方式 -----------------------------------------------------
    def set_algo(self, algo):
        """重建按当前代价模型的图，并切换分组定义。"""
        self.algo = algo if algo in ("weight", "score") else "weight"
        m = self.mod
        # 老的外部脚本没有里程数据，只能走旧算法
        if self.algo == "weight" and not getattr(m, "INTERVAL_LENGTHS", None):
            self.algo = "score"
        m.GROUPS = GROUPS_BY_ALGO[self.algo]
        try:
            m.build_graph(m.LINES, self.algo)
        except TypeError:
            m.NEIGH.clear()
            m.STATION_LINES.clear()
            m.build_graph(m.LINES)
        m.STATIONS = sorted(m.STATION_LINES)
        self.STATIONS = m.STATIONS
        self.STATION_LINES = m.STATION_LINES
        self.GROUPS = m.GROUPS
        self.search_impl = self._install_patched_search()
        return self.algo

    @property
    def algo_name(self):
        return GROUPS_BY_ALGO[self.algo][0][1]

    # -- 内置数据 ---------------------------------------------------------
    @staticmethod
    def _build_embedded_module():
        """用内嵌数据现场拼一个和原脚本同接口的模块。

        两种代价模型同时被支持（由 MetroData 通过 m.build_graph 重建图）：
          * "weight" 新版：权重 = 总里程(m) + 换乘权重，代价是 4 元组
          * "score"  旧版：得分 = 区间数 + 换乘数 x 2，代价是 2 元组
        """
        import heapq as _heapq
        import types as _types
        m = _types.ModuleType("tpc_metro_embedded")
        m.LINES = {k: list(v) for k, v in EMBEDDED_LINES.items()}
        m.NAMES = dict(EMBEDDED_NAMES)
        m.INTERVAL_LENGTHS = dict(EMBEDDED_INTERVAL_LENGTHS)
        m.LINE_GROUPS = dict(EMBEDDED_LINE_GROUPS)
        m.DEFAULT_TRANSFER_WEIGHT = EMBEDDED_TRANSFER_WEIGHT
        m.SPECIAL_TRANSFER_WEIGHT = dict(EMBEDDED_SPECIAL_TRANSFER_WEIGHT)
        m.NEIGH = {}
        m.STATION_LINES = {}
        m.TRANSFER_COST = 2
        m.RING_LINES = {k for k, v in m.LINES.items() if len(v) > 1 and v[0] == v[-1]}
        m.GROUPS = DEFAULT_GROUPS
        m.INF_COST = (10 ** 9, 10 ** 9)
        m.MODE = "weight"

        def transfer_weight(station, from_line, to_line):
            if station == "火药塔":
                pair = {from_line, to_line}
                if pair == {"L2", "L10"} or pair == {"L2", "L11"}:
                    return 250
            return m.SPECIAL_TRANSFER_WEIGHT.get(station, m.DEFAULT_TRANSFER_WEIGHT)

        def build_graph(lines, mode="weight"):
            """mode=weight -> 4 元组代价；mode=score -> 2 元组代价（旧版）。"""
            m.MODE = mode
            NEIGH, STATION_LINES = {}, {}
            for lk, seq in lines.items():
                lengths = m.INTERVAL_LENGTHS[lk]
                if len(lengths) != len(seq) - 1:
                    raise ValueError("%s 里程数 %d 与区间数 %d 不一致"
                                     % (lk, len(lengths), len(seq) - 1))
                for s in seq:
                    STATION_LINES.setdefault(s, [])
                    if lk not in STATION_LINES[s]:
                        STATION_LINES[s].append(lk)
                for index, (a, b) in enumerate(zip(seq, seq[1:])):
                    if a == b:
                        continue
                    if mode == "weight":
                        length = float(lengths[index])
                        cost = (length, length, 1, 0)
                    else:
                        cost = (1, 0)
                    NEIGH.setdefault((a, lk), []).append(((b, lk), cost))
                    NEIGH.setdefault((b, lk), []).append(((a, lk), cost))
                for s in seq:
                    NEIGH.setdefault((s, lk), [])
            for s, lks in STATION_LINES.items():
                for a in lks:
                    for b in lks:
                        if a != b:
                            if mode == "weight":
                                NEIGH[(s, a)].append(((s, b),
                                                     (transfer_weight(s, a, b), 0, 0, 1)))
                            else:
                                NEIGH[(s, a)].append(((s, b), (0, 1)))
            m.NEIGH = NEIGH
            m.STATION_LINES = STATION_LINES
        def zero():
            return (0, 0, 0, 0) if m.MODE == "weight" else (0, 0)

        def _add(a, b):
            return tuple(x + y for x, y in zip(a, b))

        def _key(mode, c):
            if m.MODE == "weight":
                weight, meters, hops, transfers = c
                if mode == "hops":
                    return (hops, weight, transfers, meters)
                if mode == "trans":
                    return (transfers, weight, hops, meters)
                return (weight, transfers, hops, meters)
            hops, transfers = c
            if mode == "hops":
                return (hops, transfers)
            if mode == "trans":
                return (transfers, hops)
            return (hops + m.TRANSFER_COST * transfers, transfers, hops)

        def dijkstra(start_states, goal_station, mode,
                     banned_states=frozenset(), banned_edges=frozenset()):
            inf = (float("inf"),) * len(zero()) if m.MODE == "weight" else (10 ** 9, 10 ** 9)
            dist, prev, pq = {}, {}, []
            for st in start_states:
                if st in banned_states:
                    continue
                dist[st] = zero()
                prev[st] = None
                _heapq.heappush(pq, (_key(mode, zero()), 0, st))
            h = 0
            while pq:
                k, _, u = _heapq.heappop(pq)
                if k != _key(mode, dist.get(u, inf)):
                    continue
                if u[0] == goal_station:
                    path = [u]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    path.reverse()
                    return path
                for v, c in m.NEIGH.get(u, ()):
                    if v in banned_states or (u, v) in banned_edges:
                        continue
                    nd = _add(dist[u], c)
                    if _key(mode, nd) < _key(mode, dist.get(v, inf)):
                        dist[v] = nd
                        prev[v] = u
                        h += 1
                        _heapq.heappush(pq, (_key(mode, nd), h, v))
            return None

        def start_states_of(station):
            return [(station, lk) for lk in m.STATION_LINES[station]]

        def path_cost(states):
            total = zero()
            for u, v in zip(states, states[1:]):
                for w, c in m.NEIGH[u]:
                    if w == v:
                        total = _add(total, c)
                        break
            return total

        def k_shortest_states(src, dst, k, mode):
            first = dijkstra(start_states_of(src), dst, mode)
            if not first:
                return []
            A, B, counter = [first], [], 0
            while len(A) < k:
                prev_path = A[-1]
                for i in range(len(prev_path) - 1):
                    root = prev_path[: i + 1]
                    banned_states = set(root[:-1])
                    banned_edges = set()
                    for p in A:
                        if len(p) > i + 1 and p[: i + 1] == root:
                            banned_edges.add((p[i], p[i + 1]))
                    spur = dijkstra([prev_path[i]], dst, mode,
                                    banned_states, banned_edges)
                    if not spur:
                        continue
                    total = root[:-1] + spur
                    if total in A:
                        continue
                    if any(total == item[2] for item in B):
                        continue
                    counter += 1
                    _heapq.heappush(B, (_key(mode, path_cost(total)), counter, total))
                if not B:
                    break
                A.append(_heapq.heappop(B)[2])
            return A

        def to_segments(state_path):
            segs, cur_line, cur_st = [], None, []
            for s, lk in state_path:
                if cur_line is None:
                    cur_line, cur_st = lk, [s]
                elif lk == cur_line:
                    if s != cur_st[-1]:
                        cur_st.append(s)
                else:
                    segs.append((cur_line, cur_st))
                    cur_line, cur_st = lk, [s]
            if cur_st:
                segs.append((cur_line, cur_st))
            return segs

        def tidy(segs):
            while len(segs) > 1 and len(segs[0][1]) == 1 and segs[1][1] and \
                    segs[1][1][0] == segs[0][1][0]:
                segs.pop(0)
            while len(segs) > 1 and len(segs[-1][1]) == 1 and \
                    segs[-2][1][-1] == segs[-1][1][0]:
                segs.pop()
            return segs

        def station_sequence(segs):
            seq = []
            for _, st in segs:
                for s in st:
                    if not seq or seq[-1] != s:
                        seq.append(s)
            return seq

        def collect(src, dst, per_mode):
            """两种算法共用：把三条排序模式下的候选路径收集起来。"""
            cands = {}
            for mode in ("score", "trans", "hops"):
                for states in k_shortest_states(src, dst, per_mode, mode):
                    segs = tidy(to_segments(states))
                    seq = station_sequence(segs)
                    if len(seq) < 2 or seq[0] != src or seq[-1] != dst:
                        continue
                    if len(set(seq)) != len(seq):
                        continue
                    key = tuple(seq)
                    if key not in cands:
                        cands[key] = (segs, path_cost(states))
            return [(key, segs, cost) for key, (segs, cost) in cands.items()]

        def search(src, dst, k=1):
            """三组各自独立取自身最优的前 k 条，组间不再去重。
            （v1.0.4：按需求取消「跨组去重」，同一走法可以在不同分组里分别出现，
              因为各组的评价标准不同，混在一起会让人误以为少了方案。）"""
            items = collect(src, dst, max(k * 4, 12))
            sections = []
            for mode, title, desc in m.GROUPS:
                ordered = sorted(items, key=lambda x: _key(mode, x[2]))
                sections.append((mode, title, desc, ordered[:k]))
            return sections

        m.transfer_weight = transfer_weight
        m.build_graph = build_graph
        m.dijkstra = dijkstra
        m.k_shortest_states = k_shortest_states
        m.to_segments = to_segments
        m.tidy = tidy
        m.station_sequence = station_sequence
        m.path_cost = path_cost
        m.collect = collect
        m.search = search
        m._key = _key
        m._add = _add
        m.parse_line_key = None
        build_graph(m.LINES, "weight")
        return m

    # -- 载入 -------------------------------------------------------------
    @staticmethod
    def _load(path):
        name = "tpc_metro_engine"
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError("无法加载 %s" % path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        for attr in ("LINES", "NAMES", "build_graph", "collect", "to_segments",
                     "tidy", "station_sequence", "path_cost", "k_shortest_states"):
            if not hasattr(mod, attr):
                raise ImportError("%s 里没有 %s，可能不是线路查询脚本" % (path, attr))
        return mod

    def _install_patched_search(self):
        """标准 search() 每次都重新跑三遍 Yen，重复计算。这里用缓存 + 生成器提速，
        排序键和分组规则（"综合较优 / 换乘最少 / 区间最少"，同一走法不重复）与原版一致。"""
        m = self.mod

        def collect_cached(src, dst, per_mode):
            for mode in ("score", "trans", "hops"):
                for states in m.k_shortest_states(src, dst, per_mode, mode):
                    yield mode, states

        def fast_search(src, dst, k=1):
            need = max(k * 4, 12)
            cands = {}
            for mode, states in collect_cached(src, dst, need):
                segs = m.tidy(m.to_segments(states))
                seq = m.station_sequence(segs)
                if len(seq) < 2 or seq[0] != src or seq[-1] != dst:
                    continue
                if len(set(seq)) != len(seq):
                    continue
                key = tuple(seq)
                if key not in cands:
                    cands[key] = (segs, m.path_cost(states))
            items = [(key, segs, cost) for key, (segs, cost) in cands.items()]

            used, sections = set(), []
            for mode, title, desc in getattr(m, "GROUPS", DEFAULT_GROUPS):
                ordered = sorted(items, key=lambda x: m._key(mode, x[2]))
                picked = []
                for x in ordered:
                    if x[0] in used:
                        continue
                    picked.append(x)
                    if len(picked) >= k:
                        break
                if not picked:
                    sections.append((mode, title, desc, []))
                    continue
                used.update(x[0] for x in picked)
                sections.append((mode, title, desc, picked))
            return sections

        # 与标准版对比一次；不一致就退回标准版，保证结果以原脚本为准
        try:
            a = m.search("葵园村", "神殿", 2)
            b = fast_search("葵园村", "神殿", 2)
            if [x[0] for x in a] != [x[0] for x in b] or \
               [[y[0] for y in x[3]] for x in a] != [[y[0] for y in x[3]] for x in b]:
                return m.search
        except Exception:
            return m.search
        return fast_search

    # -- 查询 -------------------------------------------------------------
    def search(self, src, dst, k=1):
        return self.search_impl(src, dst, k)

    def line_name(self, lk):
        nm = self.NAMES
        return nm.get(lk, lk[1:] if lk.startswith("L") else lk)

    # -- 输入解析 ---------------------------------------------------------
    def resolve(self, text):
        """站名 -> (标准站名 或 None, 候选列表, 是否直接命中)"""
        name = (text or "").strip()
        if not name:
            return None, [], True
        if name in self.STATION_LINES:
            return name, [], True
        hits = [s for s in self.STATIONS if name in s]
        if not hits:
            hits = [s for s in self.STATIONS if name.lower() in s.lower()]
        if len(hits) == 1:
            return hits[0], [], False
        near = difflib.get_close_matches(name, self.STATIONS, n=6, cutoff=0.3)
        cands = hits or near
        return None, cands, False

    def stations_matching(self, text, limit=None):
        text = (text or "").strip()
        if not text:
            return list(self.STATIONS)
        low = text.lower()
        ins = [s for s in self.STATIONS if low in s.lower()]
        if len(ins) < 12:
            pre = [s for s in self.STATIONS if s.lower().startswith(low) and s not in ins]
            ins += pre
        if not ins:
            ins = difflib.get_close_matches(text, self.STATIONS, n=12, cutoff=0.25)
        return ins[:limit] if limit else ins

    def line_key(self, text):
        t = str(text or "").strip()
        for pre in ("线路", "LINE", "line"):
            if t.upper().startswith(pre.upper()):
                t = t[len(pre):].strip()
        t = t.replace(" ", "")
        if not t:
            return None
        u = t.upper()
        groups = getattr(self, "LINE_GROUPS", {}) or {}
        # 3 / 3号线 -> 合并的 3 号线（北段+南段）
        for gk in groups:
            if u == gk.upper() or u == (self.NAMES.get(gk, "") or "").upper():
                return gk
        short = u.replace("号线", "").replace("线", "")
        for gk in groups:
            if short == gk.replace("L", "").upper():
                return gk
        for gk, parts in groups.items():
            for pk in parts:
                pname = self.NAMES.get(pk, "")
                if u in (pk.upper(), pname.upper(),
                         pname.replace("号线", "").upper(),
                         (gk.replace("L", "") + pk[-1]).upper()):
                    return pk
        parse = getattr(self.mod, "parse_line_key", None)
        if parse:
            try:
                lk = parse(text)
                if lk in self.LINES or lk in groups:
                    return lk
            except Exception:
                pass
        for lk, nm in self.NAMES.items():
            if u in (lk.upper(), nm.upper()):
                return lk
        if "L" + u in self.LINES:
            return "L" + u
        return None

    def lines_matching(self, text, limit=8):
        low = (text or "").strip().lower()
        out = []
        for lk in self.LINES:
            nm = self.line_name(lk)
            hay = (lk + " " + nm + " " + nm.replace("号线", "")).lower()
            if not low or low in hay:
                out.append(lk)
        return out[:limit]

    # -- 线路信息 ---------------------------------------------------------
    def line_info(self, lk):
        # 3 号线这种「一条线拆成两段」的写法：合并成一张站表
        group = getattr(self, "LINE_GROUPS", {}).get(lk)
        if group:
            parts = [self.line_info(k) for k in group]
            stations, idx = [], 1
            for part in parts:
                for st in part["stations"]:
                    st = dict(st)
                    st["index"] = idx
                    st["section"] = part["name"]
                    idx += 1
                    stations.append(st)
            return {
                "key": lk,
                "name": self.NAMES.get(lk, lk),
                "ring": False,
                "count": len(stations),
                "first": stations[0]["name"] if stations else "",
                "last": stations[-1]["name"] if stations else "",
                "stations": stations,
                "grouped": [p["name"] for p in parts],
            }
        seq = self.LINES[lk]
        ring = lk in self.RING
        body = seq[:-1] if ring else list(seq)
        stations = []
        for i, s in enumerate(body):
            others = [self.line_name(x) for x in self.STATION_LINES[s] if x != lk]
            stations.append({
                "name": s,
                "index": i + 1,
                "transfers": [(x, self.line_name(x)) for x in self.STATION_LINES[s] if x != lk],
                "other_names": others,
            })
        return {
            "key": lk,
            "name": self.line_name(lk),
            "ring": ring,
            "count": len(body),
            "first": seq[0],
            "last": seq[-1],
            "stations": stations,
            "grouped": None,
        }

    def line_sequence_preview(self, lk, limit=14):
        seq = self.LINES.get(lk) or []
        if lk in self.RING and len(seq) > 1:
            seq = seq[:-1]
        txt = " · ".join(seq[:limit])
        if len(seq) > limit:
            txt += " …"
        return txt

    # -- 站点查询：经过的线路 + 各方向前后一站 ---------------------------
    def station_info(self, name):
        """返回某站点的详细信息：
             lines: [{line, ...}]
             dirs:  每条线路每个方向的前一站 / 后一站
        """
        lks = self.STATION_LINES.get(name)
        if not lks:
            return None
        lines = []
        for lk in lks:
            seq = list(self.LINES[lk])
            ring = lk in self.RING
            body = seq[:-1] if ring else seq       # 环线去掉重复的终点
            n = len(body)
            idx = body.index(name) if name in body else -1
            dirs = []
            if idx >= 0 and n > 1:
                if ring:
                    prev_st = body[(idx - 1) % n]
                    next_st = body[(idx + 1) % n]
                    dirs.append({
                        "dir": "环线双向",
                        "prev": prev_st, "next": next_st,
                        "prev_label": "上一站", "next_label": "下一站",
                        "ring": True,
                    })
                else:
                    if idx > 0:
                        dirs.append({"dir": "往 %s" % body[0],
                                     "prev": body[idx - 1],
                                     "next": None, "prev_label": "上一站",
                                     "next_label": "", "ring": False})
                    if idx < n - 1:
                        dirs.append({"dir": "往 %s" % body[-1],
                                     "prev": body[idx + 1],
                                     "next": None, "prev_label": "下一站",
                                     "next_label": "", "ring": False})
            lines.append({
                "key": lk,
                "name": self.line_name(lk),
                "index": idx + 1,
                "count": n,
                "ring": ring,
                "first": body[0] if body else "",
                "last": body[-1] if body else "",
                "dirs": dirs,
            })
        transfers = [self.line_name(x) for x in lks]
        return {
            "name": name,
            "lines": lines,
            "line_names": transfers,
            "is_transfer": len(lks) > 1,
        }


DEFAULT_GROUPS = (
    ("score", "综合较优", "得分 = 区间数 + 换乘数 x 2，越小越好"),
    ("trans", "换乘最少", "先比换乘次数，再比区间数"),
    ("hops", "区间最少", "先比区间数，再比换乘次数"),
)

# 新版算法（metro_query.py）：按真实里程 + 换乘权重
WEIGHT_GROUPS = (
    ("weight", "权重最优", "总权重 = 总里程 + 换乘权重，越小越好"),
    ("trans", "换乘最少", "先比换乘次数，再比总权重"),
    ("hops", "区间最少", "先比区间数，再比总权重"),
)

GROUPS_BY_ALGO = {"score": DEFAULT_GROUPS, "weight": WEIGHT_GROUPS}


def app_dir():
    """程序所在目录（兼容 PyInstaller 打包后的单文件 EXE）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def find_data_file():
    """找外部线路脚本：只有用户在设置里指定、或同目录放了新脚本时才用。
    都没找到就返回 None，程序改用内置数据。"""
    # 默认用内置的新版数据；只有用户在「数据文件」里显式指定过外部脚本才加载它
    cfg = load_config()
    p = cfg.get("data_file")
    if p and os.path.isfile(p):
        return p
    return None


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, CONFIG_NAME), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_config(cfg):
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, CONFIG_NAME), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# __UI_START__


# ============================================================================
#  第二部分：主题 / 小部件
# ============================================================================

PALETTES = {
    "light": dict(BG=BG, CARD=CARD, BORDER=BORDER, TEXT=TEXT, MUTED=MUTED,
                  ACCENT=ACCENT, ACCENT_DK=ACCENT_DK, ACCENT_LT=ACCENT_LT, CHIP=CHIP,
                  SEL="#e3ebfd", LINK="@"),
    "dark": dict(BG=DBG, CARD=DCARD, BORDER=DBORDER, TEXT=DTEXT, MUTED=DMUTED,
                 ACCENT=DACCENT, ACCENT_DK="#8ab0ff", ACCENT_LT=DACCENT_LT, CHIP=DCHIP,
                 SEL="#2f3a50", LINK="#8ab8ff"),
}

FONT_FAMILIES = ("Microsoft YaHei UI", "Microsoft YaHei", "微软雅黑",
                 "SimHei", "Noto Sans CJK SC", "PingFang SC")


def pick_font(root):
    try:
        fams = set(tkfont.families(root))
    except Exception:
        fams = set()
    for f in FONT_FAMILIES:
        if f in fams:
            return f
    return "TkDefaultFont"


def make_fonts(root):
    fam = pick_font(root)
    base = tkfont.Font(root=root, family=fam, size=10)
    return {
        "name": fam,
        "base": base,
        "small": tkfont.Font(root=root, family=fam, size=9),
        "title": tkfont.Font(root=root, family=fam, size=20, weight="bold"),
        "h2": tkfont.Font(root=root, family=fam, size=12, weight="bold"),
        "h3": tkfont.Font(root=root, family=fam, size=10, weight="bold"),
        "mono": tkfont.Font(root=root, family="Cascadia Mono", size=10),
        "mono_s": tkfont.Font(root=root, family="Cascadia Mono", size=9),
        "big": tkfont.Font(root=root, family=fam, size=14, weight="bold"),
    }


def mix(c1, c2, t):
    """两个 #rrggbb 颜色按 t(0=c1,1=c2) 混合。"""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def h_scale(h):
    return mix("#ffffff", h, 0.80)


def h_dark(h):
    return mix(h, "#000000", 0.30)


class Style:
    """只管颜色 + 字体，控件样式每次切换主题时统一下发给子控件。"""

    def __init__(self, app):
        self.app = app
        self.theme = "light"
        self.colors = dict(PALETTES["light"])
        self.fonts = make_fonts(app.root)
        self.subscribers = []

    def c(self, key):
        return self.colors[key]

    def f(self, key):
        return self.fonts[key]

    def subscribe(self, fn):
        self.subscribers.append(fn)
        return fn

    def notify(self):
        for fn in list(self.subscribers):
            try:
                fn()
            except Exception:
                traceback.print_exc()

    def toggle(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.colors = dict(PALETTES[self.theme])
        self.notify()


class Widget:
    """方便按主题统一改色的视图基类（本身不是 tk 控件，容器放在 self.frame）。"""

    def __init__(self, style):
        self.style = style
        self._alive = True
        self._unsub = style.subscribe(self._on_style)
        self.build()

    def alive(self):
        if not self._alive:
            return False
        try:
            return bool(self.frame.winfo_exists())
        except Exception:
            return False

    def _on_style(self):
        if not self.alive():
            self._alive = False
            if self._unsub in self.style.subscribers:
                self.style.subscribers.remove(self._unsub)
            return
        self.apply_theme()

    def destroy(self):
        self._alive = False
        if self._unsub in self.style.subscribers:
            self.style.subscribers.remove(self._unsub)
        try:
            self.frame.destroy()
        except Exception:
            pass

    def build(self):
        pass

    def apply_theme(self):
        pass

    def build(self):
        pass

    def apply_theme(self):
        pass


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class RoundedButton(tk.Canvas):
    """圆角按钮（tk.Button 没法做圆角，自己画一个）。"""

    def __init__(self, parent, style, text, command=None, kind="primary", **kw):
        self.style = style
        self.text = text
        self.command = command
        self.kind = kind           # primary / secondary / ghost
        self.fw = kw.pop("font", style.f("h3"))
        self.pad = kw.pop("padx", 16)
        self.pady = kw.pop("pady", 9)
        self.enabled = True
        self.hover = False
        self._cw = None
        self._ch = None
        self._job = None
        super().__init__(parent, highlightthickness=0, bd=0,
                         cursor="hand2", **kw)
        self.bind("<Configure>", self._on_conf)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.style.subscribe(self.redraw)
        self.redraw()

    def set_text(self, text):
        self.text = text
        self.redraw()

    def set_enabled(self, flag):
        self.enabled = bool(flag)
        self.configure(cursor="hand2" if flag else "arrow")
        self.redraw()

    def _on_conf(self, ev):
        if (ev.width, ev.height) != (self._cw, self._ch):
            self._cw, self._ch = ev.width, ev.height
            self.redraw()
    def _on_enter(self, _):
        self.hover = True
        self.redraw()

    def _on_leave(self, _):
        self.hover = False
        self.redraw()

    def _on_press(self, _):
        self._pressed = True

    def _on_release(self, _):
        if getattr(self, "_pressed", False) and self.enabled:
            self._pressed = False
            if self.command:
                self.command()

    def redraw(self):
        if not self._cw or not self._ch or not self.winfo_exists():
            return
        c = self.style.c
        if self.kind == "primary":
            bg = c("ACCENT_DK") if self.hover else c("ACCENT")
            fg = "#ffffff"
            border = bg
        elif self.kind == "secondary":
            bg = c("ACCENT_LT")
            fg = c("ACCENT_DK")
            border = c("ACCENT")
        else:
            bg = c("CHIP")
            fg = c("TEXT")
            border = c("BORDER")
        if not self.enabled:
            bg = mix(bg, c("CARD"), 0.55)
            fg = c("MUTED")
            border = c("BORDER")
        self.delete("all")
        w, h = self._cw, self._ch
        self.configure(bg=c("CARD"))
        r = min(8, h // 2)
        self._round_rect(1, 1, w - 2, h - 2, r, fill=bg, outline=border)
        self.create_text(w // 2, h // 2 + 1, text=self.text, fill=fg, font=self.fw)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        n = 4                      # 每个角 4 段：圆角只在拐角处生效
        pts = []
        for cx, cy, a0 in ((x2 - r, y1 + r, 270), (x2 - r, y2 - r, 0),
                           (x1 + r, y2 - r, 90), (x1 + r, y1 + r, 180)):
            for i in range(n + 1):
                import math
                a = math.radians(a0 + 90.0 * i / n)
                pts.extend((cx + r * math.cos(a), cy + r * math.sin(a)))
        return self.create_polygon(pts, smooth=False, **kw)


class ScrollFrame(tk.Frame):
    """带竖滚动条的容器；内容放在 .inner。"""

    def __init__(self, parent, style, bg=None, **kw):
        self.style = style
        super().__init__(parent, bg=bg or style.c("BG"), **kw)
        self.canvas = tk.Canvas(self, bg=bg or style.c("BG"),
                                highlightthickness=0, bd=0)
        self.ysb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.ysb.pack(side="right", fill="y")
        self.inner = tk.Frame(self.canvas, bg=bg or style.c("BG"))
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)
        self.style.subscribe(self._theme)
        self.reset_scroll_region()

    def reset_scroll_region(self):
        self.inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_inner(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, ev):
        self.canvas.itemconfigure(self._win, width=ev.width)

    def _bind_wheel(self, _):
        self.canvas.bind_all("<MouseWheel>", self._wheel)

    def _unbind_wheel(self, _):
        self.canvas.unbind_all("<MouseWheel>")

    def _wheel(self, ev):
        first, last = self.canvas.yview()
        if first <= 0.0 and last >= 1.0:
            return
        self.canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")

    def _theme(self):
        bg = self.style.c("BG")
        self.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.inner.configure(bg=bg)

    def clear(self):
        for ch in list(self.inner.winfo_children()):
            ch.destroy()
        self.reset_scroll_region()


class StationPicker(tk.Frame):
    """可输入、可下拉的站名选择框：输入关键字过滤，回车依次试 起点/终点。"""

    def __init__(self, parent, app, role, width=16, font=None):
        self.app = app
        self.style = app.style
        self.role = role
        self.width = width
        self.font = font or self.style.f("base")
        super().__init__(parent, bd=0, highlightthickness=1)
        self.var = tk.StringVar()
        self.box = ttk.Combobox(self, textvariable=self.var, width=width,
                                font=self.font, state="normal")
        self.box.pack(fill="x", expand=True, padx=1, pady=1)
        self.var.trace_add("write", self._on_type)
        self.box.bind("<Return>", self._on_return)
        self.box.bind("<KP_Enter>", self._on_return)
        self.box.bind("<Down>", self._on_down)
        self.box.bind("<FocusOut>", lambda e: app.update_placeholders())
        self.box.bind("<FocusIn>", lambda e: app.update_placeholders())
        self.style.subscribe(self.apply_theme)
        self.apply_theme()

    def apply_theme(self):
        c = self.style.c
        try:
            self.configure(bg=c("CARD"), highlightbackground=c("BORDER"),
                           highlightcolor=c("ACCENT"))
        except tk.TclError:
            pass

    def get(self):
        return self.var.get().strip()

    def set(self, text):
        self.var.set(text)
        self.box.selection_clear()
        self.box.icursor("end")

    def focus_set(self):
        self.box.focus_set()
        self.box.select_range(0, "end")

    def _on_type(self, *_):
        text = self.var.get().strip()
        stations = self.app.data.stations_matching(text, limit=40) if text else []
        self.box.configure(values=stations)
        self.app.update_placeholders()

    def _on_down(self, _):
        if self.box.get() and not self.box["values"]:
            self._on_type()
        return None

    def _on_return(self, _):
        name = self.get()
        if not name:
            return
        hits = self.app.data.stations_matching(name, limit=1)
        if hits:
            canon = self.app.data.resolve(name)[0] or hits[0]
            self.set(canon)
        self.app.submit_from(self.role)
        return "break"


def fmt_num(x):
    """1213.0 -> '1213'，1213.5 -> '1213.5'"""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    return str(int(f)) if f.is_integer() else ("%.1f" % f)


class RouteCard(tk.Frame):
    """一条候选路径的可展开卡片：
         概要行 = 起点 → 途经线路 → 终点 + 数据
         展开后 = 逐段列出 [起点] --3号线--> [换乘站] ……
    """

    def __init__(self, parent, app, card_payload, query_symbol, on_use):
        self.app = app
        self.style = app.style
        self.p = card_payload
        self.query_symbol = query_symbol
        # on_use(name, role)  —— role 为 "src" 时设为起点，为 "dst" 时设为终点
        self.on_use = on_use
        self.open = True
        self.chips = []           # [(label 控件名, 线路键)]
        super().__init__(parent, bg=self.style.c("CARD"), bd=0,
                         highlightthickness=1)
        self.bind("<Configure>", self._on_card_conf)
        self._draw_bg()
        self.body = tk.Frame(self, bg=self.style.c("CARD"))
        self.body.pack(fill="x", expand=True, padx=12, pady=(9, 8))
        self._build_head()
        self.detail = None
        # 路线示意条常驻显示（收起时也能直接看到路线，不用再点展开）
        self._build_detail()
        self.style.subscribe(self.apply_theme)

    def _unsubscribe(self):
        try:
            self.style.subscribers.remove(self.apply_theme)
        except ValueError:
            pass

    def destroy(self):
        self._unsubscribe()
        super().destroy()

    def _on_card_conf(self, ev):
        """卡片尺寸变化：重画边框即可（路线示意由 SegmentStrip 自己处理）。"""
        self._draw_bg()

    def _draw_bg(self):
        c = self.style.c
        try:
            self.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
        except tk.TclError:
            pass

    def _build_head(self):
        c = self.style.c
        p = self.p
        top = tk.Frame(self.body, bg=c("CARD"))
        top.pack(fill="x")

        head = tk.Frame(top, bg=c("CARD"))
        head.pack(side="left", fill="x", expand=True)
        left = tk.Frame(head, bg=c("CARD"))
        left.pack(side="left", fill="x", expand=True)

        names = tk.Frame(left, bg=c("CARD"))
        names.pack(anchor="w")
        self.start_lbl = tk.Label(names, text=p["src"], bg=c("CARD"), fg=c("TEXT"),
                                  font=self.style.f("h2"), cursor="hand2")
        self.start_lbl.pack(side="left")
        self.start_lbl.bind("<Button-1>", lambda e: self.on_use(p["src"], "src"))
        self.start_lbl.bind("<Enter>", lambda e: self.start_lbl.configure(fg=c("ACCENT")))
        self.start_lbl.bind("<Leave>", lambda e: self.start_lbl.configure(fg=c("TEXT")))
        arrow = tk.Label(names, text="  %s  " % ARROW, bg=c("CARD"), fg=c("MUTED"),
                         font=self.style.f("h2"))
        arrow.pack(side="left")
        self.end_lbl = tk.Label(names, text=p["dst"], bg=c("CARD"), fg=c("TEXT"),
                                font=self.style.f("h2"), cursor="hand2")
        self.end_lbl.pack(side="left")
        self.end_lbl.bind("<Button-1>", lambda e: self.on_use(p["dst"], "dst"))
        self.end_lbl.bind("<Enter>", lambda e: self.end_lbl.configure(fg=c("ACCENT")))
        self.end_lbl.bind("<Leave>", lambda e: self.end_lbl.configure(fg=c("TEXT")))

        meta = tk.Frame(left, bg=c("CARD"))
        meta.pack(anchor="w", pady=(3, 0))
        self.meta_row = meta
        self.meta_labels = []
        for txt in self._meta_texts():
            lb = tk.Label(meta, text=txt, bg=c("CARD"), fg=c("MUTED"),
                          font=self.style.f("small"))
            lb.pack(side="left", padx=(0, 12))
            self.meta_labels.append((lb, txt))

        # 路线示意统一由 SegmentStrip 呈现（v1.0.4：去掉重复的线路标签行）

        right = tk.Frame(top, bg=c("CARD"))
        right.pack(side="right", padx=(10, 0))
        # 示意图条已常驻，按钮保留用于收起/展开细节（默认展开）
        self.toggle_btn = RoundedButton(right, self.style, "收起", self.toggle,
                                        kind="ghost", font=self.style.f("small"),
                                        padx=10, pady=5, width=64, height=26)
        self.toggle_btn.pack()

    def _meta_texts(self):
        p = self.p
        texts = ["%d 站" % p["stations"], "%d 区间" % p["hops"],
                 "换乘 %d 次" % p["trans"]]
        # 新版显示里程 + 权重；旧版只显示得分
        if p.get("meters") is not None:
            texts.append(fmt_num(p["meters"]) + " m")
            texts.append("权重 " + fmt_num(p["weight"]))
        else:
            texts.append("得分 %d" % p["score"])
        if p.get("transfer_names"):
            texts.append("换乘站：" + "、".join(p["transfer_names"]))
        return texts

    def apply_theme(self):
        if not self.winfo_exists():
            self._unsubscribe()
            return
        c = self.style.c
        self._draw_bg()
        for w in (self.body, self.toggle_btn.master, self.dst_cvs):
            w.configure(bg=c("CARD"))
        for lb, txt in self.meta_labels:
            lb.configure(bg=c("CARD"), fg=c("MUTED"))
        for w in (self.start_lbl, self.end_lbl):
            w.configure(bg=c("CARD"), fg=c("TEXT"))
        # 示意图条按新主题重画（无论展开与否都由它显示路线）
        if self.detail is not None:
            self.detail.destroy()
            self.detail = None
            self._build_detail()

    def toggle(self):
        """收起 / 展开下方路线示意条。"""
        self.open = not self.open
        self.toggle_btn.set_text("收起" if self.open else "展开")
        if self.open:
            if self.detail is None:
                self._build_detail()
        elif self.detail is not None:
            self.detail.destroy()
            self.detail = None
        self.app.refresh_later()

    def _build_detail(self):
        self.detail = SegmentStrip(self.body, self.app, self.p["segs"])
        self.detail.pack(fill="x", pady=(10, 2))
        self.app.refresh_later()


class SegmentStrip(tk.Canvas):
    """把分段路径画成示意条：

             葵园村                    林南大道                刷铁机
        ●━━━━━━━━━━━━━━━━━━━━━━━━┫━━━━━━━━━━━━━━━━━━━━━━━━━━●
         1号线 四威、涵址、暗东湖…         12号线 世纪大道东…

    竖向布局（v1.0.3 修复文字压线问题）：
        站名行   y = 0  .. 18
        色条行   y = 26 .. 32（LINE_Y = 29）
        线路行   y = 38 ..  (anchor="n")
    真实绘制宽度取自 <Configure> 的 ev.width，不用（滞后的）winfo_width。
    """

    NAME_H = 18          # 站名行高度
    LINE_Y = 29          # 色条中心纵坐标
    SUBNEXT = 9          # 色条到下方线路文字的间距
    PAD = 16
    NODE_R = 5
    XFER_R = 8
    GAP = 24
    MIN_SEG = 74

    def __init__(self, parent, app, segs):
        self.app = app
        self.style = app.style
        self.segs = segs
        self._cw = 0
        super().__init__(parent, bg=self.style.c("CARD"),
                         highlightthickness=0, bd=0, height=100)
        self.bind("<Configure>", self._on_conf)
        self.style.subscribe(self._theme)

    def _theme(self):
        if not self.winfo_exists():
            return
        self.configure(bg=self.style.c("CARD"))
        self.redraw(self._cw or None)

    def _on_conf(self, ev):
        if not self.winfo_exists():
            return
        self._cw = ev.width          # 记录真实宽度
        if ev.width > 1:
            self.redraw(ev.width)

    def _txt_w(self, text, font):
        return self.app.measure(text, font)

    def redraw(self, width=None):
        if not self.winfo_exists():
            return
        st = self.style
        c = st.c
        w = width if (width and width > 1) else max(self._cw, self.winfo_width())
        if w <= 1:                      # 布局未就绪，稍后再画
            self.after(40, lambda: self.redraw(None))
            return
        self.delete("all")
        self.configure(bg=c("CARD"))
        fb, fs = st.f("h3"), st.f("small")
        y = self.LINE_Y
        n = len(self.segs)
        if not n:
            self.configure(height=40)
            return

        # ---- 1. 每段的文字与长度 ----
        plan = []
        for lk, stations in self.segs:
            mid = stations[1:-1]
            name = self.app.data.line_name(lk)
            body = ("%s  %s" % (name, "、".join(mid))) if mid else \
                   (name + "（无途经站）")
            plan.append({"body": body,
                         "color": self.app.line_colors.get(lk, c("ACCENT"))})

        share = max(70, (w - 2 * self.PAD) / float(n) - 2 * self.GAP)
        for p in plan:
            p["lines"] = self._wrap(p["body"], fs, share)
            p["text_w"] = max(self._txt_w(t, fs) for t in p["lines"])
            p["seg_w"] = max(self.MIN_SEG, p["text_w"] + 2 * self.GAP)

        total = sum(p["seg_w"] for p in plan)
        avail = w - 2 * self.PAD
        if total > avail > 0:
            k = avail / float(total)
            for p in plan:
                p["seg_w"] = max(48, int(p["seg_w"] * k))

        xs = [self.PAD]
        for p in plan:
            xs.append(xs[-1] + p["seg_w"])

        # ---- 2. 色条：起点圆心 -> 终点圆心，连续不断 ----
        for i, p in enumerate(plan):
            self.create_line(xs[i], y, xs[i + 1], y, fill=p["color"],
                             width=6, capstyle="butt")

        # ---- 3. 色条下方的线路名 / 途经站 ----
        for i, p in enumerate(plan):
            cx = (xs[i] + xs[i + 1]) / 2.0
            for j, line in enumerate(p["lines"]):
                self.create_text(cx, y + self.SUBNEXT + j * 15, text=line,
                                 fill=c("TEXT"), font=fs, anchor="n")

        # ---- 4. 节点（画在色条之上）----
        self._node(xs[0], y, transfer=False)
        for i in range(n):
            self._node(xs[i + 1], y, transfer=(i != n - 1), solid=(i == n - 1))

        # ---- 5. 站名最后画：保证压在色条与节点之上、不被遮挡 ----
        #     以节点圆顶部为基线向上排，y 坐标固定在第 1 行文字区
        self._station_name(xs[0], self.segs[0][1][0], fb, w)
        for i in range(n):
            self._station_name(xs[i + 1], self.segs[i][1][-1], fb, w,
                               last=(i == n - 1))

        max_lines = max(len(p["lines"]) for p in plan)
        needed = int(y + self.SUBNEXT + max_lines * 15 + 8)
        if abs(int(self["height"]) - needed) > 2:
            self.configure(height=needed)

    def _station_name(self, x, name, font, w, last=False):
        """站名画在色条上方固定行，并与相邻站名做左右避让。"""
        c = self.style.c
        tw = self._txt_w(name, font)
        lo = tw / 2.0 + 2
        hi = max(lo, w - tw / 2.0 - 2)
        tx = min(max(x, lo), hi)
        # anchor="s"，基线放在色条顶部稍上方，不会碰到色条
        base_y = self.LINE_Y - self.XFER_R - 3
        self.create_text(tx, base_y, text=name, anchor="s", font=font,
                         fill=c("TEXT"))

    def _wrap(self, text, font, max_px):
        """按像素宽度折行，切点优先落在顿号之后。"""
        if max_px <= 24:
            return [text]
        if self._txt_w(text, font) <= max_px:
            return [text]
        lines, cur = [], ""
        for ch in text:
            if self._txt_w(cur + ch, font) > max_px and cur:
                cut = cur.rfind("、")
                if cut > 0 and len(cur) - cut < 14:
                    lines.append(cur[:cut + 1])
                    cur = cur[cut + 1:] + ch
                else:
                    lines.append(cur)
                    cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
        return lines[:6] or [text]

    def _node(self, x, y, transfer=False, solid=False):
        c = self.style.c
        if transfer:
            r = self.XFER_R
            self.create_oval(x - r, y - r, x + r, y + r, fill=c("CARD"),
                             outline=c("TEXT"), width=2)
            self.create_oval(x - 3.5, y - 3.5, x + 3.5, y + 3.5,
                             fill=c("TEXT"), outline="")
        elif solid:
            r = 6
            self.create_oval(x - r, y - r, x + r, y + r, fill=c("TEXT"),
                             outline=c("TEXT"), width=2)
        else:
            r = self.NODE_R
            self.create_oval(x - r, y - r, x + r, y + r, fill=c("CARD"),
                             outline=c("TEXT"), width=2)


class PathView(Widget):
    def __init__(self, style, app, parent):
        self.app = app
        self.parent = parent
        super().__init__(style)

    # -- 构建 -------------------------------------------------------------
    def build(self):
        c = self.style.c
        self.frame = tk.Frame(self.parent, bg=c("BG"))
        self.frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # 查询条
        self.bar = tk.Frame(self.frame, bg=c("CARD"), highlightthickness=1,
                            highlightbackground=c("BORDER"))
        self.bar.pack(fill="x")
        inner = tk.Frame(self.bar, bg=c("CARD"))
        inner.pack(fill="x", padx=14, pady=12)

        self.src_lbl = tk.Label(inner, bg=c("CARD"), fg=c("MUTED"),
                                font=self.style.f("small"))
        self.src_lbl.grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.src = StationPicker(inner, self.app, "src", width=15)
        self.src.grid(row=1, column=0, sticky="we", padx=(0, 6))

        self.swap_btn = RoundedButton(inner, self.style, "⇄", self.app.swap,
                                      kind="secondary", padx=8, pady=8,
                                      width=42, height=36)
        self.swap_btn.grid(row=1, column=1, padx=4)

        self.dst_lbl = tk.Label(inner, bg=c("CARD"), fg=c("MUTED"),
                                font=self.style.f("small"))
        self.dst_lbl.grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.dst = StationPicker(inner, self.app, "dst", width=15)
        self.dst.grid(row=1, column=2, sticky="we", padx=(0, 10))

        self.k_lbl = tk.Label(inner, text="每组条数", bg=c("CARD"), fg=c("MUTED"),
                              font=self.style.f("small"))
        self.k_lbl.grid(row=0, column=3, sticky="w", padx=(0, 6))
        self.k_var = tk.StringVar(value="1")
        self.k_box = ttk.Combobox(inner, textvariable=self.k_var, width=4,
                                  state="readonly", font=self.style.f("base"),
                                  values=("1", "2", "3", "5", "8", "10"))
        self.k_box.grid(row=1, column=3, sticky="w", padx=(0, 10))
        self.k_box.bind("<<ComboboxSelected>>", lambda e: self.app.submit_path())

        self.go_btn = RoundedButton(inner, self.style, "查询路径", self.app.submit_path,
                                    kind="primary", padx=18, pady=8, width=118,
                                    height=36)
        self.go_btn.grid(row=1, column=4, padx=(0, 6))
        self.clear_btn = RoundedButton(inner, self.style, "清空", self.clear,
                                       kind="ghost", padx=10, pady=8, width=64,
                                       height=36)
        self.clear_btn.grid(row=1, column=5)
        inner.columnconfigure(0, weight=3, uniform="col")
        inner.columnconfigure(2, weight=3, uniform="col")

        self.hint = tk.Label(self.frame, bg=c("BG"), fg=c("MUTED"),
                             font=self.style.f("small"), anchor="w", justify="left")
        self.hint.pack(fill="x", pady=(7, 0))

        # 结果区
        self.scroll = ScrollFrame(self.frame, self.style, bg=c("BG"))
        self.scroll.pack(fill="both", expand=True, pady=(8, 0))
        self.placeholder = tk.Frame(self.scroll.inner, bg=c("BG"))
        self.placeholder.pack(fill="x", expand=True, pady=(30, 0))
        self.build_placeholder()

        self.style.subscribe(self.apply_theme)
        self.app.update_placeholders()

    def _has_placeholder(self):
        try:
            return bool(self.placeholder.winfo_exists())
        except Exception:
            return False

    def build_placeholder(self):
        c = self.style.c
        for ch in self.placeholder.winfo_children():
            ch.destroy()
        self.placeholder.configure(bg=c("BG"))
        wrap = tk.Frame(self.placeholder, bg=c("BG"))
        wrap.pack(anchor="center")
        self.ph_title = tk.Label(wrap, text="输入起点与终点，查询最优乘车方案", bg=c("BG"),
                                 fg=c("TEXT"), font=self.style.f("big"))
        self.ph_title.pack()
        self.ph_sub = tk.Label(
            wrap,
            text=("%s 条线路 · %s 个车站\n"
                  "结果按「综合较优 / 换乘最少 / 区间最少」分组，展开可看全程站序" %
                  (len(self.app.data.LINES), len(self.app.data.STATIONS))),
            bg=c("BG"), fg=c("MUTED"), font=self.style.f("base"), justify="center")
        self.ph_sub.pack(pady=(8, 0))
        try:
            for pair in self.app.history[:6]:
                chip = RoundedButton(wrap, self.style, "%s %s %s" %
                                     (pair[0], ARROW, pair[1]),
                                     lambda a=pair[0], b=pair[1]:
                                     self.app.quick_query(a, b),
                                     kind="ghost", padx=12, pady=6, height=32)
                chip.pack(pady=2)
        except Exception:
            pass

    def apply_theme(self):
        c = self.style.c
        self.frame.configure(bg=c("BG"))
        self.bar.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
        for w in (self.bar.winfo_children()[0],):
            w.configure(bg=c("CARD"))
            for ch in w.winfo_children():
                if isinstance(ch, tk.Label):
                    ch.configure(bg=c("CARD"), fg=c("MUTED"))
        self.hint.configure(bg=c("BG"), fg=c("MUTED"))
        self.src_lbl.configure(bg=c("CARD"), fg=c("MUTED"))
        self.dst_lbl.configure(bg=c("CARD"), fg=c("MUTED"))
        self.k_lbl.configure(bg=c("CARD"), fg=c("MUTED"))
        if self._has_placeholder():
            self.build_placeholder()

    def set_inputs(self, src, dst):
        self.src.set(src)
        self.dst.set(dst)

    def get_inputs(self):
        return self.src.get(), self.dst.get()

    def k(self):
        try:
            return max(1, int(self.k_var.get()))
        except ValueError:
            return 1

    def clear(self):
        self.src.set("")
        self.dst.set("")
        self.render_state("placeholder")
        self.src.focus_set()

    def show_placeholder(self):
        self.app.update_placeholders()
        self.render_state("placeholder")

    def set_hint(self, text, warn=False):
        if not hasattr(self, "hint"):
            return
        self.render_hint = (text, warn)
        self._paint_hint()

    def _paint_hint(self):
        c = self.style.c
        text, warn = getattr(self, "render_hint", ("", False))
        self.hint.configure(text="" if text is None else text,
                            fg="#c0392b" if warn else c("MUTED"))

    # -- 渲染 -------------------------------------------------------------
    def render_state(self, state, payload=None, message=None, cands=None):
        """state: placeholder / loading / error / empty / result"""
        self.scroll.clear()
        c = self.style.c
        self._paint_hint()
        if state == "placeholder":
            self.placeholder = tk.Frame(self.scroll.inner, bg=c("BG"))
            self.placeholder.pack(fill="x", expand=True, pady=(30, 0))
            self.build_placeholder()
            self.app.update_placeholders()
            self.scroll.reset_scroll_region()
            return
        if state == "loading":
            lbl = tk.Label(self.scroll.inner, text="正在计算最优路径 …", bg=c("BG"),
                           fg=c("MUTED"), font=self.style.f("base"))
            lbl.pack(pady=40)
            self.scroll.reset_scroll_region()
            return
        if state in ("error", "empty"):
            self._render_message(state, message, cands)
            self.scroll.reset_scroll_region()
            return
        if state == "result":
            self._render_result(payload)
            self.scroll.reset_scroll_region()

    def _render_message(self, state, message, cands):
        c = self.style.c
        card = tk.Frame(self.scroll.inner, bg=c("CARD"), highlightthickness=1,
                        highlightbackground=c("BORDER"))
        card.pack(fill="x", pady=(6, 0))
        inner = tk.Frame(card, bg=c("CARD"))
        inner.pack(fill="x", padx=18, pady=16)
        icon = "!" if state == "error" else "·"
        tk.Label(inner, text=icon, bg=c("CARD"), fg=c("ACCENT"),
                 font=self.style.f("big")).pack(side="left", padx=(0, 12), anchor="n")
        box = tk.Frame(inner, bg=c("CARD"))
        box.pack(side="left", fill="x", expand=True)
        tk.Label(box, text=message or "", bg=c("CARD"), fg=c("TEXT"),
                 font=self.style.f("base"), justify="left", anchor="w",
                 wraplength=760).pack(anchor="w")
        if cands:
            row = tk.Frame(box, bg=c("CARD"))
            row.pack(anchor="w", pady=(10, 0))
            for name in cands[:8]:
                b = RoundedButton(row, self.style, name,
                                  lambda n=name: self.app.pick_station(n),
                                  kind="ghost", padx=12, pady=5, height=30)
                b.pack(side="left", padx=(0, 6))

    def _render_result(self, payload):
        c = self.style.c
        sections, src, dst, sym = (payload["sections"], payload["src"],
                                   payload["dst"], payload["symbol"])
        total = sum(len(s[3]) for s in sections)
        head = tk.Frame(self.scroll.inner, bg=c("BG"))
        head.pack(fill="x", pady=(0, 8))
        tk.Label(head, text="%s  %s  %s" % (src, ARROW, dst), bg=c("BG"),
                 fg=c("TEXT"), font=self.style.f("h2")).pack(side="left")
        tk.Label(head, text="共 %d 条方案" % total, bg=c("BG"),
                 fg=c("MUTED"), font=self.style.f("small")).pack(side="left",
                                                                 padx=(10, 0))
        # 注意：RoundedButton 是 Canvas，不给定 width 会被 side="right" 撑满
        self.result_back_btn = RoundedButton(
            head, self.style, "清空结果", self.show_placeholder, kind="ghost",
            pady=4, height=28, font=self.style.f("small"),
            padx=12, width=self.app.measure("清空结果", self.style.f("small")) + 26)
        self.result_back_btn.pack(side="right")

        for gi, (mode, title, desc, picked) in enumerate(sections):
            grp = tk.Frame(self.scroll.inner, bg=c("BG"))
            grp.pack(fill="x", pady=(10, 0))
            top = tk.Frame(grp, bg=c("BG"))
            top.pack(fill="x", pady=(0, 6))
            num = "一二三四五"[gi] if gi < 5 else str(gi + 1)
            tk.Label(top, text="%s、%s" % (num, title), bg=c("BG"), fg=c("TEXT"),
                     font=self.style.f("h2")).pack(side="left")
            tk.Label(top, text="（%s）" % desc, bg=c("BG"), fg=c("MUTED"),
                     font=self.style.f("small")).pack(side="left", padx=(6, 0))
            for idx, item in enumerate(picked, 1):
                card = RouteCard(grp, self.app, item, sym, self.app.pick_station)
                card.pack(fill="x", pady=(0, 6))


    def refresh(self):
        self.scroll.reset_scroll_region()


# ============================================================================
#  第四部分：线路查询页
# ============================================================================

class LineView(Widget):
    def __init__(self, style, app, parent):
        self.app = app
        self.parent = parent
        super().__init__(style)

    def build(self):
        c = self.style.c
        self.frame = tk.Frame(self.parent, bg=c("BG"))
        self.frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self.bar = tk.Frame(self.frame, bg=c("CARD"), highlightthickness=1,
                            highlightbackground=c("BORDER"))
        self.bar.pack(fill="x")
        inner = tk.Frame(self.bar, bg=c("CARD"))
        inner.pack(fill="x", padx=14, pady=12)
        self.search_lbl = tk.Label(inner, bg=c("CARD"), fg=c("MUTED"),
                                   font=self.style.f("small"))
        self.search_lbl.grid(row=0, column=0, sticky="w")
        self.var = tk.StringVar()
        self.box = ttk.Combobox(inner, textvariable=self.var, width=24,
                                font=self.style.f("base"), state="normal")
        self.box.grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.var.trace_add("write", self._on_type)
        self.box.bind("<Return>", lambda e: self.app.submit_line())
        self.box.bind("<<ComboboxSelected>>", lambda e: self.app.submit_line())
        self.go_btn = RoundedButton(inner, self.style, "查看线路", self.app.submit_line,
                                    kind="primary", padx=18, pady=8, width=112,
                                    height=36)
        self.go_btn.grid(row=1, column=1)
        inner.columnconfigure(0, weight=0)

        # 线路快捷选择区
        self.chip_title = tk.Label(self.frame, bg=c("BG"), fg=c("MUTED"),
                                   font=self.style.f("small"), anchor="w")
        self.chip_title.pack(fill="x", pady=(10, 4))
        self.chip_area = tk.Frame(self.frame, bg=c("BG"))
        self.chip_area.pack(fill="x")
        self.build_chips()

        self.scroll = ScrollFrame(self.frame, self.style, bg=c("BG"))
        self.scroll.pack(fill="both", expand=True, pady=(10, 0))
        self.render_state("placeholder")

    def build_chips(self):
        """创建线路标签并立即按当前宽度排版。

        排版本质是「flow layout」：标签放不下就换到下一行。
        Tk 的 pack 不会自动折行，所以在 1:1 像素坐标的 Canvas 上手动摆放：
        Canvas 里的标签用 create_window 定位，再按实际行数设置画布高度。
        """
        for ch in self.chip_area.winfo_children():
            ch.destroy()
        self.chip_canvas = tk.Canvas(self.chip_area, bg=self.style.c("BG"),
                                     highlightthickness=0, bd=0, height=30)
        self.chip_canvas.pack(fill="x")
        self.chip_canvas.bind("<Configure>", lambda e: self._relayout_chips())
        self._chip_widgets = []
        self._chip_names = []
        keys = list(self.app.data.LINES.keys())
        for lk in keys:
            h = self.app.line_colors.get(lk, "#888888")
            name = self.app.data.line_name(lk)
            chip = LineChip(self.chip_canvas, self.style, name, h,
                            lambda k=lk: self.app.query_line(k),
                            width=self.app.measure(name, self.style.f("h3")) + 26)
            self._chip_widgets.append(chip)
            self._chip_names.append(lk)
        # 先按默认一行摆好，真实位置等拿到画布宽度后再算
        self._layout_targets = []
        self._relayout_chips()

    def _relayout_chips(self):
        """按画布宽度把标签流式换行摆放。"""
        canvas = getattr(self, "chip_canvas", None)
        if canvas is None or not self._chip_widgets:
            return
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
        avail = canvas.winfo_width()
        if avail <= 1:
            canvas.after(60, self._relayout_chips)
            return
        alive = [c for c in self._chip_widgets if self._chip_alive(c)]
        if not alive:
            return
        gap = 6
        x, y, row_h = 2, 2, 26
        targets = []
        for chip in alive:
            w = int(chip["width"])
            if x > 2 and x + w > avail - 4:
                x = 2
                y += row_h + gap
            targets.append((chip, x, y))
            x += w + gap
        total_h = y + row_h + 2
        canvas.configure(height=total_h)
        # 位置没变就不动，避免每次 Configure 都重排造成闪烁
        sig = tuple((str(c), cx, cy) for c, cx, cy in targets)
        if sig == getattr(self, "_layout_sig", None):
            return
        self._layout_sig = sig
        for chip in alive:
            chip.place_forget()
        for chip, cx, cy in targets:
            chip.place(in_=canvas, x=cx, y=cy, width=int(chip["width"]),
                       height=row_h)

    @staticmethod
    def _chip_alive(chip):
        try:
            return bool(chip.winfo_exists())
        except Exception:
            return False

    def apply_theme(self):
        c = self.style.c
        self.frame.configure(bg=c("BG"))
        self.bar.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
        for ch in self.bar.winfo_children()[0].winfo_children():
            if isinstance(ch, tk.Label):
                ch.configure(bg=c("CARD"), fg=c("MUTED"))
        self.chip_title.configure(bg=c("BG"), fg=c("MUTED"))
        self.chip_area.configure(bg=c("BG"))
        self._layout_sig = None
        self.build_chips()
        self.render_state("placeholder")

    def _on_type(self, *_):
        text = self.var.get().strip()
        keys = self.app.data.lines_matching(text, limit=10)
        self.box.configure(values=[self.app.data.line_name(k) for k in keys])
        self.render_state("placeholder")

    def submit(self):
        self.app.submit_line()

    def set_text(self, text):
        self.var.set(text)

    def render_state(self, state, payload=None, message=None):
        self.scroll.clear()
        c = self.style.c
        if state == "placeholder":
            self._render_placeholder()
            self.scroll.reset_scroll_region()
            return
        if state == "error":
            tk.Label(self.scroll.inner, text=message or "未找到该线路", bg=c("BG"),
                     fg="#c0392b", font=self.style.f("base"), anchor="w",
                     justify="left", wraplength=760).pack(fill="x", pady=30, padx=6)
            self.scroll.reset_scroll_region()
            return
        self._render_line(payload)
        self.scroll.reset_scroll_region()

    def _render_placeholder(self):
        c = self.style.c
        text = self.var.get().strip()
        box = tk.Frame(self.scroll.inner, bg=c("BG"))
        box.pack(fill="both", expand=True, pady=(10, 0))
        if text:
            keys = self.app.data.lines_matching(text, limit=8)
            if keys:
                tk.Label(box, text="匹配到的线路：", bg=c("BG"), fg=c("MUTED"),
                         font=self.style.f("small")).pack(anchor="w")
                for lk in keys:
                    self._preview_row(box, lk)
            else:
                tk.Label(box, text="没有匹配的线路，试试编号 8 / 13B 或中文名 玉衡1号线",
                         bg=c("BG"), fg=c("MUTED"), font=self.style.f("base")).pack(
                    anchor="w", pady=10)
        else:
            tk.Label(box, text="在上方输入线路号或点击线路标签，查看站序与换乘信息",
                     bg=c("BG"), fg=c("MUTED"), font=self.style.f("base")).pack(anchor="w")

    def _preview_row(self, parent, lk):
        info = self.app.data.line_info(lk)
        row = tk.Frame(parent, bg=self.style.c("CARD"), highlightthickness=1,
                       highlightbackground=self.style.c("BORDER"))
        row.pack(fill="x", pady=(6, 0))
        inner = tk.Frame(row, bg=self.style.c("CARD"))
        inner.pack(fill="x", padx=12, pady=8)
        LineChip(inner, self.style, info["name"],
                 self.app.line_colors.get(lk, "#888"),
                 lambda: self.app.query_line(lk)).pack(side="left", padx=(0, 10))
        tk.Label(inner, text=self.app.data.line_sequence_preview(lk), bg=self.style.c("CARD"),
                 fg=self.style.c("MUTED"), font=self.style.f("small"),
                 anchor="w").pack(side="left", fill="x", expand=True)

    def _render_line(self, info):
        c = self.style.c
        h = self.app.line_colors.get(info["key"], c("ACCENT"))
        top = tk.Frame(self.scroll.inner, bg=c("CARD"), highlightthickness=1,
                       highlightbackground=c("BORDER"))
        top.pack(fill="x")
        inner = tk.Frame(top, bg=c("CARD"))
        inner.pack(fill="x", padx=16, pady=14)
        badge = tk.Canvas(inner, bg=c("CARD"), highlightthickness=0, bd=0,
                          width=44, height=34)
        badge.create_oval(2, 2, 34, 34, fill=h, outline=h_dark(h), width=2)
        badge.create_text(18, 18, text=short_label(info["key"]), fill="#ffffff",
                          font=self.style.f("small"))
        badge.pack(side="left", padx=(0, 12))
        box = tk.Frame(inner, bg=c("CARD"))
        box.pack(side="left", fill="x", expand=True)
        tk.Label(box, text=info["name"], bg=c("CARD"), fg=c("TEXT"),
                 font=self.style.f("title")).pack(anchor="w")
        sub = "%d 座车站%s   首站 %s   末站 %s" % (
            info["count"], "（环线，首尾相接）" if info["ring"] else "",
            info["first"], info["last"])
        tk.Label(box, text=sub, bg=c("CARD"), fg=c("MUTED"),
                 font=self.style.f("small")).pack(anchor="w", pady=(2, 0))

        seq_frame = tk.Frame(self.scroll.inner, bg=c("CARD"), highlightthickness=1,
                             highlightbackground=c("BORDER"))
        seq_frame.pack(fill="x", pady=(8, 0))
        head = tk.Frame(seq_frame, bg=c("CARD"))
        head.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(head, text="全部车站（按上行方向）", bg=c("CARD"), fg=c("TEXT"),
                 font=self.style.f("h3")).pack(side="left")
        tk.Label(head, text="◇ 点击站名设为起点，右键设为终点",
                 bg=c("CARD"), fg=c("MUTED"),
                 font=self.style.f("small")).pack(side="left", padx=(10, 0))
        body = tk.Frame(seq_frame, bg=c("CARD"))
        body.pack(fill="x", padx=10, pady=(0, 10))
        cols = 3
        for i, st in enumerate(info["stations"]):
            self._station_row(body, i // cols, i % cols, st, h)
        for col in range(cols):
            body.columnconfigure(col, weight=1, uniform="st")
        if info["ring"]:
            tk.Label(seq_frame, text="↻ 环线：%s 与 %s 相邻" % (info["last"], info["first"]),
                     bg=c("CARD"), fg=c("MUTED"), font=self.style.f("small"),
                     anchor="w").pack(fill="x", padx=16, pady=(0, 10))

    def _station_row(self, parent, r, col, st, h):
        c = self.style.c
        cell = tk.Frame(parent, bg=c("CARD"))
        cell.grid(row=r, column=col, sticky="we", padx=2, pady=1)
        cvs = tk.Canvas(cell, bg=c("CARD"), highlightthickness=0, bd=0, width=30,
                        height=24)
        cvs.pack(side="left")
        cx = 15
        transfer = bool(st["transfers"])
        if transfer:
            cvs.create_oval(cx - 6, 6, cx + 6, 18, outline=c("TEXT"), width=2,
                            fill=c("CARD"))
            cvs.create_oval(cx - 2.5, 9.5, cx + 2.5, 14.5, fill=c("TEXT"), outline="")
        else:
            cvs.create_oval(cx - 4, 8, cx + 4, 16, fill=h, outline=h_dark(h))
        cvs.create_line(cx, 0, cx, 6, fill=h, width=3)
        cvs.create_line(cx, 18, cx, 24, fill=h, width=3)

        name_box = tk.Frame(cell, bg=c("CARD"))
        name_box.pack(side="left", fill="x", expand=True)
        lbl = tk.Label(name_box, text="%2d  %s" % (st["index"], st["name"]),
                       bg=c("CARD"), fg=c("TEXT"),
                       font=self.style.f("base") if not transfer
                       else self.style.f("h3"), anchor="w", cursor="hand2")
        lbl.pack(anchor="w")
        lbl.bind("<Button-1>", lambda e: self.app.pick_station(st["name"], "src"))
        lbl.bind("<Button-3>", lambda e: self.app.pick_station(st["name"], "dst"))
        lbl.bind("<Enter>", lambda e: lbl.configure(fg=c("ACCENT")))
        lbl.bind("<Leave>", lambda e: lbl.configure(fg=c("TEXT")))
        if transfer:
            for lk, nm in st["transfers"]:
                lh = self.app.line_colors.get(lk, "#888")
                t = tk.Label(name_box, text="⇄ " + nm, bg=h_scale(lh),
                             fg=h_dark(lh), font=self.style.f("small"),
                             padx=5, pady=0, cursor="hand2")
                t.pack(anchor="w", pady=(1, 0))
                t.bind("<Button-1>", lambda e, k=lk: self.app.query_line(k))


class LineChip(tk.Canvas):
    """线路圆角标签（点击查看线路）。"""

    def __init__(self, parent, style, text, color, command, width=None):
        self.style = style
        self.text = text
        self.color = color
        self.command = command
        self.hover = False
        self.font = style.f("h3")
        w = width if width else style.app.measure(text, self.font) + 26
        super().__init__(parent, highlightthickness=0, bd=0, height=24,
                         width=max(40, w), cursor="hand2", bg=style.c("BG"))
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        style.subscribe(self.redraw)
        self.redraw()

    def _enter(self, _):
        self.hover = True
        self.redraw()

    def _leave(self, _):
        self.hover = False
        self.redraw()

    def redraw(self):
        if not self.winfo_exists():
            return
        self.configure(bg=self.style.c("BG"))
        h = self.color
        bg = h if self.hover else h_scale(h)
        fg = "#ffffff" if self.hover else h_dark(h)
        self.delete("all")
        w = int(self["width"])
        self.create_rectangle(0, 1, w - 1, 23, fill=bg, outline=h_dark(h))
        self.create_text(w / 2, 12, text=self.text, fill=fg, font=self.font)


def short_label(lk):
    """L1 -> 1, L13B -> 13B, LY1 -> Y1, LT6 -> T6, LR1 -> R1"""
    if lk.startswith("L"):
        return lk[1:]
    return lk


# ============================================================================
#  第五部分：线网概览页（统计 + 全部线路目录）
# ============================================================================

class StationView(Widget):
    """「站点查询」页签：输入站名，查看经过它的线路，
    以及每条线路在该站各个方向的前一站 / 后一站。"""

    def __init__(self, style, app, parent):
        self.app = app
        self.parent = parent
        super().__init__(style)

    def build(self):
        c = self.style.c
        f = self.style.f
        self.frame = tk.Frame(self.parent, bg=c("BG"))
        self.frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # ---- 查询条 ----
        self.bar = tk.Frame(self.frame, bg=c("CARD"), highlightthickness=1,
                            highlightbackground=c("BORDER"))
        self.bar.pack(fill="x")
        inner = tk.Frame(self.bar, bg=c("CARD"))
        inner.pack(fill="x", padx=14, pady=12)
        self.search_lbl = tk.Label(inner, bg=c("CARD"), fg=c("MUTED"),
                                   font=f("small"), text="输入站名（可只输一部分）")
        self.search_lbl.grid(row=0, column=0, sticky="w")
        self.var = tk.StringVar()
        self.box = ttk.Combobox(inner, textvariable=self.var, width=26,
                                font=f("base"), state="normal")
        self.box.grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.var.trace_add("write", self._on_type)
        self.box.bind("<Return>", lambda e: self.app.submit_station())
        self.box.bind("<<ComboboxSelected>>", lambda e: self.app.submit_station())
        self.go_btn = RoundedButton(inner, self.style, "查询站点",
                                    self.app.submit_station, kind="primary",
                                    padx=18, pady=8, width=112, height=36)
        self.go_btn.grid(row=1, column=1, padx=(0, 8))
        self.hint = tk.Label(inner, bg=c("CARD"), fg=c("MUTED"),
                             font=f("small"), anchor="w")
        self.hint.grid(row=1, column=2, sticky="w", padx=(6, 0))
        inner.columnconfigure(2, weight=1)

        self.scroll = ScrollFrame(self.frame, self.style, bg=c("BG"))
        self.scroll.pack(fill="both", expand=True, pady=(10, 0))
        self.render_state("placeholder")

    # -- 输入联想 ---------------------------------------------------------
    def _on_type(self, *_):
        text = self.var.get().strip()
        names = self.app.data.stations_matching(text, limit=40) if text else []
        self.box.configure(values=names)
        self.render_state("placeholder")

    def set_text(self, text):
        self.var.set(text)

    # -- 渲染 -------------------------------------------------------------
    def render_state(self, state, payload=None, message=None):
        self.scroll.clear()
        c = self.style.c
        f = self.style.f
        if state == "placeholder":
            text = self.var.get().strip()
            box = tk.Frame(self.scroll.inner, bg=c("BG"))
            box.pack(fill="both", expand=True, pady=(10, 0))
            if text:
                keys = self.app.data.stations_matching(text, limit=12)
                if keys:
                    tk.Label(box, text="匹配到的站点（点击查看）：", bg=c("BG"),
                             fg=c("MUTED"), font=f("small")).pack(anchor="w")
                    grid = tk.Frame(box, bg=c("BG"))
                    grid.pack(anchor="w", pady=(6, 0))
                    for i, name in enumerate(keys):
                        b = RoundedButton(grid, self.style, name,
                                          lambda n=name: self.app.query_station(n),
                                          kind="ghost", padx=12, pady=5, height=30,
                                          width=self.app.measure(name, f("small")) + 26,
                                          font=f("small"))
                        b.grid(row=i // 6, column=i % 6, padx=(0, 6), pady=3,
                               sticky="w")
                else:
                    tk.Label(box, text="没有匹配的站点，换个关键字试试",
                             bg=c("BG"), fg=c("MUTED"),
                             font=f("base")).pack(anchor="w", pady=10)
            else:
                tk.Label(box, text="在上方输入站名，查看经过该站的线路与前后站",
                         bg=c("BG"), fg=c("MUTED"), font=f("base")).pack(anchor="w")
            self.scroll.reset_scroll_region()
            return
        if state == "error":
            tk.Label(self.scroll.inner, text=message or "未找到该站点", bg=c("BG"),
                     fg="#c0392b", font=f("base"), anchor="w", justify="left",
                     wraplength=900).pack(fill="x", pady=30, padx=6)
            self.scroll.reset_scroll_region()
            return
        self._render_station(payload)
        self.scroll.reset_scroll_region()

    def _render_station(self, info):
        c = self.style.c
        f = self.style.f
        app = self.app

        # ---- 站名抬头卡片 ----
        head_card = tk.Frame(self.scroll.inner, bg=c("CARD"), highlightthickness=1,
                             highlightbackground=c("BORDER"))
        head_card.pack(fill="x")
        inner = tk.Frame(head_card, bg=c("CARD"))
        inner.pack(fill="x", padx=20, pady=16)
        tk.Label(inner, text=info["name"], bg=c("CARD"), fg=c("TEXT"),
                 font=f("title")).pack(anchor="w")
        sub = ("换乘站 · 共 %d 条线路：" % len(info["line_names"])) \
            if info["is_transfer"] else ("普通站 · 线路：")
        row = tk.Frame(inner, bg=c("CARD"))
        row.pack(anchor="w", pady=(4, 0))
        tk.Label(row, text=sub, bg=c("CARD"), fg=c("MUTED"),
                 font=f("small")).pack(side="left")
        for ln in info["lines"]:
            h = app.line_colors.get(ln["key"], "#888")
            LineChip(row, self.style, ln["name"], h,
                     lambda k=ln["key"]: app.query_line(k),
                     width=app.measure(ln["name"], f("small")) + 24).pack(
                side="left", padx=(4, 0))
        # 快捷按钮
        ops = tk.Frame(inner, bg=c("CARD"))
        ops.pack(anchor="w", pady=(10, 0))
        RoundedButton(ops, self.style, "设为起点", 
                      lambda: app.pick_station(info["name"], "src"),
                      kind="secondary", padx=12, pady=5, height=30,
                      width=app.measure("设为起点", f("small")) + 26,
                      font=f("small")).pack(side="left", padx=(0, 8))
        RoundedButton(ops, self.style, "设为终点",
                      lambda: app.pick_station(info["name"], "dst"),
                      kind="ghost", padx=12, pady=5, height=30,
                      width=app.measure("设为终点", f("small")) + 26,
                      font=f("small")).pack(side="left")

        # ---- 每条线路的方向信息 ----
        for ln in info["lines"]:
            card = tk.Frame(self.scroll.inner, bg=c("CARD"), highlightthickness=1,
                            highlightbackground=c("BORDER"))
            card.pack(fill="x", pady=(8, 0))
            h = app.line_colors.get(ln["key"], "#888")
            top = tk.Frame(card, bg=c("CARD"))
            top.pack(fill="x", padx=16, pady=(12, 4))
            LineChip(top, self.style, ln["name"], h,
                     lambda k=ln["key"]: app.query_line(k),
                     width=app.measure(ln["name"], f("h3")) + 26).pack(side="left")
            meta = "第 %d / %d 站" % (ln["index"], ln["count"])
            if ln["ring"]:
                meta += "  · 环线"
            meta += "   %s → %s" % (ln["first"], ln["last"])
            tk.Label(top, text=meta, bg=c("CARD"), fg=c("MUTED"),
                     font=f("small")).pack(side="left", padx=(10, 0))

            body = tk.Frame(card, bg=c("CARD"))
            body.pack(fill="x", padx=16, pady=(4, 12))
            if not ln["dirs"]:
                tk.Label(body, text="（该线路上找不到此站）", bg=c("CARD"),
                         fg=c("MUTED"), font=f("base")).pack(anchor="w")
                continue
            for d in ln["dirs"]:
                self._dir_row(body, d, h)

    def _dir_row(self, parent, d, color):
        c = self.style.c
        f = self.style.f
        row = tk.Frame(parent, bg=c("CHIP"))
        row.pack(fill="x", pady=2)
        inner = tk.Frame(row, bg=c("CHIP"))
        inner.pack(fill="x", padx=10, pady=6)
        tk.Label(inner, text=d["dir"], bg=c("CHIP"), fg=c("TEXT"),
                 font=f("h3"), width=12, anchor="w").pack(side="left")
        # 前一站 / 后一站
        for label, station in ((d["prev_label"], d["prev"]),
                               (d["next_label"], d["next"])):
            if not label:
                continue
            cell = tk.Frame(inner, bg=c("CHIP"))
            cell.pack(side="left", padx=(0, 18))
            tk.Label(cell, text=label, bg=c("CHIP"), fg=c("MUTED"),
                     font=f("small")).pack(side="left")
            if station:
                lb = tk.Label(cell, text=station, bg=c("CHIP"), fg=c("ACCENT_DK"),
                              font=f("base"), cursor="hand2")
                lb.pack(side="left", padx=(6, 0))
                lb.bind("<Button-1>",
                        lambda e, n=station: self.app.query_station(n))
                lb.bind("<Enter>", lambda e, w=lb: w.configure(fg=c("ACCENT")))
                lb.bind("<Leave>", lambda e, w=lb: w.configure(fg=c("ACCENT_DK")))
            else:
                tk.Label(cell, text="终点站", bg=c("CHIP"), fg=c("MUTED"),
                         font=f("small")).pack(side="left", padx=(6, 0))

    def apply_theme(self):
        c = self.style.c
        self.frame.configure(bg=c("BG"))
        self.bar.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
        for ch in self.bar.winfo_children()[0].winfo_children():
            if isinstance(ch, tk.Label):
                ch.configure(bg=c("CARD"), fg=c("MUTED"))
        current = self.app.current_station if hasattr(self.app, "current_station") else None
        if current:
            info = self.app.data.station_info(current)
            if info:
                self.render_state("result", payload=info)
                return
        self.render_state("placeholder")


class OverviewView(Widget):
    def __init__(self, style, app, parent):
        self.app = app
        self.parent = parent
        super().__init__(style)

    def build(self):
        c = self.style.c
        self.frame = tk.Frame(self.parent, bg=c("BG"))
        self.frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.scroll = ScrollFrame(self.frame, self.style, bg=c("BG"))
        self.scroll.pack(fill="both", expand=True)
        self.render()

    def render(self):
        data = self.app.data
        c = self.style.c
        self.scroll.clear()
        inner = self.scroll.inner
        lines = list(data.LINES.keys())
        transfers = [s for s in data.STATIONS if len(data.STATION_LINES[s]) > 1]
        biggest = max(lines, key=lambda k: len(data.LINES[k]))
        rings = [k for k in lines if k in data.RING]
        # 3 号线北段/南段合计算 1 条
        groups = getattr(data, "LINE_GROUPS", {}) or {}
        line_count = len(lines) - sum(len(v) for v in groups.values()) + len(groups)

        stats = tk.Frame(inner, bg=c("BG"))
        stats.pack(fill="x")
        items = [("线路", str(line_count), "条"),
                 ("车站", str(len(data.STATIONS)), "座"),
                 ("换乘站", str(len(transfers)), "座"),
                 ("环线", str(len(rings)), "条")]
        for i, (label, value, unit) in enumerate(items):
            card = tk.Frame(stats, bg=c("CARD"), highlightthickness=1,
                            highlightbackground=c("BORDER"))
            card.grid(row=0, column=i, sticky="we", padx=(0 if i == 0 else 8, 0))
            box = tk.Frame(card, bg=c("CARD"))
            box.pack(padx=16, pady=12, anchor="w")
            tk.Label(box, text=label, bg=c("CARD"), fg=c("MUTED"),
                     font=self.style.f("small")).pack(anchor="w")
            row = tk.Frame(box, bg=c("CARD"))
            row.pack(anchor="w", pady=(2, 0))
            tk.Label(row, text=value, bg=c("CARD"), fg=c("TEXT"),
                     font=self.style.f("title")).pack(side="left")
            tk.Label(row, text=unit, bg=c("CARD"), fg=c("MUTED"),
                     font=self.style.f("small")).pack(side="left", padx=(3, 0))
            stats.columnconfigure(i, weight=1, uniform="stat")

        top = sorted(transfers, key=lambda s: (-len(data.STATION_LINES[s]), s))[:12]
        box = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                       highlightbackground=c("BORDER"))
        box.pack(fill="x", pady=(10, 0))
        head = tk.Frame(box, bg=c("CARD"))
        head.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(head, text="换乘枢纽 Top 12", bg=c("CARD"), fg=c("TEXT"),
                 font=self.style.f("h3")).pack(side="left")
        tk.Label(head, text="单击站名可设为起点", bg=c("CARD"), fg=c("MUTED"),
                 font=self.style.f("small")).pack(side="left", padx=(10, 0))
        grid = tk.Frame(box, bg=c("CARD"))
        grid.pack(fill="x", padx=12, pady=(0, 12))
        for i, name in enumerate(top):
            row = tk.Frame(grid, bg=c("CARD"))
            row.grid(row=i // 3, column=i % 3, sticky="w", padx=2, pady=2)
            lb = tk.Label(row, text=name, bg=c("CARD"), fg=c("TEXT"),
                          font=self.style.f("h3"), cursor="hand2")
            lb.pack(side="left")
            lb.bind("<Button-1>", lambda e, n=name: self.app.pick_station(n, "src"))
            for lk in data.STATION_LINES[name]:
                lh = self.app.line_colors.get(lk, "#888")
                tk.Label(row, text=short_label(lk), bg=h_scale(lh), fg=h_dark(lh),
                         font=self.style.f("small"), padx=4).pack(side="left",
                                                                  padx=(3, 0))
        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform="hub")

        dir_box = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                           highlightbackground=c("BORDER"))
        dir_box.pack(fill="x", pady=(10, 0))
        dh = tk.Frame(dir_box, bg=c("CARD"))
        dh.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(dh, text="全部线路（点击查看站序）", bg=c("CARD"), fg=c("TEXT"),
                 font=self.style.f("h3")).pack(side="left")
        tk.Label(dh, text="最长：%s（%d 站）" %
                 (data.line_name(biggest), len(data.LINES[biggest])),
                 bg=c("CARD"), fg=c("MUTED"),
                 font=self.style.f("small")).pack(side="left", padx=(10, 0))
        rows = tk.Frame(dir_box, bg=c("CARD"))
        rows.pack(fill="x", padx=12, pady=(0, 12))
        for i, lk in enumerate(lines):
            self._line_row(rows, i, lk)

        # ---- 扩展信息：服务器铁路局 + 轨交趣闻 ----
        self._render_bureaus(inner)
        self._render_fun_facts(inner)
        self.scroll.reset_scroll_region()

    # -- 服务器铁路局 -----------------------------------------------------
    def _render_bureaus(self, parent):
        c = self.style.c
        f = self.style.f
        box = tk.Frame(parent, bg=c("CARD"), highlightthickness=1,
                       highlightbackground=c("BORDER"))
        box.pack(fill="x", pady=(10, 0))
        head = tk.Frame(box, bg=c("CARD"))
        head.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(head, text="服务器铁路局", bg=c("CARD"), fg=c("TEXT"),
                 font=f("h3")).pack(side="left")
        tk.Label(head, text="实心线路表示已在本软件线网中，空心表示未收录",
                 bg=c("CARD"), fg=c("MUTED"),
                 font=f("small")).pack(side="left", padx=(10, 0))

        grid = tk.Frame(box, bg=c("CARD"))
        grid.pack(fill="x", padx=12, pady=(0, 12))
        for col, title in enumerate(("编号", "线路局名称", "局主", "线路")):
            tk.Label(grid, text=title, bg=c("CARD"), fg=c("MUTED"),
                     font=f("small"), anchor="w").grid(
                row=0, column=col, sticky="w", padx=(0, 14), pady=(0, 4))
        for r, (num, bureau, owner, codes) in enumerate(RAILWAY_BUREAUS, start=1):
            tk.Label(grid, text=str(num), bg=c("CARD"), fg=c("MUTED"),
                     font=f("base"), anchor="w").grid(
                row=r, column=0, sticky="w", padx=(0, 14), pady=2)
            tk.Label(grid, text=bureau, bg=c("CARD"), fg=c("TEXT"),
                     font=f("h3"), anchor="w").grid(
                row=r, column=1, sticky="w", padx=(0, 14), pady=2)
            tk.Label(grid, text=owner or "—", bg=c("CARD"),
                     fg=c("TEXT") if owner else c("MUTED"), font=f("base"),
                     anchor="w").grid(row=r, column=2, sticky="w",
                                      padx=(0, 14), pady=2)
            cell = tk.Frame(grid, bg=c("CARD"))
            cell.grid(row=r, column=3, sticky="w", pady=2)
            if not codes:
                tk.Label(cell, text="—", bg=c("CARD"), fg=c("MUTED"),
                         font=f("small")).pack(side="left")
            for code in codes:
                lk = line_key_from_code(code)
                if lk in self.app.data.LINES:
                    h = self.app.line_colors.get(lk, "#888")
                    b = tk.Label(cell, text="● %s" % code, bg=h_scale(h),
                                 fg=h_dark(h), font=f("small"), padx=5,
                                 cursor="hand2")
                    b.pack(side="left", padx=(0, 4))
                    b.bind("<Button-1>", lambda e, k=lk: self.app.query_line(k))
                else:
                    tk.Label(cell, text="○ %s" % code, bg=c("CHIP"),
                             fg=c("MUTED"), font=f("small"),
                             padx=5).pack(side="left", padx=(0, 4))
        grid.columnconfigure(3, weight=1)

    # -- 轨交趣闻 ---------------------------------------------------------
    def _render_fun_facts(self, parent):
        c = self.style.c
        f = self.style.f
        box = tk.Frame(parent, bg=c("CARD"), highlightthickness=1,
                       highlightbackground=c("BORDER"))
        box.pack(fill="x", pady=(10, 0))
        head = tk.Frame(box, bg=c("CARD"))
        head.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(head, text="轨交趣闻", bg=c("CARD"), fg=c("TEXT"),
                 font=f("h3")).pack(side="left")
        body = tk.Frame(box, bg=c("CARD"))
        body.pack(fill="x", padx=14, pady=(0, 14))
        for title, items in FUN_FACTS:
            col = tk.Frame(body, bg=c("CARD"))
            col.pack(side="left", fill="both", expand=True, padx=(0, 24))
            tk.Label(col, text=title, bg=c("CARD"), fg=c("ACCENT_DK"),
                     font=f("h3"), anchor="w").pack(anchor="w", pady=(0, 4))
            for tag, text in items:
                row = tk.Frame(col, bg=c("CARD"))
                row.pack(anchor="w", pady=1)
                tk.Label(row, text=tag, bg=c("CARD"), fg=c("MUTED"),
                         font=f("small"), anchor="w").pack(side="left",
                                                            padx=(0, 8))
                tk.Label(row, text=text, bg=c("CARD"), fg=c("TEXT"),
                         font=f("small"), anchor="w",
                         justify="left").pack(side="left")

    def _line_row(self, parent, i, lk):
        data = self.app.data
        c = self.style.c
        h = self.app.line_colors.get(lk, "#888")
        name = data.line_name(lk)
        row = tk.Frame(parent, bg=c("CARD"))
        row.pack(fill="x", pady=1)
        LineChip(row, self.style, name, h, lambda k=lk: self.app.query_line(k),
                 width=self.app.measure(name, self.style.f("h3")) + 26).pack(
            side="left", anchor="n")
        n = len(data.LINES[lk]) - (1 if lk in data.RING else 0)
        info = tk.Frame(row, bg=c("CARD"))
        info.pack(side="left", fill="x", expand=True, padx=(10, 4))
        tk.Label(info, text=("%d 站" % n) + ("  · 环线" if lk in data.RING else ""),
                 bg=c("CARD"), fg=c("MUTED"), font=self.style.f("small"),
                 anchor="w").pack(anchor="w")
        tk.Label(info, text=data.line_sequence_preview(lk), bg=c("CARD"),
                 fg=c("TEXT"), font=self.style.f("small"), anchor="w",
                 justify="left", wraplength=860).pack(anchor="w")

    def apply_theme(self):
        self.frame.configure(bg=self.style.c("BG"))
        self.render()


# ============================================================================
#  第六部分：主程序
# ============================================================================

# ============================================================================
#  扩展信息：服务器铁路局 / 轨交趣闻（在线网概览页展示）
# ============================================================================

# (编号, 线路局名称, 局主, [线路编号...])
RAILWAY_BUREAUS = (
    (1, "服铁一局", "si_quan", ["L1", "L2", "L3", "L7", "L28", "T1"]),
    (2, "HM局", "harbin_metro", ["L4", "L6", "L19"]),
    (3, "蜻莹局", "qing_ying__", ["L8", "L12", "L16", "L20"]),
    (4, "草履虫局", "yhhaaaa", ["L9"]),
    (5, "奥力局", "fv_NETEASE", ["L5", "L10", "L11", "L13"]),
    (6, "ur_10局", "destscript", ["L17"]),
    (8, "HYH局", "HYH_HS", []),
    (9, "花火局", "Harry00025", ["L25", "R1", "R2", "T3", "T6"]),
    (10, "火花局", "xiaosunkelidegou", []),
    (11, "NDS局", "Nadoshape", ["L14"]),
    (12, "狐云笙局", "hyhs", []),
    (13, "望海局", "Zele", []),
    (14, "森原局", "", []),
    (16, "合汐野局", "XLong_0485", []),
)

# 轨交趣闻：(小标题, [(数值, 说明), ...])
FUN_FACTS = (
    ("站距王", [("Top1", "2460 m　R1 蔡徐村 - 海东村 区间"),
                ("Top2", "1440 m　L20 刷冰机 - 墟影 区间"),
                ("Top3", "883 m　L8 袭击塔西 - 婉青 区间")]),
    ("换乘距离王", [("Top1", "265 m　纺林 L4 喷泉广场方向 ←→ L10 内环方向 ←→ L19 通天竹方向"),
                    ("Top2", "70 m　西寨 L13 ←→ L14")]),
)


def line_key_from_code(code):
    """铁路局表里的线路写法（L1 / T6 / R1）-> 程序内部线路键。"""
    code = str(code).strip().upper()
    if not code:
        return None
    if code in ("T1", "T3", "T6"):
        return "LT" + code[1:]
    if code in ("R1", "R2", "R3", "R4", "R5", "R6"):
        return "LR" + code[1:]
    if code in ("Y1", "Y2"):
        return "LY" + code[1:]
    if code.startswith("L"):
        return "L" + code[1:]
    return "L" + code


# 各线路标识色：取自「服务器统计信息」表 →「线路」页 B 列的单元格填充色
# （即该线路标志色方块的颜色）。键为线路编号，L 前缀去掉后的写法。
LINE_COLORS_RAW = {
    "1":    ("#E4002B", "红色羊毛"),
    "2":    ("#B365B9", "紫色羊毛"),
    "3":    ("#00A650", "绿色羊毛"),
    # 3号线北段 / 南段：与 3 号线共用同一标志色
    "3N":   ("#00A650", "绿色羊毛"),
    "3S":   ("#00A650", "绿色羊毛"),
    "4":    ("#08498E", "蓝色混凝土"),
    "5":    ("#FCD600", "黄色混凝土"),
    "6":    ("#000000", "黑色混凝土"),
    "7":    ("#FF9900", "橙色羊毛"),
    "8":    ("#FF5CE1", "粉色混凝土"),
    "10":   ("#00FFFF", "淡蓝色混凝土"),
    "11":   ("#610F0F", "棕色混凝土"),
    "12":   ("#F795FE", "品红色羊毛"),
    "13":   ("#00FF00", "黄绿色混凝土"),
    "13B":  ("#00FF00", "黄绿色混凝土"),
    "14":   ("#DD6000", "橙色陶瓦"),
    "17":   ("#876B62", "淡灰色陶瓦"),
    "19":   ("#CFB757", "棕色陶瓦"),
    "20":   ("#800080", "粉色陶瓦"),
    "21":   ("#EACEB8", "白色陶瓦"),
    "24":   ("#478B94", "青色陶瓦"),
    "25":   ("#49DF9E", "海晶石"),
    "28":   ("#5E3844", "紫色陶瓦"),
    "Y1":   ("#F65CA2", "去皮樱花木"),
    "Y2":   ("#FF0080", "红色带釉陶瓦"),
    "R1":   ("#991233", "红色陶瓦"),
    "R2":   ("#FBC1F0", "粉红色带釉陶瓦"),
    "T1":   ("#E3D088", "竹板"),
    "T3":   ("#D2AAE3", "紫珀柱"),
    "T6":   ("#3B7D5A", ""),
}

FALLBACK_COLOR = ("#8A94A6", "")      # 表格里没配色的线路用中性灰


def line_color(lk):
    """线路键 -> (#rrggbb, 标志色方块名)。L13B -> 13B，LT6 -> T6。"""
    code = lk[1:] if lk.startswith("L") else lk
    return LINE_COLORS_RAW.get(code, FALLBACK_COLOR)


class App:
    def __init__(self, root, data_path):
        self.root = root
        self.style = Style(self)
        self.style.root = self
        cfg0 = load_config()
        algo = cfg0.get("algo") or "weight"
        self.data = MetroData(data_path, algo=algo)
        self.history = []
        self.current_station = None
        self.query_symbol = "得分"
        self._active = None
        self._build_line_colors()
        self.build_ui()
        self.style.notify()
        self.update_stats()
        self.root.after(80, self.first_focus)
        cfg = load_config()
        last = cfg.get("last_size")
        if isinstance(last, list) and len(last) == 2:
            try:
                self.root.geometry("%dx%d" % (max(980, last[0]), max(620, last[1])))
            except Exception:
                pass

    # -- 基础设施 ---------------------------------------------------------
    def _build_line_colors(self):
        """线路键 -> 标识色；标志色方块名另存一份，给「关于」和线路详情用。"""
        self.line_colors = {}
        self.line_blocks = {}
        for lk in self.data.LINES:
            color, block = line_color(lk)
            self.line_colors[lk] = color
            self.line_blocks[lk] = block

    def measure(self, text, font):
        try:
            return font.measure(text)
        except Exception:
            return tkfont.Font(root=self.root, font=font).measure(text)

    def build_ui(self):
        c = self.style.c
        self.root.configure(bg=c("BG"))

        # 顶部标题栏
        self.header = tk.Frame(self.root, bg=c("CARD"), highlightthickness=1,
                               highlightbackground=c("BORDER"))
        self.header.pack(fill="x")
        hin = tk.Frame(self.header, bg=c("CARD"))
        hin.pack(fill="x", padx=18, pady=10)
        self.logo = tk.Canvas(hin, bg=c("CARD"), highlightthickness=0, bd=0,
                              width=36, height=36)
        self.logo.pack(side="left", padx=(0, 10))
        tt = tk.Frame(hin, bg=c("CARD"))
        tt.pack(side="left")
        self.title = tk.Label(tt, text=APP_TITLE, bg=c("CARD"), fg=c("TEXT"),
                              font=self.style.f("h2"))
        self.title.pack(anchor="w")
        self.subtitle = tk.Label(tt, bg=c("CARD"), fg=c("MUTED"),
                                 font=self.style.f("small"))
        self.subtitle.pack(anchor="w")

        # 右侧工具按钮
        self.tools = tk.Frame(hin, bg=c("CARD"))
        self.tools.pack(side="right")
        self.theme_btn = RoundedButton(self.tools, self.style, "深色模式",
                                       self.toggle_theme, kind="ghost",
                                       padx=12, pady=5, height=30,
                                       font=self.style.f("small"),
                                       width=self.measure("深色模式", self.style.f("small")) + 26)
        self.theme_btn.pack(side="right", padx=(8, 0))
        self.data_btn = RoundedButton(self.tools, self.style, "数据文件",
                                      self.choose_data, kind="ghost", padx=12, pady=5,
                                      height=30, font=self.style.f("small"),
                                      width=self.measure("数据文件", self.style.f("small")) + 26)
        self.data_btn.pack(side="right", padx=(8, 0))
        # 关于改成第一个页签，见下方 notebook

        # 主体：左侧页签 + 右侧状态栏
        self.main = tk.Frame(self.root, bg=c("BG"))
        self.main.pack(fill="both", expand=True, pady=(10, 0))

        self.nb = ttk.Notebook(self.main)
        self.nb.pack(fill="both", expand=True, padx=16)
        self.tab_frames = {}
        for key, label in (("about", "关于"), ("path", "路径查询"),
                           ("line", "线路查询"), ("station", "站点查询"),
                           ("overview", "线网概览")):
            fr = tk.Frame(self.nb, bg=c("BG"))
            self.nb.add(fr, text=label)
            self.tab_frames[key] = fr

        self.about_view = AboutView(self.style, self, self.tab_frames["about"])
        self.path_view = PathView(self.style, self, self.tab_frames["path"])
        self.line_view = LineView(self.style, self, self.tab_frames["line"])
        self.station_view = StationView(self.style, self, self.tab_frames["station"])
        self.overview_view = OverviewView(self.style, self, self.tab_frames["overview"])
        self.nb.select(1)          # 默认停在「路径查询」

        self.status = tk.Frame(self.root, bg=c("BG"))
        self.status.pack(fill="x", padx=18, pady=(6, 8))
        self.status_l = tk.Label(self.status, bg=c("BG"), fg=c("MUTED"),
                                 font=self.style.f("small"), anchor="w")
        self.status_l.pack(side="left")
        self.status_r = tk.Label(self.status, bg=c("BG"), fg=c("MUTED"),
                                 font=self.style.f("small"), anchor="e")
        self.status_r.pack(side="right")

        # 快捷键
        self.root.bind("<Return>", self._on_return)
        self.root.bind("<KP_Enter>", self._on_return)
        self.root.bind("<F5>", lambda e: self.submit_current())
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.style.subscribe(self.apply_theme)

    def apply_theme(self):
        c = self.style.c
        self.root.configure(bg=c("BG"))
        for w in (self.header, self.main, self.status):
            w.configure(bg=c("BG") if w is not self.header else c("CARD"))
        self.header.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
        for ch in self.header.winfo_children():
            ch.configure(bg=c("CARD"))
            for sub in ch.winfo_children():
                if isinstance(sub, tk.Frame):
                    sub.configure(bg=c("CARD"))
                elif isinstance(sub, tk.Label):
                    sub.configure(bg=c("CARD"))
        self.title.configure(bg=c("CARD"), fg=c("TEXT"))
        self.subtitle.configure(bg=c("CARD"), fg=c("MUTED"))
        self.tools.configure(bg=c("CARD"))
        self.status_l.configure(bg=c("BG"), fg=c("MUTED"))
        self.status_r.configure(bg=c("BG"), fg=c("MUTED"))
        for fr in self.tab_frames.values():
            fr.configure(bg=c("BG"))
        self.theme_btn.set_text("浅色模式" if self.style.theme == "dark" else "深色模式")
        self.theme_btn.style_theme_fix = True
        self.draw_logo()
        self.apply_ttk_theme()

    def apply_ttk_theme(self):
        c = self.style.c
        dark = self.style.theme == "dark"
        st = ttk.Style(self.root)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure(".", background=c("CARD"), foreground=c("TEXT"),
                     fieldbackground=c("CARD"), bordercolor=c("BORDER"))
        st.configure("TNotebook", background=c("BG"), borderwidth=0,
                     tabmargins=(0, 4, 0, 0))
        st.configure("TNotebook.Tab", background=c("BG"), foreground=c("MUTED"),
                     padding=(18, 8), borderwidth=0, font=self.style.f("h3"))
        st.map("TNotebook.Tab",
               background=[("selected", c("CARD")), ("active", c("CHIP"))],
               foreground=[("selected", c("ACCENT_DK")), ("active", c("TEXT"))])
        st.configure("TCombobox", padding=6, arrowsize=14,
                     fieldbackground=c("CHIP"), background=c("CHIP"),
                     foreground=c("TEXT"), bordercolor=c("BORDER"),
                     lightcolor=c("BORDER"), darkcolor=c("BORDER"),
                     selectbackground=c("ACCENT_LT"), selectforeground=c("TEXT"))
        st.map("TCombobox",
               fieldbackground=[("readonly", c("CARD")), ("focus", c("CARD"))],
               foreground=[("readonly", c("TEXT"))],
               selectbackground=[("readonly", c("ACCENT_LT"))],
               selectforeground=[("readonly", c("TEXT"))],
               bordercolor=[("focus", c("ACCENT")), ("hover", c("ACCENT"))],
               lightcolor=[("focus", c("ACCENT")), ("hover", c("ACCENT"))],
               darkcolor=[("focus", c("ACCENT")), ("hover", c("ACCENT"))])
        st.configure("Vertical.TScrollbar", background=c("CHIP"),
                     troughcolor=c("BG"), bordercolor=c("BG"),
                     lightcolor=c("CHIP"), darkcolor=c("CHIP"), arrowsize=12)
        st.configure("Horizontal.TScrollbar", background=c("CHIP"),
                     troughcolor=c("BG"), bordercolor=c("BG"),
                     lightcolor=c("CHIP"), darkcolor=c("CHIP"), arrowsize=12)
        st.map("Vertical.TScrollbar", background=[("active", c("MUTED"))])
        st.map("Horizontal.TScrollbar", background=[("active", c("MUTED"))])
        self.root.option_add("*TCombobox*Listbox.background",
                             "#2a2f38" if dark else "#ffffff")
        self.root.option_add("*TCombobox*Listbox.foreground",
                             "#e8eaed" if dark else "#1f2937")
        self.root.option_add("*TCombobox*Listbox.selectBackground", c("ACCENT"))

    def draw_logo(self):
        c = self.style.c
        self.logo.delete("all")
        self.logo.configure(bg=c("CARD"))
        self.logo.create_oval(2, 2, 34, 34, fill=c("ACCENT"), outline="")
        for i, col in enumerate(("#ffffff", "#ffd166")):
            self.logo.create_line(11 + i * 6, 10, 17 + i * 6, 26, fill=col, width=3,
                                  capstyle="round", smooth=True)
        self.logo.create_oval(15, 24, 23, 32, fill="#ffffff", outline="")

    def update_stats(self):
        self.subtitle.configure(
            text="%d 条线路 · %d 个车站 · %s · 数据来源 %s" %
                 (len(self.data.LINES), len(self.data.STATIONS),
                  self.data.algo_name, self.data.source))

    def set_status(self, left=None, right=None):
        if left is not None:
            self.status_l.configure(text=left)
        if right is not None:
            self.status_r.configure(text=right)

    def refresh_later(self):
        """卡片展开/收起后，等布局更新完再重算滚动区域。"""
        self.root.after(30, self.path_view.refresh)

    def update_placeholders(self):
        pv = getattr(self, "path_view", None)
        if not pv:
            return
        for picker, label, default in ((pv.src, pv.src_lbl, "起点站"),
                                       (pv.dst, pv.dst_lbl, "终点站")):
            text = picker.get()
            canon, cands, exact = self.data.resolve(text) if text else (None, [], True)
            if not text:
                label.configure(text=default, fg=self.style.c("MUTED"))
            elif canon or exact:
                label.configure(text="%s  %s" % ("起点站" if default == "起点站" else "终点站",
                                                  canon or text),
                                fg=self.style.c("MUTED"))
            else:
                hint = ("%s  → %s?" % (cands[0], "")) if cands else "未找到"
                label.configure(text="%s（未找到，试试：%s）" %
                                     (text, "/".join(cands[:2]) if cands else "检查站名"),
                                fg="#c0392b")

    # -- 交互 -------------------------------------------------------------
    def current_tab(self):
        try:
            idx = self.nb.index(self.nb.select())
        except Exception:
            return "path"
        return ("about", "path", "line", "station", "overview")[idx]

    def _on_tab(self, _=None):
        self._active = self.current_tab()
        self.update_placeholders()

    def first_focus(self):
        self.path_view.src.focus_set()

    def _on_return(self, ev):
        w = self.root.focus_get()
        if isinstance(w, (ttk.Combobox, tk.Entry)):
            return None       # 交给控件自己的回车绑定
        self.submit_current()
        return "break"

    def submit_current(self):
        key = self.current_tab()
        if key == "path":
            self.submit_path()
        elif key == "line":
            self.submit_line()

    def submit_from(self, role):
        pv = self.path_view
        src, dst = pv.get_inputs()
        if role == "src" and src and not dst:
            pv.dst.focus_set()
            return
        self.submit_path()

    def submit_path(self):
        pv = self.path_view
        src_text, dst_text = pv.get_inputs()
        k = pv.k()
        self.nb.select(1)
        if not src_text and not dst_text:
            pv.set_hint("请先输入起点与终点站名")
            return
        if not src_text or not dst_text:
            pv.set_hint("起点和终点都要填写")
            return
        src, s_c = self.resolve_for(src_text)
        if src is None:
            pv.set_hint("未找到站点「%s」，可从下方候选里选一个" % src_text, warn=True)
            pv.render_state("error", message="未找到站点「%s」" % src_text,
                            cands=s_c)
            return
        dst, d_c = self.resolve_for(dst_text)
        if dst is None:
            pv.set_hint("未找到站点「%s」，可从下方候选里选一个" % dst_text, warn=True)
            pv.render_state("error", message="未找到站点「%s」" % dst_text,
                            cands=d_c)
            return
        pv.src.set(src)
        pv.dst.set(dst)
        self.update_placeholders()
        if src == dst:
            pv.set_hint("起点与终点相同：%s" % src, warn=True)
            pv.render_state("empty", message="起点与终点相同，无需乘车。")
            return
        pv.set_hint("")
        pv.render_state("loading")
        self.set_status(left="正在计算 %s → %s …" % (src, dst))
        args = (src, dst, k)

        def work():
            result = self.data.search(src, dst, k)
            self.root.after(0, lambda: self.show_result(args, result))
        jt = getattr(self, "job_thread", None)
        if jt is not None and jt.is_alive():
            # 上一次还在算就先别叠线程，直接同步算（一般 < 1s）
            try:
                self.show_result(args, self.data.search(src, dst, k))
            except Exception:
                traceback.print_exc()
            return
        self.job_thread = threading.Thread(target=work, daemon=True)
        self.job_thread.start()

    def resolve_for(self, text):
        canon, cands, exact = self.data.resolve(text)
        return canon, cands

    def cost_text(self, cost):
        """把代价元组写成一行说明（新旧算法格式不同）。"""
        if self.data.algo == "weight":
            weight, meters, hops, trans = cost
            return "%d 个区间 / %s m / 换乘 %d 次 / 权重 %s" % (
                hops, fmt_num(meters), trans, fmt_num(weight))
        hops, trans = cost
        return "%d 个区间 / 换乘 %d 次 / 得分 %d" % (
            hops, trans, hops + self.data.TRANSFER_COST * trans)

    def format_search(self, src, dst, sections):
        """生成与原命令行脚本一致的文本（可复制）。"""
        out = []
        out.append("=" * 64)
        out.append("出发: %s" % src)
        out.append("到达: %s" % dst)
        if src == dst:
            out.append("起点与终点相同。")
            return "\n".join(out)
        total = sum(len(s[3]) for s in sections)
        if total == 0:
            out.append("未找到连通路径（两站可能不在同一张路网内）。")
            return "\n".join(out)
        out.append("共列出 %d 条路径，同一线路走法只出现一次" % total)
        out.append("计算方式: %s" % self.data.algo_name)
        out.append("=" * 64)
        for gi, (mode, title, desc, picked) in enumerate(sections, 1):
            out.append("")
            out.append("【%s】%s（%s）" % ("一二三四五"[gi - 1], title, desc))
            if not picked:
                out.append("  （该组无方案）")
                continue
            for idx, (key, segs, cost) in enumerate(picked, 1):
                out.append("  [%d] %s" % (idx, self.cost_text(cost)))
                out.append("    " + key[0])
                for lk, st in segs:
                    inter = st[1:-1]
                    if inter:
                        out.append("    -> %s %s" % (self.data.line_name(lk),
                                                     "、".join(inter)))
                    else:
                        out.append("    -> %s（无途经站）" % self.data.line_name(lk))
                    out.append("    " + st[-1])
        return "\n".join(out)

    def show_result(self, args, sections):
        src, dst, k = args
        pv = self.path_view
        total = sum(len(s[3]) for s in sections)
        if total == 0:
            pv.render_state("empty",
                            message="%s 与 %s 之间没有联通路径（可能不在同一张线网里）。"
                                    % (src, dst))
            self.set_status(left="未找到连通路径")
            return
        payload_sections = []
        weighted = self.data.algo == "weight"
        for mode, title, desc, picked in sections:
            cards = []
            for key, segs, cost in picked:
                if weighted:
                    weight, meters, hops, trans = cost
                else:
                    hops, trans = cost
                    weight = meters = None
                # chain: [(站名, 其后这一程经过的线路键…), …]
                chain = []
                for i, (lk, st) in enumerate(segs):
                    chain.append((st[0], [lk]))
                    if i > 0:          # 换乘站同时属于两条线
                        chain[-1][1].insert(0, segs[i - 1][0])
                if segs:
                    chain.append((segs[-1][1][-1], []))
                if chain and chain[0][0] != src:
                    chain.insert(0, (src, []))
                chain = [(chain[0][0], chain[0][1])] + chain[1:]
                cards.append({
                    "src": src, "dst": dst,
                    "segs": segs, "chain": chain,
                    "stations": len(key), "hops": hops, "trans": trans,
                    "meters": meters, "weight": weight,
                    "score": hops + self.data.TRANSFER_COST * trans,
                    "transfer_names": [segs[i][1][-1] for i in range(len(segs) - 1)],
                })
            payload_sections.append((mode, title, desc, cards))
        self.query_symbol = self.symbol_for()
        pv.render_state("result", payload={"sections": payload_sections, "src": src,
                                           "dst": dst, "symbol": self.query_symbol})
        self.set_status(left="%s → %s   共 %d 条方案" % (src, dst, total))
        self.root.clipboard_clear()
        try:
            self.root.clipboard_append(self.format_search(src, dst, sections))
        except Exception:
            pass
        self.push_history(src, dst)

    def symbol_for(self):
        return "得分"

    def push_history(self, src, dst):
        pair = (src, dst)
        if pair in self.history:
            self.history.remove(pair)
        self.history.insert(0, pair)
        self.history = self.history[:8]
        cfg = load_config()
        cfg["history"] = [list(p) for p in self.history]
        save_config(cfg)

    def swap(self):
        pv = self.path_view
        a, b = pv.get_inputs()
        pv.src.set(b)
        pv.dst.set(a)
        self.update_placeholders()
        if a and b and self.data.resolve(a)[0] and self.data.resolve(b)[0]:
            self.submit_path()

    def quick_query(self, a, b):
        pv = self.path_view
        pv.src.set(a)
        pv.dst.set(b)
        self.submit_path()

    def pick_station(self, name, role="src"):
        """把站点填进路径页；起点已填且选的是起点时自动跳到终点框。"""
        pv = self.path_view
        self.nb.select(1)
        src_has, dst_has = bool(pv.src.get()), bool(pv.dst.get())
        if role == "dst":
            pv.dst.set(name)
            self.update_placeholders()
            if src_has:
                self.submit_path()
            else:
                pv.src.focus_set()
                self.set_status(left="已设置终点 %s，再输入起点" % name)
            return
        if not src_has and dst_has:
            # 只填了终点时，点站名先补起点
            pv.src.set(name)
            self.update_placeholders()
            self.submit_path()
            return
        pv.src.set(name)
        self.update_placeholders()
        if dst_has:
            pv.dst.focus_set()
            self.set_status(left="已设置起点 %s，按回车重新查询" % name)
        else:
            pv.dst.focus_set()
            self.set_status(left="已设置起点 %s，再输入终点" % name)

    def open_line(self, lk):
        self.query_line(lk)

    def submit_line(self):
        text = self.line_view.var.get().strip()
        if not text:
            self.line_view.render_state("placeholder")
            return
        lk = self.data.line_key(text)
        if not lk:
            self.line_view.render_state(
                "error",
                message="未识别线路「%s」。可用编号或中文名，例如 8 / 13B / 玉衡1号线 / "
                        "沼刷线 / 有轨电车3号线" % text)
            return
        self.query_line(lk)

    def query_line(self, lk):
        self.nb.select(2)
        info = self.data.line_info(lk)
        self.line_view.set_text(info["name"])
        self.line_view.render_state("result", payload=info)
        self.set_status(left="%s：%d 座车站%s" %
                             (info["name"], info["count"],
                              "（环线）" if info["ring"] else ""))

    # -- 站点查询 ---------------------------------------------------------
    def submit_station(self):
        text = self.station_view.var.get().strip()
        if not text:
            self.station_view.render_state("placeholder")
            return
        canon, cands, exact = self.data.resolve(text)
        if not canon:
            hits = self.data.stations_matching(text, limit=1)
            canon = hits[0] if hits else None
        if not canon:
            self.station_view.render_state(
                "error",
                message="未找到站点「%s」%s" % (
                    text,
                    "，你可能想找：" + " / ".join(cands[:6]) if cands else ""))
            return
        self.query_station(canon)

    def query_station(self, name):
        info = self.data.station_info(name)
        if not info:
            self.station_view.render_state("error",
                                           message="未找到站点「%s」" % name)
            return
        self.nb.select(3)
        self.current_station = name
        self.station_view.set_text(name)
        self.station_view.render_state("result", payload=info)
        n_dir = sum(len(ln["dirs"]) for ln in info["lines"])
        self.set_status(left="%s：%d 条线路，%d 个方向" %
                             (name, len(info["lines"]), n_dir))

    def toggle_theme(self):
        self.style.toggle()          # 各视图与按钮都订阅了主题，会自动重画
        self.update_placeholders()

    def choose_data(self):
        p = filedialog.askopenfilename(
            parent=self.root, title="选择线路数据脚本（可选，留空则用内置数据）",
            initialfile=os.path.basename(self.data.path) if self.data.path else "",
            filetypes=[("Python 脚本", "*.py"), ("所有文件", "*.*")])
        if not p:
            return
        try:
            new = MetroData(p)
        except Exception as exc:
            messagebox.showerror("加载失败", "%s\n\n%s" % (p, exc), parent=self.root)
            return
        self.data = new
        self._build_line_colors()
        cfg = load_config()
        cfg["data_file"] = os.path.abspath(p)
        save_config(cfg)
        self.update_stats()
        self.overview_view.apply_theme()
        for view in (self.path_view, self.line_view, self.overview_view):
            if hasattr(view, "build_chips"):
                view.build_chips()
        self.set_status(left="已切换到数据文件 %s" % os.path.basename(p))

    def show_about(self):
        """兼容老代码：切到「关于」页签。"""
        self.nb.select(0)

    def set_algo(self, algo):
        """切换计算方式：weight = 新版里程权重，score = 旧版区间计分。"""
        old = self.data.algo
        got = self.data.set_algo(algo)
        cfg = load_config()
        cfg["algo"] = got
        save_config(cfg)
        self.update_stats()
        # 已有结果用新算法重算一遍，让用户立刻看到差别
        src, dst = self.path_view.get_inputs()
        if got != old:
            what = {"weight": "新版：权重 = 总里程 + 换乘权重",
                    "score": "旧版：得分 = 区间数 + 换乘数 × 2"}[got]
            self.set_status(left="已切换为「%s」%s" % (self.data.algo_name, what))
            if src and dst and self.data.resolve(src)[0] and self.data.resolve(dst)[0]:
                self.submit_path()
        return got

    def on_close(self):
        try:
            cfg = load_config()
            cfg["last_size"] = [self.root.winfo_width(), self.root.winfo_height()]
            cfg["history"] = [list(p) for p in self.history]
            save_config(cfg)
        except Exception:
            pass
        self.root.destroy()


ABOUT_NOTICE = ("本软件仅使用于TPC服务器内群，请注意及时更新版本，避免数据过时")
ABOUT_VERSION = "v1.0.4"
# wiki 站：纯文字展示，不做点击跳转
ABOUT_WIKI_LABEL = "wiki站："
ABOUT_WIKI_URL = "wiki.tpcmc.top"
# 使用帮助：(小标题, [条目...])
ABOUT_HELP = (
    ("路径查询", [
        "「路径查询」页填起点与终点，可只输站名的一部分（如「雪」会列出所有含雪字的站）。",
        "按回车或点「查询路径」开始查询；「每组条数」控制三个分组各显示几条方案。",
        "结果分三组：权重最优 / 换乘最少 / 区间最少，各组独立给出自己的最优解。",
        "每张结果卡片下方直接画出全程站序示意条；点卡片里的站名可把它设为起点或终点。",
        "查询结果会自动复制到剪贴板，可直接粘贴到群里。",
    ]),
    ("线路查询", [
        "输入线路号即可：8 / 8号线 / L8 / 13B / 玉衡1号线 / T6 / 沼刷线 都认。",
        "3 号线分为北段与南段，输 3 会同时显示两段，输 3北段 或 3号线南段 单独显示。",
        "点下方彩色线路标签也能直接查看对应线路。",
        "线路页的站表中，单击站名设为起点，右键设为终点。",
    ]),
    ("站点查询", [
        "输入站名，可查看经过该站的所有线路。",
        "每条线路按方向列出上一站与下一站，环线显示为双向。",
        "点前后站名可以继续跳转查询相邻站点。",
    ]),
    ("其他", [
        "「关于」页可切换计算方式：新版按真实里程与换乘权重，旧版只按区间数与换乘次数。",
        "右上角「深色模式」切换配色；窗口大小与查询历史会自动记住。",
        "数据直接内置在本程序中，无需额外文件；也可用「数据文件」加载新的线路脚本。",
    ]),
)
# (标签, [每行内容, ...]) —— 一个标签下可以有多行
ABOUT_CREDITS = (
    ("数据统计", ["示全", "明月花火"]),
    ("软件开发", ["示全 —— 构建旧版综合算法",
                  "明月花火 —— 构建新版权重算法",
                  "哈九_HM —— 构建图形化界面"]),
    ("技术交流及bug反馈", ["QQ群480183016 | QQ号3973475260"]),
)
ABOUT_THANKS = ("特别致谢", "为TPC贡献的每一个人")
ABOUT_FOOTER = "TechProCraft 2026"


class AboutView(Widget):
    """「关于」页签：版本信息、署名，以及计算方式切换。"""

    def __init__(self, style, app, parent):
        self.app = app
        self.parent = parent
        super().__init__(style)

    def build(self):
        c = self.style.c
        f = self.style.f
        self.frame = tk.Frame(self.parent, bg=c("BG"))
        self.frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.scroll = ScrollFrame(self.frame, self.style, bg=c("BG"))
        self.scroll.pack(fill="both", expand=True)
        inner = self.scroll.inner

        # ---- 标题卡片 ----
        card = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                        highlightbackground=c("BORDER"))
        card.pack(fill="x")
        head = tk.Frame(card, bg=c("CARD"))
        head.pack(fill="x", padx=22, pady=18)
        logo = tk.Canvas(head, width=52, height=52, bg=c("CARD"),
                         highlightthickness=0, bd=0)
        logo.pack(side="left", padx=(0, 14))
        self.logo = logo
        tt = tk.Frame(head, bg=c("CARD"))
        tt.pack(side="left")
        self.t1 = tk.Label(tt, text=APP_TITLE, bg=c("CARD"), fg=c("TEXT"),
                           font=f("title"))
        self.t1.pack(anchor="w")
        self.t2 = tk.Label(tt, text="软件版本：" + ABOUT_VERSION, bg=c("CARD"),
                           fg=c("MUTED"), font=f("small"))
        self.t2.pack(anchor="w", pady=(3, 0))

        # ---- 提示条 ----
        self.notice = tk.Label(inner, text=ABOUT_NOTICE, bg=c("ACCENT_LT"),
                               fg=c("ACCENT_DK"), font=f("base"), anchor="w",
                               justify="left", wraplength=900, padx=14, pady=10)
        self.notice.pack(fill="x", pady=(10, 0))

        # ---- 计算方式切换 ----
        algo_card = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                             highlightbackground=c("BORDER"))
        algo_card.pack(fill="x", pady=(10, 0))
        self.algo_card = algo_card
        box = tk.Frame(algo_card, bg=c("CARD"))
        box.pack(fill="x", padx=22, pady=16)
        top = tk.Frame(box, bg=c("CARD"))
        top.pack(fill="x")
        self.algo_title = tk.Label(top, text="计算方式", bg=c("CARD"), fg=c("TEXT"),
                                   font=f("h2"))
        self.algo_title.pack(side="left")
        self.algo_now = tk.Label(top, text="", bg=c("CARD"), fg=c("ACCENT_DK"),
                                 font=f("small"))
        self.algo_now.pack(side="left", padx=(10, 0))

        self.algo_btns = tk.Frame(box, bg=c("CARD"))
        self.algo_btns.pack(fill="x", pady=(10, 0))
        self.algo_buttons = {}
        for key, text, in (("weight", "新版 · 权重最优"),
                           ("score", "旧版 · 综合较优")):
            b = RoundedButton(self.algo_btns, self.style, text,
                              lambda k=key: self.choose_algo(k), kind="ghost",
                              padx=14, pady=7, height=36, font=f("h3"),
                              width=self.app.measure(text, f("h3")) + 34)
            b.pack(side="left", padx=(0, 10))
            self.algo_buttons[key] = b
        self.algo_desc = tk.Label(box, text="", bg=c("CARD"), fg=c("MUTED"),
                                  font=f("base"), anchor="w", justify="left",
                                  wraplength=880)
        self.algo_desc.pack(fill="x", pady=(10, 0))
        self.algo_note = tk.Label(box, text="", bg=c("CARD"), fg=c("MUTED"),
                                  font=f("small"), anchor="w", justify="left",
                                  wraplength=880)
        self.algo_note.pack(fill="x", pady=(6, 0))

        # ---- 署名 ----
        credit_card = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                               highlightbackground=c("BORDER"))
        credit_card.pack(fill="x", pady=(10, 0))
        self.credit_card = credit_card
        grid = tk.Frame(credit_card, bg=c("CARD"))
        grid.pack(fill="x", padx=22, pady=16)
        self.rows = []          # [(标签控件, 值控件)] 供主题切换用
        for r, (key_text, values) in enumerate(ABOUT_CREDITS):
            key = tk.Label(grid, text=key_text, bg=c("CARD"), fg=c("MUTED"),
                           font=f("base"), anchor="nw")
            key.grid(row=r, column=0, sticky="nw", pady=(0, 12))
            val_box = tk.Frame(grid, bg=c("CARD"))
            val_box.grid(row=r, column=1, sticky="w", padx=(20, 0), pady=(0, 12))
            for line in values:
                v = tk.Label(val_box, text=line, bg=c("CARD"), fg=c("TEXT"),
                             font=f("base"), anchor="w", justify="left")
                v.pack(anchor="w", pady=1)
                self.rows.append((key, v))
        # ---- wiki 站（纯文字，不做点击跳转）----
        wiki_row = tk.Frame(credit_card, bg=c("CARD"))
        wiki_row.pack(fill="x", padx=22, pady=(0, 12))
        self.wiki_row = wiki_row
        self.wiki_lbl = tk.Label(wiki_row, text=ABOUT_WIKI_LABEL, bg=c("CARD"),
                                 fg=c("MUTED"), font=f("base"), anchor="w")
        self.wiki_lbl.pack(side="left")
        self.wiki_url = tk.Label(wiki_row, text=ABOUT_WIKI_URL, bg=c("CARD"),
                                 fg=c("TEXT"), font=f("base"), anchor="w")
        self.wiki_url.pack(side="left")
        # ---- 特别致谢 ----
        thanks = tk.Frame(credit_card, bg=c("CARD"))
        thanks.pack(fill="x", padx=22, pady=(0, 16))
        self.thanks = thanks
        self.thanks_key = tk.Label(thanks, text=ABOUT_THANKS[0], bg=c("CARD"),
                                   fg=c("ACCENT_DK"), font=f("h3"), anchor="w")
        self.thanks_key.pack(side="left")
        self.thanks_val = tk.Label(thanks, text=ABOUT_THANKS[1], bg=c("CARD"),
                                   fg=c("TEXT"), font=f("base"), anchor="w")
        self.thanks_val.pack(side="left", padx=(20, 0))
        grid.columnconfigure(1, weight=1)

        # ---- 使用帮助 ----
        help_card = tk.Frame(inner, bg=c("CARD"), highlightthickness=1,
                             highlightbackground=c("BORDER"))
        help_card.pack(fill="x", pady=(10, 0))
        self.help_card = help_card
        hh = tk.Frame(help_card, bg=c("CARD"))
        hh.pack(fill="x", padx=22, pady=(16, 4))
        self.help_title = tk.Label(hh, text="使用帮助", bg=c("CARD"),
                                   fg=c("TEXT"), font=f("h2"))
        self.help_title.pack(side="left")
        self.help_rows = []
        hb = tk.Frame(help_card, bg=c("CARD"))
        hb.pack(fill="x", padx=22, pady=(0, 16))
        for sec, items in ABOUT_HELP:
            row = tk.Frame(hb, bg=c("CARD"))
            row.pack(fill="x", pady=(8, 0))
            k = tk.Label(row, text=sec, bg=c("CARD"), fg=c("ACCENT_DK"),
                         font=f("h3"), anchor="nw", width=8)
            k.pack(side="left", anchor="n", padx=(0, 12))
            box = tk.Frame(row, bg=c("CARD"))
            box.pack(side="left", fill="x", expand=True)
            for line in items:
                v = tk.Label(box, text="· " + line, bg=c("CARD"), fg=c("TEXT"),
                             font=f("small"), anchor="w", justify="left",
                             wraplength=760)
                v.pack(anchor="w", pady=1)
                self.help_rows.append((k, v))

        # ---- 页脚 ----
        self.footer = tk.Label(inner, text=ABOUT_FOOTER, bg=c("BG"), fg=c("MUTED"),
                               font=f("small"), anchor="w")
        self.footer.pack(fill="x", pady=(12, 0), padx=4)
        self.refresh_algo_ui()

    # -- 计算方式 ---------------------------------------------------------
    def choose_algo(self, key):
        if key == self.app.data.algo:
            return
        got = self.app.set_algo(key)
        self.refresh_algo_ui()
        if got != key:
            self.algo_note.configure(
                text="当前数据文件没有区间里程，只能使用旧版算法。", fg="#c0392b")

    def refresh_algo_ui(self):
        c = self.style.c
        algo = self.app.data.algo
        name = {"weight": "权重最优", "score": "综合较优"}.get(algo, algo)
        self.algo_now.configure(text="当前：%s" % name, fg=c("ACCENT_DK"))
        if algo == "weight":
            desc = ("权重 = 总里程(m) + 换乘权重。换乘权重：普通 100，纺林 300，"
                    "欢乐谷 / 梦樱 / 刷冰机 200，火药塔的 2 号线与 10、11 号线互转 250。")
            note = "按真实站间距计算，推荐日常使用；同样的站数下会避开绕远的走法。"
        else:
            desc = "得分 = 区间数 + 换乘数 × 2，只看坐了几站、换了几次车，不考虑站间距。"
            note = "适合只想看「坐几站」的场景，或与旧版程序的结果对照。"
        self.algo_desc.configure(text=desc, fg=c("TEXT"))
        self.algo_note.configure(text=note, fg=c("MUTED"))
        for key, btn in self.algo_buttons.items():
            btn.kind = "primary" if key == algo else "ghost"
            btn.redraw()

    # -- 主题 -------------------------------------------------------------
    def apply_theme(self):
        c = self.style.c
        self.frame.configure(bg=c("BG"))
        for card in (self.algo_card, self.credit_card, self.help_card):
            card.configure(bg=c("CARD"), highlightbackground=c("BORDER"))
            for ch in card.winfo_children():
                if isinstance(ch, tk.Frame):
                    ch.configure(bg=c("CARD"))
                    for sub in ch.winfo_children():
                        if isinstance(sub, tk.Frame):
                            sub.configure(bg=c("CARD"))
        for w in self.scroll.inner.winfo_children():
            if isinstance(w, tk.Frame) and w is not self.frame:
                w.configure(bg=c("CARD"))
                for sub in w.winfo_children():
                    if isinstance(sub, tk.Frame):
                        sub.configure(bg=c("CARD"))
        self.t1.configure(bg=c("CARD"), fg=c("TEXT"))
        self.t2.configure(bg=c("CARD"), fg=c("MUTED"))
        self.notice.configure(bg=c("ACCENT_LT"), fg=c("ACCENT_DK"))
        self.algo_title.configure(bg=c("CARD"), fg=c("TEXT"))
        self.help_title.configure(bg=c("CARD"), fg=c("TEXT"))
        for key, val in self.help_rows:
            key.configure(bg=c("CARD"), fg=c("ACCENT_DK"))
            val.configure(bg=c("CARD"), fg=c("TEXT"))
        for key, val in self.rows:
            key.configure(bg=c("CARD"), fg=c("MUTED"))
            val.configure(bg=c("CARD"), fg=c("TEXT"))
        self.thanks.configure(bg=c("CARD"))
        self.thanks_key.configure(bg=c("CARD"), fg=c("ACCENT_DK"))
        self.thanks_val.configure(bg=c("CARD"), fg=c("TEXT"))
        self.wiki_row.configure(bg=c("CARD"))
        self.wiki_lbl.configure(bg=c("CARD"), fg=c("MUTED"))
        self.wiki_url.configure(bg=c("CARD"), fg=c("TEXT"))
        self.footer.configure(bg=c("BG"), fg=c("MUTED"))
        self.draw_logo()
        self.refresh_algo_ui()

    def draw_logo(self):
        c = self.style.c
        self.logo.delete("all")
        self.logo.configure(bg=c("CARD"))
        self.logo.create_oval(2, 2, 50, 50, fill=c("ACCENT"), outline="")
        for i, col in enumerate(("#ffffff", "#ffd166")):
            self.logo.create_line(17 + i * 8, 14, 25 + i * 8, 38, fill=col, width=5,
                                  capstyle="round")
        self.logo.create_oval(21, 36, 33, 48, fill="#ffffff", outline="")


def main():
    enable_dpi_awareness()
    # 默认用内置数据（单文件/EXE 直接能跑）；同目录若有新的线路脚本才用它
    data_path = find_data_file()
    root = tk.Tk()
    root.title(APP_TITLE)
    try:
        app = App(root, data_path)
    except Exception:
        root.withdraw()
        messagebox.showerror(APP_TITLE, "启动失败：\n\n" + traceback.format_exc())
        return 1
    # 默认尺寸按屏幕算，并留出任务栏的余地，保证按钮不被切掉
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    w = min(1180, max(900, sw - 200))
    h = min(820, max(600, sh - 130))
    x = max(0, (sw - w) // 2)
    y = max(0, min((sh - h) // 3, sh - h - 48))
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    root.minsize(900, 560)
    return 0 if root.mainloop() is None else 0


if __name__ == "__main__":
    sys.exit(main())


