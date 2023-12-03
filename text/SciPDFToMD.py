import io
from abc import ABC, abstractmethod

import fitz  # type: ignore
import modal
from modal.functions import FunctionCall


class SciPDFToMDInterface(ABC):
    @abstractmethod
    def __call__(self, pdf: io.BytesIO) -> str:
        pass


class SciPDFToMDMock(SciPDFToMDInterface):
    def __call__(self, pdf: io.BytesIO) -> str:
        return "This is a mock"


class SciPDFToMD(SciPDFToMDInterface):
    _dpi: int = 96
    _modal_app_name: str = "nougat-ocr"
    _modal_function_name: str = "img_to_md"
    _timeout_s: int = 180

    def __init__(self, dpi: int = 96, timeout_s: int = 180):
        self._dpi = dpi
        self._timeout_s = timeout_s

        self._modal_pred_fn = modal.Function.lookup(
            self._modal_app_name, self._modal_function_name
        )

    def __call__(self, pdf: io.BytesIO) -> str:
        images = self._pdf_to_images(pdf)
        result_id = self._predict(images)

        timeout_s = self._timeout_s + len(images) * 10

        markdown = self._get_markdown(result_id, timeout_s)

        return markdown

    def _get_markdown(self, result_id: str, timeout_s: int) -> str:
        function_call = FunctionCall.from_id(result_id)

        result = function_call.get(timeout=timeout_s)

        markdown = "\n\n".join(result)

        return markdown

    def _predict(self, images: list) -> str:
        res = self._modal_pred_fn.spawn(images)
        return res.object_id

    def _pdf_to_images(self, pdf: io.BytesIO) -> list:
        images = []

        pdf = fitz.open(stream=pdf)
        pages = range(len(pdf))

        for page_idx in pages:
            page_bytes: bytes = (
                pdf[page_idx].get_pixmap(dpi=self._dpi).pil_tobytes(format="PNG")
            )

            images.append(page_bytes)

        return images
