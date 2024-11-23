import argparse, time, urllib.request

p=argparse.ArgumentParser(); p.add_argument("url"); p.add_argument("--timeout", type=int, default=90); args=p.parse_args()
deadline=time.time()+args.timeout
while time.time()<deadline:
    try:
        with urllib.request.urlopen(args.url, timeout=3) as r:
            if 200 <= r.status < 300:
                print(f"Ready: {args.url}")
                raise SystemExit(0)
    except Exception:
        time.sleep(2)
raise SystemExit(f"Timed out waiting for {args.url}")
