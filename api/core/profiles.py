"""
Système de Profils Utilisateurs et UI Adaptative

Chaque utilisateur a un profil sauvegardé localement avec ses préférences.
L'UI s'adapte automatiquement au rôle et à l'historique d'interaction.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import hashlib


class UserRole(Enum):
    """Rôles utilisateurs dans Élyon"""
    DIVINE = "divine"  # Joeffrey - contrôle total
    ADMIN = "admin"  # Admins DLDE
    CHEF_ETABLISSEMENT = "chef_etablissement"
    ENSEIGNANT = "enseignant"
    AGENT_DLDE = "agent_dlde"
    AGENT_ETABLISSEMENT = "agent_etablissement"
    PUBLIC_READ = "public_read"  # Lecture seule interne


@dataclass
class UIPreferences:
    """Préférences d'interface sauvegardées par utilisateur"""
    theme: str = "light"  # light, dark, auto
    layout: str = "dashboard"  # dashboard, detailed, minimal
    widgets: List[str] = field(default_factory=list)  # widgets actifs
    language: str = "fr"
    font_size: int = 14
    sidebar_collapsed: bool = False
    custom_shortcuts: Dict[str, str] = field(default_factory=dict)
    last_updated: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UserProfile:
    """Profil utilisateur persisté localement"""
    user_id: str
    display_name: str
    role: UserRole
    email: str
    created_at: str
    last_login: str
    ui_preferences: UIPreferences = field(default_factory=UIPreferences)
    learning_profile: Dict[str, Any] = field(default_factory=dict)  # Pour Élyon
    access_log: List[Dict] = field(default_factory=list)

    # Contexte d'apprentissage pour Élyon
    topics_interest: List[str] = field(default_factory=list)
    conversation_history_count: int = 0

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["role"] = self.role.value
        data["ui_preferences"] = self.ui_preferences.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """Recréer un profil depuis le JSON"""
        ui_prefs = UIPreferences(**data.pop("ui_preferences", {}))
        role = UserRole(data.pop("role", "agent_dlde"))
        return cls(**data, role=role, ui_preferences=ui_prefs)


class UserProfileManager:
    """Gestion centralisée des profils utilisateurs"""

    PROFILES_DIR = Path("data/_profiles")

    def __init__(self):
        self.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, UserProfile] = {}
        self._load_all_profiles()

    def get_or_create_profile(self, user_id: str, display_name: str, role: UserRole, email: str) -> UserProfile:
        """Récupère ou crée un profil utilisateur"""
        if user_id in self.profiles:
            self.profiles[user_id].last_login = datetime.now().isoformat()
            self._save_profile(user_id)
            return self.profiles[user_id]

        # Créer nouveau profil
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            role=role,
            email=email,
            created_at=datetime.now().isoformat(),
            last_login=datetime.now().isoformat(),
        )
        self.profiles[user_id] = profile
        self._save_profile(user_id)
        return profile

    def update_ui_preferences(self, user_id: str, **kwargs) -> UIPreferences:
        """Met à jour les préférences UI d'un utilisateur"""
        if user_id not in self.profiles:
            raise ValueError(f"User {user_id} not found")

        profile = self.profiles[user_id]
        for key, value in kwargs.items():
            if hasattr(profile.ui_preferences, key):
                setattr(profile.ui_preferences, key, value)

        profile.ui_preferences.last_updated = datetime.now().isoformat()
        self._save_profile(user_id)
        return profile.ui_preferences

    def log_access(self, user_id: str, action: str, details: Dict = None):
        """Enregistre une action utilisateur"""
        if user_id not in self.profiles:
            return

        profile = self.profiles[user_id]
        access_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }
        profile.access_log.append(access_entry)

        # Garder les 1000 dernières entrées
        if len(profile.access_log) > 1000:
            profile.access_log = profile.access_log[-1000:]

        self._save_profile(user_id)

    def update_learning_profile(self, user_id: str, topics: List[str] = None, context: Dict = None):
        """Met à jour le profil d'apprentissage d'Élyon pour cet utilisateur"""
        if user_id not in self.profiles:
            return

        profile = self.profiles[user_id]
        if topics:
            profile.topics_interest = list(set(profile.topics_interest + topics))
        if context:
            profile.learning_profile.update(context)

        self._save_profile(user_id)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Récupère un profil"""
        return self.profiles.get(user_id)

    def _save_profile(self, user_id: str):
        """Sauvegarde un profil au format JSON"""
        profile = self.profiles[user_id]
        filepath = self.PROFILES_DIR / f"{user_id}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_all_profiles(self):
        """Charge tous les profils depuis le disque"""
        for filepath in self.PROFILES_DIR.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profile = UserProfile.from_dict(data)
                    self.profiles[profile.user_id] = profile
            except Exception as e:
                print(f"[ERROR] Impossible de charger {filepath}: {e}")

    def get_all_profiles_summary(self) -> List[Dict]:
        """Résumé de tous les profils"""
        return [
            {
                "user_id": p.user_id,
                "name": p.display_name,
                "role": p.role.value,
                "last_login": p.last_login,
                "conversations": p.conversation_history_count
            }
            for p in self.profiles.values()
        ]


# ============ UI ADAPTATIVE PAR RÔLE ============

class AdaptiveUIBuilder:
    """Construit l'UI adaptée à chaque rôle et profil"""

    # Configuration d'UI par rôle
    ROLE_UI_CONFIG = {
        UserRole.DIVINE: {
            "title": "Élyon Divine - Tableau de Bord Complet",
            "layout": "comprehensive",
            "widgets": [
                "monitoring_realtime",
                "system_health",
                "audit_log_browser",
                "learning_dashboard",
                "governance_panel",
                "debug_console",
                "model_training",
                "conversation_explorer",
                "corpus_manager",
                "user_management",
                "intent_analyzer",
                "performance_metrics",
            ],
            "permissions": ["read", "write", "train", "debug", "governance"],
            "theme": "dark",
            "access_level": 100
        },
        UserRole.ADMIN: {
            "title": "Élyon - Administration DLDE",
            "layout": "admin",
            "widgets": [
                "dashboard_summary",
                "user_management",
                "governance_status",
                "recent_conversations",
                "system_status",
                "report_builder",
            ],
            "permissions": ["read", "write", "governance"],
            "theme": "light",
            "access_level": 80
        },
        UserRole.CHEF_ETABLISSEMENT: {
            "title": "Élyon - Gestion Établissement",
            "layout": "focused",
            "widgets": [
                "my_dashboard",
                "lycee_status",
                "sustainability_metrics",
                "team_performance",
                "recent_queries",
            ],
            "permissions": ["read", "write"],
            "theme": "light",
            "access_level": 60
        },
        UserRole.ENSEIGNANT: {
            "title": "Élyon - Assistance Pédagogique",
            "layout": "simple",
            "widgets": [
                "quick_help",
                "curriculum_search",
                "document_assistant",
                "my_recent_searches",
            ],
            "permissions": ["read"],
            "theme": "light",
            "access_level": 40
        },
        UserRole.AGENT_DLDE: {
            "title": "Élyon - Assistance DLDE",
            "layout": "simple",
            "widgets": [
                "search_interface",
                "document_library",
                "my_recent_searches",
                "quick_reference",
            ],
            "permissions": ["read"],
            "theme": "light",
            "access_level": 30
        },
    }

    @staticmethod
    def build_ui_config(profile: UserProfile) -> Dict:
        """Construit la config UI pour un utilisateur"""
        role_config = AdaptiveUIBuilder.ROLE_UI_CONFIG.get(
            profile.role,
            AdaptiveUIBuilder.ROLE_UI_CONFIG[UserRole.AGENT_DLDE]
        )

        return {
            "user": {
                "id": profile.user_id,
                "name": profile.display_name,
                "role": profile.role.value,
            },
            "interface": {
                "title": role_config["title"],
                "layout": profile.ui_preferences.layout or role_config["layout"],
                "theme": profile.ui_preferences.theme or role_config["theme"],
                "widgets": profile.ui_preferences.widgets or role_config["widgets"],
                "permissions": role_config["permissions"],
                "access_level": role_config["access_level"],
            },
            "preferences": profile.ui_preferences.to_dict(),
            "build_timestamp": datetime.now().isoformat(),
        }


# ============ DÉTECTION AUTOMATIQUE DE RÔLE ============

class RoleDetector:
    """Détecte automatiquement le rôle d'un utilisateur via AD ou patterns"""

    @staticmethod
    def detect_from_ad(email: str, ad_groups: List[str]) -> UserRole:
        """Détecte le rôle via les groupes Active Directory"""
        email_lower = email.lower()

        # Joeffrey = rôle DIVINE (hardcodé)
        if "joeffrey.joly" in email_lower or "joly" in email_lower:
            return UserRole.DIVINE

        # Groupes AD à rôles
        for group in ad_groups:
            if "admin" in group.lower():
                return UserRole.ADMIN
            elif "chef" in group.lower() or "direction" in group.lower():
                return UserRole.CHEF_ETABLISSEMENT
            elif "enseignant" in group.lower() or "prof" in group.lower():
                return UserRole.ENSEIGNANT
            elif "dlde" in group.lower():
                return UserRole.AGENT_DLDE
            elif "agent" in group.lower():
                return UserRole.AGENT_ETABLISSEMENT

        # Par défaut : lecture seule
        return UserRole.AGENT_DLDE

    @staticmethod
    def detect_from_email_domain(email: str) -> UserRole:
        """Détecte le rôle via le domaine email"""
        if "@grandest.fr" not in email:
            return UserRole.PUBLIC_READ

        if "joeffrey.joly" in email:
            return UserRole.DIVINE
        elif "admin" in email or "direction" in email:
            return UserRole.ADMIN

        return UserRole.AGENT_DLDE
