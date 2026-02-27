#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import mmap
import os
import random
import sys
import time
from time import sleep

GB = 1024 * 1024 * 1024
MB = 1024 * 1024


def allocate_memory(size_bytes):
    """
        申请指定大小的内存，并进行初始化
    :param size_bytes:
    :return:
    """
    memory = bytearray(size_bytes)
    # 初始化内存，确保物理页被分配
    for i in range(0, size_bytes, 4096):
        memory[i] = 0
    return memory


def allocate_file_backed_memory(size_bytes, path="/tmp/access-memory.bin"):
    """
        使用文件映射替代匿名内存
    :param size_bytes:
    :param path:
    :return:
    """
    with open(path, "wb") as f:
        f.truncate(size_bytes)

    f = open(path, "r+b")
    mm = mmap.mmap(f.fileno(), size_bytes, access=mmap.ACCESS_WRITE)

    # 初始化内存，确保物理页被分配
    for i in range(0, size_bytes, 4096):
        mm[i] = 0

    return mm, f


def range_read_write(memory, target_percent=100):
    """
        对指定内存的进行一次读写
    :param memory:
    :param target_percent:
    :return:
    """
    total_size = len(memory)
    target_size = int(total_size * target_percent / 100)

    # 顺序读写前 target_percent 的内存
    for i in range(0, target_size, 4096):
        # 写操作
        memory[i] = (i % 256)
        # 读操作
        _ = memory[i]

    return target_size


def random_read_write(memory, target_percent=100):
    """
        对指定内存的进行一次读写
    :param memory:
    :param target_percent:
    :return:
    """
    total_size = len(memory)
    target_size = int(total_size * target_percent / 100)
    page_size = 4096
    total_pages = total_size // page_size
    target_pages = max(1, target_size // page_size)

    # 随机访问页，避免顺序流式模式
    for _ in range(target_pages):
        page_index = random.randrange(total_pages)
        offset = page_index * page_size
        # 写操作
        memory[offset] = (offset % 256)
        # 读操作
        _ = memory[offset]

    return target_size


def loop(memory, interval=1.0, access_percent=100, access_function=range_read_write):
    """
        持续读写内存
    :param access_function:
    :param access_percent:
    :param memory:
    :param interval:
    :return:
    """
    print("开始持续随机读写测试...")
    print(f"内存大小：{len(memory) / GB:.2f}GB")
    print(f"内存读写比例：{access_percent}%")
    print("按 Ctrl+C 退出\n")

    try:
        while True:
            start_time = time.time()
            access_function(memory, access_percent)
            current_time = time.time()
            elapsed = current_time - start_time
            print(f"[{time.strftime('%H:%M:%S')}] 总耗时：{elapsed:.1f}s")
            sleep(interval)
    except KeyboardInterrupt:
        print("测试结束统计:")


def main():
    try:
        print("当前进程 PID PID:", os.getpid())
        memory = allocate_memory(5 * GB)
        # memory, backing_file = allocate_file_backed_memory(5 * GB)
        loop(memory, access_percent=50, access_function=range_read_write)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
