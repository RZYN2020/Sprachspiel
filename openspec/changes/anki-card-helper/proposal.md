## Why

语言学习者在观看视频、阅读内容时，手动制作 Anki 单词卡流程繁琐且效率低下。现有工具要么功能单一，要么缺乏跨平台支持。需要一个统一、灵活的辅助工具，支持多种学习场景，减少制卡过程中的重复操作。

## What Changes

创建一个新的 Python 包 `sprachspiel`，提供以下新能力：

- **多数据源支持**：播放器（基于 mpv + Lua 脚本）、阅读器（PDF/EPUB/纯文本）、浏览器插件、CSV/文本文件导入
- **双模式 Anki 连接**：支持 AnkiConnect 实时推送和 .apkg 文件导出，可配置切换
- **增强服务集成**：可配置的词典 API、TTS API、AI 模型 API，支持自定义扩展
- **灵活的卡片生成**：支持实时模式和队列模式，自定义字段映射模板
- **HTTP 服务桥接**：为浏览器插件等客户端提供 HTTP API
- **可扩展架构**：字幕解析器、词典源、TTS 服务、AI 功能均支持用户自定义扩展

## Capabilities

### New Capabilities

- `card-generation`: 卡片生成核心引擎，包括字段映射、实时/队列两种生成模式
- `data-source-integration`: 多种数据源集成（播放器、阅读器、浏览器插件、文件导入）
- `enhancement-services`: 增强服务（词典查询、TTS 发音、AI 模型调用）
- `anki-connectivity`: Anki 连接层，支持 AnkiConnect 和文件导出两种方式
- `configuration-management`: 基于 YAML 的集中配置管理
- `subtitle-processing`: 多格式字幕解析（SRT/VTT/ASS），支持自定义扩展

### Modified Capabilities

（无）

## Impact

- 新增 Python 包 `sprachspiel`
- 依赖库：FastAPI（HTTP 服务）、python-mpv（播放器集成）、PyPDF2/pypdf（PDF 解析）、ebooklib（EPUB 解析）
- 新增组件：
  - Obsidian 插件
  - 浏览器插件（Chrome/Firefox/Edge）
  - mpv Lua 脚本（播放器集成）
- 新增配置文件：`config.yaml`（默认配置模板）
- 不影响现有代码，这是一个全新项目
