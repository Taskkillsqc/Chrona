"""
LLM 客户端模块 - V3 版本
支持多种 LLM 提供商和自定义配置
"""

import requests
import json
from typing import Dict, Any, Optional

class LLMClient:
    """统一的LLM客户端，支持多种提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_config = self._parse_config()
        
    def _parse_config(self) -> Dict[str, Any]:
        """解析配置，支持新旧格式"""
        # 优先使用新的 llm 配置
        if 'llm' in self.config:
            llm_config = self.config['llm']
            
            # 如果启用了自定义配置
            if llm_config.get('custom', {}).get('enabled', False):
                return {
                    'provider': 'custom',
                    'url': llm_config['custom']['url'],
                    'model': llm_config['custom']['model'],
                    'headers': llm_config['custom'].get('headers', {}),
                    'payload_format': llm_config['custom'].get('payload_format', 'openai'),
                    'response_format': llm_config['custom'].get('response_format', 'openai'),
                    'timeout': llm_config['custom'].get('timeout', 30),
                    'parameters': llm_config.get('parameters', {})
                }
            else:
                # 使用预设提供商
                provider = llm_config.get('provider', 'gemini')  # 默认 gemini
                api_key = llm_config.get('api_key')
                
                # 检查 API 密钥是否存在
                if not api_key:
                    print(f"⚠️ 警告: {provider} 提供商的 API 密钥未配置")
                
                return {
                    'provider': provider,
                    'api_key': api_key,
                    'parameters': llm_config.get('parameters', {}),
                    'timeout': 30
                }
        else:
            # 向后兼容旧配置
            provider = self.config.get('model', 'gemini')  # 默认 gemini
            api_key = self.config.get('api_key')
            
            # 检查 API 密钥是否存在
            if not api_key:
                print(f"⚠️ 警告: {provider} 提供商的 API 密钥未配置")
            
            return {
                'provider': provider,
                'api_key': api_key,
                'parameters': {},
                'timeout': 30
            }
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """生成回复"""
        try:
            if self.llm_config['provider'] == 'gemini':
                return self._call_gemini(prompt)
            elif self.llm_config['provider'] == 'deepseek':
                return self._call_deepseek(prompt)
            elif self.llm_config['provider'] == 'openai':
                return self._call_openai(prompt)
            elif self.llm_config['provider'] == 'custom':
                return self._call_custom(prompt)
            else:
                return {"error": f"不支持的提供商: {self.llm_config['provider']}"}
                
        except Exception as e:
            return {"error": f"LLM调用失败: {str(e)}"}
    
    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """调用 Gemini API"""
        api_key = self.llm_config.get('api_key')
        if not api_key:
            return {"error": "Gemini API密钥未配置"}
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.llm_config['parameters'].get('temperature', 0.7),
                "maxOutputTokens": self.llm_config['parameters'].get('max_tokens', 1000),
                "topP": self.llm_config['parameters'].get('top_p', 0.9)
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=self.llm_config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "text": text}
        else:
            return {"error": f"Gemini API请求失败: {response.status_code}", "raw": response.text}
    
    def _call_deepseek(self, prompt: str) -> Dict[str, Any]:
        """调用 DeepSeek API"""
        api_key = self.llm_config.get('api_key')
        if not api_key:
            return {"error": "DeepSeek API密钥未配置"}
            
        url = "https://api.deepseek.com/chat/completions"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.llm_config['parameters'].get('temperature', 0.7),
            "max_tokens": self.llm_config['parameters'].get('max_tokens', 1000),
            "top_p": self.llm_config['parameters'].get('top_p', 0.9)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=self.llm_config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            return {"success": True, "text": text}
        else:
            return {"error": f"DeepSeek API请求失败: {response.status_code}", "raw": response.text}
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """调用 OpenAI API"""
        api_key = self.llm_config.get('api_key')
        if not api_key:
            return {"error": "OpenAI API密钥未配置"}
            
        url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.llm_config['parameters'].get('temperature', 0.7),
            "max_tokens": self.llm_config['parameters'].get('max_tokens', 1000),
            "top_p": self.llm_config['parameters'].get('top_p', 0.9)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=self.llm_config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            return {"success": True, "text": text}
        else:
            return {"error": f"OpenAI API请求失败: {response.status_code}", "raw": response.text}
    
    def _call_custom(self, prompt: str) -> Dict[str, Any]:
        """调用自定义 API"""
        url = self.llm_config.get('url')
        if not url:
            return {"error": "自定义API URL未配置"}
        
        # 构建请求头
        headers = {"Content-Type": "application/json"}
        custom_headers = self.llm_config.get('headers', {})
        headers.update(custom_headers)
        
        # 构建请求体
        payload_format = self.llm_config.get('payload_format', 'openai')
        
        if payload_format == 'openai':
            payload = {
                "model": self.llm_config.get('model', 'gpt-3.5-turbo'),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.llm_config['parameters'].get('temperature', 0.7),
                "max_tokens": self.llm_config['parameters'].get('max_tokens', 1000),
                "top_p": self.llm_config['parameters'].get('top_p', 0.9)
            }
        else:
            # 自定义格式，用户需要在配置中定义
            payload = {
                "prompt": prompt,
                "model": self.llm_config.get('model'),
                **self.llm_config['parameters']
            }
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=self.llm_config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # 解析响应
            response_format = self.llm_config.get('response_format', 'openai')
            
            if response_format == 'openai':
                text = data['choices'][0]['message']['content']
            else:
                # 自定义响应格式，尝试常见字段
                text = data.get('text') or data.get('content') or data.get('response')
                if not text:
                    return {"error": "无法解析自定义API响应", "raw": data}
            
            return {"success": True, "text": text}
        else:
            return {"error": f"自定义API请求失败: {response.status_code}", "raw": response.text}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        return {
            "provider": self.llm_config['provider'],
            "model": self.llm_config.get('model', 'N/A'),
            "url": self.llm_config.get('url', 'N/A'),
            "parameters": self.llm_config.get('parameters', {})
        }
