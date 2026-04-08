"""
File operations for Gold Tier Autonomous AI Employee.

Handles reading and writing task files from Obsidian vault folders
with proper error handling and validation.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass
import structlog


logger = structlog.get_logger("file_operations")


@dataclass
class TaskFile:
    """Represents a task file in the vault."""
    path: Path
    filename: str
    content: str
    folder: str
    created_at: datetime
    modified_at: datetime

    @classmethod
    def from_path(cls, path: Path) -> "TaskFile":
        """
        Load task file from path.

        Args:
            path: Path to task file

        Returns:
            TaskFile instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a markdown file
        """
        if not path.exists():
            raise FileNotFoundError(f"Task file not found: {path}")

        if path.suffix != ".md":
            raise ValueError(f"Task file must be markdown (.md): {path}")

        stat = path.stat()

        return cls(
            path=path,
            filename=path.name,
            content=path.read_text(encoding="utf-8"),
            folder=path.parent.name,
            created_at=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        )

    def save(self):
        """Save task file to disk."""
        self.path.write_text(self.content, encoding="utf-8")
        logger.info(
            "task_file_saved",
            path=str(self.path),
            folder=self.folder,
            filename=self.filename
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "path": str(self.path),
            "filename": self.filename,
            "folder": self.folder,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "content_length": len(self.content)
        }


class FileOperations:
    """
    File operations manager for task files.

    Handles reading, writing, and moving task files between vault folders.
    """

    def __init__(self, vault_root: Path):
        """
        Initialize file operations.

        Args:
            vault_root: Root directory of the Obsidian vault
        """
        self.vault_root = Path(vault_root)
        self.inbox = self.vault_root / "Inbox"
        self.needs_action = self.vault_root / "Needs_Action"
        self.plans = self.vault_root / "Plans"
        self.done = self.vault_root / "Done"
        self.pending_approval = self.vault_root / "Pending_Approval"
        self.approved = self.vault_root / "Approved"
        self.rejected = self.vault_root / "Rejected"

        # Ensure directories exist
        for folder in [
            self.inbox,
            self.needs_action,
            self.plans,
            self.done,
            self.pending_approval,
            self.approved,
            self.rejected
        ]:
            folder.mkdir(parents=True, exist_ok=True)

    def scan_folder(self, folder: Path) -> List[TaskFile]:
        """
        Scan folder for task files.

        Args:
            folder: Folder to scan

        Returns:
            List of TaskFile instances
        """
        if not folder.exists():
            logger.warning("folder_not_found", path=str(folder))
            return []

        task_files = []
        for path in folder.glob("*.md"):
            try:
                task_file = TaskFile.from_path(path)
                task_files.append(task_file)
            except Exception as e:
                logger.error(
                    "task_file_load_failed",
                    path=str(path),
                    error=str(e)
                )

        logger.info(
            "folder_scanned",
            folder=folder.name,
            file_count=len(task_files)
        )

        return task_files

    def scan_inbox(self) -> List[TaskFile]:
        """Scan Inbox folder for new tasks."""
        return self.scan_folder(self.inbox)

    def scan_needs_action(self) -> List[TaskFile]:
        """Scan Needs_Action folder for tasks requiring action."""
        return self.scan_folder(self.needs_action)

    def scan_pending_approval(self) -> List[TaskFile]:
        """Scan Pending_Approval folder for tasks awaiting approval."""
        return self.scan_folder(self.pending_approval)

    def read_task(self, path: Path) -> TaskFile:
        """
        Read task file.

        Args:
            path: Path to task file

        Returns:
            TaskFile instance

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        return TaskFile.from_path(path)

    def write_task(
        self,
        folder: Path,
        filename: str,
        content: str,
        overwrite: bool = False
    ) -> TaskFile:
        """
        Write task file.

        Args:
            folder: Destination folder
            filename: Filename (must end with .md)
            content: File content
            overwrite: Whether to overwrite existing file

        Returns:
            TaskFile instance

        Raises:
            ValueError: If filename invalid or file exists and overwrite=False
        """
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        path = folder / filename

        if path.exists() and not overwrite:
            raise ValueError(f"Task file already exists: {path}")

        path.write_text(content, encoding="utf-8")

        logger.info(
            "task_file_written",
            path=str(path),
            folder=folder.name,
            filename=filename,
            overwrite=overwrite
        )

        return TaskFile.from_path(path)

    def move_task(
        self,
        task_file: TaskFile,
        destination_folder: Path,
        new_filename: Optional[str] = None
    ) -> TaskFile:
        """
        Move task file to different folder.

        Args:
            task_file: Task file to move
            destination_folder: Destination folder
            new_filename: Optional new filename

        Returns:
            Updated TaskFile instance

        Raises:
            ValueError: If destination file already exists
        """
        filename = new_filename or task_file.filename
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        destination_path = destination_folder / filename

        if destination_path.exists():
            raise ValueError(f"Destination file already exists: {destination_path}")

        # Move file
        task_file.path.rename(destination_path)

        logger.info(
            "task_file_moved",
            source=str(task_file.path),
            destination=str(destination_path),
            source_folder=task_file.folder,
            destination_folder=destination_folder.name
        )

        # Return updated TaskFile
        return TaskFile.from_path(destination_path)

    def move_to_needs_action(self, task_file: TaskFile) -> TaskFile:
        """Move task to Needs_Action folder."""
        return self.move_task(task_file, self.needs_action)

    def move_to_plans(self, task_file: TaskFile) -> TaskFile:
        """Move task to Plans folder."""
        return self.move_task(task_file, self.plans)

    def move_to_done(self, task_file: TaskFile) -> TaskFile:
        """Move task to Done folder."""
        return self.move_task(task_file, self.done)

    def move_to_pending_approval(self, task_file: TaskFile) -> TaskFile:
        """Move task to Pending_Approval folder."""
        return self.move_task(task_file, self.pending_approval)

    def move_to_approved(self, task_file: TaskFile) -> TaskFile:
        """Move task to Approved folder."""
        return self.move_task(task_file, self.approved)

    def move_to_rejected(self, task_file: TaskFile) -> TaskFile:
        """Move task to Rejected folder."""
        return self.move_task(task_file, self.rejected)

    def delete_task(self, task_file: TaskFile):
        """
        Delete task file.

        Args:
            task_file: Task file to delete
        """
        task_file.path.unlink()

        logger.warning(
            "task_file_deleted",
            path=str(task_file.path),
            folder=task_file.folder,
            filename=task_file.filename
        )

    def create_task_in_inbox(
        self,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskFile:
        """
        Create new task in Inbox.

        Args:
            title: Task title
            description: Task description
            metadata: Optional metadata dictionary

        Returns:
            TaskFile instance
        """
        # Generate filename from title
        filename = self._sanitize_filename(title)

        # Build content with frontmatter
        content_parts = ["---"]

        # Add metadata
        if metadata:
            for key, value in metadata.items():
                content_parts.append(f"{key}: {value}")

        content_parts.extend([
            f"created: {datetime.now(timezone.utc).isoformat()}",
            "status: new",
            "---",
            "",
            f"# {title}",
            "",
            description
        ])

        content = "\n".join(content_parts)

        return self.write_task(self.inbox, filename, content)

    def _sanitize_filename(self, title: str) -> str:
        """
        Sanitize title for use as filename.

        Args:
            title: Task title

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        filename = title
        for char in invalid_chars:
            filename = filename.replace(char, "")

        # Replace spaces with hyphens
        filename = filename.replace(" ", "-")

        # Limit length
        max_length = 100
        if len(filename) > max_length:
            filename = filename[:max_length]

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}-{filename}"

        return filename

    def get_folder_stats(self) -> Dict[str, int]:
        """
        Get file counts for all folders.

        Returns:
            Dictionary mapping folder name to file count
        """
        stats = {}
        for folder_name, folder_path in [
            ("inbox", self.inbox),
            ("needs_action", self.needs_action),
            ("plans", self.plans),
            ("done", self.done),
            ("pending_approval", self.pending_approval),
            ("approved", self.approved),
            ("rejected", self.rejected)
        ]:
            count = len(list(folder_path.glob("*.md")))
            stats[folder_name] = count

        logger.debug("folder_stats", stats=stats)
        return stats
