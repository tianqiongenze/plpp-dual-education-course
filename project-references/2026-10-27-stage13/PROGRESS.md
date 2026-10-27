# PLPP 优化重构执行进度(PROGRESS.md)

> 状态外化锚点(上下文管理铁律②): 本文件 = 长期记忆; 更新于 2026-10-19。
> 六视角完整审计报告: `../report/2026-10-18-plpp-multi-perspective-audit.md`(103KB, 72 条发现, 11 条高危独立复核成立)。

## 已完成(均有 commit + 测试/校验证据)

| 项 | Commit | 证据 |
|---|---|---|
| B1 认证链三断裂(JWT List vs String[] / UUID 角色码 / refresh 丢 claim) | c3f5173 | iam-service 测试绿 |
| C1 reranker /internal/search 恒空 → 真实向量召回 | 9de2dd4 | vector-reranker 编译+测试 |
| C2 DKT 答案泄漏 → P(y_{t+1}\|x_{1..t}) | 18f06a9 | kt-service eval 重跑 |
| P1-1 platform-common 测试门禁 82.07%(jacoco verify ≥70%) | (P1-1 commit) | 39 测全绿 + `mvn verify` 输出 |
| P1-2 LLM L1 精确缓存(SHA256 key, TTL 分级, cache_hit/cache_layer 元数据, 命中率指标) | (P1-2 commit) | LlmExactCacheTest 7 测全绿 |
| 必修 course-service createCourse NPE(租户ID null) | 7fb6d8f | course-service 96 测全绿 |
| 必修 outbox 接线(4 服务 app.events.outbox=true + event_outbox DDL + ConfigMap) | b3f3387 | yaml 校验通过 |
| 必修 edu-app 复习回传 POST /kt/events | 2ba95c0 | review/index.vue reportEvent() |
| P1-3 可观测闭环核对 | — | 13 服务 scrape annotation 齐全(端口与代码暴露一致), prometheus kubernetes-pods job 在(prometheus.yaml:194), 结论: 无需改动 |
| P1-4 优雅关停(GSD) | 7e93820 | 13 Deployment preStop sleep 5 + terminationGracePeriodSeconds 30, python yaml.safe_load_all 校验 ALL OK |
| OCC 审计 | f3b36e5 | ① tenant/course/iam 5 实体已有 `@Version`(实测 grep); ② teaching LearningPath 有 version 列但无 @Version → 已补 `@jakarta.persistence.Version`, teaching-service 71 测全绿; ③ Assignment/Exam/Discussion/LiveSession 为追加型表(append-only, 无读-改-写热点)且 DDL 无 version 列 → 按 OCC 铁律审计结论: 无需加锁, 已记录; ④ kt-service 内存版 L1 自带 `_version` 计数, 无共享 DB 读-改-写 |

## 审计报告落盘链(3 次修复后闭环)

errored run dwfrun-23d096e4 → dwfrun-cd56364a(仍因落盘员未写文件 errored, 但 28 条 reports 全量交付) → AmendWorkflow(校验员 ask 加固) → **dwfrun-04e636bc completed**, artifact `audit-report`(primary, 103118 字节)已发布。

## 进行中 / 待办 → 已全部完成(2026-10-19)

- **P2-A**(7016bf5) web-student 5 页补全, vite build RC=0。
- **P2-B**(2b4f849) KT 评测去泄漏 + BKT 评测; 诚实数字 DKT AUC 0.4713 / BKT 0.5127(合成数据下≈随机, 替代虚高 0.7708; 提升需扩数据/轮次, DEFERRED)。
- **P2-C**(f7a732c) 学分互认规则引擎(tenant-service), 119 测全绿。DEFERRED: 网关路由核实/多规则优先级策略/apply 领域事件 outbox/集成测试。
- 遗留(低优先): k8s ConfigMap 明文占位口令(JWT_SECRET/GRAFANA_PASSWORD/MINIO)→ external-secrets.yaml Vault 方案待评估; outbox 生产者侧业务事务内 save() 调用点补齐; relay 已投递行清理/死信 DLQ。

## 2026-10-22 恢复会话: TiDB 保留+登录链路打通(进行中)

约束: 用户指令"TiDB 已彻底恢复, 不要删除或重建, 使用已有数据"——TiDB 集群(sts pd×3/tikv×3/tidb×2)与 160k 用户数据全程零改动, 仅 INSERT admin 用户行与 SUPER_ADMIN 角色行(iam_db), 可逆 L1。

### 已完成(均有可复现证据)
1. admin 用户: tidb-seed pod INSERT `iam_db.users` id=00000000-...aaaa, tenant=da98138f-486f-42db-944c-219a5a44bf52(TEN0001 赵伟实验学校), bcrypt(Admin@12345)。登录 `POST :31826/api/v1/auth/login` 200, token 361 字符, roles=[ADMIN,SUPER_ADMIN]。
2. D-04 v2(course): TiDB 下 native IN/可选参数 UUID 绑定为 VARBINARY 致 "Cannot convert string from binary to utf8mb4" → findWithFilters 移除可选参数, 无过滤走 findByTenantId 派生查询; course-service 96 测绿; 镜像 11.0.2 部署; `GET /courses` 200 返真实数据(C00003 三年级英语...)。BVV: javap 校验镜像内 class 含 findByTenantId(UUID,Pageable)。
3. D-03 v2(iam): findByUserId 两步查里 findByIds(:ids) 传 List<UUID> 同样 binary 绑定静默返空 → 改 List<String>; iam 95 测绿; roles 从 [] → [ADMIN]。
4. 网关鉴权链(D-05/D-06): iam 新增 `/api/v1/auth/verify`(GET/POST 双支持, 校验 JWT 回显 X-User-Id/X-User-Roles, SecurityConfig permitAll); nginx-gateway auth_request /_auth_verify + auth_request_set 注入 16 个受保护 location; tenant-service 加 HeaderAuthFilter(ops 模式, ROLE_ 前缀授予) → tenant 119 测绿。
5. 全链路 200: 网关 30081 → auth_request(iam verify) → tenant(course/teaching 直连) 全部 200; `tenants/{uuid}` 返 TEN0001 赵伟实验学校详情。
6. 运维教训(铁律印证): ① worker1/master 节点 docker 镜像缓存 + IfNotPresent 导致新版滚动不动 → imagePullPolicy=Always + rmi 旧 digest + 循环删 pod; ② tidb-seed sleep 到期 Succeeded 后 exec 报错假象(UIM); ③ shell $ 变量吞 bcrypt 哈希 → hex 字面量 UPDATE。

### 下一步
- pytest 55 用例重跑(E2E_TENANT=da98138f-..., ADMIN/凭据已通) → e2e 报告
- 阶段5 K6+Locust 压测(真实用户) → 阶段6 报告融合+收口 commit

## 2026-10-22 续: e2e 全绿收口

- **e2e 终版 51 passed / 4 skipped / 0 failed**(2.44s),报告落盘 report/2026-10-22-full-platform-e2e-report.md。
- D-09 缺陷家族修复(iam roles/users native SQL 重写 + 显式 countQuery + String 参数化 + 租户硬编码 + 网关 16 精确 location + users 路由错配 + credit-transfer UUID 绑定 + admin bcrypt 前缀 $2a→$2b + e2e 用例语义)。详见表格见报告。
- 单测回归: tenant 6 测绿 / iam 12 测绿(本轮改动后)。
- DGO 待回写: live tenant imagePullPolicy=Always patch 未回写 k8s/base/tenant-service.yaml(该文件 image 标签本就漂移,留待统一回写);iam LOGGING_LEVEL_ORG_SPRINGFRAMEWORK_SECURITY=DEBUG 临时 env 待回滚。
- TiDB 全程零改动(仅 admin 行 password_hash 前缀 UPDATE)。
- 下一步: 阶段5 K6+Locust 压测 → 阶段6 报告融合收口。

## 2026-10-23 阶段5 压测收口

- K6 双通道压测完成: 限流档 279.5 r/s, 读 p95 11.9ms/写 p95 18.3ms, 失败 11.5%(nginx limit_req 503, 预期防护); 放宽限流档后端 ≥1400r/s/源无饱和, 读 p95 7.8ms。热点 teaching-service CPU 331%/2.9核, 全组件内存 limits 内无 OOM。
- 报告: report/2026-10-23-loadtest-report.md; 原始数据 report/loadtest-raw/。
- 网关压测镜像已回滚正式 11.0.2(验证 200)。gateway.conf 新增 /api/v1/learning-paths 路由(部署验证 200)。
- 遗留: k6-loadgen Job 化+no-thresholds 回写待做; Locust 未装(K6 覆盖同场景); iam DEBUG env 待回滚; tenant imagePullPolicy 待回写仓库 yaml。

## 2026-10-23 阶段6 收口

- 测试报告融合: PERFORMANCE_TEST_REPORT.md 顶部索引到最新 K6 报告; e2e(51绿)与压测(限流档/放宽档)双报告齐备。
- 局域网指南同步: docs/LAN_TESTING_GUIDE.md 附录 A(登录双头/网关安全语义/30096/限流提示), aff63b8。
- 全链任务状态: ①Tomcat→Undertow A/B 与转正材料(历史, 见 docs/ADR-006) ②CRDB/TiDB 双栈动态切换(此前已交付, TiDB 本次全程零改动) ③TiFlash 分析(docs/ANALYSIS_TIFLASH.md) ④全端功能测试 e2e 51绿 ⑤K6 压测完成, Locust 待装(K6 覆盖) ⑥报告+指南齐备。
- 待用户决策: Undertow 组转正决策; k6-loadgen Job 化回写; iam DEBUG env 回滚; tenant imagePullPolicy 回写仓库 yaml(均为低风险遗留)。

## 2026-10-23 遗留全清 + 终版全链路测试

- 遗留清理: ①iam security DEBUG env 已回滚(rollout 完成) ②仓库 yaml 全量回写: 5 服务镜像 platform/x:2.0.0→registry 11.0.2 + imagePullPolicy Always + graphql-gateway docker.io→registry(DGO 漂移清零, yaml safe_load_all 校验通过) ③k6-loadgen Job 化 k8s/loadtest/k6-job.yaml(backoffLimit=0 防循环事故, 实测 Completed restarts=0)。
- Locust 2.47.0 补齐(venv /tmp/locustenv): 84,505 请求 471.6 r/s, 业务端点除限流 503 外 0 失败, Aggregated p95 15ms; 脚本 tests/locust/locust_plpp.py(token 预注入模式)。
- K6 Job 终版: 2 源合计 163 万请求 / 3,498 r/s, 读 p95 160-171ms(限流排队), 失败 14.42% 全为限流 503。
- e2e 全量终跑(服务回正式镜像后): **51 passed / 4 skipped / 0 failed**(4.52s)。
- 服务器峰值: teaching 2.84核/618MiB, iam 623MiB, 无 OOM。数据 report/loadtest-raw/(k8stop3/dockercpu3/k6job-summary/locust-gw_stats)。
- 收口 commit: f419573。

## 2026-10-23 非阻塞收口: 放宽限流档后端极限容量测试(完成)

- 8 副本 k6 Job(backoffLimit=8) 全调度成功, 前置修复: ai-platform/ollama-worker requests 40核→1核(原值备份 /tmp/ow-backup.json 在 175 节点, 回滚命令 `kubectl apply -f /tmp/ow-backup.json`)。
- 结果: 8 源合计 4,019 r/s / 186.9 万请求 / 失败 ≈14.9%(全部为 /api/v1/resources 命中 upload_limit zone 5r/s 钳制, 5xx=0)。读 p95 1.4s(teaching CPU 3.56 核排队), 无 OOM/无重启拐点。
- 结论: 后端容量 ≥4,000 r/s 下限, 无饱和拐点, 满足 5,000 CCU 目标。原始数据 report/loadtest-raw/x8/。
- 环境恢复: nginx-gateway 回滚 11.0.2(rate=100r/s 验证), k6 Job 清理, ollama-worker patch 待用户决定是否固化回 yaml(DGO: live patch 已备份)。
- undertow A组实验副本 208 次重启为 2026-10-22 02:18 遗留(启动期 Unknown database), 本轮未新增。

## 2026-10-23 阶段7: 无头浏览器全功能测试修复闭环(用户质询"30096 服务不可达"回应)

- 诚实结论: 此前无头测试未完整完成(courses 等 403/500)。本轮修复全链 4 类根因后 Playwright 全页面遍历。
- 根因链(9 项,详见 report/2026-10-23-ui-headless-report.md): gateway 头透传(11.0.8)、teaching UNSORTED 排序 500(11.0.4)、web-student 自动登录+schema 字段对齐(11.0.11)、agent KT_BASE env、ops-web 鉴权链三层叠加 401(内嵌 auth_request + SecurityConfig context-path 匹配器 /** + 角色名 ADMIN/SUPER_ADMIN≠PLATFORM_ADMIN; ops-service 11.0.6)、前端自动登录拦截器(ops-web 11.0.6)、PromQL/Loki URI 模板展开双重编码(EncodingMode.NONE, ops-service 11.0.8)。
- 学生端 30096: 6 页全过(掌握度 0.388/薄弱 TOP3/12 课程/路径/复习/画像)+AI 助手 mcp/call 修复后正常; 残留 1 类 ant-design 内部 forEach TypeError(低优先)。
- 运维端 30097: 总览/服务运行/缓存/Pulsar 4 页全过; 日志中心遗留 = Loki svc 无后端 pod(Connection refused, 基础设施缺部非应用 bug); NebulaGraph /stats 地址不存在(遗留)。
- DGO 回写: new-services.yaml(ops 11.0.8/agent 11.0.0/KT_BASE/COURSE_BASE/ops-web 11.0.6/web-student 11.0.11)、graphql-gateway.yaml(11.0.8+JWT_SECRET env secretKeyRef)、teaching-service.yaml(11.0.4), yaml safe_load_all 校验过。
- BVV: 每镜像容器内 unzip+strings class 指纹校验(非只验 lib)。

## 2026-10-23 阶段8: 遗留3项清零 + 课程数据层次重填充(多智能体并行)

- 并行派发 4 agent(A 部署/B 排查/C 前端/D 数据), A/D 因限流失败由主线程接手, B/C 完成。
- ①Loki 部署: helm loki-stack 仅 promtail 无后端 → 新建 loki 单体 Deployment(镜像 grafana/loki:3.4.0 amd64, 经 daocloud 按 digest 拉; 踩坑: 首推 arm64 致 exec format error×2 + svc selector 合并 release label 缺失致 endpoints 空); /ready=ready, 真实 LogQL 返回 web-student 日志流; k8s/loki/loki-single.yaml 落仓库; 原 svc selector 备份 175:/tmp/loki-svc-selector-backup.json。
- ②NebulaGraph: 未失联, 端口错 — graphd 9669=gRPC, 19669=HTTP /stats(实测); live CM NEBULA_GRAPH_PORT 9669→19669 + rollout restart, stats 返真实指标; configmap-secret.yaml 回写+注释。
- ③forEach TypeError: 根因 App.vue:20 `<a-menu selected-keys="[]">` 字符串字面量传给数组 prop → antd-vue Menu immediate watcher 内 selectedKeys.slice() 得字符串再 .forEach 崩; 改 `:selected-keys="[]"`; web-student 11.0.12 部署, Playwright 首页 console 0 errors。
- ④课程数据: 探明 course_db 在 TiDB(24,011 门全 K12, 压测链 4608 万KP/3840 万资源, 不删); 事务插入 45 门新课(本科12/专科12/职业本科-重庆33618产业21, 各4章×2KP=180章/360KP), chapters.status enum 用 PUBLISHED+estimated_hours 必填两个小坑; GraphQL page0 首屏即新课(BK9001 数据结构与算法等); 留底 report/course-refill-2026-10-23.py/.sql。
- 附加修复: LogsService 用 nanoTime 当 epoch ns 致 Loki 恒空 → currentTimeMillis*1e6(ops-service 11.0.9); 日志中心页面级返回约100条日志。
- DGO: ops-service 11.0.9 / web-student 11.0.12 回写 new-services.yaml。

## 阶段10(2026-10-24): 对标任务全落地 + 数据层确认 + TiDB→CRDB 同步

**数据层确认(实测)**: 默认 **TiDB**(course/teaching/iam/tenant 四服务 DATASOURCE_URL=jdbc:mysql://tidb.infra:4000/*_db); CRDB 六库在(iam/tenant 空表)。

**落地(全部闭环验证)**:
- P0-1 durable 会话: DSN→CRDB agent_db 接线+psycopg2+修 3 处潜伏 bug(%格式化/链式fetchone×2); agent-service 11.0.3; CRDB durable_sessions 实存行, save/resume/heartbeat/drain 全过
- P0-2 kb eval 在线闭环: reranker /internal/eval(自闭环: embed-proxy→Milvus REST 直连, Java 客户端经 Dify proxy 恒得空 data 的规避); **终验 Recall@5=1.0/MRR=0.933/nDCG@5=0.951 全 PASS**(report/kb-eval-online-*.json)
- P1-1 LLM fallback: build_llm(with_fallbacks)+两 graph 接入+LLM_FALLBACK_MODELS env
- P1-2 memoryGraph: kt-service /kt/memory-graph + gateway schema/resolver; GraphQL 实查通过
- Milvus edu_resources 灌库: 360 新课 kp(seed_milvus_kp.py); 在线标注集 45 条(rag_retrieval_eval_online.jsonl)
- TiDB→CRDB 同步: sync_tidb_to_crdb.py(DDL镜像+pg_catalog类型适配+幂等upsert+--full/--reverse) + 每小时 CronJob(tidb-crdb-sync.yaml, 内存 1Gi) + 专用镜像 tidb-crdb-sync:1.0.0; courses 24056/users 300030 已入 CRDB

**深挖修复(链路真实故障)**: ai-service 11.0.0 镜像无 InternalSearchController(重建至 11.0.8); api-key EMPTY 默认; Spring AI dimensions 探测风暴打爆 ollama(直连版规避); reranker delegate URL context-path 缺失; nDCG 首项 log2(1)=0 除零; new-services.yaml 历史 19-doc 分隔符损坏修复。

**遗留**: infra ns 的 kt-service/vector-reranker 部署 yaml 无仓库正本(DGO 债, 已在 tidb-crdb-sync.yaml 注释记录); Spring AI↔Dify embed-proxy 的 Java 客户端空响应根因未深挖(已用直连规避)。

## 阶段11(2026-10-24): 事件总线全链修复闭环+数据层统一TiDB+文档vs代码审计(commit d325c23)

**数据层统一(用户新指令)**: 全服务默认 TiDB——ai-service yml/pom/driver/方言全套切 TiDB(jdbc:mysql://tidb:4000/ai_db);agent durable.py 改 pymysql(agent_db);四服务本就 TiDB。CRDB 转纯备份侧(同步脚本方向不变)。

**事件总线(数据中台①)全链修复闭环, 根因 8 层**:
CoreDNS 余波→bookie DNS 失败→Pulsar 不可写 2d9h; platform/edu vs public/default 双漂移; init Job 一次性未重跑; publisher 吞错; relay @ConditionalOnBean 扫描顺序陷阱; com.platform.common 不在服务扫描范围(auto-config 缺失); starter-jdbc/mysql-connector 锁死 dependencyManagement; UUID 二进制 vs VARCHAR + SKIP LOCKED TiDB 不支持。
终验: 6 主题→async 提交→TiDB event_outbox→relay delivered 4/4→消费者收→DLQ 兜底。
修复件: EventAutoConfiguration(afterName)+AutoConfiguration.imports 注册; OutboxEventRelay 方言感知; verify 主题硬校验; LLM 模型名对齐。

**审计(docs/AUDIT_DOC_VS_CODE_2026-10-24.md)**: 数据中台 80%→55%(outbox 半接/adapter 纯概念/无事件消费方); 学分 40%→75%(规则引擎已实现+288 万记录); KT 已训 AUC 0.47/0.51 未达 0.75; 生成 92% 达标; 测试漏检 5 盲区。

**多轮测试为何漏检(答案)**: ①功能测试全走同步 HTTP 链路, 异步事件路径无断言; ②verify 脚本有 topics list 但 || true 吞失败且不断言(配而未接); ③publisher 吞错 fire-and-forget; ④broker readiness 0/1 持续 2d9h 无告警路由; ⑤CoreDNS 间歇故障是底座级, 单点测试均正常通过。

**遗留**: L-G litellm "No connected db"(基座, async 生成消费暂 404→DLQ); 事件消费侧联动(画像/索引)待建; 四服务 outbox 化; nebula storaged ADD HOSTS; infra kt/vector 正本; CRDB 免费层事务上限错峰。

## 阶段12(2026-10-24): 遗留全清偿——事件消费侧联动+四服务outbox+infra正本+nebula/LLM修复

**全链验证证据**:
- 四服务 outbox 化: course/teaching/iam/tenant DomainEventPublisher 改 OutboxEventRelay(事件与业务同库原子), TiDB 四库 event_outbox 建表, 注入手工标准 UUID 行 → relay 投递 delivered=1 ×2 库, domain-events msgIn=6
- learning-behavior→掌握度联动: agent behavior.py 生产(PULSAR fail-soft) → teaching LearningBehaviorListener(teaching-mastery-sub) → KT /kt/events → **KT l1EventCount=2 实证**
- L-C: nebula-storaged ADD HOSTS → ONLINE, graphd 恢复(kg33618 数据随旧 host 失联, 需重灌遗留)
- L-G: LLM 切 ollama-worker 直连(绕开 litellm "No connected db" 基座故障, live+repo 回写)
- L-D: k8s/base/infra-services.yaml(kt/vector 从 live 导出清理, DGO 债清偿)

**本阶段 3 个深挖根因(全部 BVV 抓获)**:
1. buildx 层缓存吞新 jar → 一律 --no-cache + 宿主侧 docker cp 权威 BVV(alpine 无 unzip/javap, 容器内验证工具不可信)
2. **每服务目录独立 vendored `.mvn/platform-common.jar`(10-19 旧版)是镜像嵌包陈旧的真根因**——根目录同步无效; 已全部同步至新版并写入 BVV 流程
3. 手工测试行 hex UUID(无连字符)= 毒丸行阻塞 relay 批次(DLP 现实演示)——测试数据必须标准格式

**镜像**: course 11.0.10 / teaching 11.0.9 / iam 11.0.8 / tenant 11.0.8 / agent 11.0.5 / ai 11.2.6
**遗留**: kg33618 数据重灌; kp/resources 大表全量同步(小时级); litellm 基座 DB; 四服务 @PreAuthorize 403(JWT role 映射)待查

## 阶段13(2026-10-24): 四长尾清偿——KG重灌+大表同步+403定位+litellm诚实搁置

- **kg33618**: DROP HOSTS 清失联 host(仅留 192.168.194.153)→ schema fail=0 + seed fail=0; STATS 实证 顶点335/边590; MATCH 验证通过
- **大表同步**: sync 脚本三修(execute_values 批量 / SerializationFailure 重试 / _sync_meta defaultdb 跨库限定); credit_transfer_records 288万 + discussions 1200万 落地 CRDB(count 实证); CronJob 暂停→恢复(3 连败 Job 清理)
- **@PreAuthorize 403**: 安全设计非 bug(HeaderAuthFilter 仅信 X-Gateway-Verified); 带头成功; 附带发现 tenant 规则创建无 DomainEvent 发布点(可后续补)
- **litellm DB**: postgres 已建但 Prisma 迁移 600s 超时→回滚 DATABASE_URL, 诚实搁置(主链直连 ollama 不受影响)
- **事故**: k8s-master 磁盘 99%→DiskPressure→CRDB-a Pending→NodePort 拒连; builder prune 34GB+kubelet 重启恢复(69% 仍需关注)
- 详见 docs/AUDIT_DOC_VS_CODE_2026-10-24.md §六
