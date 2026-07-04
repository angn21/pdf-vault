"""Quick integration test for PDF tools (no external CLIs required)."""



from __future__ import annotations



import io

import sys

from pathlib import Path



from reportlab.pdfgen import canvas



sys.path.insert(0, str(Path(__file__).parent))



from storage import JobStore

from tools import compress_pdf, merge_pdf, pdf_to_jpg, protect_pdf, remove_pages, rotate_pdf, unlock_pdf





def make_pdf(text: str) -> bytes:

    buf = io.BytesIO()

    c = canvas.Canvas(buf)

    c.drawString(100, 750, text)

    c.showPage()

    c.save()

    return buf.getvalue()





def main() -> None:

    store = JobStore(data_dir="./data/test-jobs", ttl_seconds=60)

    job = store.create("merge", {})

    store.save_input(job.id, "a.pdf", make_pdf("Page A"))

    store.save_input(job.id, "b.pdf", make_pdf("Page B"))

    job.options["fileOrder"] = ["a.pdf", "b.pdf"]

    merged = merge_pdf(store, job)

    assert merged.exists() and merged.stat().st_size > 0

    print("merge: ok")



    job2 = store.create("rotate", {"angle": 90})

    store.save_input(job2.id, "doc.pdf", merged.read_bytes())

    rotated = rotate_pdf(store, job2)

    assert rotated.exists()

    print("rotate: ok")



    job2b = store.create("remove-pages", {"removePages": "2-3"})

    store.save_input(job2b.id, "doc.pdf", merged.read_bytes())

    removed = remove_pages(store, job2b)

    assert removed.exists()

    from pypdf import PdfReader

    assert len(PdfReader(str(removed)).pages) == 1

    print("remove-pages: ok")



    job2c = store.create("pdf-to-jpg", {"format": "jpeg"})

    store.save_input(job2c.id, "doc.pdf", merged.read_bytes())

    images_zip = pdf_to_jpg(store, job2c)

    assert images_zip.exists() and images_zip.suffix == ".zip"

    print("pdf-to-jpg: ok")



    job3 = store.create("protect", {"password": "secret"})

    store.save_input(job3.id, "doc.pdf", rotated.read_bytes())

    protected = protect_pdf(store, job3)

    assert protected.exists()

    print("protect: ok")



    job4 = store.create("unlock", {"password": "secret"})

    store.save_input(job4.id, "doc.pdf", protected.read_bytes())

    unlocked = unlock_pdf(store, job4)

    assert unlocked.exists()

    print("unlock: ok")



    job5 = store.create("compress", {"quality": "ebook"})

    store.save_input(job5.id, "doc.pdf", unlocked.read_bytes())

    compressed = compress_pdf(store, job5)

    assert compressed.exists() and compressed.stat().st_size > 0

    print("compress: ok")



    store.purge(job.id)

    store.purge(job2.id)

    store.purge(job2b.id)

    store.purge(job2c.id)

    store.purge(job3.id)

    store.purge(job4.id)

    store.purge(job5.id)

    print("all tests passed")





if __name__ == "__main__":

    main()

