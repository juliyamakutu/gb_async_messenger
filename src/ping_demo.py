from common.utils import host_ping, host_range_ping, host_range_ping_tab


EXAMPLE_HOSTS = [
    "ya.ru",
    "google.com",
    "youtube.com",
    "8.8.8.8",
    "62.165.32.250",
    "10.10.10.10",
    "192.168.254.254",
]


if __name__ == "__main__":
    host_ping(host_list=EXAMPLE_HOSTS)
    host_range_ping(start_ip="192.168.0.253", ip_count=5)
    host_range_ping_tab(start_ip="192.168.0.1", ip_count=5)