from unittest.mock import Mock, patch

from adapters.database_models.ModelConfig import ModelConfig
from lib.GPT.SingleFlashcardGenerator import SingleFlashcardGenerator


def test_single_flashcard_generator():
    openai_api_key = "YOUR_OPENAI_API_KEY"
    mock_config = Mock(spec=ModelConfig)
    mock_config.system_message = "Your system message here"
    generator = SingleFlashcardGenerator(
        openai_api_key=openai_api_key, model_config=mock_config
    )

    # Mock the _get_completion method
    with patch.object(
        SingleFlashcardGenerator,
        "_get_completion",
        return_value="Q: What is Python?\nA: A programming language.",
    ):
        result = generator("Tell me about Python.", "user123")
        assert result.question == "What is Python?"
        assert result.answer == "A programming language."
