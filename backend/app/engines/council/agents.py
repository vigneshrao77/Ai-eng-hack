import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from app.config import settings
from app.engines.council.schema import (
    CouncilDecision,
    CouncilDebate,
    DissentItem,
    PatternType,
    SpecialistOpinion,
    StrategyType,
)
from app.engines.council.validator import validate_decision

logger = logging.getLogger("modernrx.council.agents")

STRATEGY_EFFORT_PER_KLOC = {
    "Retire": 0.5,
    "Retain": 0.2,
    "Rehost": 1.5,
    "Relocate": 2.0,
    "Replatform": 3.5,
    "Repurchase": 4.0,
    "Refactor": 6.0,
}

GXP_EFFORT_MULTIPLIERS = {
    "HIGH": 1.8,
    "MEDIUM": 1.3,
    "LOW": 1.0,
}


def compute_baseline_effort(
    total_loc: int, gxp_tier: str, strategy: str
) -> Tuple[float, float, float]:
    """
    Computes a 3-point estimate (optimistic, likely, pessimistic) in weeks.
    Based on blueprint §12.5: effort = f(LOC, gxp_tier, strategy)
    """
    kloc = max(0.2, total_loc / 1000.0)
    base_rate = STRATEGY_EFFORT_PER_KLOC.get(strategy, 3.0)
    gxp_mult = GXP_EFFORT_MULTIPLIERS.get(gxp_tier, 1.0)
    likely = round(max(1.0, kloc * base_rate * gxp_mult), 1)
    optimistic = round(max(0.5, likely * 0.75), 1)
    pessimistic = round(likely * 1.45, 1)
    return (optimistic, likely, pessimistic)


class SpecialistAgent:
    def __init__(self, role: str, title: str):
        self.role = role
        self.title = title

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        raise NotImplementedError


class CloudArchitectAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("Cloud Architect", "Staff Cloud Systems Architect")

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        cluster_name = cluster_info.get("name", "Cluster")
        loc = cluster_info.get("total_loc", 500)
        nodes = cluster_info.get("nodes", [])

        if gxp_tier == "HIGH":
            strategy: StrategyType = "Replatform"
            patterns: List[PatternType] = ["StranglerFig", "Containerized", "ManagedDB"]
            target_services = ["AWS ECS / Fargate", "Amazon RDS PostgreSQL", "AWS PrivateLink"]
            rationale = (
                f"For HIGH GxP {cluster_name}, a big-bang rewrite poses immense operational risk. "
                f"We recommend Replatforming with an incremental Strangler Fig facade and containerization, "
                f"migrating persistent storage to managed relational database with automated multi-AZ replication."
            )
            risks = [
                "Maintaining dual-write consistency during Strangler Fig cutover",
                "Network latency over private VPC peering during phased migration",
            ]
        elif gxp_tier == "MEDIUM":
            strategy = "Refactor"
            patterns = ["Containerized", "APIGateway", "EventDriven"]
            target_services = ["AWS App Runner", "Amazon SNS/SQS", "AWS Secrets Manager"]
            rationale = (
                f"Medium-criticality cluster {cluster_name} has high modernization leverage. "
                f"Decompose into loosely coupled microservices exposed via API Gateway, with asynchronous "
                f"event streaming for downstream audit consumers."
            )
            risks = ["Event ordering guarantees across distributed services"]
        else:
            strategy = "Rehost"
            patterns = ["Containerized", "Serverless"]
            target_services = ["AWS Lambda / Fargate", "S3 Storage"]
            rationale = (
                f"Low-criticality cluster {cluster_name} represents an immediate quick-win. "
                f"Containerize or migrate to serverless execution with minimal architectural disruption."
            )
            risks = ["Cold-start latencies on ad-hoc invocations"]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)
        return SpecialistOpinion(
            agent=self.role,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            rationale=rationale,
            risks=risks,
            effort_weeks=effort,
            evidence_node_ids=valid_node_ids[:3] if valid_node_ids else ["SYSTEM"],
        )


class ValidationQAAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("Validation & QA Lead", "CSV & Regulatory Assurance Lead")

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        cluster_name = cluster_info.get("name", "Cluster")
        loc = cluster_info.get("total_loc", 500)
        gaps = cluster_info.get("gaps", [])

        if gxp_tier == "HIGH":
            strategy: StrategyType = "Retain"
            patterns: List[PatternType] = ["StranglerFig"]
            target_services = ["Validated Cloud Host", "WORM Audit Store"]
            rationale = (
                f"High-criticality components in {cluster_name} directly govern electronic signatures, "
                f"audit trails, and batch release decisions. Rewriting or refactoring invalidates existing "
                f"21 CFR Part 11 validation collateral. Retain core logic under a validated API facade with "
                f"exhaustive characterization tests before attempting any migration."
            )
            risks = [
                "Full formal re-validation (IQ/OQ/PQ) required if business logic or calculation code changes",
                "Risk of unrecorded audit gaps during data schema alterations",
            ]
        elif gxp_tier == "MEDIUM":
            strategy = "Replatform"
            patterns = ["Containerized", "ManagedDB"]
            target_services = ["AWS ECS", "Amazon Aurora PostgreSQL"]
            rationale = (
                f"Medium GxP components require CSA (Computer Software Assurance) testing. "
                f"Replatform to managed containers with automated regression verification."
            )
            risks = ["Audit trail continuity during table schema migration"]
        else:
            strategy = "Rehost"
            patterns = ["Containerized"]
            target_services = ["Container Registry", "Fargate"]
            rationale = (
                f"Low-criticality components carry zero Part 11 or Annex 11 regulatory consequence. "
                f"Unscripted exploratory testing and baseline smoke checks are sufficient under FDA CSA guidelines."
            )
            risks = ["Regression on peripheral report templates"]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)
        return SpecialistOpinion(
            agent=self.role,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            rationale=rationale,
            risks=risks,
            effort_weeks=effort,
            evidence_node_ids=valid_node_ids[:3] if valid_node_ids else ["SYSTEM"],
        )


class SecurityOfficerAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("Security Officer", "Pharma Information Security Officer")

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        loc = cluster_info.get("total_loc", 500)
        hardcoded_secrets = cluster_info.get("has_hardcoded_secrets", False)

        strategy: StrategyType = "Replatform"
        patterns: List[PatternType] = ["Containerized", "APIGateway"]
        target_services = ["AWS KMS (HSM-backed)", "AWS IAM Zero Trust", "HashiCorp Vault"]
        rationale = (
            "Enforce strict Zero Trust architecture: eliminate hard-coded database credentials and local "
            "file path mounts. Implement envelope encryption for sensitive patient/batch data at rest, "
            "and enforce mutual TLS (mTLS) for all inter-service communications."
        )
        risks = [
            "Credential leakage if legacy configuration property files are copied directly",
            "Insecure local file shares must be transitioned to encrypted object stores with presigned URLs",
        ]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)
        return SpecialistOpinion(
            agent=self.role,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            rationale=rationale,
            risks=risks,
            effort_weeks=effort,
            evidence_node_ids=valid_node_ids[:2] if valid_node_ids else ["SYSTEM"],
        )


class FinOpsAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("FinOps Analyst", "Cloud Financial Operations Lead")

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        loc = cluster_info.get("total_loc", 500)
        is_dead_code = cluster_info.get("is_dead_code", False)

        if is_dead_code:
            strategy: StrategyType = "Retire"
            patterns: List[PatternType] = []
            target_services = ["Decommissioning Workflow"]
            rationale = "Candidate dead code identified with 0 fan-in. Retire immediately to save maintenance and cloud run costs."
            risks = ["Verify no dynamic reflection invokes these routines prior to deletion"]
        elif gxp_tier == "LOW":
            strategy = "Rehost"
            patterns = ["Containerized", "Serverless"]
            target_services = ["AWS Lambda / ECS Fargate Spot"]
            rationale = "Low complexity enables immediate rehost with minimal engineering spend, delivering immediate 35% run-rate savings."
            risks = ["Budget overruns if auto-scaling limits are not enforced"]
        else:
            strategy = "Replatform"
            patterns = ["ManagedDB", "Containerized"]
            target_services = ["Managed Postgres (RDS)", "Savings Plans"]
            rationale = "Replacing high-cost proprietary database licenses with open-source managed Postgres provides optimal long-term ROI."
            risks = ["Higher initial engineering investment amortized over 24 months"]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)
        return SpecialistOpinion(
            agent=self.role,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            rationale=rationale,
            risks=risks,
            effort_weeks=effort,
            evidence_node_ids=valid_node_ids[:2] if valid_node_ids else ["SYSTEM"],
        )


class RegulatoryAffairsAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("Regulatory Affairs", "Global Regulatory Compliance Director")

    def form_opinion(
        self, cluster_info: Dict[str, Any], valid_node_ids: List[str]
    ) -> SpecialistOpinion:
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        loc = cluster_info.get("total_loc", 500)

        strategy: StrategyType = "Replatform" if gxp_tier != "HIGH" else "Retain"
        patterns: List[PatternType] = ["StranglerFig"]
        target_services = ["GxP-qualified Cloud Region", "NTP Stratum-1 Time Sync", "Cloud Audit Trail"]
        rationale = (
            "EU GMP Annex 11 and FDA 21 CFR Part 11 require validated electronic signatures, "
            "independent time-synchronization (preventing local clock tampering), and full supplier audit "
            "oversight of the cloud vendor's SOC 1 / SOC 2 type II certifications."
        )
        risks = [
            "Data residency compliance across jurisdictional boundaries",
            "Audit trail continuity gap if timestamps deviate from regulated atomic time standard",
        ]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)
        return SpecialistOpinion(
            agent=self.role,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            rationale=rationale,
            risks=risks,
            effort_weeks=effort,
            evidence_node_ids=valid_node_ids[:2] if valid_node_ids else ["SYSTEM"],
        )


class CouncilModeratorAgent:
    def __init__(self):
        self.role = "Moderator (Chair)"

    def conduct_rebuttal(
        self, opinions: List[SpecialistOpinion]
    ) -> List[Dict[str, str]]:
        rebuttals: List[Dict[str, str]] = []
        op_by_agent = {op.agent: op for op in opinions}

        qa = op_by_agent.get("Validation & QA Lead")
        cloud = op_by_agent.get("Cloud Architect")
        sec = op_by_agent.get("Security Officer")
        fin = op_by_agent.get("FinOps Analyst")

        if qa and cloud:
            if qa.strategy in ("Retain", "Replatform") and cloud.strategy == "Refactor":
                rebuttals.append({
                    "from": "Validation & QA Lead",
                    "to": "Cloud Architect",
                    "text": (
                        "A full Refactor introduces unacceptable GxP re-validation risk under Annex 11. "
                        "We counter-propose a Strangler Fig facade with containerized Replatforming "
                        "to isolate regulated write paths while modernizing peripheral read services."
                    ),
                })
                rebuttals.append({
                    "from": "Cloud Architect",
                    "to": "Validation & QA Lead",
                    "text": (
                        "Conceded. Strangler Fig satisfies our decoupling requirements while allowing "
                        "QA to validate each slice sequentially rather than all-at-once."
                    ),
                })

        if sec:
            rebuttals.append({
                "from": "Security Officer",
                "to": "All",
                "text": (
                    "Regardless of migration strategy, secrets in properties files and local filesystem dependencies "
                    "must be remediated with cloud HSM key management and object storage presigned access."
                ),
            })

        return rebuttals

    def synthesize(
        self,
        cluster_info: Dict[str, Any],
        opinions: List[SpecialistOpinion],
        rebuttals: List[Dict[str, str]],
        valid_node_ids: List[str],
        offline_simulated: bool = True,
    ) -> CouncilDecision:
        cluster_id = cluster_info.get("id", "cluster_0")
        gxp_tier = cluster_info.get("gxp_max", "LOW")
        loc = cluster_info.get("total_loc", 500)

        # Collect dissent
        dissent: List[DissentItem] = []
        qa_op = next((o for o in opinions if o.agent == "Validation & QA Lead"), None)
        cloud_op = next((o for o in opinions if o.agent == "Cloud Architect"), None)

        if gxp_tier == "HIGH":
            strategy: StrategyType = "Replatform"
            patterns: List[PatternType] = ["StranglerFig", "Containerized", "ManagedDB"]
            target_services = ["AWS ECS Fargate", "Amazon RDS PostgreSQL", "AWS Secrets Manager", "AWS KMS"]
            confidence = 0.88
            rationale = (
                f"AI Council Consensus for HIGH-tier cluster ({cluster_id}): Adopt Replatforming via Strangler Fig. "
                f"Retaining core business logic within containerized micro-services preserves established "
                f"Part 11 verification baselines while eliminating legacy host OS and local filesystem risks. "
                f"QA concerns are addressed via comprehensive characterization test harnesses."
            )
            risks = [
                "Dual-write synchronization during Strangler migration wave",
                "Formal CSA qualification and independent QA review mandatory prior to production release",
            ]
            if qa_op and qa_op.strategy == "Retain":
                dissent.append(
                    DissentItem(
                        agent="Validation & QA Lead",
                        position="Preferred Retain",
                        reason="Argued that any change to electronic signature or batch release write paths incurs re-validation expense.",
                    )
                )
        elif gxp_tier == "MEDIUM":
            strategy = "Refactor"
            patterns = ["Containerized", "APIGateway", "ManagedDB"]
            target_services = ["AWS App Runner / ECS", "Amazon RDS", "API Gateway"]
            confidence = 0.91
            rationale = (
                f"AI Council Consensus for MEDIUM-tier cluster ({cluster_id}): Modernize to decoupled containerized services. "
                f"Standardized REST APIs and managed databases reduce technical debt while CSA risk remains manageable."
            )
            risks = ["Inter-service schema contracts must be strictly backward compatible"]
        else:
            strategy = "Rehost"
            patterns = ["Containerized", "Serverless"]
            target_services = ["AWS Lambda / Fargate Spot", "Amazon S3"]
            confidence = 0.95
            rationale = (
                f"AI Council Consensus for LOW-tier cluster ({cluster_id}): Fast-track Rehost as an immediate quick win. "
                f"Low regulatory impact enables aggressive cloud adoption and early cost reductions."
            )
            risks = ["Minor configuration drift across cloud environments"]

        all_evidence = list(dict.fromkeys([
            nid for op in opinions for nid in op.evidence_node_ids if nid in valid_node_ids
        ]))
        if not all_evidence and valid_node_ids:
            all_evidence = valid_node_ids[:3]

        effort = compute_baseline_effort(loc, gxp_tier, strategy)

        return CouncilDecision(
            cluster_id=cluster_id,
            strategy=strategy,
            target_pattern=patterns,
            target_services=target_services,
            confidence=confidence,
            rationale=rationale,
            risks=risks,
            dissent=dissent,
            evidence_node_ids=all_evidence,
            effort_weeks=effort,
            model_id=settings.LLM_MODEL,
            offline_simulated=offline_simulated,
            status="PROPOSED",
        )
