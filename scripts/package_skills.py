"""Build six standalone skills from the approved shared and lens sources."""

import argparse
import io
import json
import zipfile
from pathlib import Path


DESCRIPTIONS = {
    "design": "使用者呼叫 design 濾鏡時，檢查系統限制、上游選擇與下游成本，協助比較整體工程取捨。",
    "feedback": "使用者呼叫 feedback 濾鏡時，檢查假設到可信回饋的距離，協助選擇能辨別結果的下一步與停止點。",
    "evolve": "使用者呼叫 evolve 濾鏡時，追蹤具體需求的知識歸屬、共同變更理由與協調成本。",
    "simplicity": "使用者呼叫 simplicity 濾鏡時，檢查資料、責任與控制流程是否直接表達必要行為。",
    "reliability": "使用者呼叫 reliability 濾鏡時，檢查狀態、可行事件順序、重試與中斷是否守住系統承諾。",
    "performance": "使用者呼叫 performance 濾鏡時，沿實際執行與量測範圍比較可改善成本及必要工作。",
}


def split_document(path):
    title, body = path.read_text(encoding="utf-8").strip().split("\n", 1)
    return title.removeprefix("# "), body.strip()


def package(root, output, check=False):
    root, output = Path(root), Path(output)
    _, common = split_document(root / "drafts/common.md")
    license_text = (root / "LICENSE").read_bytes()
    files = {}
    for name, description in DESCRIPTIONS.items():
        title, lens = split_document(root / f"drafts/{name}.md")
        quoted_description = json.dumps(description, ensure_ascii=False)
        skill = (
            f"---\nname: {name}\ndescription: {quoted_description}\nlicense: MIT\n---\n\n"
            f"# {title}\n\n## 共用契約\n\n{common}\n\n{lens}\n"
        )
        interface = (
            f"interface:\n  display_name: {json.dumps(title, ensure_ascii=False)}\n"
            f"  short_description: {quoted_description}\n"
            "policy:\n  allow_implicit_invocation: false\n"
        )
        files[f"{name}/SKILL.md"] = skill.encode("utf-8")
        files[f"{name}/agents/openai.yaml"] = interface.encode("utf-8")
        files[f"{name}/LICENSE"] = license_text

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, content in sorted(files.items()):
            entry = zipfile.ZipInfo(relative, date_time=(2026, 9, 5, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content)

    expected = {output / "skills" / relative: content for relative, content in files.items()}
    expected[output / "masters-lenses.zip"] = buffer.getvalue()
    if check:
        differences = [str(path) for path, content in expected.items()
                       if not path.is_file() or path.read_bytes() != content]
        existing = {path for path in (output / "skills").rglob("*") if path.is_file()}
        differences += [str(path) for path in sorted(existing - set(expected))]
        if differences:
            raise ValueError("Package differs from approved sources: " + ", ".join(differences))
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        package(root, root / "dist", check=args.check)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    print("Six standalone skills: " + ("verified" if args.check else "packaged"))


if __name__ == "__main__":
    main()
