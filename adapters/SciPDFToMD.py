import io
import re
from abc import ABC, abstractmethod
from uuid import uuid4

import fitz  # type: ignore
import modal
import pypandoc  # type: ignore
from modal.functions import FunctionCall


class SciPDFToMDInterface(ABC):
    @abstractmethod
    def __call__(self, pdf: io.BytesIO) -> str:
        pass


class SciPDFToMDMock(SciPDFToMDInterface):
    def __call__(self, pdf: io.BytesIO) -> str:
        return "This is a mock"


def find_next_punctuation(s: str, start_inx=0):
    """
    Find the index of the next punctuation mark

    Args:
        s: String to examine
        start_inx: Index where to start
    """

    for i in range(start_inx, len(s)):
        if s[i] in [".", "?", "!", "\n"]:
            return i

    return None


def find_last_punctuation(s: str, start_inx=0):
    """
    Find the index of the last punctuation mark before start_inx

    Args:
        s: String to examine
        start_inx: Index where to look before
    """

    for i in range(start_inx - 1, 0, -1):
        if s[i] in [".", "?", "!", "\n"]:
            return i

    return None


def truncate_repetitions(s: str, min_len=30):
    """
    Attempt to truncate repeating segments in the input string.

    This function looks for the longest repeating substring at the end of the input string and truncates
    it to appear only once. To be considered for removal, repetitions need to be continuous.

    Args:
        s (str): The input raw prediction to be truncated.
        min_len (int): The minimum length of the repeating segment.

    Returns:
        str: The input string with repeated segments truncated.
    """
    s_lower = s.lower()
    s_len = len(s_lower)

    if s_len < 2 * min_len:
        return s

    # try to find a length at which the tail is repeating
    max_rep_len = None
    for rep_len in range(min_len, int(s_len / 2)):
        # check if there is a repetition at the end
        same = True
        for i in range(0, rep_len):
            if s_lower[s_len - rep_len - i - 1] != s_lower[s_len - i - 1]:
                same = False
                break

        if same:
            max_rep_len = rep_len

    if max_rep_len is None:
        return s

    lcs = s_lower[-max_rep_len:]

    # remove all but the last repetition
    st = s
    st_lower = s_lower
    while st_lower.endswith(lcs):
        st = st[:-max_rep_len]
        st_lower = st_lower[:-max_rep_len]

    # this is the tail with the repetitions
    repeating_tail = s_lower[len(st_lower) :]

    # add until next punctuation and make sure last sentence is not repeating
    st_lower_out = st_lower
    while True:
        sentence_end = find_next_punctuation(s_lower, len(st_lower_out))
        sentence_start = find_last_punctuation(s_lower, len(st_lower_out))
        if sentence_end and sentence_start:
            sentence = s_lower[sentence_start:sentence_end]
            st_lower_out = s_lower[: sentence_end + 1]
            if sentence in repeating_tail:
                break
        else:
            break

    s_out = s[: len(st_lower_out)]

    return s_out


def close_envs(s: str) -> str:
    """checks if table envs are opened but not closed. Appends the closing statements and returns the new string"""
    envs = ("bmatrix", "pmatrix", "matrix", "tabular", "table")
    for env in envs:
        begins, ends = s.count(r"\begin{%s}" % env), s.count(r"\end{%s}" % env)
        if begins > ends:
            s += (r"\end{%s}" % env) * (begins - ends)
    return s


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
        latex_math_pattern = r"(\$\$?.*?\$\$?)|(\*\*.*?\*\*)"

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

        markdown_post_processed = truncate_repetitions(markdown_post_processed, 10)

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
