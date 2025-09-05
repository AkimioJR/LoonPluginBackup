from typing import Generator
from dataclasses import dataclass

from httpx import Client


@dataclass
class Resource:
    prefix: str
    plugin_prefix: str
    script_prefix: str
    jq_prefix: str
    urls: list[str]


def get_kelee_plugin_urls() -> list[str]:
    """
    从可莉github中提取表格中的插件URL
    """
    URL = "https://99z.top/https://hub.kelee.one/list.json"
    headers = {
        "Referer": "https://hub.kelee.one/",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
    }
    urls: list[str] = []
    with Client(headers=headers) as client:
        response = client.get(URL)
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(response)
            return []

    for item in response.json().get("lists", []):
        url = item.get("url", "").replace("loon://import?plugin=", "")
        if url:
            urls.append(url)

    return urls


def get_sources() -> Generator[Resource]:
    yield Resource(
        prefix="kelee",
        plugin_prefix="https://kelee.one/Tool/Loon/",
        script_prefix="https://kelee.one/Resource/",
        jq_prefix="https://kelee.one/Resource/",
        urls=get_kelee_plugin_urls(),
    )


if __name__ == "__main__":
    # 提取插件URL
    urls = get_kelee_plugin_urls()
    print(f"找到 {len(urls)} 个插件URL:")
    for url in urls:
        print(url)
