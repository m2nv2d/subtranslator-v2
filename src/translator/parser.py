import math
import srt
import aiofiles
import aiofiles.os

from translator.exceptions import ParsingError, ValidationError
from translator.models import SubtitleBlock

MAX_FILE_SIZE_MB = 2
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

async def parse_srt(file_path: str, chunk_max_blocks: int) -> list[list[SubtitleBlock]]:
    """Parses an SRT file from a given path, validates it, and chunks the content.

    Args:
        file_path: The path to the SRT file.
        chunk_max_blocks: The maximum number of subtitle blocks per chunk.

    Returns:
        A list of lists, where each inner list is a chunk of SubtitleBlock objects.

    Raises:
        ValidationError: If the file fails validation (extension, size).
        ParsingError: If the SRT content is malformed.
    """
    # Input File Validation
    if not file_path or not file_path.lower().endswith('.srt'):
        raise ValidationError("Invalid file type. Only .srt files are accepted.")

    # Check file size
    try:
        stat_result = await aiofiles.os.stat(file_path)
        file_size = stat_result.st_size
    except OSError as e:
        raise ValidationError(f"Could not access file: {e}")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"File size exceeds the limit of {MAX_FILE_SIZE_MB}MB.")

    if file_size == 0:
         raise ValidationError("File is empty.")

    # SRT Content Parsing
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = await f.read()
        parsed_subs = list(srt.parse(content))
    except FileNotFoundError:
        raise ParsingError(f"File not found: {file_path}")
    except Exception as e:
        raise ParsingError(f"Failed to parse SRT file '{file_path}': {e}") from e

    if not parsed_subs:
        return [] # Return empty list if the SRT file has no subtitles

    # Data Structure Mapping
    subtitle_blocks: list[SubtitleBlock] = []
    for sub in parsed_subs:
        block = SubtitleBlock(
            index=sub.index,
            start=sub.start,
            end=sub.end,
            content=sub.content,
            translated_content=None
        )
        subtitle_blocks.append(block)

    # Chunking Logic
    num_chunks = math.ceil(len(subtitle_blocks) / chunk_max_blocks)
    chunks = []
    for i in range(num_chunks):
        start_index = i * chunk_max_blocks
        end_index = start_index + chunk_max_blocks
        chunks.append(subtitle_blocks[start_index:end_index])

    return chunks
