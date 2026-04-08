"""
Log Rotation System
Automatically rotates and compresses old log files
"""

import os
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List


class LogRotator:
    """
    Manages log file rotation and cleanup
    """

    def __init__(self):
        """Initialize log rotator"""
        self.project_root = Path(__file__).parent.parent

        # Log directories to manage
        self.log_dirs = [
            self.project_root / "Audit_Logs",
            self.project_root / "service_logs"
        ]

        # Rotation settings
        self.max_age_days = int(os.getenv('LOG_MAX_AGE_DAYS', '30'))
        self.compress_age_days = int(os.getenv('LOG_COMPRESS_AGE_DAYS', '7'))
        self.max_size_mb = int(os.getenv('LOG_MAX_SIZE_MB', '100'))

    def rotate_all_logs(self):
        """Rotate logs in all configured directories"""
        print("="*60)
        print("LOG ROTATION")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        total_compressed = 0
        total_deleted = 0
        total_space_freed = 0

        for log_dir in self.log_dirs:
            if not log_dir.exists():
                continue

            print(f"Processing: {log_dir}")

            # Compress old logs
            compressed = self.compress_old_logs(log_dir)
            total_compressed += len(compressed)

            # Delete very old logs
            deleted, space_freed = self.delete_old_logs(log_dir)
            total_deleted += len(deleted)
            total_space_freed += space_freed

            print()

        print("="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Files compressed: {total_compressed}")
        print(f"Files deleted: {total_deleted}")
        print(f"Space freed: {total_space_freed / (1024*1024):.2f} MB")
        print()

    def compress_old_logs(self, log_dir: Path) -> List[Path]:
        """
        Compress log files older than compress_age_days

        Args:
            log_dir: Directory containing log files

        Returns:
            List of compressed files
        """
        compressed_files = []
        cutoff_date = datetime.now() - timedelta(days=self.compress_age_days)

        # Find uncompressed log files
        for log_file in log_dir.glob('*.log'):
            # Skip if already compressed
            if log_file.suffix == '.gz':
                continue

            # Check file age
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                try:
                    # Compress file
                    compressed_path = log_file.with_suffix(log_file.suffix + '.gz')

                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Remove original
                    log_file.unlink()

                    compressed_files.append(compressed_path)
                    print(f"  [Compressed] {log_file.name}")

                except Exception as e:
                    print(f"  [Error] Failed to compress {log_file.name}: {e}")

        # Also compress JSON files
        for json_file in log_dir.glob('*.json'):
            if json_file.name == 'processed_emails.json' or json_file.name == 'processed_mentions.json':
                continue  # Skip active tracking files

            file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
            if file_time < cutoff_date:
                try:
                    compressed_path = json_file.with_suffix(json_file.suffix + '.gz')

                    with open(json_file, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    json_file.unlink()

                    compressed_files.append(compressed_path)
                    print(f"  [Compressed] {json_file.name}")

                except Exception as e:
                    print(f"  [Error] Failed to compress {json_file.name}: {e}")

        return compressed_files

    def delete_old_logs(self, log_dir: Path) -> tuple:
        """
        Delete log files older than max_age_days

        Args:
            log_dir: Directory containing log files

        Returns:
            Tuple of (deleted files list, total bytes freed)
        """
        deleted_files = []
        total_bytes_freed = 0
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

        # Find old compressed files
        for gz_file in log_dir.glob('*.gz'):
            file_time = datetime.fromtimestamp(gz_file.stat().st_mtime)
            if file_time < cutoff_date:
                try:
                    file_size = gz_file.stat().st_size
                    gz_file.unlink()

                    deleted_files.append(gz_file)
                    total_bytes_freed += file_size
                    print(f"  [Deleted] {gz_file.name}")

                except Exception as e:
                    print(f"  [Error] Failed to delete {gz_file.name}: {e}")

        return deleted_files, total_bytes_freed

    def check_large_logs(self, log_dir: Path) -> List[Path]:
        """
        Find log files exceeding max size

        Args:
            log_dir: Directory containing log files

        Returns:
            List of large files
        """
        large_files = []
        max_size_bytes = self.max_size_mb * 1024 * 1024

        for log_file in log_dir.glob('*.log'):
            if log_file.stat().st_size > max_size_bytes:
                large_files.append(log_file)

        return large_files

    def get_log_statistics(self) -> dict:
        """Get statistics about log files"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'compressed_files': 0,
            'uncompressed_files': 0,
            'by_directory': {}
        }

        for log_dir in self.log_dirs:
            if not log_dir.exists():
                continue

            dir_stats = {
                'files': 0,
                'size_mb': 0,
                'compressed': 0,
                'uncompressed': 0
            }

            for log_file in log_dir.glob('*'):
                if log_file.is_file():
                    size_mb = log_file.stat().st_size / (1024 * 1024)

                    dir_stats['files'] += 1
                    dir_stats['size_mb'] += size_mb

                    if log_file.suffix == '.gz':
                        dir_stats['compressed'] += 1
                    else:
                        dir_stats['uncompressed'] += 1

            stats['total_files'] += dir_stats['files']
            stats['total_size_mb'] += dir_stats['size_mb']
            stats['compressed_files'] += dir_stats['compressed']
            stats['uncompressed_files'] += dir_stats['uncompressed']
            stats['by_directory'][str(log_dir)] = dir_stats

        return stats


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage log file rotation")
    parser.add_argument("action", choices=["rotate", "stats"],
                        help="Action to perform")

    args = parser.parse_args()

    rotator = LogRotator()

    if args.action == "rotate":
        rotator.rotate_all_logs()
    elif args.action == "stats":
        stats = rotator.get_log_statistics()

        print("="*60)
        print("LOG STATISTICS")
        print("="*60)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"Compressed: {stats['compressed_files']}")
        print(f"Uncompressed: {stats['uncompressed_files']}")
        print()

        for dir_path, dir_stats in stats['by_directory'].items():
            print(f"{dir_path}:")
            print(f"  Files: {dir_stats['files']}")
            print(f"  Size: {dir_stats['size_mb']:.2f} MB")
            print(f"  Compressed: {dir_stats['compressed']}")
            print(f"  Uncompressed: {dir_stats['uncompressed']}")
            print()


if __name__ == "__main__":
    main()
