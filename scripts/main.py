import shutil
import argparse

from pathlib import Path

from source import get_sources, Resource
from download import download_data
from parse import parse_script_url, parse_jq_url, parse_script_time
from version import get_current_tag, has_file_changed, get_tag_when_file_last_modified

REPO = "Akimio521/LoonPluginBackup"

PROJECT_ROOT = Path(__file__).parent.parent  # 项目根目录


TAG = get_current_tag()
REPO_RAW_URL_PREFIX = f"https://raw.githubusercontent.com/{REPO}"


def proccess_source(resource: Resource, clean: bool) -> None:
    print(f"来源: {resource.prefix} 找到 {len(resource.urls)} 个插件URL")
    base_path = PROJECT_ROOT / resource.prefix

    if clean:
        print(f"清理旧目录: {base_path}")
        if base_path.exists():
            shutil.rmtree(base_path)  # 删除旧目录及其内容
        base_path.mkdir(parents=True, exist_ok=True)  # 创建新目录

    # 下载并解析每个插件
    for plugin_url in resource.urls:
        if not plugin_url.startswith("https://kelee.one/Tool/Loon/"):
            print(
                f"插件 URL: {plugin_url} 不含前缀: {resource.plugin_prefix}，跳过处理"
            )
            continue

        print(f"正在处理插件: {plugin_url}")
        plugin_content = download_data(plugin_url)
        plugin_path = base_path / plugin_url.replace(resource.plugin_prefix, "")
        plugin_path.parent.mkdir(parents=True, exist_ok=True)
        if plugin_path.exists():
            with open(plugin_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            old_time = parse_script_time(existing_content)
            new_time = parse_script_time(plugin_content)
            if old_time and new_time and old_time == new_time:
                print(f"插件 {plugin_path} 的更新时间未变化，跳过处理")
                continue

        for script_url in parse_script_url(plugin_content):
            if not script_url.startswith(resource.script_prefix):
                print(
                    f"JS 脚本 URL: {script_url} 不含前缀: {resource.script_prefix}，跳过处理"
                )
                continue

            script_dest = script_url.replace(resource.script_prefix, "")
            script_path = base_path / script_dest
            print(f"将 JS 脚本 {script_url.split('/')[-1]} 下载到 {script_path}")
            script_content = download_data(script_url)
            script_path.parent.mkdir(parents=True, exist_ok=True)

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            if has_file_changed(PROJECT_ROOT, script_path):
                print(f"JS 脚本 {script_dest} 已修改，保存到 {script_path}")
                new_script_url = (
                    f"{REPO_RAW_URL_PREFIX}/{TAG}/{resource.prefix}/{script_dest}"
                )
            else:
                old_tag = get_tag_when_file_last_modified(PROJECT_ROOT, script_path)
                new_script_url = (
                    f"{REPO_RAW_URL_PREFIX}/{old_tag}/{resource.prefix}/{script_dest}"
                )

            plugin_content = plugin_content.replace(script_url, new_script_url)
            print(f"将插件中的 JS 脚本路径 「{script_url}」替换为 「{new_script_url}」")

            for jq_url in parse_jq_url(plugin_content):
                if not jq_url.startswith(resource.jq_prefix):
                    print(
                        f"JQ 脚本 URL: {jq_url} 不含前缀: {resource.jq_prefix}，跳过处理"
                    )
                    continue

                jq_dest = jq_url.replace(resource.jq_prefix, "")
                jq_path = base_path / jq_dest
                print(f"将 JQ 脚本 {jq_url.split('/')[-1]} 下载到 {jq_path}")
                jq_content = download_data(jq_url)
                jq_path.parent.mkdir(parents=True, exist_ok=True)

                with open(jq_path, "w", encoding="utf-8") as f:
                    f.write(jq_content)

                if has_file_changed(PROJECT_ROOT, jq_path):
                    print(f"JQ 脚本 {jq_dest} 已修改，保存到 {jq_path}")
                    new_jq_url = (
                        f"{REPO_RAW_URL_PREFIX}/{TAG}/{resource.prefix}/{jq_dest}"
                    )
                else:
                    old_tag = get_tag_when_file_last_modified(PROJECT_ROOT, jq_path)
                    new_jq_url = (
                        f"{REPO_RAW_URL_PREFIX}/{old_tag}/{resource.prefix}/{jq_dest}"
                    )

            plugin_content = plugin_content.replace(jq_url, new_jq_url)
            print(f"将插件中的 JQ 脚本路径 「{jq_url}」替换为 「{new_jq_url}」")

        # 保存修改后的插件内容
        with open(plugin_path, "w", encoding="utf-8") as f:
            f.write(plugin_content)
        print(f"插件已保存到: {plugin_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clean", help="清理已有文件", action="store_true")
    args = parser.parse_args()
    for resource in get_sources():
        proccess_source(resource, args.clean)
