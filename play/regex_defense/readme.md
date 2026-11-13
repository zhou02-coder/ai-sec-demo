# 【项目架构笔记】工业级正则表达式网关防御沙盒 (Regex Gateway Sandbox)

* **项目代号**: `regex_gateway_sandbox`
* **核心技术栈**: Python, Regular Expressions (re), OOP, Defensive Programming, Audit Trail
* **设计标准**: 预编译加速、绝对边界锚点、ReDoS 熔断防御、多向量威胁扫描

---

## 一、 核心架构设计意图

本项目的核心目标是构建一个**抗击打、高吞吐、防御闭环**的正则表达式网关沙盒。在面对复杂的网络攻击载荷（如 SQL 注入、XSS、RCE 及畸形 DoS 攻击）时，网关必须能够在入口处完成精准识别与熔断，绝不把风险放行至后端核心系统。

---

## 二、 四大核心防御支柱落地实现

### 1. 预编译机制 (`Pre-compilation Pool`)
* **实现机制**: 在类初始化 `__init__` 时通过 `re.compile()` 将所有威胁扫描规则预编译成字节码。
* **架构意义**: 避免高并发下每次请求重复解析正则表达式的性能损耗。

### 2. 绝对边界锚点 (`Absolute Boundary Anchors: \A 与 \Z`)
* **实现机制**: 强制采用 `\A`（整个字符串的绝对开头）和 `\Z`（整个字符串的绝对结尾）。
* **架构意义**: 彻底粉碎初学者使用 `^` 和 `$` 时容易被多行换行符（`\n`）注入绕过的漏洞。

### 3. ReDoS 与 DoS 熔断防御 (`Circuit Breaker & Length Hard Constraint`)
* **实现机制**: 所有通配符采用非贪婪模式 `.*?`，并在入口设置 `MAX_INPUT_LENGTH = 2048` 长度硬约束。
* **架构意义**: 杜绝恶意大文本引发的 CPU 灾难性回溯（ReDoS）或内存崩溃。

### 4. 多向量并行扫描与审计闭环 (`Multi-Vector Scanning & Audit Trail`)
* **实现机制**: 在同一条网关管道内并行检测 SQLi、XSS、RCE，并将所有放行或拦截记录写入不可篡改的结构化 `audit_logs` 中。

---

## 三、 关键踩坑与演进复盘 (Troubleshooting)

* **痛点问题**: 在混沌压测第 5 个测试用例（超长载荷 DoS 拦截）时，返回的审计字典漏掉了 `scan_duration_ms` 字段，且外部打印直接使用中括号查找，触发了 `KeyError: 'threat_type'` 崩溃。
* **终极解法**: 
  1. 统一网关内所有返回路径的字典结构，补齐基础字段。
  2. 外部读取时严格采用 `.get('key', default_value)` 进行安全取值，彻底消除崩溃隐患。

---

## 四、 混沌压测验证结果 (Chaos Testing Results)

在 5 个多向量测试用例（正常请求、SQLi、XSS、RCE、超长载荷）的压测中：
* **总处理请求数**: 5
* **成功拦截威胁数**: 4
* **运行状态**: 零报错，各向量精准拦截，审计链路完美闭环。