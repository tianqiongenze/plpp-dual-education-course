# 《千人千面 AI 学习平台项目实战》课程仓库

> 高职高专 AI/大数据专业 · 双元制本土化项目实战课程(64 课时)
> 载体:真实企业级项目 **PLPP 个性化学习平台**(`tianqiongenze/personalized-learning-platform-plus`)
> 方法论:德国双元制六步法 + 费曼学习法 + 布鲁姆认知模型
> 基准:PLPP 阶段 13(2026-10-24)

## 目录结构

```
00-课程总览/    课程标准 · 授课计划(64课时) · 教学方案总纲 · 双元制实施方案 · 考核评价方案
01-学习领域方案/ LF1-LF8 学习领域方案汇编
02-教学设计方案/ S01-S16 每次课 180 分钟教学设计(教师版)
03-学习任务单/   S01-S16 学生任务单(契约式:目标/步骤/检查清单/费曼/评分)
04-课件PPT/      S01-S16 每次课课件(pptx)
05-学生手册/     学徒须知(角色/守则/费曼卡/求助)
06-考核评价/     (见 00-课程总览/05-考核评价方案.md,含费曼答辩细则与题库)
07-项目对接与同步/ PLPP⇄课程仓同步机制
project-references/ PLPP 文档快照(按日期+阶段归档)
tools/           生成器(generate.py)与同步脚本(sync-from-plpp.sh)
word/ pdf/       全部 md 资料的 Word/PDF 版(供直接分发学生)
```

## 授课教师快速上手

1. 课前:跑 `./tools/sync-from-plpp.sh` 拉项目近况 → 复核情境;
2. 发《学习任务单》给学生(打印或 word/ 目录);
3. 按《教学设计方案》180 分钟节律授课;
4. 期末:费曼答辩按《考核评价方案》§3 执行。

## 重新生成/维护

```bash
python tools/generate.py          # 幂等重渲染 48 个课次产物(任务单/教学设计/PPT)
./tools/sync-from-plpp.sh         # 同步 PLPP 最新文档快照
```

## 配套真仓

- 项目仓:`https://github.com/tianqiongenze/personalized-learning-platform-plus`(私有)
- 同步约定:**凡 PLPP 更新,相关课程材料同步更新**(见 07-项目对接与同步)。
