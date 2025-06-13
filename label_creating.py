from blabel import LabelWriter
from pathlib import Path



def print_label(caption: str = "", codecontent:str | None = None, longcaption: str | None = None, icon: str | None = None):
    current_dir = Path(__file__).parent


    label_writer = LabelWriter(
        str(current_dir / "static" / "Flex_Label.html"),
        default_stylesheets=(str(current_dir / "static" / "flex_style.css"),),
    )
    path=str(current_dir / "static" / "print.pdf")

    """Adds a label to the list to be printed
    :param caption: The caption for the label
    :param codecontent: The content for the QR code, if None, no QR code is generated
    :param longcaption: A longer caption for the label, if None, no long caption is displayed
    :param icon: An icon to be displayed on the label, if None, no icon is displayed
    """
    records = []
    if codecontent is not None and icon is not None:
        raise ValueError("Cannot have both codecontent and icon at the same time")
    records.append(
        dict(
            caption=caption,
            qr_text=codecontent,
            longcaption=longcaption,
            icon=icon
        )
    )
    label_writer.write_labels(records, target=path)
    records = []
