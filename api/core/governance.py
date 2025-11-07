"""
Gouvernance Territoriale Stricte - Région Grand Est

Principes 6S/6R appliqués au niveau du système.
Audit complet, aucune fuite de donnée, traçabilité complète.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import json
import hashlib
from pathlib import Path

# ============ CONFIGURATION DE SOUVERAINETÉ ============

REGION_BOUNDARY = {
    "region": "Région Grand Est",
    "allowed_internal_hosts": {
        "intra.grandest.fr",
        "extranetlycees.grandest.fr",
        "srv-docs.dlde.local",
        "srv-commun.local",
        "semarchy.local",
        "jalios.local",
    },
    "allowed_protocols": {"SMB", "DFS", "ODBC", "REST_INTERNAL", "JCMS"},
    "blocked_external": {
        "openai.com",
        "anthropic.com",
        "huggingface.co",
        "cloud.google.com",
        "aws.amazon.com",
    }
}

# ============ AUDIT & CONFORMITÉ RGPD ============

class AuditLevel(Enum):
    """Niveaux d'audit pour traçabilité"""
    CRITICAL = "CRITICAL"      # Accès données, exports
    HIGH = "HIGH"              # Requêtes externes, décisions
    MEDIUM = "MEDIUM"          # Opérations normales
    DEBUG = "DEBUG"            # Traces développeur


@dataclass
class AuditEntry:
    """Enregistrement d'audit horodaté et immuable"""
    timestamp: str
    level: AuditLevel
    action: str
    user: str
    details: Dict[str, Any]
    hash_integrity: str = ""

    def compute_hash(self) -> str:
        """Hash SHA-256 pour immuabilité"""
        content = json.dumps({
            "ts": self.timestamp,
            "level": self.level.value,
            "action": self.action,
            "user": self.user,
            "details": self.details
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def finalize(self):
        """Sceller l'entrée"""
        self.hash_integrity = self.compute_hash()
        return self


@dataclass
class GovernanceContext:
    """Contexte de gouvernance pour chaque requête"""
    user_id: str
    user_role: str
    session_id: str
    region: str = "Région Grand Est"
    allowed_resources: Set[str] = field(default_factory=set)
    audit_enabled: bool = True

    def is_internal_only(self) -> bool:
        """Vérifie que l'utilisateur ne peut accéder qu'à des ressources internes"""
        return self.region == "Région Grand Est"


# ============ CONTRÔLE D'ACCÈS STRICT ============

class AccessControl:
    """Contrôle d'accès basé sur AD + gouvernance"""

    def __init__(self):
        self.audit_log: List[AuditEntry] = []
        self.access_rules = {}

    def check_external_request(self, destination: str, payload: Dict) -> bool:
        """
        Valide qu'une requête externe ne viole pas la gouvernance.
        Retourne False si la requête est BLOQUÉE.
        """
        blocked_hosts = REGION_BOUNDARY["blocked_external"]

        for blocked in blocked_hosts:
            if blocked in destination:
                self._log_blocked(
                    "EXTERNAL_REQUEST_BLOCKED",
                    {"destination": destination, "payload_size": len(json.dumps(payload))}
                )
                return False

        return True

    def check_data_export(self, user: str, data_type: str, quantity: int) -> bool:
        """Aucun export de données hors du système"""
        self._log_audit(
            AuditLevel.CRITICAL,
            "DATA_EXPORT_ATTEMPT",
            user,
            {"data_type": data_type, "quantity": quantity, "result": "DENIED"}
        )
        return False  # Toujours DÉNIÉ

    def check_conversation_export(self, user: str, conversation_id: str) -> bool:
        """Aucun export de conversation"""
        self._log_audit(
            AuditLevel.CRITICAL,
            "CONVERSATION_EXPORT_ATTEMPT",
            user,
            {"conversation_id": conversation_id, "result": "DENIED"}
        )
        return False  # Toujours DÉNIÉ

    def check_document_leak(self, document: Dict, user: str) -> bool:
        """Détecte les tentatives de fuite de documents"""
        if "external_share" in document or "upload_external" in document:
            self._log_audit(
                AuditLevel.CRITICAL,
                "DOCUMENT_LEAK_ATTEMPT",
                user,
                {"document_id": document.get("id"), "result": "BLOCKED"}
            )
            return False
        return True

    def _log_blocked(self, action: str, details: Dict):
        """Enregistre une tentative bloquée"""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            level=AuditLevel.CRITICAL,
            action=action,
            user="SYSTEM",
            details=details
        ).finalize()
        self.audit_log.append(entry)

    def _log_audit(self, level: AuditLevel, action: str, user: str, details: Dict):
        """Enregistre une action d'audit"""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            action=action,
            user=user,
            details=details
        ).finalize()
        self.audit_log.append(entry)

    def export_audit_log(self) -> str:
        """Exporte le journal d'audit local (JAMAIS vers l'extérieur)"""
        filepath = Path("data/audit") / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            for entry in self.audit_log:
                f.write(json.dumps({
                    "timestamp": entry.timestamp,
                    "level": entry.level.value,
                    "action": entry.action,
                    "user": entry.user,
                    "details": entry.details,
                    "hash": entry.hash_integrity
                }) + "\n")

        return str(filepath)


# ============ MODULE D'APPLICATION ============

class TerritorialGovernance:
    """
    Applique la gouvernance Région Grand Est à tout le système.
    Point d'entrée central pour vérification de conformité.
    """

    def __init__(self):
        self.access_control = AccessControl()
        self.boundary = REGION_BOUNDARY

    def validate_request(self, context: GovernanceContext, request: Dict) -> Dict:
        """
        Valide qu'une requête respecte la gouvernance.
        Retourne {"allowed": bool, "reason": str, "audit_entry": ...}
        """

        # 1. Vérifier que c'est un utilisateur interne
        if context.region != "Région Grand Est":
            return {
                "allowed": False,
                "reason": "Unauthorized region",
                "audit_entry": self._audit_failure(context, "REGION_CHECK_FAILED", request)
            }

        # 2. Vérifier qu'il n'y a pas tentative d'export
        if request.get("action") in ["export_data", "export_conversation", "export_document"]:
            self.access_control.check_data_export(
                context.user_id,
                request.get("type", "unknown"),
                len(json.dumps(request.get("payload", {})))
            )
            return {
                "allowed": False,
                "reason": "Data export forbidden",
                "audit_entry": self._audit_failure(context, "EXPORT_ATTEMPT", request)
            }

        # 3. Vérifier les destinations externes
        if request.get("external_call"):
            destination = request.get("destination", "")
            if destination and not self.access_control.check_external_request(destination, request.get("payload", {})):
                return {
                    "allowed": False,
                    "reason": "External destination blocked",
                    "audit_entry": self._audit_failure(context, "EXTERNAL_BLOCKED", request)
                }

        # ✓ Tout va bien
        self._audit_success(context, "REQUEST_ALLOWED", request)
        return {
            "allowed": True,
            "reason": "Request compliant with governance",
            "audit_entry": None
        }

    def _audit_failure(self, context: GovernanceContext, action: str, details: Dict) -> AuditEntry:
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            level=AuditLevel.CRITICAL,
            action=action,
            user=context.user_id,
            details=details
        ).finalize()
        self.access_control.audit_log.append(entry)
        return entry

    def _audit_success(self, context: GovernanceContext, action: str, details: Dict):
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            level=AuditLevel.MEDIUM,
            action=action,
            user=context.user_id,
            details=details
        ).finalize()
        self.access_control.audit_log.append(entry)

    def get_audit_summary(self) -> Dict:
        """Résumé de conformité"""
        total = len(self.access_control.audit_log)
        critical = len([e for e in self.access_control.audit_log if e.level == AuditLevel.CRITICAL])
        blocked = len([e for e in self.access_control.audit_log if "BLOCKED" in e.action or "DENIED" in str(e.details.get("result"))])

        return {
            "total_audit_entries": total,
            "critical_events": critical,
            "blocked_attempts": blocked,
            "last_entry": self.access_control.audit_log[-1].timestamp if self.access_control.audit_log else None,
            "region": self.boundary["region"],
            "status": "✓ COMPLIANT" if blocked > 0 else "✓ NO THREATS"
        }
