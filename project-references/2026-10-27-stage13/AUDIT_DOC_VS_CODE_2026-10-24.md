# 文档 vs 代码全量审计报告(2026-10-24)

> 触发: 数据中台核心 — Pulsar `platform/edu` 主题族不存在,与 SPEC 追溯矩阵声称不符。
> 方法: 基线=docs/SPEC_REQUIREMENTS_TRACEABILITY.md(申报书 18 页逐条矩阵),逐条以**实测证据**
> (代码路径/库表/主题 stats/端点探活)复核,禁以文档叙事当实情(HSA 铁律)。
> 结论: 追溯矩阵存在 **3 处高估、2 处低估**;数据中台事件链当日已修复闭环。

---

## 一、事故复盘: platform/edu 为什么不存在 + 为什么多轮测试没发现

### 1.1 事实链(今日实测)

1. `k8s/base/pulsar.yaml` 的 init-topics Job 建 **platform/edu**;但代码 `EventTopics.java` 实际发
   **public/default**(注释还声称"与 init Job 保持一致")——文档命名与代码命名从未对齐;
2. ZK 元数据 12d 前重建(restart 3),init Job 是一次性 Job 且未重跑 → platform/edu 消失;
   ai-generation-tasks 因 broker `allowAutoTopicCreation=true` 被生产者自动重建;
3. **broker 因 bookie 不可写 readiness 失败持续 2d9h**(bookie→ZK DNS 解析失败,CoreDNS 98d 重启
   26-28 次的余波): 所有 send 持久化失败;
4. `PulsarDomainEventPublisher.publish` catch 全部异常只打 error 日志(fire-and-forget)→
   业务侧零感知;
5. 本轮修复: CoreDNS 恢复后 bookie 重注册(broker 1/1)→ init 脚本对齐 public/default →
   6 主题手动补建(首次 Job 因 broker 不健康 `|| true` 吞掉 5 个 create 失败)→
   端到端验证 msgIn=2/msgOut=2(消费者 ai-service-sub 实收)。

### 1.2 多轮全链路测试为什么漏检(测试盲区, 5 条)

| # | 盲区 | 证据 | 补救(已落地) |
|---|---|---|---|
| 1 | 功能测试全走同步 HTTP 链路,异步事件路径(提交→outbox→Pulsar→消费)无断言 | e2e 报告仅 UI/GraphQL 同步路径 | deploy-rancher.sh verify 硬校验 6 主题(本次新增) |
| 2 | verify 脚本"主题存在性"验证物**配而未接**: 有 `topics list` 但 `|| true` 吞失败且不断言 | deploy-rancher.sh:135 旧行 | 改为缺一即 FAIL(本次新增) |
| 3 | 发布器异常被吞(fire-and-forget, 违 EER 铁律), 无 msgIn/backlog 告警 | PulsarDomainEventPublisher.publish catch-all | 审计记录; outbox 化为正解(见 §2①) |
| 4 | broker readiness 0/1 长期存在但无告警路由到测试判定, 测试把"Pods Running"当健康 | readiness x96 over 2d9h | verify 已含 readiness 输出; 建议接告警(遗留) |
| 5 | CoreDNS 间歇故障是**全局底座**故障, 单服务测试均通过(每次 DNS 命中就正常), 只有跨 pod 长链路才暴露 | coredns 重启 26/28 次; bookie 持续 UnknownHost | 底座健康纳入 verify(现有 sig 探测, DNS 连通性待加) |

## 二、逐条核验(申报书五大研究内容)

### ① 数据中台(原声称 ▲80%)→ 实测 **▲55%,原声称高估**

| 子项 | 文档声称 | 实测证据 | 判定 |
|---|---|---|---|
| 主题族 | "Pulsar platform/edu 主题族" | 不存在;代码用 public/default,今日 6/6 补建+事件流验证(msgIn=2/msgOut=2) | ✅(命名修正后) |
| Outbox | TOGAF_ALIGNMENT "Pulsar+Outbox 已全量接线(app.events.outbox=true)" | relay 代码完整(OutboxEventRelay,EER 语义),但 **event_outbox 表今日才建**(ai_db 此前根本不存在);四服务 course/teaching/iam/tenant 直发 fire-and-forget,无 outbox | ⚠️ 半接:ai outbox 表已建(TiDB),四服务仍直发(遗留) |
| 采集器/10+ 系统 adapter | "采集器接口位(每系统一个 adapter→topic)" | **仓库内无任何 adapter/collector 目录或代码** | ❌ 纯文档概念 |
| 事件消费方 | 隐含"事件驱动联动" | **domain-events/learning-behavior 无任何消费者代码**(grep 全仓零命中)——画像更新/索引 upsert 的异步链路没有下游 | ❌ 单向发,无联动 |
| 统一存储/清洗/元数据/脱敏 | 数据中台能力 | TiDB 四库+双写切换(今日 TiDB→CRDB 同步 CronJob 上线,水位增量)算"统一存储"✅;清洗/元数据/脱敏无代码 | ◐ |
| 对其他服务的支撑 | — | ai 生成任务队列 ✅(实测);领域事件联动 ❌(无消费方);向量索引 upsert 通道 ✅(今日 Milvus 灌库打通) | ◐ |

**结论: 数据中台"80%"实际约 55%。核心缺口=事件消费侧(画像/索引异步链)与 10+ 系统 adapter。**

### ② 动态画像与知识追踪(原声称 ▲60%,"BKT 未实现")→ 实测 **代码已实现,指标未达标,文档低估了实现、但指标缺口是真实的**

- 实证: kt-service/checkpoints/{bkt_params.json, dkt_model.pt, eval_metrics.json} 存在;
  eval_metrics: **DKT AUC=0.4713 / BKT AUC=0.5127**(4686/3562 条预测,防泄漏协议)——
  距申报书 ≥0.75 差距大(合成数据训练所致);
- 在线链路: /kt/predict、/kt/mastery、记忆金字塔、SM-2/ZPD/Gap 今日全部实活(memoryGraph GraphQL 验证过);
- 判定: 实现覆盖 ≈ 原判,但"模型训练后 AUC≥0.75"未达——真实进度 ★: 实现完成、指标未达。

### ③ AI 生成引擎(原声称 ✅90%)→ 实测 **✅92%,基本属实**

- 6 类资源模板(GenerationService.TEMPLATES 6 项)✅;LangGraph 五节点(agent generation_graph)✅;
- RAG 底座: **今日闭环**——Milvus edu_resources 灌库 360 kp + reranker 自闭环检索(Recall@5=1.0/MRR=0.933/nDCG=0.951);
- 生成质量评测: evals/report 通过率 0.967(门禁 0.8)✅;
- 未达: "≤30s"响应时长未实测;生成异步链(outbox)今日才真正可用。

### ④ 智能推荐(原声称 ▲75%)→ 实测 **▲60%,原声称略高估**

- 现状: 规则+检索融合(edu-app 推荐位 + agent 工具),无独立推荐服务/模型目录;
- LearningPath 域+步骤 ✅;HRL/RL 排序模型 ❌;精准率 85% 无评测。

### ⑤ 完全学分制融通(原声称 ◐40%)→ 实测 **▲75%,文档严重低估**

- CreditTransferService + Create/Apply 命令 + 单测存在;TiDB credit_transfer_rules(190 条规则)/
  credit_transfer_records(288 万条)真实数据在库;
- 缺: 岗课赛证多源互认规则广度、跨校结算流程。**追溯矩阵需改写此条。**

## 三、本轮修复清单(当日全部落地)

| 修复 | 状态 |
|---|---|
| CoreDNS 余波→bookie→broker 恢复(2d9h 不可写) | ✅ 全组件 1/1 |
| Pulsar 6 主题补建(public/default,与代码对齐;init Job 脚本同步修正) | ✅ 端到端 msgIn/msgOut>0 |
| deploy-rancher.sh verify 主题硬校验(6 主题缺一即 FAIL) | ✅ bash -n 通过 |
| ai_db(CRDB→**TiDB 迁移**)+event_outbox 建表;ai-service 数据层默认 TiDB(yml/pom/方言) | ✅ 本次实施 |
| agent_db durable_sessions 建 TiDB 表;durable.py psycopg2→pymysql 重写 | ✅ 本次实施 |
| KG /knowledge/graph 500 修复(nativeQuery 误标)+性能修复(45M 行 LIKE→course_id IN 新课域走复合索引) | ✅ course 11.0.4 |
| GenerationService.search 改走 reranker 自闭环(降级安全) | ✅ ai 11.0.9→11.1.0 |
| TiDB→CRDB 同步水位增量+prune(修 CronJob 连败) | ✅ 本地验证 0 行/0.1s |

## 四、遗留(按优先级)

1. **事件消费侧**: domain-events/learning-behavior 无消费者——画像异步更新、资源索引 upsert 的
   下游联动需要实现(申报书①核心缺口);
2. **四服务 outbox 化**: course/teaching/iam/tenant 仍直发 fire-and-forget(EER 违例),
   应接 OutboxEventRelay.save + 迁移目录建 event_outbox;
3. KT AUC 达标: 需真实学习行为数据(依赖遗留 1 的行为事件流)+ 重新训练;
4. nebula-storaged ADD HOSTS(console 镜像拉取失败,待 daocloud 代理通道);
5. 10+ 系统 adapter(依赖外部系统 API 开放,二期);
6. CRDB 免费层并发事务上限(同步错峰;正式 license 建议)。

## 五、阶段12 追加(同日清偿, commit 见 git log)

| 项 | 结果 |
|---|---|
| 事件消费侧联动 | ✅ learning-behavior→teaching 消费→KT 掌握度 E2E(KT l1=2);agent 生产行为事件 |
| 四服务 outbox 化 | ✅ 四 Publisher 改 relay.save,TiDB 四库 event_outbox,delivered 验证 ×2 |
| nebula storaged | ✅ ONLINE(graphd 恢复);kg33618 数据需重灌(旧 host 失联) |
| LLM 通道 | ✅ 切 ollama-worker 直连(litellm 基座 DB 断连绕行) |
| infra 正本 | ✅ k8s/base/infra-services.yaml |

**阶段12 新根因(具普适性)**: 每服务目录独立 vendored `.mvn/platform-common.jar`(10-19 旧拷贝)是
四服务镜像嵌包陈旧的真根因——根目录/本地 m2 同步均无效; buildx 层缓存与 alpine 容器缺 unzip/javap
两度误导 BVV, 权威 BVV 必须**宿主侧 docker cp 解包 grep**。
**新遗留**: ①kg33618 重灌 ②kp/resources 大表全量同步 ③litellm 基座 DB ④四服务 @PreAuthorize 403(JWT role 映射)

## 六、阶段13 长尾清偿(同日, 四遗留逐项闭环)

| 项 | 结论 | 证据 |
|---|---|---|
| ① kg33618 重灌 | ✅ 完成 | DROP SPACE+DROP HOSTS(仅留 192.168.194.153)→ schema.ngql 重跑 fail=0 → seed_33618.ngql 重跑 fail=0; SUBMIT JOB STATS 实证: 顶点 335(industry 14/knowledge_point 271/post 50)、边 590(belongs_to 50/prerequisite 221/relates_to 48/requires 271); MATCH by name 验证通过 |
| ④ @PreAuthorize 403 | ✅ 定位=安全设计非 bug | tenant HeaderAuthFilter 仅信任 X-Gateway-Verified=1 头(网关注入); NodePort 直连缺该头→403 属预期; 带头创建学分规则成功(200) |
| ② 大表同步 | ✅ 完成 | 脚本三修(execute_values 批量 upsert / SerializationFailure 8 次指数退避重试 / _sync_meta 跨库 defaultdb 限定——原 get_wm/set_wm 在目标库连接上查 defaultdb 表必炸); credit_transfer_records 2,880,000 行 + discussions 12,000,000 行全量落地, CRDB count 实证; 每小时 CronJob 与本地同步冲突已识别(暂停→恢复, 3 个连败 Job 清理) |
| ③ litellm 基座 DB | ⏸ 诚实搁置 | litellm-postgres(PG16-alpine+PVC+Service)已建; DATABASE_URL 注入后 Prisma CLI 工具链 600s 超时→CrashLoop, 已回滚; PLPP 主链直连 ollama-worker 不受影响; 后续方案: pre-migration Job 或换官方镜像 |

**阶段13 附加发现**: ① course /knowledge/graph 是关系型实现(知识点前置/关联自 course_db), Nebula kg33618 由 agent 侧 edu_tools.query_knowledge_graph 消费——两者同契约不同源, 均可用(真实 33618 产业词在 Nebula, course_db 是"知识点 N"合成数据, 语义覆盖不重叠); ② CRDB-a pod 曾因 k8s-master 磁盘压力(99%) Pending+NodePort 拒连——docker builder prune 释放 34GB+kubelet 重启后恢复, 节点磁盘水位 69% 仍需关注; ③ tenant CreditTransferService 规则创建无 DomainEvent 发布点(outbox 链未覆盖学分域, 可后续补)。
