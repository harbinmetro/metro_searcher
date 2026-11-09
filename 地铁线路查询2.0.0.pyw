# -*- coding: utf-8 -*-
"""TPC 服务器 · 地铁线路查询  (PySide6 单文件版)

直接运行：  python 地铁线路查询.pyw
依赖：      pip install PySide6

包含：线路数据 / 寻路算法 / 图形界面 全部内容，单文件即可运行。
"""

import os
import sys
import json
import difflib
import types
import heapq
import datetime

from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QRect, QPointF, QRectF
from PySide6.QtGui import (QColor, QFont, QFontMetrics, QImage, QPainter,
                           QPainterPath, QPixmap, QBrush, QPen)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QComboBox, QScrollArea, QSizePolicy, QFileDialog,
    QTabWidget, QGridLayout, QMessageBox, QSlider, QLayout,
)

ARROW = "→"

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


CONFIG_NAME = "metro_gui.json"


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, CONFIG_NAME), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def config_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_NAME)


def save_config(cfg):
    """原子写入：先写临时文件再替换，避免写到一半崩溃导致配置损坏。"""
    path = config_path()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        return False

# ---------------------------------------------------------------- 明暗配色
BG        = "#f3f5f9"
CARD      = "#ffffff"
BORDER    = "#dde3ec"
TEXT      = "#1f2937"
MUTED     = "#75808f"
ACCENT    = "#2f6df6"
ACCENT_DK = "#1f52c9"
ACCENT_LT = "#e8f0ff"
CHIP      = "#f6f8fb"

DBG        = "#1b1e24"
DCARD      = "#23272f"
DBORDER    = "#343a45"
DTEXT      = "#e8eaed"
DMUTED     = "#9aa4b2"
DACCENT    = "#6d9bff"
DACCENT_LT = "#26324a"
DCHIP      = "#2b3039"

PALETTES = {
    "light": dict(BG=BG, CARD=CARD, BORDER=BORDER, TEXT=TEXT, MUTED=MUTED,
                  ACCENT=ACCENT, ACCENT_DK=ACCENT_DK, ACCENT_LT=ACCENT_LT,
                  CHIP=CHIP),
    "dark": dict(BG=DBG, CARD=DCARD, BORDER=DBORDER, TEXT=DTEXT, MUTED=DMUTED,
                 ACCENT=DACCENT, ACCENT_DK="#8ab0ff", ACCENT_LT=DACCENT_LT,
                 CHIP=DCHIP),
}

APP_TITLE = "TPC服务器 · 地铁线路查询"

# 全局站点表（供界面快速使用）
_ST = {}
for _lk, _seq in LINES.items():
    for _s in _seq:
        _ST.setdefault(_s, [])
        if _lk not in _ST[_s]:
            _ST[_s].append(_lk)
STATIONS = sorted(_ST)
STATION_LINES = _ST


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


def short_line_code(lk):
    """线路键 -> 短编号：L1 -> 1，L13B -> 13B，LY1 -> Y1。"""
    return lk[1:] if lk.startswith("L") else lk


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



APP_TITLE = APP_TITLE
VERSION = "v2.0.0"


# ============================================================ 主题 / 配色
class Theme:
    """明暗配色 + 背景配置（图片背景由 Qt 原生支持透明度）。"""

    def __init__(self):
        self.cfg = {
            "mode": "light",
            "bg_type": "solid",
            "bg_color": "#f3f5f9",
            "bg_image": "",
            "bg_opacity": 0.55,
            "bg_blur": 0,
            "bg_fit": "fill",
            "panel_opacity": 0.22,
        }

    def load(self, cfg):
        if isinstance(cfg, dict):
            for k, v in cfg.items():
                if k in self.cfg:
                    self.cfg[k] = v

    def as_dict(self):
        return dict(self.cfg)

    @property
    def dark(self):
        return self.cfg.get("mode") == "dark"

    def color(self, key):
        base = PALETTES["dark" if self.dark else "light"]
        return QColor(base[key])

    def rgba(self, key, alpha):
        c = self.color(key)
        c.setAlphaF(max(0.0, min(1.0, alpha)))
        return c

    def bg_base(self):
        """窗口底色（纯色背景取用户色，图片背景取主题底色）。"""
        if self.cfg.get("bg_type") == "solid":
            return QColor(self.cfg.get("bg_color") or "#f3f5f9")
        return self.color("BG")


# ============================================================ 背景控件
class BackgroundWidget(QWidget):
    """窗口背景：纯色或图片（不透明度/模糊度/适应方式）。"""

    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._pix_src = None
        self._pix_path = None
        self.setAutoFillBackground(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def refresh(self):
        self.theme = self.theme
        path = self.theme.cfg.get("bg_image") or ""
        if self.theme.cfg.get("bg_type") == "image" and path != self._pix_path:
            self._pix_path = path
            self._pix_src = QPixmap(path) if path and os.path.isfile(path) else None
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        r = self.rect()
        p.fillRect(r, self.theme.bg_base())
        if self.theme.cfg.get("bg_type") != "image":
            return
        if self._pix_src is None or self._pix_src.isNull():
            return

        # 三种显示方式：
        #   cover  放大填充：等比放大到铺满窗口，超出部分裁掉（不留空）
        #   stretch 拉伸填充：非等比拉伸到正好铺满窗口
        #   none   不处理：保持原始像素尺寸，居中显示（小图四周留底色）
        fit = self.theme.cfg.get("bg_fit", "cover")
        src = self._pix_src
        target = r.size()
        if fit == "stretch":
            img = src.scaled(target, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif fit == "none":
            img = src          # 原始尺寸，不缩放
        else:                  # cover
            img = src.scaled(target, Qt.KeepAspectRatioByExpanding,
                             Qt.SmoothTransformation)

        blur = int(self.theme.cfg.get("bg_blur", 0) or 0)
        if blur > 0:
            img = apply_blur(img, blur)

        x = (r.width() - img.width()) // 2
        y = (r.height() - img.height()) // 2
        p.setOpacity(float(self.theme.cfg.get("bg_opacity", 1.0)))
        p.drawPixmap(x, y, img)
        p.setOpacity(1.0)



def apply_blur(pix: QPixmap, radius: int) -> QPixmap:
    """用 Qt 自带能力做模糊：缩小再放大 + 平滑，边缘自然。"""
    if radius <= 0:
        return pix
    k = max(1, radius // 2 + 1)
    small = pix.scaled(max(1, pix.width() // k), max(1, pix.height() // k),
                       Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return small.scaled(pix.width(), pix.height(), Qt.IgnoreAspectRatio,
                        Qt.SmoothTransformation)


class FlowLayout(QLayout):
    """自动换行的流式布局（Qt 没有内置，这里实现一个简洁版）。"""

    def __init__(self, parent=None, margin=0, spacing=6):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for it in self._items:
            size = size.expandedTo(it.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect, test_only):
        m = self.contentsMargins()
        eff = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x = eff.x()
        y = eff.y()
        line_h = 0
        sp = self._spacing
        for it in self._items:
            w = it.sizeHint().width()
            h = it.sizeHint().height()
            if x + w > eff.right() + 1 and line_h > 0:
                x = eff.x()
                y = y + line_h + sp
                line_h = 0
            if not test_only:
                it.setGeometry(QRect(QPoint(x, y), QSize(w, h)))
            x = x + w + sp
            line_h = max(line_h, h)
        return y + line_h - rect.y() + m.bottom()



# ============================================================ 通用样式
def button_style(theme: Theme, kind="ghost"):
    c = theme.color
    dark = theme.dark
    if kind == "primary":
        bg, fg, bd = c("ACCENT"), QColor("#ffffff"), c("ACCENT")
        hov = bg.lighter(112)
    elif kind == "secondary":
        bg, fg, bd = theme.rgba("ACCENT_LT", 0.9), c("ACCENT_DK"), c("ACCENT")
        hov = bg.lighter(106)
    else:
        bg, fg = theme.rgba("CHIP", 0.75), c("TEXT")
        bd = theme.color("BORDER")
        hov = bg.lighter(108)
    return f"""
    QPushButton {{
        background-color: rgba({bg.red()},{bg.green()},{bg.blue()},{bg.alpha()});
        color: rgb({fg.red()},{fg.green()},{fg.blue()});
        border: 1px solid rgb({bd.red()},{bd.green()},{bd.blue()});
        border-radius: 6px; padding: 7px 14px;
    }}
    QPushButton:hover {{
        background-color: rgba({hov.red()},{hov.green()},{hov.blue()},{hov.alpha()});
    }}
    QPushButton:disabled {{ color: #999; }}
    """


# ============================================================ 通用卡片
class Card(QFrame):
    """半透明卡片：Qt 下可以用透明背景色，背景图能真实透出。"""

    def __init__(self, theme: Theme, panel_alpha=None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.panel_alpha = panel_alpha
        self.setObjectName("card")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, ev):
        th = self.theme
        # 关键：让父控件的背景（含背景图）先画出来，卡片才能真正透出
        super().paintEvent(ev)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        # 卡片不透明度 = 1 - 卡片模糊度（模糊度越大越"实"其实相反，
        # 这里按用户直觉：卡片模糊度越大 -> 卡片越实 -> alpha 越大）
        if th.cfg.get("bg_type") == "image":
            alpha = float(th.cfg.get("panel_opacity", 0.22))
            alpha = 0.04 + 0.92 * max(0.0, min(1.0, alpha))
        else:
            alpha = 1.0
        if self.panel_alpha is not None:
            alpha = self.panel_alpha
        col = th.color("CARD")
        col.setAlphaF(max(0.0, min(1.0, alpha)))
        path = QPainterPath()
        path.addRoundedRect(r, 8, 8)
        p.fillPath(path, QBrush(col))
        # 边框
        bd = th.color("BORDER")
        bd.setAlphaF(min(1.0, alpha + 0.2))
        p.setPen(QPen(bd, 1))
        p.drawPath(path)


# ============================================================ 页面基类
class Page(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.theme = app.theme
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(16, 12, 16, 12)
        self.root.setSpacing(10)

    def scroll_page(self):
        """返回一个可滚动的内容容器（透明，让窗口背景图透出来）。"""
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setFrameShape(QFrame.NoFrame)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setStyleSheet("QScrollArea{background:transparent;border:none;}"
                         "QScrollArea > QWidget > QWidget{background:transparent;}")
        sa.viewport().setAutoFillBackground(False)
        sa.viewport().setStyleSheet("background:transparent;")
        holder = QWidget()
        holder.setAutoFillBackground(False)
        holder.setAttribute(Qt.WA_TranslucentBackground, True)
        holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 8, 0)
        lay.setSpacing(10)
        sa.setWidget(holder)
        return sa, holder, lay

    def retheme(self):
        pass


# ============================================================ 欢迎页
class WelcomePage(Page):
    START = datetime.date(2023, 8, 23)

    def __init__(self, app):
        super().__init__(app)
        self.root.addStretch(1)
        self.title = QLabel("欢迎使用")
        self.big = QLabel("TPC服务器地铁查询软件")
        self.date_lbl = QLabel("")
        self.clock_lbl = QLabel("")
        self.days_lbl = QLabel("")
        self.tip = QLabel("从上方「路径查询 / 线路查询 / 站点查询 / 线网概览」开始使用")
        for w, align in ((self.title, Qt.AlignCenter), (self.big, Qt.AlignCenter),
                         (self.date_lbl, Qt.AlignCenter),
                         (self.clock_lbl, Qt.AlignCenter),
                         (self.days_lbl, Qt.AlignCenter), (self.tip, Qt.AlignCenter)):
            w.setAlignment(align)
        self.card = Card(self.theme)
        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(48, 26, 48, 26)
        cl.setSpacing(10)
        for w in (self.date_lbl, self.clock_lbl, self.days_lbl):
            cl.addWidget(w)
        self.root.addWidget(self.title)
        self.root.addWidget(self.big)
        self.root.addSpacing(16)
        self.root.addWidget(self.card, alignment=Qt.AlignCenter)
        self.root.addSpacing(18)
        self.root.addWidget(self.tip)
        self.root.addStretch(1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._tick()
        self.retheme()

    def _tick(self):
        now = datetime.datetime.now()
        wd = "一二三四五六日"[now.weekday()]
        self.date_lbl.setText("%d 年 %d 月 %d 日　星期%s" %
                              (now.year, now.month, now.day, wd))
        self.clock_lbl.setText(now.strftime("%H:%M:%S"))
        days = (datetime.date.today() - self.START).days
        self.days_lbl.setText("TPC服务器已经运营 %d 天" % days)

    def retheme(self):
        th = self.theme
        c = th.color
        self.title.setStyleSheet("color:%s;font-size:20px;" % c("MUTED").name())
        self.big.setStyleSheet(
            "color:%s;font-size:30px;font-weight:700;" % c("TEXT").name())
        self.date_lbl.setStyleSheet(
            "color:%s;font-size:17px;font-weight:600;" % c("TEXT").name())
        self.clock_lbl.setStyleSheet(
            "color:%s;font-size:44px;font-weight:700;" % c("ACCENT").name())
        self.days_lbl.setStyleSheet("color:%s;font-size:13px;" % c("MUTED").name())
        self.tip.setStyleSheet("color:%s;font-size:12px;" % c("MUTED").name())
        self.card.update()


# ============================================================ 路径查询页
class PathPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.data = app.data
        # ---- 查询条 ----
        bar = Card(self.theme, panel_alpha=0.9)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 12, 14, 12)
        bl.setSpacing(8)

        def field(label):
            box = QVBoxLayout()
            box.setSpacing(3)
            lb = QLabel(label)
            lb.setStyleSheet("font-size:11px;color:%s;" % self.theme.color("MUTED").name())
            box.addWidget(lb)
            return box

        self.src = QComboBox()
        self.src.setEditable(True)
        self.src.setMinimumWidth(160)
        self.dst = QComboBox()
        self.dst.setEditable(True)
        self.dst.setMinimumWidth(160)
        self.src.addItems(STATIONS)
        self.dst.addItems(STATIONS)
        self.src.setCurrentIndex(-1)
        self.dst.setCurrentIndex(-1)
        self.src.setCurrentText("")
        self.dst.setCurrentText("")

        sb = field("起点站")
        sb.addWidget(self.src)
        db = field("终点站")
        db.addWidget(self.dst)
        bl.addLayout(sb, 3)
        swap = QPushButton("⇄")
        swap.setFixedWidth(42)
        swap.clicked.connect(self._swap)
        self.swap_btn = swap
        bl.addWidget(swap, alignment=Qt.AlignBottom)

        bl.addLayout(db, 3)
        kb = field("每组条数")
        self.kbox = QComboBox()
        self.kbox.addItems(["1", "2", "3", "5", "8", "10"])
        KB = 78
        kb.addWidget(self.kbox)
        bl.addLayout(kb)
        self.go = QPushButton("查询路径")
        self.go.setMinimumWidth(110)
        self.go.clicked.connect(self.submit)
        bl.addWidget(self.go, alignment=Qt.AlignBottom)
        clear = QPushButton("清空")
        clear.setObjectName("ghost")
        clear.clicked.connect(self.clear)
        bl.addWidget(clear, alignment=Qt.AlignBottom)
        self.root.addWidget(bar)
        self.bar = bar

        self.hint = QLabel("")
        self.hint.setStyleSheet("color:%s;font-size:12px;" % self.theme.color("MUTED").name())
        self.root.addWidget(self.hint)

        sa, holder, self.result_lay = self.scroll_page()
        self.result_holder = holder
        self.root.addWidget(sa, 1)
        self.show_placeholder()

    # ---------------- 交互 ----------------
    def inputs(self):
        return self.src.currentText().strip(), self.dst.currentText().strip()

    def k(self):
        try:
            return max(1, int(self.kbox.currentText()))
        except Exception:
            return 1

    def _swap(self):
        a, b = self.inputs()
        self.src.setCurrentText(b)
        self.dst.setCurrentText(a)
        if a and b:
            self.submit()

    def clear(self):
        self.src.setCurrentText("")
        self.dst.setCurrentText("")
        self.show_placeholder()

    def show_placeholder(self):
        self._clear_results()
        lay = QVBoxLayout()
        lay.setSpacing(14)
        t = QLabel("输入起点与终点，查询最优乘车方案")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:20px;font-weight:600;color:%s;"
                        % self.theme.color("TEXT").name())
        s = QLabel("%d 条线路 · %d 个车站" %
                   (len(self.data.LINES), len(self.data.STATIONS)))
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet("color:%s;" % self.theme.color("MUTED").name())
        lay.addStretch(1)
        lay.addWidget(t)
        lay.addWidget(s)
        lay.addStretch(1)
        wrap = Card(self.theme, panel_alpha=0.5)
        self.hint.setText("")
        wrap.setLayout(lay)
        self.result_lay.addWidget(wrap)
        self.result_lay.addStretch(1)

    def _clear_results(self):
        while self.result_lay.count():
            item = self.result_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def submit(self):
        src_text, dst_text = self.inputs()
        if not src_text and not dst_text:
            self._hint("请先输入起点与终点站名")
            return
        if not src_text or not dst_text:
            self._hint("起点和终点都要填写")
            return
        src = self.data.resolve(src_text)[0]
        dst = self.data.resolve(dst_text)[0]
        if not src:
            self._hint("未找到站点「%s」" % src_text, warn=True)
            return
        if not dst:
            self._hint("未找到站点「%s」" % dst_text, warn=True)
            return
        if src == dst:
            self._hint("起点与终点相同：%s" % src, warn=True)
            return
        self.src.setCurrentText(src)
        self.dst.setCurrentText(dst)
        self._hint("")
        sections = self.data.search(src, dst, self.k())
        self.render_result(src, dst, sections)

    def _hint(self, text, warn=False):
        col = "#c0392b" if warn else self.theme.color("MUTED").name()
        self.hint.setStyleSheet("color:%s;font-size:12px;" % col)
        self.hint.setText(text)

    # ---------------- 结果 ----------------
    def render_result(self, src, dst, sections):
        self._clear_results()
        total = sum(len(s[3]) for s in sections)
        head = QHBoxLayout()
        h1 = QLabel("%s  →  %s" % (src, dst))
        h1.setStyleSheet("font-size:17px;font-weight:700;color:%s;"
                         % self.theme.color("TEXT").name())
        h2 = QLabel("共 %d 条方案" % total)
        h2.setStyleSheet("color:%s;" % self.theme.color("MUTED").name())
        head.addWidget(h1)
        head.addWidget(h2)
        head.addStretch(1)
        hw = Card(self.theme, panel_alpha=0.35)
        hw.setLayout(head)
        hw.layout().setContentsMargins(12, 8, 12, 8)
        self.result_lay.addWidget(hw)

        weighted = self.data.algo == "weight"
        for gi, (mode, title, desc, picked) in enumerate(sections):
            num = "一二三四五"[gi] if gi < 5 else str(gi + 1)
            grp = QHBoxLayout()
            g1 = QLabel("%s、%s" % (num, title))
            g1.setStyleSheet("font-size:16px;font-weight:700;color:%s;"
                             % self.theme.color("TEXT").name())
            g2 = QLabel("（%s）" % desc)
            g2.setStyleSheet("font-size:12px;color:%s;"
                             % self.theme.color("MUTED").name())
            grp.addWidget(g1)
            grp.addWidget(g2)
            grp.addStretch(1)
            gw = Card(self.theme, panel_alpha=0.35)
            gw.setLayout(grp)
            gw.layout().setContentsMargins(12, 6, 12, 6)
            self.result_lay.addWidget(gw)
            for idx, (key, segs, cost) in enumerate(picked, 1):
                self.result_lay.addWidget(self._route_card(key, segs, cost, weighted))
        self.result_lay.addStretch(1)

    def _route_card(self, key, segs, cost, weighted):
        th = self.theme
        card = Card(th, panel_alpha=0.92)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(7)

        # 头部：起终点
        names = QHBoxLayout()
        a = QLabel(segs[0][1][0])
        a.setStyleSheet("font-size:16px;font-weight:700;color:%s;"
                        % th.color("TEXT").name())
        arrow = QLabel("→")
        arrow.setStyleSheet("color:%s;" % th.color("MUTED").name())
        b = QLabel(segs[-1][1][-1])
        b.setStyleSheet("font-size:16px;font-weight:700;color:%s;"
                        % th.color("TEXT").name())
        names.addWidget(a)
        names.addWidget(arrow)
        names.addWidget(b)
        names.addStretch(1)
        nw = QWidget()
        nw.setLayout(names)
        lay.addWidget(nw)

        # 指标
        if weighted:
            weight, meters, hops, trans = cost
            meta = "%d 站    %d 区间    换乘 %d 次    %s m    权重 %s" % (
                len(key), hops, trans, fmt(meters), fmt(weight))
        else:
            hops, trans = cost
            meta = "%d 站    %d 区间    换乘 %d 次    得分 %d" % (
                len(key), hops, trans, hops + self.data.TRANSFER_COST * trans)
        ml = QLabel(meta)
        ml.setStyleSheet("color:%s;font-size:12px;" % th.color("MUTED").name())
        lay.addWidget(ml)

        # 路线预览：起点 → 线路 → 换乘站 → 线路 → 终点
        lay.addWidget(RouteStrip(th, self.data, segs,
                                 line_colors=self.app.line_colors))
        return card

    def retheme(self):
        c = self.theme.color
        self.hint.setStyleSheet("color:%s;font-size:12px;" % c("MUTED").name())
        self.bar.update()
        for b in self.findChildren(QPushButton):
            b.setStyleSheet(button_style(self.theme, "primary" if b is self.go else "ghost"))
        for cb in self.findChildren(QComboBox):
            cb.setStyleSheet(combo_style(self.theme))
        for lbl in self.findChildren(QLabel):
            lbl.setStyleSheet("color:%s;" % c("MUTED").name())


def fmt(x):
    try:
        f = float(x)
    except Exception:
        return str(x)
    return str(int(f)) if f.is_integer() else ("%.1f" % f)


# ============================================================ 路线示意图
class RouteStrip(QWidget):
    """把分段路径画成一条连续的彩色线路条（Qt 画布，文字不遮挡）。"""

    def __init__(self, theme, data, segs, line_colors=None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.data = data
        self.segs = segs
        self.line_colors = line_colors or {}
        self.setMinimumHeight(78)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def color_of(self, lk):
        c = self.line_colors.get(lk)
        return QColor(c) if c else self.theme.color("ACCENT")

    def sizeHint(self):
        return QSize(600, 78)

    def paintEvent(self, ev):
        th = self.theme
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        w = self.width()
        y = 28
        n = len(self.segs)
        if not n:
            return
        pad = 18
        font = QFont(self.font())
        font.setPointSizeF(9.0)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()

        # 每段长度：按文字长度分配
        seg_w = []
        for lk, st in self.segs:
            label = self.data.line_name(lk)
            mid = "、".join(st[1:-1])
            txt = label + ("  " + mid if mid else "")
            tw = fm.horizontalAdvance(txt)
            seg_w.append(max(110, min(tw + 70, (w - 2 * pad) / max(1, n) * 1.8)))
        total = sum(seg_w)
        avail = w - 2 * pad
        if total > avail and total > 0:
            k = avail / total
            seg_w = [x * k for x in seg_w]
        xs = [pad]
        for sw in seg_w:
            xs.append(xs[-1] + sw)

        # 色条
        for i, (lk, st) in enumerate(self.segs):
            pen = QPen(self.color_of(lk), 7)
            pen.setCapStyle(Qt.FlatCap)
            p.setPen(pen)
            p.drawLine(int(xs[i]), y, int(xs[i + 1]), y)

        # 下方线路文字
        pen = QPen(th.color("TEXT"))
        p.setPen(pen)
        for i, (lk, st) in enumerate(self.segs):
            label = self.data.line_name(lk)
            mid = "、".join(st[1:-1])
            txt = label + ("  " + mid if mid else "（无途经站）")
            rect = QRectF(xs[i], y + 10, xs[i + 1] - xs[i], 34)
            p.drawText(rect, Qt.AlignHCenter | Qt.TextWordWrap, txt)

        # 节点 + 站名
        pen = QPen(th.color("TEXT"), 2)
        p.setPen(pen)
        p.setBrush(QBrush(th.color("CARD")))
        for x in xs:
            p.drawEllipse(QPointF(x, y), 5, 5)
        # 终点实心
        p.setBrush(QBrush(th.color("TEXT")))
        p.drawEllipse(QPointF(xs[-1], y), 6, 6)

        # 站名（色条上方）
        p.setBrush(Qt.NoBrush)
        nf = QFont(self.font())
        nf.setPointSizeF(9.5)
        nf.setBold(True)
        p.setFont(nf)
        names = [self.segs[0][1][0]] + [st[-1] for _, st in self.segs]
        for i, name in enumerate(names):
            tw = p.fontMetrics().horizontalAdvance(name)
            tx = min(max(xs[i], tw / 2 + 2), max(tw / 2 + 2, w - tw / 2 - 2))
            p.drawText(QRectF(tx - tw / 2 - 4, 2, tw + 8, 20),
                       Qt.AlignCenter, name)


def combo_style(theme: Theme):
    c = theme.color
    bg = c("CARD")
    bg.setAlphaF(0.95)
    return f"""
    QComboBox, QLineEdit {{
        background-color: rgba({bg.red()},{bg.green()},{bg.blue()},{bg.alpha()});
        color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()});
        border: 1px solid rgb({c('BORDER').red()},{c('BORDER').green()},{c('BORDER').blue()});
        border-radius: 5px; padding: 5px 7px;
    }}
    QComboBox QAbstractItemView {{
        background-color: rgb({bg.red()},{bg.green()},{bg.blue()});
        color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()});
        selection-background-color: rgb({c('ACCENT_LT').red()},{c('ACCENT_LT').green()},{c('ACCENT_LT').blue()});
        selection-color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()});
    }}
    """


# ============================================================ 线路查询页
class LinePage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.data = app.data
        bar = Card(self.theme, panel_alpha=0.9)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 12, 14, 12)
        self.box = QComboBox()
        self.box.setEditable(True)
        self.box.setMinimumWidth(260)
        self.box.addItems([self.data.line_name(k) for k in self.data.LINES])
        self.box.setCurrentIndex(-1)
        self.box.setCurrentText("")
        self.box.lineEdit().returnPressed.connect(self.submit)
        self.go = QPushButton("查看线路")
        self.go.clicked.connect(self.submit)
        bl.addWidget(QLabel("线路名称或编号"))
        bl.addWidget(self.box, 1)
        bl.addWidget(self.go)
        self.root.addWidget(bar)
        self.bar = bar

        self.chip_row = QWidget()
        self.chip_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.chip_lay = FlowLayout(self.chip_row, margin=2, spacing=6)
        self.root.addWidget(self.chip_row)
        self._build_chips()

        sa, holder, self.lay = self.scroll_page()
        self.holder = holder
        self.root.addWidget(sa, 1)
        self.retheme()

    def _build_chips(self):
        while self.chip_lay.count():
            it = self.chip_lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for lk in self.data.LINES:
            name = self.data.line_name(lk)
            h = QColor(self.app.line_colors.get(lk, "#888888"))
            btn = QPushButton(name)
            btn.setFixedHeight(26)
            btn.setCursor(Qt.PointingHandCursor)
            # 按文字实际宽度定尺寸，避免被布局压缩导致文字被裁
            f = btn.font()
            f.setPixelSize(12)
            f.setBold(True)
            btn.setFont(f)
            fm = QFontMetrics(f)
            btn.setFixedWidth(fm.horizontalAdvance(name) + 24)
            bg = h.lighter(180)
            btn.setStyleSheet(f"""
                QPushButton {{background-color: rgb({bg.red()},{bg.green()},{bg.blue()});
                    color: rgb({h.darker(150).red()},{h.darker(150).green()},{h.darker(150).blue()});
                    border:1px solid rgb({h.red()},{h.green()},{h.blue()});
                    border-radius:5px;padding:2px 9px;font-size:12px;font-weight:600;}}
                QPushButton:hover {{background-color: rgb({h.red()},{h.green()},{h.blue()});
                    color:white;}}
            """)
            btn.clicked.connect(lambda _=False, k=lk: self.query(k))
            self.chip_lay.addWidget(btn)

    def submit(self):
        text = self.box.currentText().strip()
        if not text:
            return
        lk = self.data.line_key(text)
        if not lk:
            self._error("未识别线路「%s」。可输入 8 / 13B / 玉衡1号线 / 沼刷线" % text)
            return
        self.query(lk)

    def _error(self, msg):
        self._clear()
        lb = QLabel(msg)
        lb.setStyleSheet("color:#c0392b;")
        self.lay.addWidget(lb)
        self.lay.addStretch(1)

    def _clear(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def query(self, lk):
        info = self.data.line_info(lk)
        self.box.setCurrentText(info["name"])
        self._clear()
        th = self.theme
        # 抬头
        top = Card(th)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(18, 14, 18, 14)
        h = QColor(self.app.line_colors.get(lk, "#888888"))
        badge = QLabel(info["key"].replace("L", ""))
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(42, 42)
        badge.setStyleSheet("background-color:rgb(%d,%d,%d);color:white;"
                            "border-radius:21px;font-weight:700;font-size:13px;"
                            % (h.red(), h.green(), h.blue()))
        tl.addWidget(badge)
        box = QVBoxLayout()
        nm = QLabel(info["name"])
        nm.setStyleSheet("font-size:24px;font-weight:700;color:%s;" % th.color("TEXT").name())
        sub = QLabel("%d 座车站%s　首站 %s　末站 %s" %
                     (info["count"], "（环线）" if info["ring"] else "",
                      info["first"], info["last"]))
        sub.setStyleSheet("color:%s;" % th.color("MUTED").name())
        box.addWidget(nm)
        box.addWidget(sub)
        tl.addLayout(box)
        tl.addStretch(1)
        self.lay.addWidget(top)

        # 站表（三列）
        grid_card = Card(th)
        gl = QVBoxLayout(grid_card)
        gl.setContentsMargins(18, 14, 18, 14)
        head = QHBoxLayout()
        t2 = QLabel("全部车站（按上行方向）")
        t2.setStyleSheet("font-weight:700;font-size:14px;color:%s;" % th.color("TEXT").name())
        hint = QLabel("点击站名可查看该站详情")
        hint.setStyleSheet("font-size:11px;color:%s;" % th.color("MUTED").name())
        head.addWidget(t2)
        head.addWidget(hint)
        head.addStretch(1)
        gl.addLayout(head)
        grid = QGridLayout()
        grid.setSpacing(6)
        cols = 3
        for i, st in enumerate(info["stations"]):
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(0, 2, 0, 2)
            hl.setSpacing(6)
            name = QLabel("%2d  %s" % (st["index"], st["name"]))
            name.setCursor(Qt.PointingHandCursor)
            name.setStyleSheet("font-size:13px;color:%s;%s"
                               % (th.color("TEXT").name(),
                                  "font-weight:700;" if st["transfers"] else ""))
            name.mousePressEvent = (lambda e, n=st["name"]: self.app.goto_station(n))
            hl.addWidget(name)
            for xlk, xname in st["transfers"]:
                hh = QColor(self.app.line_colors.get(xlk, "#888"))
                tag = QLabel("⇄ " + xname)
                tag.setStyleSheet(
                    "font-size:10px;color:rgb(%d,%d,%d);background-color:rgb(%d,%d,%d);"
                    "border-radius:3px;padding:1px 4px;"
                    % (hh.darker(160).red(), hh.darker(160).green(), hh.darker(160).blue(),
                       hh.lighter(185).red(), hh.lighter(185).green(), hh.lighter(185).blue()))
                hl.addWidget(tag)
            hl.addStretch(1)
            grid.addWidget(w, i // cols, i % cols)
        gl.addLayout(grid)
        self.lay.addWidget(grid_card)
        self.lay.addStretch(1)

    def retheme(self):
        c = self.theme.color
        for b in (self.go,):
            b.setStyleSheet(button_style(self.theme, "primary"))
        self.box.setStyleSheet(combo_style(self.theme))
        self.bar.update()


# ============================================================ 站点查询页
class StationPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.data = app.data
        bar = Card(self.theme, panel_alpha=0.9)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 12, 14, 12)
        self.box = QComboBox()
        self.box.setEditable(True)
        self.box.setMinimumWidth(240)
        self.box.addItems(STATIONS)
        self.box.setCurrentIndex(-1)
        self.box.setCurrentText("")
        self.box.lineEdit().returnPressed.connect(self.submit)
        self.go = QPushButton("查询站点")
        self.go.clicked.connect(self.submit)
        bl.addWidget(QLabel("输入站名（可只输一部分）"))
        bl.addWidget(self.box, 1)
        bl.addWidget(self.go)
        self.root.addWidget(bar)
        self.bar = bar

        sa, holder, self.lay = self.scroll_page()
        self.holder = holder
        self.root.addWidget(sa, 1)
        self.retheme()

    def _clear(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def submit(self):
        text = self.box.currentText().strip()
        if not text:
            return
        canon = self.data.resolve(text)[0]
        if not canon:
            hits = self.data.stations_matching(text, limit=1)
            canon = hits[0] if hits else None
        if not canon:
            self._clear()
            lb = QLabel("未找到站点「%s」" % text)
            lb.setStyleSheet("color:#c0392b;")
            self.lay.addWidget(lb)
            self.lay.addStretch(1)
            return
        self.query(canon)

    def query(self, name):
        info = self.data.station_info(name)
        if not info:
            return
        self.box.setCurrentText(name)
        th = self.theme
        self._clear()

        top = Card(th)
        tl = QVBoxLayout(top)
        tl.setContentsMargins(18, 14, 18, 14)
        nm = QLabel(info["name"])
        nm.setStyleSheet("font-size:26px;font-weight:700;color:%s;" % th.color("TEXT").name())
        tl.addWidget(nm)
        row = QHBoxLayout()
        sub = QLabel("换乘站 · 共 %d 条线路：" % len(info["line_names"])
                     if info["is_transfer"] else "普通站 · 线路：")
        sub.setStyleSheet("color:%s;" % th.color("MUTED").name())
        row.addWidget(sub)
        for ln in info["lines"]:
            hh = QColor(self.app.line_colors.get(ln["key"], "#888"))
            tag = QLabel(ln["name"])
            tag.setStyleSheet(
                "font-size:11px;color:rgb(%d,%d,%d);background-color:rgb(%d,%d,%d);"
                "border-radius:4px;padding:2px 7px;font-weight:600;"
                % (hh.darker(160).red(), hh.darker(160).green(), hh.darker(160).blue(),
                   hh.lighter(185).red(), hh.lighter(185).green(), hh.lighter(185).blue()))
            row.addWidget(tag)
        row.addStretch(1)
        tl.addLayout(row)
        self.lay.addWidget(top)

        # 每条线路的方向
        for ln in info["lines"]:
            card = Card(th)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            hh = QColor(self.app.line_colors.get(ln["key"], "#888"))
            head = QHBoxLayout()
            badge = QLabel(ln["name"])
            badge.setStyleSheet(
                "font-size:12px;color:white;background-color:rgb(%d,%d,%d);"
                "border-radius:4px;padding:3px 9px;font-weight:700;"
                % (hh.red(), hh.green(), hh.blue()))
            meta = "第 %d / %d 站%s　%s → %s" % (
                ln["index"], ln["count"], "  · 环线" if ln["ring"] else "",
                ln["first"], ln["last"])
            ml = QLabel(meta)
            ml.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
            head.addWidget(badge)
            head.addWidget(ml)
            head.addStretch(1)
            cl.addLayout(head)
            for d in ln["dirs"]:
                row = QHBoxLayout()
                dl = QLabel(d["dir"])
                dl.setMinimumWidth(110)
                dl.setStyleSheet("font-weight:600;color:%s;" % th.color("TEXT").name())
                row.addWidget(dl)
                for lab, sta in ((d["prev_label"], d["prev"]), (d["next_label"], d["next"])):
                    if not lab:
                        continue
                    ll = QLabel(lab)
                    ll.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
                    row.addWidget(ll)
                    if sta:
                        sl = QLabel(sta)
                        sl.setCursor(Qt.PointingHandCursor)
                        sl.setStyleSheet("color:%s;font-weight:600;" % th.color("ACCENT_DK").name())
                        sl.mousePressEvent = (lambda e, n=sta: self.query(n))
                        row.addWidget(sl)
                    else:
                        el = QLabel("终点站")
                        el.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
                        row.addWidget(el)
                    row.addSpacing(18)
                row.addStretch(1)
                cl.addLayout(row)
            self.lay.addWidget(card)
        self.lay.addStretch(1)

    def retheme(self):
        self.go.setStyleSheet(button_style(self.theme, "primary"))
        self.box.setStyleSheet(combo_style(self.theme))
        self.bar.update()


# ============================================================ 线网概览页
class OverviewPage(Page):
    def __init__(self, app):
        super().__init__(app)
        sa, holder, self.lay = self.scroll_page()
        self.root.addWidget(sa, 1)
        self.build()

    def _clear(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def build(self):
        th = self.theme
        data = self.app.data
        self._clear()
        lines = list(data.LINES.keys())
        transfers = [s for s in data.STATIONS if len(data.STATION_LINES[s]) > 1]
        groups = getattr(data, "LINE_GROUPS", {}) or {}
        line_count = len(lines) - sum(len(v) for v in groups.values()) + len(groups)
        rings = [k for k in lines if k in data.RING]

        # 统计卡
        stats = QHBoxLayout()
        for label, value, unit in (("线路", line_count, "条"),
                                   ("车站", len(data.STATIONS), "座"),
                                   ("换乘站", len(transfers), "座"),
                                   ("环线", len(rings), "条")):
            card = Card(th)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 12, 18, 12)
            l1 = QLabel(label)
            l1.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
            l2 = QLabel("%d %s" % (value, unit))
            l2.setStyleSheet("font-size:24px;font-weight:700;color:%s;" % th.color("TEXT").name())
            cl.addWidget(l1)
            cl.addWidget(l2)
            stats.addWidget(card, 1)
        sw = QWidget()
        sw.setLayout(stats)
        self.lay.addWidget(sw)

        # 换乘枢纽
        top = sorted(transfers, key=lambda s: (-len(data.STATION_LINES[s]), s))[:12]
        hub = Card(th)
        hl = QVBoxLayout(hub)
        hl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("换乘枢纽 Top 12")
        t.setStyleSheet("font-weight:700;color:%s;" % th.color("TEXT").name())
        hl.addWidget(t)
        grid = QGridLayout()
        for i, name in enumerate(top):
            w = QWidget()
            r = QHBoxLayout(w)
            r.setContentsMargins(0, 2, 0, 2)
            lb = QLabel(name)
            lb.setCursor(Qt.PointingHandCursor)
            lb.setStyleSheet("font-weight:600;color:%s;" % th.color("TEXT").name())
            lb.mousePressEvent = (lambda e, n=name: self.app.goto_station(n))
            r.addWidget(lb)
            for lk in data.STATION_LINES[name]:
                hh = QColor(self.app.line_colors.get(lk, "#888"))
                tag = QLabel(short_line_code(lk))
                tag.setStyleSheet(
                    "font-size:10px;color:rgb(%d,%d,%d);background-color:rgb(%d,%d,%d);"
                    "border-radius:3px;padding:1px 4px;"
                    % (hh.darker(170).red(), hh.darker(170).green(), hh.darker(170).blue(),
                       hh.lighter(185).red(), hh.lighter(185).green(), hh.lighter(185).blue()))
                r.addWidget(tag)
            r.addStretch(1)
            grid.addWidget(w, i // 3, i % 3)
        hl.addLayout(grid)
        self.lay.addWidget(hub)

        # 全部线路
        dircard = Card(th)
        dl = QVBoxLayout(dircard)
        dl.setContentsMargins(16, 12, 16, 12)
        t2 = QLabel("全部线路（点击查看站序）")
        t2.setStyleSheet("font-weight:700;color:%s;" % th.color("TEXT").name())
        dl.addWidget(t2)
        for lk in lines:
            hh = QColor(self.app.line_colors.get(lk, "#888"))
            row = QHBoxLayout()
            nm = data.line_name(lk)
            badge = QPushButton(nm)
            badge.setCursor(Qt.PointingHandCursor)
            badge.setFixedHeight(24)
            badge.setStyleSheet(
                "QPushButton{background-color:rgb(%d,%d,%d);color:white;border:none;"
                "border-radius:4px;padding:2px 9px;font-size:11px;font-weight:700;}"
                "QPushButton:hover{background-color:rgb(%d,%d,%d);}"
                % (hh.lighter(185).red(), hh.lighter(185).green(), hh.lighter(185).blue(),
                   hh.red(), hh.green(), hh.blue()))
            badge.clicked.connect(lambda _=False, k=lk: self.app.goto_line(k))
            row.addWidget(badge)
            n = len(data.LINES[lk]) - (1 if lk in data.RING else 0)
            prev = data.line_sequence_preview(lk)
            info = QLabel("%d 站%s　%s" % (n, "  · 环线" if lk in data.RING else "", prev))
            info.setStyleSheet("font-size:11px;color:%s;" % th.color("MUTED").name())
            row.addWidget(info, 1)
            dl.addLayout(row)
        self.lay.addWidget(dircard)

        # 服务器铁路局
        self.lay.addWidget(self._bureau_card())
        # 轨交趣闻
        self.lay.addWidget(self._fun_card())
        self.lay.addStretch(1)

    def _bureau_card(self):
        th = self.theme
        card = Card(th)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("服务器铁路局")
        t.setStyleSheet("font-weight:700;color:%s;" % th.color("TEXT").name())
        h = QLabel("实心线路表示已在本软件线网中，空心表示未收录")
        h.setStyleSheet("font-size:11px;color:%s;" % th.color("MUTED").name())
        cl.addWidget(t)
        cl.addWidget(h)
        grid = QGridLayout()
        for c, title in enumerate(("编号", "线路局名称", "局主", "线路")):
            lb = QLabel(title)
            lb.setStyleSheet("font-size:11px;color:%s;" % th.color("MUTED").name())
            grid.addWidget(lb, 0, c)
        for r, (num, bureau, owner, codes) in enumerate(RAILWAY_BUREAUS, start=1):
            grid.addWidget(QLabel(str(num)), r, 0)
            nb = QLabel(bureau)
            nb.setStyleSheet("font-weight:600;color:%s;" % th.color("TEXT").name())
            grid.addWidget(nb, r, 1)
            ob = QLabel(owner or "—")
            ob.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
            grid.addWidget(ob, r, 2)
            cell = QWidget()
            rr = QHBoxLayout(cell)
            rr.setContentsMargins(0, 0, 0, 0)
            rr.setSpacing(4)
            if not codes:
                rr.addWidget(QLabel("—"))
            for code in codes:
                lk = line_key_from_code(code)
                if lk in self.app.data.LINES:
                    hh = QColor(self.app.line_colors.get(lk, "#888"))
                    lb = QLabel("● " + code)
                    lb.setStyleSheet(
                        "font-size:11px;color:rgb(%d,%d,%d);background-color:rgb(%d,%d,%d);"
                        "border-radius:3px;padding:1px 5px;"
                        % (hh.darker(170).red(), hh.darker(170).green(), hh.darker(170).blue(),
                           hh.lighter(185).red(), hh.lighter(185).green(), hh.lighter(185).blue()))
                else:
                    lb = QLabel("○ " + code)
                    lb.setStyleSheet("font-size:11px;color:%s;" % th.color("MUTED").name())
                rr.addWidget(lb)
            rr.addStretch(1)
            grid.addWidget(cell, r, 3)
        cl.addLayout(grid)
        return card

    def _fun_card(self):
        th = self.theme
        card = Card(th)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("轨交趣闻")
        t.setStyleSheet("font-weight:700;color:%s;" % th.color("TEXT").name())
        cl.addWidget(t)
        for title, items in FUN_FACTS:
            st = QLabel(title)
            st.setStyleSheet("font-weight:700;color:%s;" % th.color("ACCENT_DK").name())
            cl.addWidget(st)
            for tag, text in items:
                lb = QLabel("%s  %s" % (tag, text))
                lb.setStyleSheet("font-size:12px;color:%s;" % th.color("TEXT").name())
                cl.addWidget(lb)
        return card

    def retheme(self):
        self.build()


# ============================================================ 设置页
class SettingsPage(Page):
    def __init__(self, app):
        super().__init__(app)
        sa, holder, self.lay = self.scroll_page()
        self.root.addWidget(sa, 1)
        self.build()

    def _clear(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def _card(self, title, hint=""):
        th = self.theme
        card = Card(th)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)
        head = QHBoxLayout()
        t = QLabel(title)
        t.setStyleSheet("font-size:17px;font-weight:700;color:%s;" % th.color("TEXT").name())
        head.addWidget(t)
        if hint:
            h = QLabel(hint)
            h.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
            head.addWidget(h)
        head.addStretch(1)
        lay.addLayout(head)
        self.lay.addWidget(card)
        return card, lay

    def _seg(self, lay, label, options, current, on_pick):
        th = self.theme
        row = QHBoxLayout()
        lb = QLabel(label)
        lb.setMinimumWidth(84)
        lb.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        row.addWidget(lb)
        for key, text in options:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setChecked(key == current)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._seg_style())
            b.clicked.connect(lambda _=False, k=key: on_pick(k))
            row.addWidget(b)
        row.addStretch(1)
        lay.addLayout(row)

    def _seg_style(self):
        th = self.theme
        c = th.color
        bg = th.rgba("CHIP", 0.8)
        return f"""
        QPushButton {{
            background-color: rgba({bg.red()},{bg.green()},{bg.blue()},{bg.alpha()});
            color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()});
            border: 1px solid rgb({c('BORDER').red()},{c('BORDER').green()},{c('BORDER').blue()});
            border-radius: 6px; padding: 6px 16px;
        }}
        QPushButton:checked {{
            background-color: rgb({c('ACCENT').red()},{c('ACCENT').green()},{c('ACCENT').blue()});
            color: white; border: 1px solid rgb({c('ACCENT').red()},{c('ACCENT').green()},{c('ACCENT').blue()});
        }}
        """

    def build(self):
        th = self.theme
        self._clear()

        # ---------- 外观主题 ----------
        _, lay = self._card("外观主题", "明暗配色与窗口背景")

        self._seg(lay, "明暗配色",
                  (("light", "明亮主题"), ("dark", "暗色主题")),
                  th.cfg.get("mode"), self._set_mode)
        self._seg(lay, "背景类型",
                  (("solid", "纯色背景"), ("image", "图片背景")),
                  th.cfg.get("bg_type"), self._set_bg_type)

        # 纯色
        self.solid_box = QWidget()
        sl = QVBoxLayout(self.solid_box)
        sl.setContentsMargins(0, 4, 0, 0)
        cl = QLabel("背景颜色")
        cl.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        sl.addWidget(cl)
        row = QHBoxLayout()
        for col in ("#f3f5f9", "#ffffff", "#eef3fb", "#f7f2e8", "#eaf5ee",
                    "#f5eefa", "#1b1e24", "#23272f", "#2b2f38", "#0f1720"):
            b = QPushButton()
            b.setFixedSize(30, 30)
            b.setCursor(Qt.PointingHandCursor)
            cur = (th.cfg.get("bg_color") or "").lower() == col.lower()
            b.setStyleSheet(
                "QPushButton{background-color:%s;border:%s;border-radius:5px;}"
                % (col, ("3px solid %s" % th.color("ACCENT").name()) if cur
                   else "1px solid #888888"))
            b.clicked.connect(lambda _=False, cc=col: self._set_color(cc))
            row.addWidget(b)
        row.addStretch(1)
        sl.addLayout(row)
        lay.addWidget(self.solid_box)
        self.solid_box.setVisible(th.cfg.get("bg_type") == "solid")

        # 图片
        self.image_box = QWidget()
        il = QVBoxLayout(self.image_box)
        il.setContentsMargins(0, 4, 0, 0)
        il.setSpacing(8)
        prow = QHBoxLayout()
        pick = QPushButton("选择图片…")
        pick.clicked.connect(self._pick_image)
        pick.setStyleSheet(button_style(th, "secondary"))
        path = th.cfg.get("bg_image") or ""
        self.img_label = QLabel(os.path.basename(path) if path
                                else "还没有选择图片，点击左侧按钮上传")
        self.img_label.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        prow.addWidget(pick)
        prow.addWidget(self.img_label)
        prow.addStretch(1)
        il.addLayout(prow)

        # 图片大小
        fr = QHBoxLayout()
        fl = QLabel("显示方式")
        fl.setMinimumWidth(84)
        fl.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        fr.addWidget(fl)
        for key, text in (("cover", "放大填充"), ("stretch", "拉伸填充"),
                          ("none", "不处理")):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setChecked(th.cfg.get("bg_fit") == key)
            b.setStyleSheet(self._seg_style())
            b.clicked.connect(lambda _=False, k=key: self._set_fit(k))
            fr.addWidget(b)
        fr.addStretch(1)
        il.addLayout(fr)

        # 滑动条
        il.addLayout(self._slider("不透明度", "bg_opacity", 5, 100,
                                  lambda v: "%d%%" % v,
                                  lambda v: self._set_opacity(v)))
        il.addLayout(self._slider("卡片模糊度", "panel_opacity", 0, 100,
                                  lambda v: "%d%%" % v,
                                  lambda v: self._set_panel(v)))
        il.addLayout(self._slider("图片模糊度", "bg_blur", 0, 25,
                                  lambda v: "%d" % v,
                                  lambda v: self._set_blur(v)))
        lay.addWidget(self.image_box)
        self.image_box.setVisible(th.cfg.get("bg_type") == "image")

        # ---------- 版本 ----------
        _, vl = self._card("版本")
        ver = QLabel("软件版本：" + VERSION)
        ver.setStyleSheet("color:%s;" % th.color("TEXT").name())
        note = QLabel("设置会自动保存，下次打开仍然生效。")
        note.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        vl.addWidget(ver)
        vl.addWidget(note)
        self.lay.addStretch(1)

    def _slider(self, label, key, lo, hi, fmtf, on_change):
        th = self.theme
        row = QHBoxLayout()
        lb = QLabel(label)
        lb.setMinimumWidth(84)
        lb.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        row.addWidget(lb)
        val = QLabel("")
        val.setMinimumWidth(52)
        val.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        s = QSlider(Qt.Horizontal)
        s.setRange(lo, hi)
        cur = th.cfg.get(key, lo)
        s.setValue(int(round(float(cur) * 100)) if key != "bg_blur" else int(cur))
        val.setText(fmtf(s.value() if key == "bg_blur"
                         else int(round(s.value()))))
        s.valueChanged.connect(lambda v: (val.setText(fmtf(v)), on_change(v)))
        row.addWidget(s, 1)
        row.addWidget(val)
        self._slider_vals = getattr(self, "_slider_vals", {})
        self._slider_vals[key] = val
        return row

    # ---------- 事件 ----------
    def _set_mode(self, key):
        self.theme.cfg["mode"] = key
        self.app.apply_theme()

    def _set_bg_type(self, key):
        self.theme.cfg["bg_type"] = key
        if key == "image" and not (self.theme.cfg.get("bg_image") or ""):
            self._pick_image()
        self.app.apply_theme()

    def _set_color(self, col):
        self.theme.cfg["bg_color"] = col
        self.theme.cfg["bg_type"] = "solid"
        self.app.apply_theme()

    def _set_fit(self, key):
        self.theme.cfg["bg_fit"] = key
        self.app.apply_theme()

    def _set_opacity(self, v):
        self.theme.cfg["bg_opacity"] = max(0.05, v / 100.0)
        self.app.apply_theme(rebuild_self=False)

    def _set_panel(self, v):
        self.theme.cfg["panel_opacity"] = max(0.0, min(1.0, v / 100.0))
        self.app.apply_theme(rebuild_self=False)

    def _set_blur(self, v):
        self.theme.cfg["bg_blur"] = int(v)
        self.app.apply_theme(rebuild_self=False)

    def _pick_image(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "图片 (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;所有文件 (*.*)")
        if p:
            self.theme.cfg["bg_image"] = p
            self.theme.cfg["bg_type"] = "image"
        self.app.apply_theme()

    def retheme(self):
        self.build()


# ============================================================ 关于页
class AboutPage(Page):
    def __init__(self, app):
        super().__init__(app)
        sa, holder, self.lay = self.scroll_page()
        self.root.addWidget(sa, 1)
        self.build()

    def _clear(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def build(self):
        th = self.theme
        self._clear()

        # 标题
        card = Card(th)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 18, 22, 18)
        t = QLabel(APP_TITLE)
        t.setStyleSheet("font-size:26px;font-weight:700;color:%s;" % th.color("TEXT").name())
        v = QLabel("软件版本：" + VERSION)
        v.setStyleSheet("color:%s;" % th.color("MUTED").name())
        cl.addWidget(t)
        cl.addWidget(v)
        self.lay.addWidget(card)

        # 提示
        notice = Card(th, panel_alpha=0.9)
        nl = QVBoxLayout(notice)
        nl.setContentsMargins(20, 12, 20, 12)
        nt = QLabel("本软件仅使用于TPC服务器内群，请注意及时更新版本，避免数据过时")
        nt.setStyleSheet("color:%s;" % th.color("ACCENT_DK").name())
        nl.addWidget(nt)
        self.lay.addWidget(notice)

        # 计算方式
        card2 = Card(th)
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(20, 16, 20, 16)
        h = QLabel("计算方式")
        h.setStyleSheet("font-size:17px;font-weight:700;color:%s;" % th.color("TEXT").name())
        c2.addWidget(h)
        row = QHBoxLayout()
        self.algo_btns = {}
        for key, text in (("weight", "新版 · 权重最优"), ("score", "旧版 · 综合较优")):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setChecked(self.app.data.algo == key)
            b.setStyleSheet(self._seg_style())
            b.clicked.connect(lambda _=False, k=key: self._set_algo(k))
            row.addWidget(b)
            self.algo_btns[key] = b
        row.addStretch(1)
        c2.addLayout(row)
        if self.app.data.algo == "weight":
            desc = ("权重 = 总里程(m) + 换乘权重。普通换乘 100，纺林 300，"
                    "欢乐谷 / 梦樱 / 刷冰机 200，火药塔 2 号线与 10、11 号线互转 250。")
        else:
            desc = "得分 = 区间数 + 换乘数 × 2，只看坐了几站、换了几次车。"
        d = QLabel(desc)
        d.setWordWrap(True)
        d.setStyleSheet("font-size:12px;color:%s;" % th.color("MUTED").name())
        c2.addWidget(d)
        self.lay.addWidget(card2)

        # 署名
        card3 = Card(th)
        g = QGridLayout(card3)
        g.setContentsMargins(22, 18, 22, 18)
        g.setHorizontalSpacing(24)
        g.setVerticalSpacing(8)
        rows = [("数据统计", ["示全", "明月花火"]),
                ("软件开发", ["示全 —— 构建旧版综合算法",
                              "明月花火 —— 构建新版权重算法",
                              "哈九_HM —— 构建图形化界面"]),
                ("技术交流及bug反馈", ["QQ群480183016 | QQ号3973475260"])]
        r = 0
        for key, vals in rows:
            kl = QLabel(key)
            kl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            kl.setStyleSheet("color:%s;" % th.color("MUTED").name())
            g.addWidget(kl, r, 0, Qt.AlignTop)
            vb = QVBoxLayout()
            for line in vals:
                lb = QLabel(line)
                lb.setStyleSheet("color:%s;" % th.color("TEXT").name())
                vb.addWidget(lb)
            g.addLayout(vb, r, 1)
            r += 1
        wiki = QHBoxLayout()
        wl = QLabel("wiki站：")
        wl.setStyleSheet("color:%s;" % th.color("MUTED").name())
        wu = QLabel("wiki.tpcmc.top")
        wu.setStyleSheet("color:%s;" % th.color("TEXT").name())
        wiki.addWidget(wl)
        wiki.addWidget(wu)
        wiki.addStretch(1)
        g.addLayout(wiki, r, 0, 1, 2)
        r += 1
        thanks = QHBoxLayout()
        tk_ = QLabel("特别致谢")
        tk_.setStyleSheet("font-weight:700;color:%s;" % th.color("ACCENT_DK").name())
        tv = QLabel("为TPC贡献的每一个人")
        tv.setStyleSheet("color:%s;" % th.color("TEXT").name())
        thanks.addWidget(tk_)
        thanks.addWidget(tv)
        thanks.addStretch(1)
        g.addLayout(thanks, r, 0, 1, 2)
        g.setColumnStretch(1, 1)
        self.lay.addWidget(card3)

        # 使用帮助
        card4 = Card(th)
        h4 = QVBoxLayout(card4)
        h4.setContentsMargins(22, 18, 22, 18)
        hh = QLabel("使用帮助")
        hh.setStyleSheet("font-size:17px;font-weight:700;color:%s;" % th.color("TEXT").name())
        h4.addWidget(hh)
        helps = [
            ("路径查询", ["填起点与终点，可只输站名一部分。",
                          "结果分三组：权重最优 / 换乘最少 / 区间最少。",
                          "卡片下方直接画出全程站序示意条。",
                          "查询结果自动复制到剪贴板。"]),
            ("线路查询", ["输入 8 / 8号线 / L8 / 13B / 玉衡1号线 / T6 都可以。",
                          "3 号线分北段与南段，输 3 显示两段。"]),
            ("站点查询", ["查看经过该站的线路与各方向前后站。"]),
            ("其他", ["设置页可换明暗配色、纯色或图片背景。",
                      "图片背景支持不透明度、卡片模糊度、图片模糊度与缩放方式。",
                      "窗口大小与查询历史会自动记住。"]),
        ]
        for sec, items in helps:
            sl = QLabel(sec)
            sl.setStyleSheet("font-weight:700;color:%s;" % th.color("ACCENT_DK").name())
            h4.addWidget(sl)
            for it in items:
                lb = QLabel("· " + it)
                lb.setWordWrap(True)
                lb.setStyleSheet("font-size:12px;color:%s;" % th.color("TEXT").name())
                h4.addWidget(lb)
        self.lay.addWidget(card4)
        self.lay.addStretch(1)

    def _seg_style(self):
        th = self.theme
        c = th.color
        bg = th.rgba("CHIP", 0.8)
        return f"""
        QPushButton {{
            background-color: rgba({bg.red()},{bg.green()},{bg.blue()},{bg.alpha()});
            color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()});
            border: 1px solid rgb({c('BORDER').red()},{c('BORDER').green()},{c('BORDER').blue()});
            border-radius: 6px; padding: 6px 16px;
        }}
        QPushButton:checked {{
            background-color: rgb({c('ACCENT').red()},{c('ACCENT').green()},{c('ACCENT').blue()});
            color: white;
        }}
        """

    def _set_algo(self, key):
        if key != self.app.data.algo:
            self.app.data.set_algo(key)
            cfg = load_config()
            cfg["algo"] = key
            save_config(cfg)
        self.build()

    def retheme(self):
        self.build()


# ============================================================ 主窗口
class MainWindow(QMainWindow):
    INDEX = {"welcome": 0, "path": 1, "line": 2, "station": 3,
             "overview": 4, "settings": 5, "about": 6}

    def __init__(self, data_path):
        super().__init__()
        self.cfg = load_config()
        self.theme = Theme()
        self.theme.load(self.cfg.get("theme"))
        self.data = MetroData(data_path, algo=self.cfg.get("algo") or "weight")
        self.line_colors = {lk: line_color(lk)[0] for lk in self.data.LINES}

        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 800)

        self.bg = BackgroundWidget(self.theme)
        self.setCentralWidget(self.bg)
        outer = QVBoxLayout(self.bg)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 顶部
        self.header = QFrame()
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(18, 10, 18, 10)
        self.logo = QLabel()
        self.logo.setFixedSize(36, 36)
        self.title = QLabel(APP_TITLE)
        self.subtitle = QLabel("")
        tv = QVBoxLayout()
        tv.setSpacing(0)
        tv.addWidget(self.title)
        tv.addWidget(self.subtitle)
        hl.addWidget(self.logo)
        hl.addLayout(tv)
        hl.addStretch(1)
        self.theme_btn = QPushButton("深色模式")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.data_btn = QPushButton("数据文件")
        self.data_btn.clicked.connect(self.choose_data)
        hl.addWidget(self.data_btn)
        hl.addWidget(self.theme_btn)
        outer.addWidget(self.header)

        # 页签
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        outer.addWidget(self.tabs, 1)

        self.welcome = WelcomePage(self)
        self.path = PathPage(self)
        self.line = LinePage(self)
        self.station = StationPage(self)
        self.overview = OverviewPage(self)
        self.settings = SettingsPage(self)
        self.about = AboutPage(self)
        for w, name in ((self.welcome, "欢迎"), (self.path, "路径查询"),
                        (self.line, "线路查询"), (self.station, "站点查询"),
                        (self.overview, "线网概览"), (self.settings, "设置"),
                        (self.about, "关于")):
            self.tabs.addTab(w, name)
        self.tabs.setCurrentIndex(0)

        # 状态栏
        self.status_label = QLabel("")
        self.statusBar().addWidget(self.status_label, 1)

        self.update_stats()
        self.apply_theme()

    # ---------------- 主题 ----------------
    def apply_theme(self, rebuild_self=True):
        th = self.theme
        self.bg.refresh()
        self.update_stats()
        for page in (self.welcome, self.path, self.line, self.station,
                     self.overview, self.settings, self.about):
            page.retheme()
        if rebuild_self:
            self._style_chrome()
        # 任何主题改动（包括拖滑块）都立刻写盘
        self.save_all()

    def save_all(self):
        """把当前主题、算法、窗口尺寸合并写回配置文件。"""
        try:
            disk = load_config()          # 先读磁盘，避免覆盖掉别的键
            disk["theme"] = self.theme.as_dict()
            disk["algo"] = self.data.algo
            geo = self.geometry()
            disk["last_size"] = [geo.width(), geo.height()]
            self.cfg = disk
            ok = save_config(disk)
            if not ok:
                self.statusBar().showMessage("设置保存失败（目录可能不可写）", 5000)
            return ok
        except Exception:
            return False

    def _style_chrome(self):
        th = self.theme
        c = th.color
        hdr_bg = th.rgba("CARD", 0.72 if th.cfg.get("bg_type") == "image" else 1.0)
        self.header.setStyleSheet(
            "QFrame{background-color:rgba(%d,%d,%d,%d);border-bottom:1px solid rgb(%d,%d,%d);}"
            % (hdr_bg.red(), hdr_bg.green(), hdr_bg.blue(), hdr_bg.alpha(),
               c("BORDER").red(), c("BORDER").green(), c("BORDER").blue()))
        self.title.setStyleSheet("font-size:16px;font-weight:700;color:%s;" % c("TEXT").name())
        self.subtitle.setStyleSheet("font-size:11px;color:%s;" % c("MUTED").name())
        self.theme_btn.setStyleSheet(button_style(th, "ghost"))
        self.data_btn.setStyleSheet(button_style(th, "ghost"))
        self.theme_btn.setText("浅色模式" if th.dark else "深色模式")
        # 页签样式
        self.tabs.setStyleSheet(f"""
        QTabWidget::pane {{border:1px solid rgba({c('BORDER').red()},{c('BORDER').green()},{c('BORDER').blue()},120);
            background: transparent;}}
        QTabBar::tab {{
            background: rgba({c('BG').red()},{c('BG').green()},{c('BG').blue()},120);
            color: rgb({c('MUTED').red()},{c('MUTED').green()},{c('MUTED').blue()});
            padding: 8px 20px; border: 1px solid transparent;
            border-top-left-radius:6px; border-top-right-radius:6px;
            font-size: 13px; font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background: rgba({c('CARD').red()},{c('CARD').green()},{c('CARD').blue()},150);
            color: rgb({c('ACCENT_DK').red()},{c('ACCENT_DK').green()},{c('ACCENT_DK').blue()});
            border: 1px solid rgba({c('BORDER').red()},{c('BORDER').green()},{c('BORDER').blue()},140);
            border-bottom-color: transparent;
        }}
        QTabBar::tab:hover {{ color: rgb({c('TEXT').red()},{c('TEXT').green()},{c('TEXT').blue()}); }}
        """)
        self.setStyleSheet(
            "QStatusBar{background:transparent;color:rgb(%d,%d,%d);}"
            % (c("MUTED").red(), c("MUTED").green(), c("MUTED").blue()))
        self._draw_logo()

    def _draw_logo(self):
        th = self.theme
        pm = QPixmap(36, 36)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing, True)
        acc = th.color("ACCENT")
        p.setBrush(QBrush(acc))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, 36, 36)
        pen = QPen(QColor("#ffffff"), 3)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(13, 10, 19, 26)
        p.setPen(QPen(QColor("#ffd166"), 3, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(20, 10, 26, 26)
        p.setBrush(QBrush(QColor("#ffffff")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(17, 24, 9, 9)
        p.end()
        self.logo.setPixmap(pm)

    def toggle_theme(self):
        th = self.theme
        th.cfg["mode"] = "light" if th.dark else "dark"
        self.apply_theme()

    # ---------------- 其它 ----------------
    def update_stats(self):
        self.subtitle.setText("%d 条线路 · %d 个车站 · %s · 数据来源 内置数据"
                              % (len(self.data.LINES), len(self.data.STATIONS),
                                 self.data.algo_name))

    def goto_station(self, name):
        self.tabs.setCurrentIndex(self.INDEX["station"])
        self.station.query(name)

    def goto_line(self, lk):
        self.tabs.setCurrentIndex(self.INDEX["line"])
        self.line.query(lk)

    def choose_data(self):
        p, _ = QFileDialog.getOpenFileName(self, "选择线路数据脚本", "",
                                           "Python 脚本 (*.py);;所有文件 (*.*)")
        if not p:
            return
        try:
            self.data = MetroData(p)
        except Exception as exc:
            QMessageBox.critical(self, "加载失败", str(exc))
            return
        self.line_colors = {lk: line_color(lk)[0] for lk in self.data.LINES}
        self.path.data = self.data
        self.line.data = self.data
        self.station.data = self.data
        self.update_stats()

    def closeEvent(self, ev):
        self.save_all()
        super().closeEvent(ev)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    win = MainWindow(None)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
