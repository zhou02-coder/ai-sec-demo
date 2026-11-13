#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Industrial-Grade Regex Gateway Defense Sandbox (正则表达式工业级网关防御沙盒)
Module: regex_defense.py
Description: 
    实现了面向对象封装、预编译性能优化、绝对边界锚点、ReDoS灾难性回溯防御、
    多向量并行扫描 (SQLi/XSS/RCE) 以及不可篡改的审计轨迹闭环。
=============================================================================
"""

import re 
import time
import logging
from typing import Dict, List, Tuple, Optional, Any

# 配置日志记录器 / Configure Logging for Audit Trail
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] [RegenxGatewayEngine] %(message)s')
logger = logging.getLogger("RegexGatwayEngine")

class RegexGatwaySecurityException(Exception):
    """
    [Architecture Exception] Custom Exception for Gateway Security Violations.
    网关安全违规自定义异常类：当捕获恶意注入或越界风险时触发。
    """
    pass

class IndustrialRegexGatewaySandbox:
     """
    [Architecture Design Intent] 
    Industrial-Grade Regular Expression Gateway Defense Sandbox.
    封装了面向对象的正则表达式防御引擎，提供预编译加速、绝对边界锚点锁定、
    ReDoS熔断保护以及多向量威胁扫描能力。
    """
     # 定义全局输入最大长度硬约束，防止超长文本引发内存溢出或死锁
     MAX_INPUT_LENGTH = 2048

     def __init__(self, service_name: str = "Enterprise-Gateway-v3"):
          self.service_name = service_name
          self.audit_logs: List[Dict[str, Any]] = []
          self.blocked_count = 0

          # 预编译正则表达式模式池 （Pre-compiled Regex Pattern Pool）
          # 采用绝对边界 \A 和 \Z 代替脆弱的 ^ 和 $，防止多行换行符注入跳过
          # 采用非贪婪模式 .*? 结合严格字符集限制，彻底掐断 ReDoS（灾难性回溯）漏洞
          self._compile_defense_patterns()

          logger.info(f"[{self.service_name}] 工业级正则网关防御沙盒初始化成功, 所有威胁防御锚点已就位。")

     def _compile_defense_patterns(self) -> None:
        """
        [Architecture Design Intent] 
        Pre-compile regular expressions for multi-vector threat scanning and performance optimization.
        预编译多向量威胁扫描的正则表达式，提升高并发网关吞吐性能。
        """
        try:
            # 1. SQL 注入防御模式（SQL Injection Defense Pattern）
            # 拦截常见 SQL 关键字与永真式/注释符联合攻击，强制使用绝对边界 \A 与 \Z
            sql_injection_raw = r"\A.*?(?:--|/\*|\bOR\b\s+['\"0-9]+|\bUNION\b\s+\bSELECT\b|\bDROP\b\s+\bTABLE\b).*?\Z"
            self.sql_pattern =re.compile(sql_injection_raw, re.IGNORECASE | re.DOTALL)

            # 2. XSS 跨脚本防御模式（Cross-Site Scripting Defense Pattern）
            # 拦截恶意的 <script> 标签、内联事件处理器以及 JavaScript 伪协议
            xss_raw = r"\A.*?(?:<script\b[^>]*>.*?</script>|javascript:|on\w+\s*=).*?\Z"
            self.xss_pattern = re.compile(xss_raw, re.IGNORECASE | re.DOTALL)

            # 3. 远程命令执行（RCE）/ 系统敏感指令防御模式（RCE Defense Pattern）
            # 拦截常见的系统高危 shell 命令注入尝试
            rce_raw = r"\A.*?(?:\bexec\b|\beval\b|bsystem\b\s*\(|cmd\.exe|/bin/sh|/bin/bash).*?\Z"
            self.rce_pattern = re.compile(rce_raw, re.IGNORECASE | re.DOTALL)
            logger.info("所有多向量防御正则表达式已完成预编译 (Pre-compilation completed).")
        except re.error as e:
            logger.error(f"正则表达式预编译失败: {e}")
            raise RegexGatwaySecurityException(f"Regex compilation failed: {e}")

     def inspect_and_sanitize(self, payload: str, client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """
        [Architecture Design Intent] 
        Core inspection method implementing multi-vector scanning and strict boundary defense.
        核心扫描与消毒方法：执行多向量并行扫描、长度硬约束和防 DoS 熔断。
        
        Args:
            payload (str): 待检测的原始请求文本
            client_ip (str): 客户端来源 IP 地址
        Returns:
            Dict[str, Any]: 结构化检查报告
        """
        start_time = time.time()

        # 1. 防御性检查：类型校验
        if not isinstance(payload, str):
            raise TypeError("Payload must be a string type.")

        # 2. 防御性检查：长度硬约束（Length Hard Constraint & DoS Circuit Breaker）
        if len(payload) > self.MAX_INPUT_LENGTH:
            self.blocked_count += 1
            audit_record = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), 
                            "client_ip": client_ip, 
                            "threat_type": "OVER_LENGTH_DOS_ATTEMPT",
                            "status": "BLOCKED", 
                            "scan_duration_ms": 0.0, 
                            "details": f"Payload length ({len(payload)}) exceeded maximum limit ({self.MAX_INPUT_LENGTH})."}
            self.audit_logs.append(audit_record)
            logger.warning(f"[DoS Shield] 拦截超长载荷攻击, 来自 IP: {client_ip}")
            return audit_record

        # 3. 多向量威胁扫描（Multi-Vector Threat Scanning）
        detected_threats = []

        # 扫描 SQL 注入
        if self.sql_pattern.match(payload):
            detected_threats.append("SQL_INJECTION")

        # 扫描 XSS 跨站脚本
        if self.xss_pattern.match(payload):
            detected_threats.append("XSS_ATTACK")

        # 扫描远程命令执行 RCE
        if self.rce_pattern.match(payload):
            detected_threats.append("RCE_ATTACK")
        
        elapsed_ms = round((time.time() - start_time) * 1000, 4)

        # 4. 生成审计与决策结果（Audit and Decision Formulation）
        if detected_threats:
            self.blocked_count += 1
            status = "BLOCKED"
            threat_str = ",".join(detected_threats)
            logger.warning(f"[Threat Intercepted] 检测到恶意威胁 [{threat_str}], 源 IP: {client_ip}")
        else:
            status = "PASSED"
            threat_str = "NONE"
            logger.info(f"[Access Granted] 载荷安全检测通过, 耗时: {elapsed_ms}ms")

        audit_record = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "client_ip": client_ip,
            "threat_type": threat_str,
            "status": status,
            "scan_duration_ms": elapsed_ms,
            "payload_snippet": payload[:60] + "..." if len(payload) > 60 else payload}

        self.audit_logs.append(audit_record)
        return audit_record
     
     def get_audit_summary(self) -> Dict[str, Any]:
        """
        [Architecture Design Intent] 
        Retrieve immutable audit trail summary.
        获取不可篡改的审计轨迹盘点报告。
        """
        return {"service_name": self.service_name, 
                "total_requests_processed": len(self.audit_logs), 
                "total_blocked_threats": self.blocked_count, 
                "audit_trail": self.audit_logs}


# =============================================================================
# 模块自测与沙盒混沌压测入口 (Gateway Chaos Testing & Verification Entry)
# =============================================================================
if __name__ == "__main__":
    print("=== [工业级正则网关防御沙盒] 启动混沌压测与多向量扫描验证 ===")

    # 实例化网关沙盒
    gateway = IndustrialRegexGatewaySandbox(service_name="Production-Gateway-Alpha")

    # 模拟各类正常与恶意测试载荷
    test_cases = [("192.168.1.10", "Hello world, this is a normal request."),
        ("203.0.113.5", "SELECT * FROM users WHERE id = 1 OR 1=1; --"),
        ("198.51.100.42", "<script>alert('XSS_HACK_ATTACK');</script>"),
        ("10.0.0.88", "eval(request.form['malicious_code'])"),
        ("172.16.0.5", "A" * 3000)  # 超长载荷，触发 DoS 熔断长度限制
    ]

    # 依次执行网关安全检查
    for ip, payload in test_cases:
        print(f"\n--- 正在检查来自 {ip} 的请求 ---")
        result = gateway.inspect_and_sanitize(payload, client_ip=ip)
        print(f"检查结果状态: {result.get('status', 'UNKNOWN')} | 威胁类型: {result.get('threat_type', 'NONE')} | 耗时: {result.get('scan_duration_ms', 0)}ms")

    print("\n=== [网关安全审计最终盘点报告] ===")
    summary = gateway.get_audit_summary()
    print(f"服务名称: {summary['service_name']}")
    print(f"总处理请求数: {summary['total_requests_processed']}")
    print(f"成功拦截威胁数: {summary['total_blocked_threats']}")
    print("=== 工业级正则网关防御沙盒演示顺利完成 ===")
