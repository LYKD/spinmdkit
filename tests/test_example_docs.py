import re
from pathlib import Path


def _fenced_blocks(markdown: str) -> list[str]:
    return re.findall(r"```(?:bash|text)\n(.*?)\n```", markdown, flags=re.DOTALL)


def test_example_index_and_cases_have_bilingual_readmes():
    examples_root = Path(__file__).resolve().parents[1] / "examples"
    case_dirs = sorted(
        path for path in examples_root.iterdir() if path.is_dir() and not path.name.startswith(".")
    )

    assert case_dirs, "at least one example case is required"

    missing = {
        directory.relative_to(examples_root).as_posix() or ".": [
            filename
            for filename in ("README.md", "README.zh-CN.md")
            if not (directory / filename).is_file()
        ]
        for directory in (examples_root, *case_dirs)
    }
    missing = {directory: files for directory, files in missing.items() if files}

    assert not missing, f"example documentation must be bilingual: {missing}"

    for directory in (examples_root, *case_dirs):
        english = (directory / "README.md").read_text(encoding="utf-8")
        chinese = (directory / "README.zh-CN.md").read_text(encoding="utf-8")
        assert 'href="README.zh-CN.md"' in english
        assert 'href="README.md"' in chinese
        assert _fenced_blocks(english) == _fenced_blocks(chinese)
