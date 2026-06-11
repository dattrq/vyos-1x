#!/usr/bin/env python3
#
# Kịch bản quản lý cấu hình dịch vụ Ndtechapp trên VyOS 1.5
#

import sys
from vyos.config import Config
from vyos.util import call

# Định nghĩa đường dẫn file cấu hình thực tế mà ứng dụng Ndtechapp cần đọc
CONFIG_FILE = '/etc/ndtechapp.conf'
SERVICE_NAME = 'ndtechapp'

def get_config(config=None):
    """Get NDTechApp configuration"""

    base = ['service', 'ndtechapp']

    if config:
        conf = config
    else:
        conf = Config()

    if not conf.exists(base):
        return None

    conf_data = {
        'interface': conf.get_string(base + ['interface'],
                                     default='wlan0'),

        'driver': conf.get_string(base + ['driver'],
                                  default='nl80211'),

        'ssid': conf.get_string(base + ['ssid'],
                                default='MyWiFiNetwork'),

        'country_code': conf.get_string(base + ['country-code'],
                                        default='VN'),

        'hw_mode': conf.get_string(base + ['hw-mode'],
                                   default='g'),

        'channel': conf.get_string(base + ['channel'],
                                   default='6'),

        'wpa': conf.get_string(base + ['security', 'wpa'],
                               default='2'),

        'wpa_passphrase':
            conf.get_string(base + ['security', 'passphrase'],
                            default='MySecretPassword'),

        'wpa_key_mgmt':
            conf.get_string(base + ['security', 'key-mgmt'],
                            default='WPA-PSK'),

        'rsn_pairwise':
            conf.get_string(base + ['security', 'rsn-pairwise'],
                            default='CCMP')
    }

    return conf_data

def verify(ndtechapp_config):
    """Giai đoạn 1: Kiểm tra tính hợp lệ của dữ liệu trước khi ghi (Verify)"""
    if ndtechapp_config is None:
        return

    # Ví dụ kiểm tra: Bắt buộc người dùng phải nhập SSID, không được để trống mặc định bừa bãi
    if not ndtechapp_config['ssid']:
        raise ValueError("Lỗi: Tên mạng 'ssid' không được để trống!")

def generate(ndtechapp_config):
    """Giai đoạn 2: Tạo nội dung file cấu hình văn bản (Generate)"""
    if ndtechapp_config is None:
        # Nếu người dùng xóa cấu hình, ta cũng xóa file cấu hình hệ thống
        import os
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        return

    # Sinh chuỗi cấu hình văn bản thô theo định dạng bạn yêu cầu
    config_text = f"""# --- Basic Configuration ---
interface={ndtechapp_config['interface']}
driver={ndtechapp_config['driver']}
ssid={ndtechapp_config['ssid']}
country_code={ndtechapp_config['country_code']}

# --- Radio/Frequency Settings ---
# hw_mode: a (5GHz), b/g (2.4GHz)
hw_mode={ndtechapp_config['hw_mode']}
channel={ndtechapp_config['channel']}

# --- Security Settings (WPA2/WPA3) ---
wpa={ndtechapp_config['wpa']}
wpa_passphrase={ndtechapp_config['wpa_passphrase']}
wpa_key_mgmt={ndtechapp_config['wpa_key_mgmt']}
rsn_pairwise={ndtechapp_config['rsn_pairwise']}
"""

    # Ghi nội dung trên vào file hệ thống thực tế
    with open(CONFIG_FILE, 'w') as f:
        f.write(config_text)

def apply(ndtechapp_config):
    """Giai đoạn 3: Áp dụng cấu hình và điều khiển dịch vụ hệ thống (Apply)"""
    if ndtechapp_config is None:
        # Nếu bị xóa cấu hình, dừng ứng dụng ngay lập tức
        try:
            call(f'systemctl stop {SERVICE_NAME}')
        except Exception:
            pass
        return

    # Nếu có cấu hình, thực hiện nạp lại (reload) hoặc khởi động lại (restart) dịch vụ hệ thống
    # VyOS sử dụng lệnh 'call' để chạy các lệnh terminal của Linux hệ thống
    try:
        # Kiểm tra xem dịch vụ có đang chạy không, nếu có thì reload/restart, nếu chưa thì start
        call(f'systemctl daemon-reload')
        call(f'systemctl restart {SERVICE_NAME}')
    except Exception as e:
        print(f"Cảnh báo: Không thể khởi chạy dịch vụ {SERVICE_NAME}. Lỗi: {e}")

if __name__ == '__main__':
    """Hàm chạy chính khi được VyOS Core gọi lúc Commit"""
    try:
        cfg = get_config()
        verify(cfg)
        generate(cfg)
        apply(cfg)
    except Exception as err:
        print(f"Config error: {err}")
        sys.exit(1)

