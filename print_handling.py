from eln_packages_common.resourcemanage import Resource_Manager
from pypdf import PdfWriter
import io
from pathlib import Path

rm = Resource_Manager()
current_dir = Path(__file__).parent
temp_path = str(current_dir / "static" / "print.pdf")


def add_item(ids: list[int]):
    merger = PdfWriter()
    for id in ids:
        # looks at all the files uploaded to the item, but only selects ones named label.pdf
        for file in rm.get_uploaded_files(id):
            if file.to_dict()["real_name"] == "label.pdf":
                new_label = io.BytesIO(  # reads the file as binary
                    rm.uploadsapi.read_upload(  # type: ignore
                        "items",
                        id,
                        file.to_dict()["id"],
                        format="binary",
                        _preload_content=False,
                    ).data  # type: ignore
                )
                merger.append(new_label)
        merger.write(open(temp_path, "wb"))
        merger.close()  # closes the merger --- potentially there would be benefit to leaving the merger open until write_labels but then this would have to be another objectprinterqueue

