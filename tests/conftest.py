import os
import sys

# бот открывает базы по путям ../db относительно папки code — запускаем как в проде, но во временной папке
import tempfile

ROOT = tempfile.mkdtemp()
os.makedirs(os.path.join(ROOT, "code"))
os.chdir(os.path.join(ROOT, "code"))
os.environ.setdefault("BOT_TOKEN", "123456:TEST")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
