from app.core.minio import MinioObjectStore, REQUIRED_BUCKETS

if __name__ == "__main__":
    store = MinioObjectStore(); store.ensure_buckets()
