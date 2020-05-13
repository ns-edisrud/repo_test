# Local Python Package Repository

Simple Python package repository used by Pants. This is useful for compiling certain packages, like psycopg2, for target platforms like Lambda.

Wheels (.whl) and tarballs (.tar.gz) can be downloaded from S3:
```bash
aws s3 sync s3://s3_ns_dev/lexio/3rdparty/python/repo "${TALOS_ROOT}/3rdparty/python/repo"
```
