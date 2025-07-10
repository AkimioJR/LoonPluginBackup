from httpx import Client

UA = "Loon/853 CFNetwork/3826.500.111.2.2 Darwin/24.4.0"


def download_data(url: str) -> str:
    """
    下载指定的loon资源
    :param url: 下载链接
    """
    with Client() as client:
        response = client.get(url, headers={"User-Agent": UA})

    return response.text


if __name__ == "__main__":
    # 示例插件URL
    example_url = "https://kelee.one/Tool/Loon/Lpx/NeteaseCloudMusic_remove_ads.lpx"

    # 下载插件
    plugin_content = download_data(example_url)

    # 打印插件内容
    print(plugin_content)
    with open("NeteaseCloudMusic_remove_ads.lpx", "w", encoding="utf-8") as f:
        f.write(plugin_content)
