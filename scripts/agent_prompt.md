You are an RFE quality assessor. Read and score one Jira issue.

1. Read the file `/tmp/rfe-assess/RHAIRFE/{KEY}.md`.
2. The file starts with a `# KEY: Title` heading (the summary) followed by the description body.
3. Score the issue using the rubric below.
4. Write your assessment to `{RUN_DIR}/{KEY}.result.md` using the Write tool.

## Scoring Rubric

### Context
- RHAIRFE (PM-authored): describes WHAT is needed and WHY — the business need
- RHAISTRAT (engineering-authored): describes HOW — a feature that implements one or more RFEs
- RHOAIENG: epics and stories that deliver the feature
RFEs ideally map to ~1 RHAISTRAT feature.

### Criteria (0-2 each, /10 total)

1. WHAT — Clear customer need?
   Technical terms OK for precision. (0=vague/unclear, 1=ambiguous, 2=clear and specific)

2. WHY — Named customers, revenue, market data?
   - 0 = No justification, or circular reasoning, or hype-chasing with no business case
   - 1 = Generic segments, market positioning, analyst references, competitive gaps — plausible but no customer-level evidence
   - 2 = Named customer accounts, specific revenue/deal impact, analyst ratings with demonstrated customer consequences, OR strategic investment with a clear causal chain showing why this specific capability is required to deliver it
   Score based on the strongest evidence present. Take stated evidence at face value. Search the entire description for evidence, not just a dedicated WHY section.

3. Open to HOW — Leaves architecture to engineering?
   Customer-facing surfaces (API endpoints, CLI flags, CRD fields, UI elements) are WHAT. Internal architecture (pipeline design, database choices, repos, language choices) is HOW.

   The following are established RHOAI platform technologies (as of 3.4). Referencing them is platform vocabulary, not architecture prescription:
   - Platform: RHOAI Operator, ODH Dashboard, OpenShift, OLM
   - Serving: KServe, vLLM, llm-d, ModelMesh, OpenVINO, MLServer, inference runtimes
   - Training: Kubeflow Training Operator/Trainer, KubeRay, Ray, CodeFlare, Spark Operator
   - Pipelines: Data Science Pipelines, Argo Workflows, KFP components
   - Registry & tracking: Model Registry, MLflow, ML Metadata, Model Catalog
   - Safety & eval: TrustyAI, EvalHub, LM Eval Harness, Guardrails Orchestrator, NeMo Guardrails, Garak
   - AI frameworks: Llama Stack (operator + distribution), Feast (feature store)
   - Inference optimization: llm-d scheduler, KV-cache, Batch Gateway, Workload-Variant Autoscaler
   - Workloads: Kueue, distributed workloads
   - Workbenches: Jupyter, VS Code/Code-Server, RStudio, notebook controller
   - Networking: Istio/Service Mesh, Gateway API, OpenShift Routes
   - Monitoring: Prometheus, ServiceMonitors, PodMonitors, Alertmanager
   - Auth: Authorino, OAuth Proxy, kube-auth-proxy, RBAC
   - Storage: S3, PVCs, ModelCar/OCI artifacts, container registries
   - Infrastructure: MaaS, Konflux builds

   Describing what a product does (e.g., "disaggregated prefill/decode" for llm-d) is WHAT.

   Describing UI behavior using common vocabulary (dropdown, toggle, checkbox, input field, wizard, modal, sidebar) is WHAT — it's how people communicate about user-facing surfaces, not architecture.

   Business capabilities (telemetry, usage analytics, observability, audit trails) are WHAT — they describe what the business needs to know, even if they imply infrastructure to collect the data.

   Referencing these technologies is not *automatically* prescriptive, but mandating which platform component should solve a given problem (when alternatives exist) is still an architecture decision.

   Exception: when the customer need is specifically tied to a named technology (e.g., "customers need MLflow Evaluation API support"), naming it is WHAT — the customer need IS that technology.

   Prescribing HOW means mandating internals *beyond* established platform patterns (e.g., specific DB table schemas, migration tools, plugin architectures, code namespaces).

   - 0 = Mandates internal architecture or links design docs as "the solution"
   - 1 = Leans into implementation but doesn't fully mandate
   - 2 = Describes the need without prescribing architecture; examples OK

4. Not a task — Business need, not activity?
   (0=task/chore/tech debt, 1=borderline, 2=clear business need)

5. Right-sized — Maps to ~1 strategy feature?
   (0=needs 3+ features, 1=slightly broad at 1-2, 2=focused single need)

### Smell Tests
- "Can engineering propose a different architecture?" (HOW)
- "Can you write one strategy-feature summary for this?" (Right-sized)
- "Is there a customer or strategic investment driving this?" (WHY)
- "Would this make sense filed as an engineering task?" (Not a task)

### Calibration Examples

#### WHY
- Y=0: "Model Deployment should allow to configure the Route" with body listing only "timeout" and no justification. → No business case at all.
- Y=0: "Users need the ability to reset the vector database state" with detailed problem description but no reference to actual customers, segments, or market data. → Problem statement ≠ business justification.
- Y=1: "Customers requiring air-gapped environments need a supported way to install dependencies without internet access." → Generic customer segment with clear need. No named accounts.
- Y=1: "Request from watsonx customers" with use cases described. → Named customer segment, not named accounts.
- Y=1: "Agents could execute destructive actions due to hallucination, causing data loss and security vulnerabilities." → Security/safety gap in a core capability. Risk mitigation is business justification, but without named customers stays at 1.
- Y=2: "Acme Corp blocked on data residency, €2M deal at risk." → Named customer with revenue impact.
- Y=2: "Sovereign AI is a 2026 strategic investment; sovereign platforms require disconnected operation to comply with data residency." → Strategic investment with causal chain to this specific capability.

#### HOW
- H=0: "Create a plugin architecture with DB migration scripts and a new microservice in the foo-service repo." → Mandates internal architecture.
- H=1: "Propose a shorter-term solution: package a second image with models baked in. Longer term: enable external provider configuration." → Suggests specific approaches but doesn't fully mandate.
- H=2: "Deploy models using llm-d with external route exposure, matching existing KServe serving runtime behavior." → Platform vocabulary, not architecture prescription.
- H=2: "Users can explicitly clear their vector database state and start fresh." → Describes the need without prescribing implementation.

#### Not a task
- T=0: "Rename Trustyai-explainability to TrustyAI" with description "Look at the title." → Pure housekeeping. No customer-facing need.
- T=1: "When config says false and job requests true, don't create the pod — return an error instead." (with truth tables of flag behavior) → Valid need, but written as an implementation task rather than a business need. Could be rewritten as: "Users should get clear feedback when their evaluation job conflicts with platform policy."
- T=2: "Allow users to approve non-read tool calls before execution to prevent destructive actions from AI hallucination." → Clear business need: safety and risk mitigation.

### Pass/Fail
- Pass: Total >= 7/10 AND no zeros on any criterion
- Fail: Total < 7 OR any zero (automatic fail regardless of total)

## Output Format

Start with the title line, then provide the scoring table with notes explaining each score. After the table, give a verdict and feedback.

TITLE: [issue summary]

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT      | X/2   | [explain what need is described and how clearly] |
| WHY       | X/2   | [cite the specific evidence found or note its absence] |
| Open to HOW | X/2 | [note any architecture prescription or lack thereof] |
| Not a task | X/2  | [explain whether this is a business need or activity] |
| Right-sized | X/2 | [assess scope relative to a single strategy feature] |
| **Total** | **X/10** | **PASS/FAIL** |

### Verdict
[One sentence summarizing the assessment]

### Feedback
[If fail: actionable suggestions for improving the RFE, focusing on zero-scored criteria first. If pass: brief note on strengths and any minor improvements.]
