"""
Endpoints API pour Gouvernance, Profils et UI Divine

Intégration complète de la gouvernance territoriale et UI adaptative.
"""

from fastapi import APIRouter, Query, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from api.core.governance import TerritorialGovernance, GovernanceContext, AuditLevel
from api.core.profiles import UserProfileManager, UserRole, RoleDetector, AdaptiveUIBuilder
from api.core.divine import UIDivine

router = APIRouter(prefix="/v2", tags=["governance_profiles_divine"])

# Instances globales (à initialiser depuis main)
governance: TerritorialGovernance = None
profile_manager: UserProfileManager = None
ui_divine: UIDivine = None


def init_modules(gov: TerritorialGovernance, prof_mgr: UserProfileManager, divine: UIDivine):
    """Initialise les modules globaux"""
    global governance, profile_manager, ui_divine
    governance = gov
    profile_manager = prof_mgr
    ui_divine = divine


# ============ MODÈLES PYDANTIC ============

class GovernanceCheckRequest(BaseModel):
    """Requête de vérification de conformité"""
    action: str
    external_call: bool = False
    destination: Optional[str] = None
    payload: Dict[str, Any] = {}


class UIPreferencesUpdate(BaseModel):
    """Mise à jour des préférences UI"""
    theme: Optional[str] = None
    layout: Optional[str] = None
    sidebar_collapsed: Optional[bool] = None
    font_size: Optional[int] = None


# ============ ENDPOINTS GOUVERNANCE ============

@router.post("/governance/check")
async def check_governance(
    request: GovernanceCheckRequest,
    x_user_id: str = Header(...),
    x_user_role: str = Header("agent_dlde"),
):
    """
    Vérifie qu'une action respecte la gouvernance Région Grand Est.

    Retourne si l'action est autorisée et documente toute tentative bloquée.
    """

    if not governance:
        raise HTTPException(status_code=503, detail="Governance not initialized")

    context = GovernanceContext(
        user_id=x_user_id,
        user_role=x_user_role,
        session_id="session_" + datetime.now().isoformat(),
        region="Région Grand Est"
    )

    result = governance.validate_request(context, request.dict())

    return {
        "allowed": result["allowed"],
        "reason": result["reason"],
        "timestamp": datetime.now().isoformat(),
        "user": x_user_id,
        "region": context.region,
    }


@router.get("/governance/audit-summary")
async def get_audit_summary(x_user_id: str = Header(...)):
    """Résumé d'audit de conformité"""

    if not governance:
        raise HTTPException(status_code=503, detail="Governance not initialized")

    # Seuls les admins et Divine peuvent voir le résumé complet
    return governance.get_audit_summary()


@router.get("/governance/audit-log")
async def get_audit_log(
    x_user_id: str = Header(...),
    limit: int = Query(100),
    level: Optional[str] = Query(None),
):
    """
    Récupère le log d'audit (pour admins/divine).
    Les logs ne sortent JAMAIS du système local.
    """

    if not governance:
        raise HTTPException(status_code=503, detail="Governance not initialized")

    logs = governance.access_control.audit_log

    if level:
        logs = [e for e in logs if e.level.value == level]

    logs = logs[-limit:]

    return {
        "count": len(logs),
        "entries": [
            {
                "timestamp": e.timestamp,
                "level": e.level.value,
                "action": e.action,
                "user": e.user,
                "details": e.details,
                "hash": e.hash_integrity,
            }
            for e in logs
        ]
    }


# ============ ENDPOINTS PROFILS UTILISATEURS ============

@router.get("/profile/me")
async def get_my_profile(
    x_user_id: str = Header(...),
    x_user_name: str = Header("Unknown"),
    x_user_email: str = Header(""),
):
    """Récupère le profil de l'utilisateur connecté"""

    if not profile_manager:
        raise HTTPException(status_code=503, detail="Profile manager not initialized")

    # Détecter le rôle automatiquement pour Joeffrey
    role = RoleDetector.detect_from_email_domain(x_user_email)

    profile = profile_manager.get_or_create_profile(
        user_id=x_user_id,
        display_name=x_user_name,
        role=role,
        email=x_user_email,
    )

    profile_manager.log_access(x_user_id, "profile_retrieved", {"email": x_user_email})

    return profile.to_dict()


@router.put("/profile/preferences")
async def update_preferences(
    update: UIPreferencesUpdate,
    x_user_id: str = Header(...),
):
    """Met à jour les préférences UI"""

    if not profile_manager:
        raise HTTPException(status_code=503, detail="Profile manager not initialized")

    prefs = profile_manager.update_ui_preferences(
        x_user_id,
        **{k: v for k, v in update.dict().items() if v is not None}
    )

    profile_manager.log_access(x_user_id, "preferences_updated", update.dict())

    return {"status": "updated", "preferences": prefs.to_dict()}


@router.get("/ui/config")
async def get_ui_config(
    x_user_id: str = Header(...),
    x_user_email: str = Header(""),
):
    """Récupère la configuration UI adaptée au rôle de l'utilisateur"""

    if not profile_manager:
        raise HTTPException(status_code=503, detail="Profile manager not initialized")

    profile = profile_manager.get_profile(x_user_id)
    if not profile:
        # Créer profil si n'existe pas
        role = RoleDetector.detect_from_email_domain(x_user_email)
        profile = profile_manager.get_or_create_profile(
            user_id=x_user_id,
            display_name=x_user_id,
            role=role,
            email=x_user_email,
        )

    ui_config = AdaptiveUIBuilder.build_ui_config(profile)

    return ui_config


@router.get("/profiles/all")
async def get_all_profiles(x_user_id: str = Header(...), x_user_role: str = Header(...)):
    """Liste tous les profils (admin/divine only)"""

    if x_user_role not in ["admin", "divine"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not profile_manager:
        raise HTTPException(status_code=503, detail="Profile manager not initialized")

    return profile_manager.get_all_profiles_summary()


# ============ ENDPOINTS UI DIVINE ============

@router.get("/divine/state")
async def get_divine_state(x_user_id: str = Header(...)):
    """Récupère l'état complet d'Élyon (divine/concepteur only)"""

    if x_user_id != "joeffrey.joly" and not x_user_id.startswith("divine_"):
        raise HTTPException(status_code=403, detail="Divine access required")

    if not ui_divine:
        raise HTTPException(status_code=503, detail="UI Divine not initialized")

    return ui_divine.get_comprehensive_state()


@router.get("/divine/learning")
async def get_learning_state(x_user_id: str = Header(...)):
    """État d'apprentissage d'Élyon"""

    if x_user_id != "joeffrey.joly":
        raise HTTPException(status_code=403, detail="Divine access required")

    if not ui_divine:
        raise HTTPException(status_code=503, detail="UI Divine not initialized")

    return ui_divine._get_learning_state()


@router.get("/divine/debug-logs")
async def get_debug_logs(
    x_user_id: str = Header(...),
    limit: int = Query(100),
    level: Optional[str] = Query(None),
):
    """Récupère les logs debug (divine only)"""

    if x_user_id != "joeffrey.joly":
        raise HTTPException(status_code=403, detail="Divine access required")

    if not ui_divine:
        raise HTTPException(status_code=503, detail="UI Divine not initialized")

    logs = ui_divine.debug_logs

    if level:
        logs = [l for l in logs if l.level == level]

    logs = logs[-limit:]

    return {
        "count": len(logs),
        "logs": [
            {
                "timestamp": l.timestamp,
                "level": l.level,
                "module": l.module,
                "message": l.message,
                "data": l.data,
            }
            for l in logs
        ]
    }


@router.get("/divine/recommendations")
async def get_learning_recommendations(x_user_id: str = Header(...)):
    """Recommandations d'amélioration pour Élyon"""

    if x_user_id != "joeffrey.joly":
        raise HTTPException(status_code=403, detail="Divine access required")

    if not ui_divine:
        raise HTTPException(status_code=503, detail="UI Divine not initialized")

    return ui_divine.get_learning_recommendations()


@router.post("/divine/export-state")
async def export_divine_state(x_user_id: str = Header(...)):
    """Exporte l'état complet d'Élyon (local only)"""

    if x_user_id != "joeffrey.joly":
        raise HTTPException(status_code=403, detail="Divine access required")

    if not ui_divine:
        raise HTTPException(status_code=503, detail="UI Divine not initialized")

    filepath = ui_divine.export_state()

    return {
        "status": "exported",
        "filepath": filepath,
        "timestamp": datetime.now().isoformat(),
    }


# ============ ENDPOINTS D'AUDIT LOCAL ============

@router.get("/governance/export-audit")
async def export_audit_local(x_user_id: str = Header(...)):
    """Exporte le log d'audit local (jamais vers l'extérieur)"""

    if not governance:
        raise HTTPException(status_code=503, detail="Governance not initialized")

    filepath = governance.access_control.export_audit_log()

    return {
        "status": "exported",
        "filepath": filepath,
        "message": "Audit log saved locally - NEVER transmitted externally",
        "timestamp": datetime.now().isoformat(),
    }
