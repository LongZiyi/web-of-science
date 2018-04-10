import hashlib

def get_md5(doi):
    if isinstance(doi, str):
        doi = doi.encode("utf-8")
    m = hashlib.md5()
    m.update(doi)
    return m.hexdigest()
