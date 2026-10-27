# 学习领域方案汇编(LF1–LF8)

> 德国双元制"学习领域(Lernfeld)"课程模式:每个学习领域=一个职业行动能力域,由若干**学习情境**(=一次 4 课时课)构成。本汇编给出 8 个领域的能力画像、情境序列与资源。课次级细案见 `02-教学设计方案`,学生材料见 `03-学习任务单`。

---

## LF1 项目认知与需求工程(6 课时, S01–S02)

**能力画像**:能以学徒身份进入一个真实企业项目——读懂业务全景、盘点文档与实现的差距、写出可验收的用户故事。

**学习情境**:
- S01 平台全景认知(4):8 服务地图、端到端一次学习旅程(注册→学习→测评→掌握度→路径);
- S02 需求工程与文档对账(2+... 合并第 2 周课):对照申报书/AUDIT 审计报告,复现"3 高估 2 低估"诊断过程。

**关键资源**:PLPP README、PROGRESS.md(阶段 1–13)、docs/AUDIT_DOC_VS_CODE_2026-10-24.md、软件著作权文档。

**出口能力**【析/评】:能独立完成一份"文档 vs 实现"对账表——这是高职学生最稀缺的工程阅读能力。

---

## LF2 微服务架构与平台基座(10 课时, S03–S05)

**能力画像**:能解释微服务拆分依据,能使用平台公共包开发,能跑通认证授权与多租户链路。

**学习情境**:
- S03 网关与信任链(4):nginx-gateway 注入 X-Gateway-Verified 的零信任设计;NodePort 直连 403 复现实验;
- S04 platform-common 公共包(4):共享包 vs 复制,vendored jar 陈旧事故复盘,构建链实操;
- S05 IAM 多租户(2 + 第 5 周课余):JWT 结构(sub/roles/tenant_id 实测值)、登录链路脚本、越权用例。

**关键资源**:nginx-gateway/、iam-service/、platform-common/、k8s/base/(NodePort 表)。

**出口能力**【应/析】:带 G 脚本完成登录→携带租户头→调用受保护接口全链;解释"为什么直连 403 是对的"。

---

## LF3 数据中台与双存储工程(10 课时, S06–S07)

**能力画像**:能操作 TiDB/CRDB 双存储,能实现并解释水位增量同步,能对一次真实事故做根因复盘。

**学习情境**:
- S06 TiDB 分布式认知(4):TiDB/TiKV/PD 三组件、五库(course/teaching/iam/tenant/agent)拓扑、160k 学生数据规模感;
- S07 同步工程与事故复盘(4):sync_tidb_to_crdb.py 三修(execute_values 批量/SerializationFailure 重试/_sync_meta 跨库限定)逐行剖析;288 万+1200 万行实测对齐。

**关键资源**:scripts/sync_tidb_to_crdb.py、TiDB NodePort 30210、CRDB 30257、_sync_meta 水位表。

**出口能力**【析/应】:能说清"单批冒烟通过而 main 路径必炸"的机制;能独立完成一次增量同步并出对账表。

---

## LF4 知识图谱与向量检索(8 课时, S08–S09)

**能力画像**:能用 NebulaGraph 建图灌数,能跑通向量检索-重排与 KB 评测闭环。

**学习情境**:
- S08 KG33618 实战(4):33618 产业图谱语义(space/tag/edge)、schema+seed 灌数、STATS 验证(335 顶点/590 边)、MATCH 查询;
- S09 RAG 与评测(4):Milvus edu_resources 召回、reranker 重排、/internal/eval 指标(Recall 1.0/MRR 0.933/nDCG 0.951 基线)复测。

**关键资源**:kg-loader pod、configmap kg33618-ngql、vector-reranker、ai-service /internal/vector-search。

**出口能力**【应/解】:能解释"关系型图谱端点(course_db)与 Nebula 图谱同契约不同源"的设计,并演示两条链。

---

## LF5 AI 智能体与 LLM 编排(8 课时, S10–S11)

**能力画像**:能搭建与诊断 LLM 服务链,能追踪智能体工具调用与事件联动数据流。

**学习情境**:
- S10 LLM 通道工程(4):litellm 基座(Prisma 迁移超时案例)、ollama 直连切换、fallback 链、三层缓存(LCO)理念;
- S11 智能体工具链(4):edu_tools 四工具(检索/KG/掌握度/路径)、agent→teaching→KT 行为事件联动、fail-soft 生产者。

**关键资源**:agent-service/app/(tools/graphs)、k8s/base/configmap-secret.yaml(LLM_BASE_URL)、KT l1EventCount 实证链。

**出口能力**【析/应】:能从一次"事件没到 KT"的现象出发,逐跳排查 producer→Pulsar→listener→KT 四段。

---

## LF6 智慧教学核心域(8 课时, S12–S13)

**能力画像**:能解释 KT 模型输出并查询接口,能分析 SRS 并发正确性设计。

**学习情境**:
- S12 知识追踪(4):BKT 四参数直觉、KT 掌握度接口、学习行为→掌握度更新的端到端验证;
- S13 学习路径与 SRS(4):SM-2 算法、乐观锁(OCC)version 列与重读重试、lost update 攻防实验(并发脚本)。

**关键资源**:kt-service /kt/mastery、teaching-service SRS/OCC 代码、KT memory-graph。

**出口能力**【析/创】:能写出一个会触发并发覆盖的反例,并给出版本号修复用例——创造层目标。

---

## LF7 事件总线与韧性工程(8 课时, S14–S15)

**能力画像**:能验证 Outbox 闭环,能设计并验证一条降级路径,能读懂可观测面板。

**学习情境**:
- S14 Pulsar+Outbox(4):fire-and-forget 三宗罪(sendAsync/队列满静默丢/失败仅 warn)、transactional outbox 四要素、delivered 4/4 实证;
- S15 韧性与可观测(4):限流/熔断/超时分级/重试退避/舱壁/降级六件套、/metrics scrape 闭环、UIM 误诊案例复盘。

**关键资源**:platform-common OutboxEventRelay/EventAutoConfiguration、Pulsar NodePort 32679、Prometheus targets。

**出口能力**【析/应】:注入一次 Redis 故障,捕获降级行为并与 DPC 契约测试对表。

---

## LF8 测试运维与工程纪律(6 课时, S16)

**能力画像**:能完成一次部署+压测闭环,能按工程铁律做诚实自评与答辩。

**学习情境**:
- S16 终局课(4):K8s 部署演练、K6/Locust 压测(10 万并发基线报告解读)、M4 里程碑验收、费曼答辩、企业工程师终评。

**关键资源**:DEPLOYMENT_OPERATIONS_MANUAL.md、locust/、K6 脚本、PERFORMANCE_TEST_REPORT.md。

**出口能力**【应/评】:交付压测报告+完成答辩;拷问他人架构时使用"四问"(瓶颈/容灾/扩缩容/成本)。

---

## 学习领域与考核映射速查

| LF | 任务单 | 里程碑 | 费曼题源 |
|---|---|---|---|
| LF1 | S01-S02 | M1 | 文档对账 |
| LF2 | S03-S05 | M1 | 403/信任链 |
| LF3 | S06-S07 | M2 | 跨库事故 |
| LF4 | S08-S09 | M3 | 双源图谱 |
| LF5 | S10-S11 | M3 | 事件排查 |
| LF6 | S12-S13 | — | OCC 攻防 |
| LF7 | S14-S15 | — | Outbox/降级 |
| LF8 | S16 | M4 | 压测复核 |
