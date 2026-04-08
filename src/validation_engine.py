"""
Validation engine for Gold Tier Autonomous AI Employee.

Provides comprehensive validation for task files, action contexts,
and data structures to ensure data integrity and safety.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path
import structlog


logger = structlog.get_logger("validation")


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    field: str
    message: str
    value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "severity": self.severity.value,
            "field": self.field,
            "message": self.message,
            "value": str(self.value) if self.value is not None else None
        }


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    issues: List[ValidationIssue]

    def has_errors(self) -> bool:
        """Check if result has any errors."""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if result has any warnings."""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)

    def get_errors(self) -> List[ValidationIssue]:
        """Get all error issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warning issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "valid": self.valid,
            "error_count": len(self.get_errors()),
            "warning_count": len(self.get_warnings()),
            "issues": [issue.to_dict() for issue in self.issues]
        }


class ValidationEngine:
    """
    Validation engine for data integrity and safety checks.

    Provides validation for:
    - Task file content and structure
    - Action contexts before execution
    - Configuration values
    - File paths and names
    - Email addresses and URLs
    """

    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # URL regex pattern
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    def validate_task_file_content(self, content: str, filename: str) -> ValidationResult:
        """
        Validate task file content.

        Args:
            content: File content
            filename: Filename for context

        Returns:
            ValidationResult
        """
        issues = []

        # Check if content is empty
        if not content or not content.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="content",
                message="Task file content is empty"
            ))
            return ValidationResult(valid=False, issues=issues)

        # Check for frontmatter
        if not content.startswith("---"):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field="frontmatter",
                message="Task file missing frontmatter"
            ))

        # Check for title (# heading)
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field="title",
                message="Task file missing title heading"
            ))

        # Check content length
        if len(content) < 10:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field="content",
                message="Task file content is very short",
                value=len(content)
            ))

        # Check for suspicious content
        suspicious_patterns = [
            (r'<script', "Potential script injection"),
            (r'javascript:', "Potential JavaScript injection"),
            (r'eval\(', "Potential eval injection"),
        ]

        for pattern, message in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="content",
                    message=message
                ))

        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)

        logger.debug(
            "task_file_validated",
            filename=filename,
            valid=valid,
            issue_count=len(issues)
        )

        return ValidationResult(valid=valid, issues=issues)

    def validate_action_context(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate action context before execution.

        Args:
            context: Action context dictionary

        Returns:
            ValidationResult
        """
        issues = []

        # Required fields
        required_fields = ["action_type", "description"]
        for field in required_fields:
            if field not in context:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field,
                    message=f"Required field '{field}' missing"
                ))

        # Validate action_type format
        if "action_type" in context:
            action_type = context["action_type"]
            if not isinstance(action_type, str) or not action_type:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="action_type",
                    message="action_type must be non-empty string",
                    value=action_type
                ))
            elif not re.match(r'^[a-z_]+\.[a-z_]+$', action_type):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="action_type",
                    message="action_type should follow 'category.action' format",
                    value=action_type
                ))

        # Validate description
        if "description" in context:
            description = context["description"]
            if not isinstance(description, str) or not description.strip():
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="description",
                    message="description must be non-empty string",
                    value=description
                ))

        # Validate financial_impact if present
        if "financial_impact" in context:
            financial_impact = context["financial_impact"]
            if not isinstance(financial_impact, (int, float)):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="financial_impact",
                    message="financial_impact must be numeric",
                    value=financial_impact
                ))
            elif financial_impact < 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="financial_impact",
                    message="financial_impact cannot be negative",
                    value=financial_impact
                ))

        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)

        logger.debug(
            "action_context_validated",
            valid=valid,
            issue_count=len(issues)
        )

        return ValidationResult(valid=valid, issues=issues)

    def validate_email(self, email: str) -> ValidationResult:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            ValidationResult
        """
        issues = []

        if not email or not email.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="email",
                message="Email address is empty"
            ))
        elif not self.EMAIL_PATTERN.match(email):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="email",
                message="Invalid email address format",
                value=email
            ))

        valid = len(issues) == 0
        return ValidationResult(valid=valid, issues=issues)

    def validate_url(self, url: str) -> ValidationResult:
        """
        Validate URL.

        Args:
            url: URL to validate

        Returns:
            ValidationResult
        """
        issues = []

        if not url or not url.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="url",
                message="URL is empty"
            ))
        elif not self.URL_PATTERN.match(url):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="url",
                message="Invalid URL format",
                value=url
            ))

        valid = len(issues) == 0
        return ValidationResult(valid=valid, issues=issues)

    def validate_file_path(self, path: Path, must_exist: bool = False) -> ValidationResult:
        """
        Validate file path.

        Args:
            path: Path to validate
            must_exist: Whether path must exist

        Returns:
            ValidationResult
        """
        issues = []

        # Check if path is absolute
        if not path.is_absolute():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field="path",
                message="Path is not absolute",
                value=str(path)
            ))

        # Check if path exists (if required)
        if must_exist and not path.exists():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="path",
                message="Path does not exist",
                value=str(path)
            ))

        # Check for suspicious path components
        suspicious_components = ["..", "~", "$"]
        path_str = str(path)
        for component in suspicious_components:
            if component in path_str:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="path",
                    message=f"Path contains suspicious component: {component}",
                    value=path_str
                ))

        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        return ValidationResult(valid=valid, issues=issues)

    def validate_filename(self, filename: str) -> ValidationResult:
        """
        Validate filename.

        Args:
            filename: Filename to validate

        Returns:
            ValidationResult
        """
        issues = []

        if not filename or not filename.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="filename",
                message="Filename is empty"
            ))
            return ValidationResult(valid=False, issues=issues)

        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="filename",
                    message=f"Filename contains invalid character: {char}",
                    value=filename
                ))

        # Check length
        if len(filename) > 255:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="filename",
                message="Filename too long (max 255 characters)",
                value=len(filename)
            ))

        # Check for reserved names (Windows)
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
                         "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2",
                         "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="filename",
                message=f"Filename uses reserved name: {name_without_ext}",
                value=filename
            ))

        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        return ValidationResult(valid=valid, issues=issues)

    def validate_config_value(
        self,
        value: Any,
        field_name: str,
        required: bool = True,
        value_type: Optional[type] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate configuration value.

        Args:
            value: Value to validate
            field_name: Field name for error messages
            required: Whether value is required
            value_type: Expected type
            min_value: Minimum value (for numeric types)
            max_value: Maximum value (for numeric types)

        Returns:
            ValidationResult
        """
        issues = []

        # Check if required
        if required and (value is None or value == ""):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field=field_name,
                message=f"Required configuration value '{field_name}' is missing"
            ))
            return ValidationResult(valid=False, issues=issues)

        # Check type
        if value_type and value is not None and not isinstance(value, value_type):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field=field_name,
                message=f"Configuration value '{field_name}' has wrong type (expected {value_type.__name__})",
                value=type(value).__name__
            ))

        # Check numeric bounds
        if isinstance(value, (int, float)):
            if min_value is not None and value < min_value:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                    message=f"Configuration value '{field_name}' below minimum ({min_value})",
                    value=value
                ))
            if max_value is not None and value > max_value:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                    message=f"Configuration value '{field_name}' above maximum ({max_value})",
                    value=value
                ))

        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        return ValidationResult(valid=valid, issues=issues)


# Global validation engine instance
validation_engine = ValidationEngine()
