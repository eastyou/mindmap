# mindmap

[![CI](https://github.com/eastyou/mindmap/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/mindmap/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

用缩进大纲生成 SVG 思维导图：写几行带缩进的文字，一条命令得到一张可投屏、可打印、可缩放的单文件 HTML。

不想打开复杂的脑图软件，也不想注册账号？用记事本写提纲就够了。零依赖，输出不引用任何外部资源。

## 特性

- **缩进即层级**：空格或 Tab 都可以，缩进单位自动识别
- **支持列表符号**：`-`、`*`、`•` 开头会自动去掉
- **自动布局**：父节点居中于子节点之间，同层节点不重叠
- **文字宽度估算**：中文按全角、英文按半角计算，节点不会挤在一起
- **按层配色**：根节点深色，往下依次是蓝、绿、橙、紫、红
- **单文件 HTML**：内嵌 SVG，断网可用，浏览器直接打开
- **A4 横向打印**：适合课堂讲义、复习提纲、项目规划
- **36 个单元测试**：大纲解析、布局坐标与 HTML 渲染

## 安装

```bash
pip install "git+https://github.com/eastyou/mindmap.git"
```

或者不安装直接运行：

```bash
git clone https://github.com/eastyou/mindmap.git
cd mindmap
python3 -m mindmap -i examples/outline.txt -o 思维导图.html
```

## 快速开始

新建 `outline.txt`：

```text
初中物理复习
  力学
    运动与静止
      参照物
      速度
    力
      重力
      摩擦力
  光学
    光的反射
    凸透镜成像
  电学
    串联与并联
    欧姆定律
```

生成页面：

```console
$ mindmap -i outline.txt -o 思维导图.html --title "初中物理复习"
已生成 思维导图.html：17 个节点，4 层
```

双击 HTML 即可查看；按 `Ctrl/Cmd + P`，选择 A4 横向，可以打印或导出 PDF。

## 大纲规则

- 第一行是根节点，不能缩进
- 用缩进表示层级，缩进单位由第一条缩进行决定（常见是 2 个或 4 个空格）
- 只能有一个根节点
- 每行最多比上一行多缩进一级，不能跳级
- 空行会被忽略
- 每个节点最多 20 个字，整张图最多 300 个节点、6 级
- 行首的 `- `、`* `、`• ` 会被去掉

正确示例：

```text
项目计划
  第一阶段
    需求调研
    竞品分析
  第二阶段
    原型设计
    开发排期
```

错误示例：

```text
项目计划
      需求调研
```

第一条缩进行缩进太多不是问题（会被当作第 1 级），但**从第 1 级直接跳到第 3 级**会报「缩进跳级」。

## 参数

| 参数 | 说明 |
| --- | --- |
| `-i, --input` | 大纲文本文件，必填，UTF-8 编码 |
| `-o, --output` | 输出 HTML，默认 `mindmap.html` |
| `--title` | 页面标题，默认「思维导图」 |

### 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 写入文件失败 |
| `2` | 文件、大纲或参数不合法 |

## 使用建议

- 节点文字尽量控制在 8 个字以内，图会更紧凑
- 一门课的复习提纲建议不超过 40 个节点，一页 A4 刚好
- 需要改配色时，编辑 `mindmap/render.py` 里的 `LEVEL_STYLES`
- 导出 PDF 时记得打开「背景图形」，否则节点只剩边框

## 开发与测试

```bash
python3 -m unittest discover -s tests -v
```

CI 覆盖 Python 3.9 ~ 3.13 与 Linux / macOS / Windows，并会用示例大纲实际生成一次页面。

## License

[MIT](LICENSE) © 2026 eastyou
