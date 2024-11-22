import re
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Logging for debugging
logger = logging.getLogger(__name__)

# Khởi tạo trạng thái mặc định cho các thiết bị
device_status = {
    "đèn": {"status": "off", "brightness": 0},  # độ sáng từ 0 đến 100
    "quạt": {"status": "off", "speed": 1},      # mức gió 1, 2, 3
    "máy lạnh": {"status": "off", "temperature": 24}  # nhiệt độ mặc định là 24 độ C
}

# Dictionary ánh xạ từ đồng nghĩa cho tất cả các thiết bị
device_synonyms = {
    "bóng đèn": "đèn",
    "đèn điện": "đèn",
    "đèn bàn": "đèn",
    "quạt điện": "quạt",
    "quạt máy": "quạt",
    "quạt trần": "quạt",
    "điều hòa": "máy lạnh",
    "máy điều hòa": "máy lạnh"
}

def normalize_device_name(device: str) -> str:
    """Trả về tên chuẩn của thiết bị dựa vào từ đồng nghĩa."""
    return device_synonyms.get(device, device)

# Hành động bật thiết bị
class ActionTurnOnDevice(Action):
    def name(self) -> Text:
        return "action_turn_on_device"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = tracker.get_slot("device")
        device = normalize_device_name(device)
        if not device:
            dispatcher.utter_message(text="Bạn muốn bật thiết bị nào?")
            return []
        if device in device_status:
            if device_status[device]["status"] == 'on':
                dispatcher.utter_message(text=f"Thiết bị {device} đã bật trước đó.")
            else:
                device_status[device]["status"] = 'on'
                if device == "đèn":
                    device_status[device]["brightness"] = 100
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được bật. Độ sáng hiện tại: {device_status[device]['brightness']}%.")
                elif device == "máy lạnh":
                    device_status[device]["temperature"] = 24
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được bật. Nhiệt độ hiện tại: {device_status[device]['temperature']}°C.")
                elif device == "quạt":
                    device_status[device]["speed"] = 1
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được bật. Mức gió hiện tại: {device_status[device]['speed']}.")
        else:
            dispatcher.utter_message(text=f"Thiết bị {device} không được hỗ trợ hoặc không tồn tại.")
        return []

# Hành động tắt thiết bị
class ActionTurnOffDevice(Action):
    def name(self) -> Text:
        return "action_turn_off_device"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = tracker.get_slot("device")
        device = normalize_device_name(device)
        if not device:
            dispatcher.utter_message(text="Bạn muốn tắt thiết bị nào?")
            return []
        if device in device_status:
            if device_status[device]["status"] == 'off':
                dispatcher.utter_message(text=f"Thiết bị {device} đã tắt trước đó.")
            else:
                device_status[device]["status"] = 'off'  
                # Đặt giá trị về mặc định khi tắt thiết bị
                if device == "đèn":
                    device_status[device]["brightness"] = 0
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được tắt. Độ sáng hiện tại: 0%.")
                elif device == "máy lạnh":
                    device_status[device]["temperature"] = 0  # Đặt nhiệt độ về 0 khi tắt
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được tắt. Nhiệt độ hiện tại: không xác định.")
                elif device == "quạt":
                    device_status[device]["speed"] = 0  # Đặt mức gió về 0 khi tắt
                    dispatcher.utter_message(text=f"Thiết bị {device} đã được tắt. Mức gió hiện tại: không xác định.")
        else:
            dispatcher.utter_message(text=f"Thiết bị {device} không được hỗ trợ hoặc không tồn tại.")
        return []


# Hành động lấy thông tin thiết bị
class ActionGetDeviceDetails(Action):
    def name(self) -> Text:
        return "action_get_device_details"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = tracker.get_slot("device")
        device = normalize_device_name(device)
        if not device:
            dispatcher.utter_message(text="Bạn muốn kiểm tra trạng thái của thiết bị nào?")
            return []
        if device in device_status:
            details = device_status[device]
            if device == "đèn":
                dispatcher.utter_message(
                    text=f"Đèn hiện đang ở trạng thái {details['status']}, độ sáng: {details['brightness']}%.")
            elif device == "quạt":
                speed = details['speed'] if details['status'] == 'on' else "không xác định"
                dispatcher.utter_message(
                    text=f"Quạt hiện đang ở trạng thái {details['status']}, mức gió: {speed}.")
            elif device == "máy lạnh":
                temperature = details['temperature'] if details['status'] == 'on' else "không xác định"
                dispatcher.utter_message(
                    text=f"Máy lạnh hiện đang ở trạng thái {details['status']}, nhiệt độ: {temperature}°C.")
        else:
            dispatcher.utter_message(text=f"Không tìm thấy thông tin cho thiết bị {device}.")
        return []


# Hành động liệt kê các thiết bị
class ActionGetDeviceList(Action):
    def name(self) -> Text:
        return "action_get_device_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        device_list = ", ".join(device_status.keys())
        dispatcher.utter_message(text=f"Các thiết bị hiện có mà bạn có thể điều khiển là: {device_list}.")
        return []

# Hành động đặt độ sáng
class ActionSetBrightness(Action):
    def name(self) -> Text:
        return "action_set_brightness"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = "đèn"
        brightness_text = tracker.get_slot("brightness")
        # Loại bỏ ký tự không cần thiết như "%"
        brightness_text = re.sub(r"[^\d]", "", brightness_text)
        try:
            brightness = int(brightness_text)
            if not (0 <= brightness <= 100):
                raise ValueError("Giá trị độ sáng không hợp lệ.")
        except ValueError:
            dispatcher.utter_message(text="Vui lòng nhập giá trị độ sáng hợp lệ từ 0 đến 100.")
            return []
        device_status[device]["brightness"] = brightness
        device_status[device]["status"] = 'on'
        dispatcher.utter_message(text=f"Độ sáng của {device} đã được đặt thành {brightness}%.")
        return [SlotSet("brightness", None)]


# Hành động đặt nhiệt độ
class ActionSetTemperature(Action):
    def name(self) -> Text:
        return "action_set_temperature"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = "máy lạnh"
        temperature_text = tracker.get_slot("temperature")
        # Loại bỏ ký tự không cần thiết như "độ", "C"
        temperature_text = re.sub(r"[^\d]", "", temperature_text)
        try:
            temperature = int(temperature_text)
            if not (16 <= temperature <= 30):
                raise ValueError("Giá trị nhiệt độ không hợp lệ.")
        except ValueError:
            dispatcher.utter_message(text="Vui lòng nhập giá trị nhiệt độ từ 16 đến 30°C.")
            return []
        device_status[device]["temperature"] = temperature
        device_status[device]["status"] = 'on'
        dispatcher.utter_message(text=f"Nhiệt độ của {device} đã được đặt thành {temperature}°C.")
        return [SlotSet("temperature", None)]


# Hành động đặt tốc độ quạt
class ActionSetFanSpeed(Action):
    def name(self) -> Text:
        return "action_set_fan_speed"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        device = "quạt"
        speed_text = tracker.get_slot("speed")
        # Loại bỏ ký tự không cần thiết
        speed_text = re.sub(r"[^\d]", "", speed_text)
        try:
            speed = int(speed_text)
            if speed not in [1, 2, 3]:
                raise ValueError("Mức gió không hợp lệ.")
        except ValueError:
            dispatcher.utter_message(text="Vui lòng chọn mức gió 1, 2, hoặc 3.")
            return []
        device_status[device]["speed"] = speed
        device_status[device]["status"] = 'on'
        dispatcher.utter_message(text=f"Mức gió của {device} đã được đặt thành {speed}.")
        return [SlotSet("speed", None)]
