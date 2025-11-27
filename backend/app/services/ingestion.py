from pathlib import Path
from typing import Iterable
import mimetypes

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None


class IngestionService:
    """
    Handles file validation, basic security checks, and low-level file-type
    identification (Step 2 of the methodology: File Type Identification).
    """

    allowed_extensions: set[str] = {
        ".jpg",
        ".jpeg",
        ".png",
        ".pdf",
        ".txt",
        ".mp4",
    }

    def validate(self, artifact_path: Path) -> dict[str, str]:
        """
        Perform lightweight validation and classify the raw file type using:
        - Extension
        - Python mimetypes
        - Magic-byte header inspection (python-magic)
        """
        extension = artifact_path.suffix.lower()
        mime_guess, _ = mimetypes.guess_type(str(artifact_path))
        
        # Try to get magic type, fallback to mime_guess if magic not available
        if MAGIC_AVAILABLE and magic:
            try:
                magic_type = magic.from_file(str(artifact_path), mime=True)
            except Exception:
                magic_type = mime_guess
        else:
            magic_type = mime_guess

        # Decide high-level bucket used by the rest of the pipeline
        if magic_type and magic_type.startswith("image/"):
            high_level_type = "image"
        elif magic_type and magic_type in {"application/pdf"}:
            high_level_type = "document"
        elif magic_type and magic_type.startswith("video/"):
            high_level_type = "video"
        else:
            high_level_type = "other"

        status = "accepted" if extension in self.allowed_extensions else "needs_review"

        return {
            "filename": artifact_path.name,
            "extension": extension,
            "mime_guess": mime_guess or "unknown",
            "magic_type": magic_type or "unknown",
            "high_level_type": high_level_type,
            "status": status,
        }

    def chunk_files(self, artifact_path: Path) -> Iterable[Path]:
        """
        For now, we treat each upload as a single artifact.
        This can be extended to unzip folders or split videos into frames.
        """
        yield artifact_path

