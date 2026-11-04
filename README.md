# 雀魂 Unity 立绘适配与安装恢复工具

A resource-specific portrait build and rollback pipeline for **Mahjong Soul / 雀魂**, with pixel readback and hash checks.

本项目作用于《雀魂／Mahjong Soul》的 Unity 角色立绘资源。当前收录亚丝娜初始全身图的 **872×1305** 适配流程：等比放入原画布，重建 Texture2D 与 Sprite 的矩形网格/UV，再核对纹理解码和 Sprite 解码后的像素。它不修改麻将规则、账号数据或服务端内容。

**仓库只有制作代码与示例输入契约，没有私人立绘、角色内容包、`.majset`、原版 bundle、账号信息或已安装状态文件。** 这是特定资源的源码流程，不是任意角色、任意游戏版本的通用补丁。

## 环境与文件

需要 Python 3、Pillow、numpy 和 UnityPy。脚本使用 `2022.3.62f2` 作为 Unity 解析回退版本。原流程面向本机 Steam 资源，当前游戏更新或其他平台需要重新确认对象结构和画布，不应直接绕过断言。

可先使用独立 Python 环境安装公开依赖：

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install UnityPy Pillow numpy
```

| 文件 | 用途 |
| --- | --- |
| `tools/fit.py` | 等比缩放用户自备透明图，放入872×1305画布，生成背景预览与边缘检查；不添加新的美术元素 |
| `tools/build_bundle.py` | 读取用户自己的原版/当前bundle，重建矩形网格与UV，验证对象ID及纹理/Sprite像素，生成候选资源和安装记录 |
| `tools/install_or_restore.py` | 根据本机生成的安装记录校验并原子安装或恢复 |
| `inputs/*.example.json` | 无个人路径或真实哈希的输入结构示例；不能直接拿来安装 |

## 准备自己的输入

1. 从自己的合法游戏副本提取对应 bundle，记录原版SHA256。`asset_path` 应为脚本当前支持的 `myassets/deco/character/yasina/full/full.png`。
2. 把两个 `.example.json` 复制为同目录的 `source-records.json` 与 `previous-install.json`，填入自己的文件路径与哈希。`source-records.json` 保存原版哈希；`previous-install.json` 保存当前已安装版本的哈希。若当前为原版，两者可填写同一原版哈希。
3. 自备 `inputs/replacement.png`。不要把未经确认的第三方安装记录指向自己的游戏文件。

这些实际输入文件、备份和输出已忽略，示例只说明格式，不包含可用的原资源或图片。

## 生成与校验

```sh
python3 tools/fit.py
python3 tools/build_bundle.py output/full_872x1305.png
```

`fit.py` 的比例、偏移和检查区域来自这一特定目标，不保证适合其他人物。图片不满足透明度、尺寸或放置边界时，应重新调整输入，不删除检查。构建工具会在本机 `backup/original/`、`backup/previous/` 保留原版与上一次安装资源，在 `output/candidate/` 写候选，并生成 `output/install-record.json`。

构建只读游戏源文件，不自动安装。脚本会处理输入包内的全部 Texture2D 与 Sprite，因此只能用于已经确认结构与本流程一致的单角色资源，不能对多角色合集包直接运行。输出验证包括对象ID/类型保持、Texture2D与Sprite像素回读、源文件哈希未变。

## 安装、恢复与退出游戏

先完全退出雀魂，并保留整个本地工作目录。安装器校验payload、当前游戏文件和已知原版/前次版本哈希，使用独占临时文件与原子替换；它不负责关闭游戏进程。

```sh
python3 tools/install_or_restore.py install
python3 tools/install_or_restore.py restore
```

安装记录只适用于生成它的那份资源版本。游戏更新、其他替换包或未知哈希都会导致拒绝覆盖。恢复依赖 `backup/original/`，不要删除它或套用他人的真实安装记录。

## 验证状态与其他角色

原亚丝娜v8记录包含纹理/Sprite像素回读和安装哈希，说明中仍要求重启后检查游戏画面。本次整理只做源码与临时合成文件测试，没有重新构建、安装或打开游戏。

原目录另有斋藤治、汪次郎、约瑟夫等素材与替换尝试；其中斋藤治v4说明明确尚未安装。这些私人内容与其他角色流程没有收录，不能把本仓库当成已经验证的多角色合集。

```sh
python3 -m unittest discover -s tests -v
```

公开范围只含代码与脱敏示例。游戏资源、角色权利及第三方依赖不因本仓库公开而获得再分发许可。
