# 排除非技術文件指南

## 目標

抓取文檔時,僅保留純 CLI 操作知識,排除所有非技術性內容。

## 排除類型

### 社群與組織資訊

- 團隊介紹 (team, contributors, authors)
- 貢獻指南 (contributing, code of conduct)
- 外部資源連結 (external resources, community links)
- 贊助資訊 (sponsors, funding)

### 個人經驗分享

- 個人使用心得 (how I use, my workflow)
- 案例研究 (case studies, success stories)
- 訪談內容 (interviews)

### 非操作性內容

- 專案歷史與背景 (about, history, motivation)
- 路線圖與規劃 (roadmap, future plans)
- 版本發布說明 (changelog, release notes)
- 品牌資產 (logos, branding guidelines)

## 保留內容

### ✅ 核心技術文檔

- CLI 命令參考
- API 文檔
- 配置說明
- 架構設計

### ✅ 實用技術資源

- FAQ (技術問題)
- Troubleshooting (故障排除)
- Cookbook/Recipes (技術範例)
- Glossary (技術術語)

## 識別方法

檢查 URL 路徑或頁面標題,常見關鍵字:

- ❌ `/team`, `/about`, `/community`, `/contributing`
- ❌ `/blog`, `/news`, `/press`, `/media`
- ❌ `/how-i-use`, `/case-study`, `/testimonial`
- ❌ `/roadmap`, `/changelog`, `/release`
- ✅ `/cli`, `/api`, `/guide`, `/reference`
- ✅ `/faq`, `/troubleshooting`, `/cookbook`

## 實際案例 (mise)

**排除:**

```json
"/team.html",
"/contributing.html",
"/external-resources.html",
"/how-i-use-mise.html",
"/about.html"
```

**保留:**

```json
"/cli/",
"/dev-tools/",
"/environments/",
"/tasks/",
"/plugins/",
"/faq",
"/troubleshooting",
"/mise-cookbook/"
```
