# GitHub Actions 设置指南

本项目已配置 GitHub Actions 来自动运行单元测试和生成代码覆盖率报告。

## 工作流说明

### 主要工作流文件

1. **`.github/workflows/ci.yml`** - 主要的CI工作流
   - 在推送到 `main`, `develop`, `feature_*` 分支时触发
   - 在创建针对 `main`, `develop` 分支的 Pull Request 时触发
   - 运行 Python 3.12 的测试
   - 生成覆盖率报告并上传到 Codecov

2. **`.github/workflows/test-coverage.yml`** - 更全面的测试和覆盖率工作流
   - 支持多个 Python 版本 (3.12, 3.13)
   - 包含覆盖率徽章生成功能
   - 定期运行测试 (每周日)

## 设置步骤

### 1. Codecov 设置

1. 访问 [Codecov](https://codecov.io/) 并使用 GitHub 账户登录
2. 找到您的 `lumi_filter` 仓库并启用它
3. 获取 Codecov Token
4. 在 GitHub 仓库设置中添加以下 Secret：
   - `CODECOV_TOKEN`: 您的 Codecov token

### 2. 覆盖率徽章设置 (可选)

如果您想使用动态覆盖率徽章，需要额外设置：

1. 创建一个 GitHub Gist 来存储徽章数据
2. 生成一个 Personal Access Token 并赋予 gist 权限
3. 在仓库设置中添加以下 Secrets：
   - `GIST_SECRET`: 您的 Personal Access Token
   - `GIST_ID`: 您创建的 Gist 的 ID

### 3. README 中添加徽章

在您的 README.md 中添加以下徽章：

```markdown
<!-- GitHub Actions Badge -->
![CI](https://github.com/chaleaoch/lumi_filter/workflows/CI%20Tests%20and%20Coverage/badge.svg)

<!-- Codecov Badge -->
[![codecov](https://codecov.io/gh/chaleaoch/lumi_filter/branch/main/graph/badge.svg)](https://codecov.io/gh/chaleaoch/lumi_filter)

<!-- Dynamic Coverage Badge (如果设置了 Gist) -->
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/lumi-filter-coverage.json)
```

## 覆盖率配置

项目的覆盖率配置在 `pyproject.toml` 中：

- 源代码目录: `lumi_filter`
- 排除文件: 测试文件、缓存文件等
- 最低覆盖率要求: 70% (可在 CI 工作流中调整)
- HTML 报告输出目录: `htmlcov`

## 本地测试

您可以在本地运行相同的测试命令：

```bash
# 安装依赖
uv sync --dev

# 运行测试和覆盖率
uv run pytest --cov=lumi_filter --cov-report=xml --cov-report=html --cov-report=term-missing

# 查看 HTML 覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 故障排除

1. **测试失败**: 检查测试代码和依赖是否正确安装
2. **覆盖率上传失败**: 确认 `CODECOV_TOKEN` 设置正确
3. **徽章不显示**: 检查 Gist 设置和权限

## 工作流特性

- ✅ 自动运行单元测试
- ✅ 生成详细的覆盖率报告
- ✅ 上传覆盖率数据到 Codecov
- ✅ 保存 HTML 覆盖率报告为构建产物
- ✅ 支持多种触发条件
- ✅ 覆盖率阈值检查
- ✅ 构建状态徽章
