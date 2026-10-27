# -*- coding: utf-8 -*-
"""渲染 16 课次三套产物:学习任务单(md)+教学设计方案(md)+课件PPT(pptx)。
用法: python tools/generate.py  (课程仓根目录运行)"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

S = load("sessions_a").SESSIONS_A + load("sessions_b").SESSIONS_B

# ---------- 任务单 md ----------
def task_sheet(s):
    L = [f"# 学习任务单 {s['num']}:{s['title']}\n",
         f"> 学习领域 {s['lf']} | 第 {s['week']} 周 | 4 课时(180min)| 双元制六步法+费曼讲台\n",
         "## 布鲁姆目标(本课你要达到)\n"]
    for lv, t in s["bloom"]:
        L.append(f"- **[{lv}]** {t}")
    L.append("\n## 情境导入(资讯)\n" + s["scene"])
    L.append("\n## 上节回顾\n" + s["review"])
    L.append("\n## 计划与决策\n"
             "1. 工单员领单,组内宣读目标与交付物;\n2. 拆解实训步骤,分配操作员/检查员;\n"
             "3. 向教师陈述 30 秒方案,**重申安全红线**(禁 L2/L3 越权操作)。\n")
    L.append("## 知识建构精讲要点(理论 35min,教师主持)\n")
    for t, pts in s["knowledge"]:
        L.append(f"### {t}")
        for p in pts:
            L.append(f"- {p}")
    L.append("\n## 实训实施(70min,双师巡回)\n")
    for i, (st, d) in enumerate(s["lab"], 1):
        L.append(f"{i}. **{st}** — {d}")
    L.append("\n## 检查清单(15min,检查员主持·互查组复核)\n")
    for lv, c in s["check"]:
        L.append(f"- [ ] [{lv}] {c}")
    L.append(f"\n## 费曼讲台(15min)\n**讲题:{s['feynman']}**\n"
             "规程:白纸讲授 6min(不看笔记)→同伴追问 4min(卡壳即回炉)→类比压缩 3min。"
             "未过检查清单的小组不得上台。\n")
    L.append("## 课后作业\n")
    for h in s["homework"]:
        L.append(f"- {h}")
    L.append("\n## 评分点\n" + s["score"])
    L.append("\n---\n*证据纪律:所有'完成'必须附命令输出/截图;如实记录失败与返工(诚实=加分)。*")
    return "\n".join(L)

# ---------- 教学设计方案 md ----------
def lesson_plan(s):
    L = [f"# 教学设计方案 {s['num']}:{s['title']}\n",
         f"> 学习领域 {s['lf']} | 第 {s['week']} 周 | 授课教师版 | 180 分钟\n",
         "## 1. 教学目标(布鲁姆分层)\n"]
    for lv, t in s["bloom"]:
        L.append(f"- [{lv}] {t}")
    L.append("\n## 2. 教学重难点\n"
             f"- 重点:{s['bloom'][-1][1]}\n"
             f"- 难点:{s['bloom'][-2][1]}\n"
             "- 突破策略:情境导入(真实事故/需求)→知识建构精讲→真仓实训→检查互证→费曼外化\n")
    L.append("## 3. 教学准备\n"
             "- 教学集群可用性预检(教师课前 30min);任务单打印/电子发牌;\n"
             "- 情境素材核对:以 PLPP 最新 PROGRESS 阶段刷新本课情境(同步脚本拉取 project-references/)。\n")
    L.append("## 4. 180 分钟流程\n"
             "| 环节 | 时长 | 教师动作 | 学生活动 | 观测点 |\n|---|---|---|---|---|\n"
             "| A 情境导入 | 20' | 讲情境、发任务单 | 领会工单、明确目标 | 能复述本课目标 |\n"
             "| B 计划 | 10' | 巡视,不代拆 | 组内拆解分工 | 计划可执行 |\n"
             "| C 决策 | 5' | 把关安全红线 | 30 秒方案陈述 | 红线重申到位 |\n"
             "| D 理论精讲 | 35' | 按'知识建构要点'爬梯,层层提问 | 答+记笔记+追问 | 每层有应答 |\n"
             "| E 实施 | 70' | 双师巡回,只提问不代写 | 真仓实操、记工单 | 步骤推进与证据留存 |\n"
             "| F 检查 | 15' | 抽查 | 检查员勾验+互查 | 清单全过 |\n"
             "| G 评价+费曼 | 25' | 评分点回收;费曼只提问 | 费曼员上台 | 外行能懂 |\n")
    L.append("## 5. 理论精讲提纲(35min)\n")
    for i, (t, pts) in enumerate(s["knowledge"], 1):
        L.append(f"### {i}) {t}")
        for p in pts:
            L.append(f"- {p}")
    L.append("\n## 6. 实训指导(70min)\n")
    for i, (st, d) in enumerate(s["lab"], 1):
        L.append(f"{i}. **{st}**:{d}")
    L.append("\n## 7. 布鲁姆提问设计(课堂穿插)\n")
    qmap = {"记": "请说出…", "解": "为什么…而不是…?", "应": "现场演示…", "析": "如果…坏了,断在哪一跳?", "评": "你判断这是…的依据?", "创": "给它补一个…会怎样?"}
    for lv, t in s["bloom"]:
        L.append(f"- [{lv}] {qmap.get(lv,'…')}({t[:24]}…)")
    L.append(f"\n## 8. 费曼讲题与引导\n讲题:{s['feynman']}\n"
             "追问链:还有吗?→换个说法?→如果外行问…你怎么答?→一句话压缩?\n")
    L.append("## 9. 评价与作业\n评分点:" + s["score"] + "\n作业:\n")
    for h in s["homework"]:
        L.append(f"- {h}")
    L.append("\n## 10. 板书设计\n"
             "左板:本课目标(三层) | 中板:核心流程图(随精讲生长) | 右板:实训进度墙(各组勾验状态)\n")
    return "\n".join(L)

# ---------- PPTX ----------
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

BRAND = RGBColor(0x1F, 0x3B, 0x73); ACCENT = RGBColor(0xE8, 0x71, 0x22)

def add_title_slide(prs, s):
    sl = prs.slides.add_slide(prs.slide_layouts[0])
    sl.shapes.title.text = f"{s['num']} {s['title']}"
    sl.placeholders[1].text = ("《千人千面 AI 学习平台项目实战》双元制项目课程 | "
                               f"{s['lf']} | 第 {s['week']} 周 | 4 课时")

def add_bullets(prs, title, bullets, sub=None):
    sl = prs.slides.add_slide(prs.slide_layouts[1])
    sl.shapes.title.text = title
    tf = sl.placeholders[1].text_frame; tf.clear()
    first = True
    for b in bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = b; p.font.size = Pt(16)
    if sub:
        p = tf.add_paragraph(); p.text = sub; p.font.size = Pt(12); p.font.italic = True

def build_ppt(s, out):
    prs = Presentation()
    add_title_slide(prs, s)
    add_bullets(prs, "布鲁姆目标(今天你要达到)", [f"[{lv}] {t}" for lv, t in s["bloom"]],
                "评判标准:下课时你能做到,并讲给别人听")
    add_bullets(prs, "情境导入(真实工程)", [s["scene"][:220] + ("…" if len(s["scene"]) > 220 else "")])
    add_bullets(prs, "上节回顾", [s["review"]])
    add_bullets(prs, "六步法节律(180min)", ["A 情境导入 20' → B 计划 10' → C 决策 5'",
        "D 理论精讲 35' → E 实训实施 70'", "F 检查 15' → G 评价+费曼讲台 25'"])
    for t, pts in s["knowledge"]:
        add_bullets(prs, "知识建构 · " + t, pts)
    add_bullets(prs, "实训任务(70min,双师巡回)", [f"{i}. {st} — {d[:110]}" for i, (st, d) in enumerate(s["lab"], 1)],
                "纪律:只提问不代写;证据必须留存")
    add_bullets(prs, "检查清单(15min 互查)", [f"[{lv}] {c}" for lv, c in s["check"]])
    add_bullets(prs, "费曼讲台(15min)", ["讲题:" + s["feynman"], "白纸讲授 6' → 追问 4' → 类比压缩 3'",
        "讲不清=没学会;卡壳处就是回炉点"])
    add_bullets(prs, "课后作业", s["homework"] + ["评分点:" + s["score"]])
    prs.save(out)

def main():
    d1 = os.path.join(ROOT, "03-学习任务单"); d2 = os.path.join(ROOT, "02-教学设计方案"); d3 = os.path.join(ROOT, "04-课件PPT")
    for d in (d1, d2, d3): os.makedirs(d, exist_ok=True)
    for s in S:
        open(os.path.join(d1, f"{s['num']}-学习任务单.md"), "w", encoding="utf-8").write(task_sheet(s))
        open(os.path.join(d2, f"{s['num']}-教学设计方案.md"), "w", encoding="utf-8").write(lesson_plan(s))
        build_ppt(s, os.path.join(d3, f"{s['num']}-{s['title']}.pptx"))
        print(s["num"], "ok")
    print("ALL", len(S), "sessions rendered")

if __name__ == "__main__":
    main()
