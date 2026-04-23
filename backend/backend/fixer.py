import ast
import os
import subprocess
import tempfile

def analyze_python(code: str):
    result = {
        "success": False,
        "language": "python",
        "errors": [],
        "fixed_code": code,
        "message": ""
    }

    try:
        ast.parse(code)
        result["success"] = True
        result["message"] = "No syntax errors found."
        return result
    except SyntaxError as e:
        result["errors"].append({
            "line": e.lineno,
            "offset": e.offset,
            "message": e.msg
        })

    fixed = auto_fix_python(code, result["errors"])
    result["fixed_code"] = fixed

    try:
        ast.parse(fixed)
        result["success"] = True
        result["message"] = "Syntax errors found and fixed automatically."
    except SyntaxError as e:
        result["message"] = "Syntax errors found. Auto-fix was not fully successful."
        result["errors"].append({
            "line": e.lineno,
            "offset": e.offset,
            "message": e.msg
        })

    return result


def auto_fix_python(code: str, errors: list):
    lines = code.splitlines()

    for err in errors:
        msg = err["message"].lower()
        line_no = err["line"]

        if not line_no or line_no > len(lines):
            continue

        i = line_no - 1
        line = lines[i]

        if "expected ':'" in msg and not line.rstrip().endswith(":"):
            lines[i] = line.rstrip() + ":"

        if "invalid syntax" in msg and line.strip().startswith("print ") and not line.strip().startswith("print("):
            content = line.strip()[6:]
            lines[i] = f"print({content})"

    return "\\n".join(lines)


def analyze_cpp(code: str):
    result = {
        "success": False,
        "language": "cpp",
        "errors": [],
        "fixed_code": code,
        "message": ""
    }

    fixed = auto_fix_cpp(code)

    with tempfile.TemporaryDirectory() as tmpdir:
        cpp_path = os.path.join(tmpdir, "main.cpp")
        exe_path = os.path.join(tmpdir, "main")

        with open(cpp_path, "w", encoding="utf-8") as f:
            f.write(fixed)

        try:
            proc = subprocess.run(
                ["g++", cpp_path, "-o", exe_path],
                capture_output=True,
                text=True
            )

            if proc.returncode == 0:
                result["success"] = True
                result["fixed_code"] = fixed
                result["message"] = "Compiled successfully."
                return result

            result["errors"].append({
                "message": proc.stderr
            })
            result["fixed_code"] = fixed
            result["message"] = "Compilation failed."
            return result

        except FileNotFoundError:
            result["errors"].append({
                "message": "g++ compiler not found. Install g++ first."
            })
            result["message"] = "Compiler missing."
            return result


def auto_fix_cpp(code: str):
    lines = code.splitlines()
    fixed_lines = []

    has_iostream = any("#include <iostream>" in line for line in lines)
    has_std = any("using namespace std;" in line for line in lines)

    if not has_iostream:
        fixed_lines.append("#include <iostream>")

    for line in lines:
        stripped = line.strip()

        if "cout" in stripped and "std::cout" not in stripped and not has_std:
            line = line.replace("cout", "std::cout")

        if "cin" in stripped and "std::cin" not in stripped and not has_std:
            line = line.replace("cin", "std::cin")

        if (
            stripped
            and not stripped.startswith("#")
            and not stripped.endswith(";")
            and not stripped.endswith("{")
            and not stripped.endswith("}")
            and "if" not in stripped
            and "for" not in stripped
            and "while" not in stripped
            and "main(" not in stripped
        ):
            if "cout" in stripped or "return" in stripped or "=" in stripped:
                line = line.rstrip() + ";"

        fixed_lines.append(line)

    return "\\n".join(fixed_lines)
