# Hermes QQBot 社群运营补丁

[English](README.en.md)

这是一个针对 [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) 的版本化补丁，用于增强官方 QQBot 适配器，使其更适合 QQ 群社群运营。

它不是独立机器人运行时。消息会话、工具调用、记忆、消息队列、`NO_REPLY` 静默机制、Gateway 生命周期和 Dashboard 都继续由 Hermes 提供。

## 主要功能

- 接收普通 `GROUP_MESSAGE_CREATE` 群消息，不再仅限于 `@` 机器人。
- 每个 QQ 群使用一个共享 Agent 会话，同时保留每条消息的发送者身份。
- 基于 OpenID 的严格群与群主白名单。
- 固定目标的“群主私聊转发到群”和“群内通知群主私聊”工具。
- 群聊与 C2C 主动消息显式路由，包含 Gateway 停机通知。
- 可选 HTTPS 昵称解析，带 TTL 缓存、失败负缓存、并发单飞和昵称安全清洗。
- 非授权群和非授权私聊静默拒绝，不创建 Session、不进入模型。
- Hermes Dashboard 图形化配置：`Channels > QQBot > Configure`。
- 授权、并发、队列、去重、静默、API 路由和配置写入回归测试。

## 环境要求

- Hermes Agent 的 Git checkout。
- Hermes 本身所需的 Python 和 Node.js 环境。
- 一个 QQ 开放平台官方机器人应用，以及对应的 App ID 和 Client Secret。

## 安装

```bash
git clone https://github.com/bilieebiliee1-design/hermes-qqbot-community-patch.git
python hermes-qqbot-community-patch/install.py /path/to/Hermes-Agent
```

安装器会先执行 `git apply --check`。如果当前 Hermes 版本与补丁不兼容，安装会停止，不会自动进行模糊冲突合并。

仅应用补丁、暂时跳过测试：

```bash
python install.py /path/to/Hermes-Agent --skip-tests
```

## 图形化配置

1. 启动 Dashboard：`hermes dashboard`。
2. 打开 **Channels**。
3. 选择 **QQBot > Configure**。
4. 输入 QQBot App ID 和 Client Secret。
5. 填写允许私聊控制机器人的用户 OpenID。
6. 填写目标群 OpenID。
7. 填写唯一群主 OpenID。
8. 将私聊策略和群策略设为 `Allowlist`。
9. 将普通群消息模式设为 `Dispatch all messages`。
10. 根据需要启用昵称解析和 Markdown。
11. 保存并重启 Gateway。

行为配置写入 `config.yaml`，凭据写入 `.env`。项目不会把 Client Secret 写入普通配置文件。

手动配置示例见 [config.example.yaml](config.example.yaml)。

## 安全模型

- 未授权消息在附件处理、Session 创建和模型调用之前被拒绝。
- 群主权限仅由配置的 OpenID 决定。平台角色、昵称、引用内容和自称身份均不能授予权限。
- 跨会话发送工具使用固定目标，模型不能指定任意 QQ 用户或群。
- 群消息使用 Queue 模式，普通群聊不会中断正在进行的 Agent 任务。
- 昵称属于不可信展示数据，会清理换行、控制字符、双向文本控制符和身份分隔符，并限制长度。
- 主动发送超时会返回“投递状态未知”，不允许模型自动重试，避免重复消息。
- 昵称解析默认关闭。开启后会通过 HTTPS 向昵称服务发送成员 OpenID 和 App ID，并缓存返回结果。

提示词不是完整的安全隔离。面对不可信公开社群时，应关闭不必要的 Terminal、File、Browser 等高权限工具集。

## 验证

```bash
scripts/run_tests.sh \
  tests/gateway/test_qqbot.py \
  tests/tools/test_qqbot_messaging_tool.py \
  tests/hermes_cli/test_web_server.py -q

cd web
npm run check
npm run build
```

## 卸载

```bash
python uninstall.py /path/to/Hermes-Agent
```

卸载器只反向应用本项目补丁，不删除用户的 `config.yaml`、`.env` 或 QQBot 凭据。

## 升级

1. 使用 `uninstall.py` 移除旧补丁。
2. 更新 Hermes Agent。
3. 拉取本仓库最新版本。
4. 重新运行 `install.py`。

## 项目定位

长期建议拆分为两层：

- QQBot 协议、主动消息路由、共享群会话和 Dashboard 配置等通用能力，适合提交到 Hermes Agent 上游。
- 具体社群的人设、知识库、反馈收集和运营规则，适合放在独立 Hermes 插件中。

## 许可证

本项目采用 MIT License。Hermes Agent 保留其自身许可证和版权。
