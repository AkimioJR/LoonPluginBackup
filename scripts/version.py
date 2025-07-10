import subprocess
from datetime import datetime
from pathlib import Path


def get_last_time_tag(pr: Path, br: str = "main") -> str:
    """
    获取当前 HEAD 指向的 tag，如果没有 tag 则返回 br 分支
    """
    try:
        tag = (  # 首先尝试获取当前 HEAD 的确切 tag
            subprocess.check_output(
                ["git", "describe", "--exact-match", "--tags", "HEAD"],
                cwd=pr,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return tag
    except subprocess.CalledProcessError:
        try:
            tag = (  # 如果没有确切的 tag，获取最近的 tag
                subprocess.check_output(
                    ["git", "describe", "--tags", "--abbrev=0"],
                    cwd=pr,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            return tag
        except subprocess.CalledProcessError:
            return br  # 如果没有任何 tag，回退到 br 分支


def get_current_tag() -> str:
    return datetime.now().strftime("%Y%m%d")


def has_file_changed(project_root: Path, file_path: Path) -> bool:
    """
    检查文件是否有未提交的变化
    """
    try:
        result = (
            subprocess.check_output(
                ["git", "status", "--porcelain", file_path.as_posix()],
                cwd=project_root,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return bool(result)  # 如果有输出说明文件有变化
    except subprocess.CalledProcessError:
        return False


def get_tag_when_file_last_modified(project_root: Path, file_path: Path) -> str:
    """
    获取文件最后被修改时的 tag
    """
    try:
        last_commit = (  # 获取文件最后修改的提交 hash
            subprocess.check_output(
                ["git", "log", "-1", "--format=%H", "--", file_path.as_posix()],
                cwd=project_root,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        result = (  # 查找包含这个提交的最新 tag
            subprocess.check_output(
                ["git", "describe", "--tags", "--contains", last_commit],
                cwd=project_root,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        if "^" in result:  # 如果结果包含 ^ 符号，提取 tag 名称
            return result.split("^")[0]
        return result

    except subprocess.CalledProcessError:
        # 如果没有找到相关的 tag 或提交就指向上一次提交
        return get_last_time_tag(project_root)


if __name__ == "__main__":
    print(get_current_tag())
