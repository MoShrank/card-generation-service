import io
import re
from abc import ABC, abstractmethod
from uuid import uuid4

import fitz  # type: ignore
import modal
import pypandoc
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

        self._latex_table_pattern = r"\\begin{tabular}.*?\\end{tabular}"

    def __call__(self, pdf: io.BytesIO) -> str:
        images = self._pdf_to_images(pdf)
        result_id = self._predict(images)

        timeout_s = self._timeout_s + len(images) * 10

        markdown = self._get_markdown(result_id, timeout_s)

        return markdown

    def _get_markdown(self, result_id: str, timeout_s: int) -> str:
        function_call = FunctionCall.from_id(result_id)

        result = function_call.get(timeout=timeout_s)

        markdown = self._postprocess(result)

        return markdown

    def _predict(self, images: list) -> str:
        res = self._modal_pred_fn.spawn(images)
        return res.object_id

    def _replace_delimiters(self, text: str) -> str:
        text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text)
        text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text)

        return text

    def _temp_replace_latex_in_table(self, text: str) -> tuple[str, dict]:
        latex_mapping = {}
        latex_math_pattern = r"(\$\$?.*?\$\$?)"

        def replace_latex(match):
            table_content = match.group(0)

            def replace_expression(expression_match):
                unique_id = uuid4().hex
                latex_mapping[unique_id] = f"\n\n{expression_match.group(0)}"
                return unique_id

            modified_table = re.sub(
                latex_math_pattern, replace_expression, table_content
            )
            return modified_table

        modified_latex = re.sub(
            self._latex_table_pattern, replace_latex, text, flags=re.DOTALL
        )

        return modified_latex, latex_mapping

    def _restore_latex_from_mapping(self, modified_latex: str, mapping: dict) -> str:
        """Restore the LaTeX expressions from the mapping."""
        for unique_id, latex_expression in mapping.items():
            modified_latex = modified_latex.replace(unique_id, latex_expression)
        return modified_latex

    def _find_latex_tables(self, text: str) -> list:
        """Find all LaTeX table substrings in the text."""
        return re.findall(self._latex_table_pattern, text, re.DOTALL)

    def _convert_latex_table_to_html(self, latex_table: str) -> str:
        """Convert a LaTeX table to HTML format using pypandoc."""
        return pypandoc.convert_text(latex_table, "html", format="latex")

    def _convert_latex_tables_in_text(self, text: str) -> str:
        """Convert all LaTeX tables in the text to HTML."""
        latex_tables = self._find_latex_tables(text)
        for latex_table in latex_tables:
            html_table = self._convert_latex_table_to_html(latex_table)
            text = text.replace(latex_table, html_table)
        return text

    def _postprocess(self, markdown: list[str]) -> str:
        markdown_post_processed = "\n\n".join(markdown)

        markdown_post_processed = self._replace_delimiters(markdown_post_processed)

        markdown_post_processed, latex_mapping = self._temp_replace_latex_in_table(
            markdown_post_processed
        )

        markdown_post_processed = self._convert_latex_tables_in_text(
            markdown_post_processed
        )

        markdown_post_processed = self._restore_latex_from_mapping(
            markdown_post_processed, latex_mapping
        )

        return markdown_post_processed

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
