import re


def parse_script_url(data: str) -> list[str]:
    """
    从loon插件脚本中提取js脚本路径
    :param data: loon插件脚本内容
    :return: 提取到的脚本url列表
    """
    script_block_pattern = (
        r"\[Script\](.*?)(?=\[|\Z)"  # 匹配[Script]到下一个[或文件结束
    )
    script_block = re.search(script_block_pattern, data, re.DOTALL)

    if not script_block:
        return []

    # 从区块中提取所有script-path
    path_pattern = r"script-path=(https?://[^\s,]+)"
    paths = re.findall(path_pattern, script_block.group(1))

    return list(set(paths))  # 去重后返回


def parse_jq_url(data: str) -> list[str]:
    """
    从loon插件脚本中提取jq脚本路径
    :param data: loon插件脚本内容
    :return: 提取到的脚本url列表
    """
    # rewrite_block_pattern = (
    #     r"\[Rewrite\](.*?)(?=\[|\Z)"  # 匹配[Rewrite]到下一个[或文件结束
    # )
    # rewrite_block = re.search(rewrite_block_pattern, data, re.DOTALL)

    # if not rewrite_block:
    #     return []

    # 从区块中提取所有jq-path
    jq_path_pattern = r'jq-path="?(https?://[^\s,"]+)"?'
    paths = re.findall(jq_path_pattern, data)

    return list(set(paths))  # 去重后返回


def parse_script_time(data: str) -> str:
    """
    从loon插件尝试解析更新时间
    """
    pattern = r"#!date=(.+?)(?=\n|$)"
    match = re.search(pattern, data, re.DOTALL)
    return str(match.group(1)).strip() if match else ""


if __name__ == "__main__":
    from download import download_data

    data = download_data("https://kelee.one/Tool/Loon/Lpx/Bilibili_remove_ads.lpx")

    script_paths = parse_script_url(data)
    print("提取到的脚本路径:")
    for path in script_paths:
        print(path)

    print("\n提取到的JQ脚本路径:")
    for jq_url in parse_jq_url(data):
        print(jq_url)
