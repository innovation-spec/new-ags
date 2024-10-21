import argparse, time, urllib.request

p=argparse.ArgumentParser(); p.add_argument("url"); p.add_argument("--timeout", type=int, default=90); args=p.parse_args()
deadline=time.time()+args.timeout
