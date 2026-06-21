"""
NotebookLM extraction helper for the content-synthesis skill.

Uses the unofficial notebooklm-py library to get richer content extraction
than raw transcript/article fetching alone. This is an optional enhancement —
the skill works without it, but produces better output when it's available.

Requirements:
  pip install notebooklm-py
  notebooklm login  # one-time browser-based Google auth

Usage:
  python notebooklm_extract.py <url_or_filepath> [--output-dir <dir>] [--formats summary,mindmap,sources]

Outputs JSON to stdout with extracted content. Also saves artifacts
(mind map JSON, etc.) to the output directory if specified.
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path


async def extract_content(source: str, output_dir: str | None = None, formats: list[str] | None = None):
    """
    Create a temporary notebook, add the source, extract content, then clean up.

    Args:
        source: URL (YouTube, article) or file path
        output_dir: Optional directory to save artifact files
        formats: List of extraction formats. Options: summary, mindmap, sources, chat
                 Defaults to all.
    """
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        return {
            "success": False,
            "error": "notebooklm-py not installed. Run: pip install notebooklm-py",
            "fallback": True
        }

    if formats is None:
        formats = ["summary", "mindmap", "sources"]

    result = {
        "success": False,
        "source": source,
        "title": None,
        "summary": None,
        "mindmap": None,
        "source_texts": [],
        "errors": []
    }

    try:
        async with await NotebookLMClient.from_storage() as client:
            # Create a temporary notebook for this extraction
            nb = await client.notebooks.create(f"_synthesis_tmp")

            try:
                # Add the source — detect type
                source_path = Path(source)
                if source_path.exists() and source_path.is_file():
                    await client.sources.add_file(nb.id, source, wait=True)
                elif source.startswith("http://") or source.startswith("https://"):
                    await client.sources.add_url(nb.id, source, wait=True)
                else:
                    # Treat as pasted text
                    await client.sources.add_text(nb.id, source, wait=True)

                # Extract summary via chat
                if "summary" in formats:
                    try:
                        chat_result = await client.chat.ask(
                            nb.id,
                            "Provide a comprehensive summary of this content. "
                            "Include: main topics covered, key arguments or methodology, "
                            "notable people/tools/frameworks mentioned, and the most "
                            "important takeaways. Be thorough but concise."
                        )
                        result["summary"] = chat_result.answer
                    except Exception as e:
                        result["errors"].append(f"Summary extraction failed: {str(e)}")

                # Extract mind map
                if "mindmap" in formats:
                    try:
                        mindmap = await client.artifacts.generate_mind_map(nb.id)
                        result["mindmap"] = mindmap

                        if output_dir:
                            os.makedirs(output_dir, exist_ok=True)
                            mindmap_path = os.path.join(output_dir, "mindmap.json")
                            with open(mindmap_path, "w") as f:
                                json.dump(mindmap, f, indent=2)
                    except Exception as e:
                        result["errors"].append(f"Mind map generation failed: {str(e)}")

                # Extract source full text
                if "sources" in formats:
                    try:
                        sources = await client.sources.list(nb.id)
                        for src in sources:
                            try:
                                text = await client.sources.get_text(nb.id, src.id)
                                result["source_texts"].append({
                                    "title": getattr(src, "title", "Unknown"),
                                    "text": text
                                })
                            except Exception:
                                pass
                    except Exception as e:
                        result["errors"].append(f"Source text extraction failed: {str(e)}")

                # Get notebook title (often derived from source)
                try:
                    nb_info = await client.notebooks.get(nb.id)
                    result["title"] = getattr(nb_info, "title", None)
                except Exception:
                    pass

                result["success"] = True

            finally:
                # Clean up the temporary notebook
                try:
                    await client.notebooks.delete(nb.id)
                except Exception:
                    result["errors"].append("Warning: couldn't delete temporary notebook. Clean up manually in NotebookLM.")

    except Exception as e:
        error_msg = str(e)
        if "credentials" in error_msg.lower() or "auth" in error_msg.lower():
            result["error"] = (
                "NotebookLM authentication failed. Run 'notebooklm login' to authenticate, "
                "then try again."
            )
        else:
            result["error"] = f"NotebookLM extraction failed: {error_msg}"
        result["fallback"] = True

    return result


def main():
    parser = argparse.ArgumentParser(description="Extract content via NotebookLM")
    parser.add_argument("source", help="URL or file path to extract from")
    parser.add_argument("--output-dir", help="Directory to save artifact files")
    parser.add_argument(
        "--formats",
        default="summary,mindmap,sources",
        help="Comma-separated list of formats: summary, mindmap, sources"
    )
    args = parser.parse_args()

    formats = [f.strip() for f in args.formats.split(",")]
    result = asyncio.run(extract_content(args.source, args.output_dir, formats))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
