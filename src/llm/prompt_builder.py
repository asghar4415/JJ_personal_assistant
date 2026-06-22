"""
prompt_builder.py - System prompt construction

Builds complete system prompts by combining user profile, system base, and context.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class PromptBuilder:
    """System prompt builder for LLM context"""

    def __init__(self, profile_path: str = None, base_prompt_path: str = None):
        """
        Initialize prompt builder

        Args:
            profile_path: Path to user_profile.json (uses default if not provided)
            base_prompt_path: Path to system_prompt_base.txt (uses default if not provided)
        """
        # Set default paths
        if profile_path is None:
            profile_path = Path(__file__).parent.parent.parent / \
                "data" / "user_profile.json"
        if base_prompt_path is None:
            base_prompt_path = Path(
                __file__).parent.parent.parent / "data" / "system_prompt_base.txt"

        self.profile_path = Path(profile_path)
        self.base_prompt_path = Path(base_prompt_path)

        # Load profile
        self.user_profile = self._load_profile()

        # Load base prompt
        self.base_prompt = self._load_base_prompt()

        # Context history
        self.conversation_history: List[Dict] = []
        self.max_history = 10

        logger.info("PromptBuilder initialized")

    def _load_profile(self) -> Dict:
        """Load user profile from JSON file"""
        try:
            if self.profile_path.exists():
                with open(self.profile_path, 'r') as f:
                    profile = json.load(f)
                logger.info(
                    f"User profile loaded: {profile.get('user_name', 'Unknown')}")
                return profile
            else:
                logger.warning(f"Profile not found at {self.profile_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return {}

    def _load_base_prompt(self) -> str:
        """Load base system prompt from file"""
        try:
            if self.base_prompt_path.exists():
                with open(self.base_prompt_path, 'r') as f:
                    prompt = f.read()
                logger.info("Base system prompt loaded")
                return prompt
            else:
                logger.warning(
                    f"Base prompt not found at {self.base_prompt_path}")
                return ""
        except Exception as e:
            logger.error(f"Error loading base prompt: {e}")
            return ""

    def build_prompt(self, include_history: bool = True, additional_context: str = "") -> str:
        """
        Build complete system prompt

        Args:
            include_history: Whether to include conversation history
            additional_context: Any additional context to append

        Returns:
            Complete system prompt string
        """
        prompt_parts = []

        # Base system prompt
        if self.base_prompt:
            prompt_parts.append(self.base_prompt)

        # User profile context
        if self.user_profile:
            prompt_parts.append("\n## Profile Details")
            profile_text = self._format_profile(self.user_profile)
            prompt_parts.append(profile_text)

        # Conversation history
        if include_history and self.conversation_history:
            prompt_parts.append("\n## Recent Conversation Context")
            history_text = self._format_history()
            prompt_parts.append(history_text)

        # Current date/time
        now = datetime.now()
        prompt_parts.append(f"\n## Current Context")
        prompt_parts.append(
            f"Current date and time: {now.strftime('%Y-%m-%d %A, %H:%M:%S')}")

        # Additional context
        if additional_context:
            prompt_parts.append(f"\n## Additional Context")
            prompt_parts.append(additional_context)

        # Instructions
        prompt_parts.append("\n## Instructions")
        prompt_parts.append("- Be concise and direct")
        prompt_parts.append("- Reference past conversations when relevant")
        prompt_parts.append("- Respect the user's communication style")
        prompt_parts.append("- Provide context-aware responses")

        complete_prompt = "\n".join(prompt_parts)

        logger.debug(f"System prompt built: {len(complete_prompt)} characters")
        return complete_prompt

    def add_to_history(self, role: str, content: str) -> None:
        """
        Add message to conversation history

        Args:
            role: "user" or "assistant"
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

        # Keep history size limited
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        logger.debug(
            f"History updated: {len(self.conversation_history)} messages")

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def _format_profile(self, profile: Dict) -> str:
        """Format profile for inclusion in prompt"""
        lines = []

        if "user_name" in profile:
            lines.append(f"Name: {profile['user_name']}")

        if "user_bio" in profile:
            lines.append(f"Bio: {profile['user_bio']}")

        if "background" in profile:
            bg = profile["background"]
            if isinstance(bg, dict):
                lines.append(f"Background:")
                for key, value in bg.items():
                    lines.append(f"  - {key}: {value}")

        if "current_projects" in profile:
            lines.append(f"Current Projects:")
            projects = profile["current_projects"]
            if isinstance(projects, list):
                for proj in projects:
                    if isinstance(proj, dict):
                        lines.append(
                            f"  - {proj.get('name', 'Project')}: {proj.get('description', '')}")
                    else:
                        lines.append(f"  - {proj}")

        if "work_context" in profile:
            lines.append(f"Work Context: {profile['work_context']}")

        if "preferences" in profile:
            prefs = profile["preferences"]
            if isinstance(prefs, dict):
                for key, value in prefs.items():
                    lines.append(f"Preference ({key}): {value}")

        return "\n".join(lines)

    def _format_history(self) -> str:
        """Format conversation history for inclusion in prompt"""
        lines = []

        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "").upper()
            content = msg.get("content", "")[:100]  # Truncate long messages
            lines.append(f"{role}: {content}...")

        return "\n".join(lines)

    def update_profile(self, profile_updates: Dict) -> None:
        """
        Update user profile

        Args:
            profile_updates: Dictionary of profile fields to update
        """
        self.user_profile.update(profile_updates)
        logger.info(f"Profile updated with {len(profile_updates)} fields")

    def get_profile(self) -> Dict:
        """Get current user profile"""
        return self.user_profile.copy()

    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()

    def set_max_history(self, max_history: int) -> None:
        """Set maximum history size"""
        self.max_history = max(1, max_history)
        logger.info(f"Max history set to {self.max_history}")

    def get_info(self) -> Dict:
        """Get builder info"""
        return {
            "user": self.user_profile.get("user_name", "Unknown"),
            "history_messages": len(self.conversation_history),
            "max_history": self.max_history,
            "profile_loaded": bool(self.user_profile),
            "base_prompt_loaded": bool(self.base_prompt),
        }
