from paho.mqtt import client as mqtt
import sys

BROKER = "iot.dfrobot.com.cn"
PORT = 1883
TOPIC = "1zAmJ1Hvg"
CLIENT_ID = "test_client"
USERNAME = "HgKzJJHvR"
PASSWORD = "HTQuCLHvg"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ 连接成功!")
        print(f"   服务器: {BROKER}:{PORT}")
        print(f"   用户名: {USERNAME}")
        client.subscribe(TOPIC)
        client.publish(TOPIC, "测试消息: 连接成功!")
        print(f"   已发布测试消息到主题: {TOPIC}")
    else:
        print(f"❌ 连接失败! 错误码: {reason_code}")
        sys.exit(1)

def on_message(client, userdata, msg):
    print(f"📩 收到消息: {msg.topic} -> {msg.payload.decode()}")

def main():
    print("=" * 50)
    print("🔌 MQTT 连接测试")
    print("=" * 50)
    print(f"   服务器: {BROKER}")
    print(f"   端口: {PORT}")
    print(f"   主题: {TOPIC}")
    print(f"   用户名: {USERNAME}")
    print("=" * 50)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("正在连接...")
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
