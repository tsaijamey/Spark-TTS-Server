import os
import unittest
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TestSparkTTSAPI():
    BASE_URL = "https://page.frago.ai/spark"
    API_KEY = os.getenv("API_KEY", "default_api_key")
    
    def test_basic_synthesis(self):
        """测试基本文本转语音功能"""
        url = f"{self.BASE_URL}/synthesize"
        headers = {"X-API-Key": self.API_KEY}
        files = {
            "text": (None, "你好，这是测试文本"),
            "output_format": (None, "mp3")
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, verify=False)
        except requests.exceptions.SSLError as e:
            print(f"SSL Error occurred: {e}")
            print("Trying with SSL verification disabled...")
            response = requests.post(url, headers=headers, files=files, verify=False)
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("audio_url", response.json())
        
    def test_project_based_synthesis(self):
        """测试带project_id的语音合成"""
        url = f"{self.BASE_URL}/synthesize"
        headers = {"X-API-Key": self.API_KEY}
        project_id = "test_project_123"
        files = {
            "text": (None, "这是项目测试文本"),
            "project_id": (None, project_id),
            "output_format": (None, "wav")
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, verify=False)
        except requests.exceptions.SSLError as e:
            print(f"SSL Error occurred: {e}")
            print("Trying with SSL verification disabled...")
            response = requests.post(url, headers=headers, files=files, verify=False)
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("audio_url", result)
        self.assertEqual(result.get("project_id"), project_id)
        
    def test_invalid_api_key(self):
        """测试无效API密钥"""
        url = f"{self.BASE_URL}/synthesize"
        headers = {"X-API-Key": "invalid_key"}
        files = {
            "text": (None, "无效密钥测试"),
            "output_format": (None, "mp3")
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, verify=False)
        except requests.exceptions.SSLError as e:
            print(f"SSL Error occurred: {e}")
            print("Trying with SSL verification disabled...")
            response = requests.post(url, headers=headers, files=files, verify=False)
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 401)
        
    def test_different_formats(self):
        """测试不同输出格式"""
        formats = ["mp3", "wav", "ogg"]
        url = f"{self.BASE_URL}/synthesize"
        headers = {"X-API-Key": self.API_KEY}
        
        for fmt in formats:
            with self.subTest(format=fmt):
                files = {
                    "text": (None, f"测试{fmt}格式"),
                    "output_format": (None, fmt)
                }
                try:
                    response = requests.post(url, headers=headers, files=files, verify=False)
                except requests.exceptions.SSLError as e:
                    print(f"SSL Error occurred: {e}")
                    print("Trying with SSL verification disabled...")
                    response = requests.post(url, headers=headers, files=files, verify=False)
                print(f"Response: {response.json()}")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["audio_url"].endswith(fmt))

if __name__ == "__main__":
    test = TestSparkTTSAPI
    test.test_basic_synthesis(test)