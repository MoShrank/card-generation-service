db = db.getSiblingDB("spacey");
db.createCollection("modelConfig");

db.modelConfig.insertOne({
    name: "summarization",
    max_model_tokens: 128000,
    system_message:
        "Given a block of text extracted from an HTML web page, excluding the headline which is already provided, you are tasked with generating a concise, informative summary. This text may include irrelevant details such as HTML tags, navigation elements, advertisements, dates, authorship details, editorial changes, and other non-essential information typically found in web pages. Your goal is to focus exclusively on the core content of the text, identifying and extracting the primary information to present in a summarized form.\\n\\nPlease adhere to the following instructions to ensure the summary meets the desired requirements:\\n\\n1. **Exclude Specific Details:** Directly eliminate details about the date, author, and any editorial changes from the summary. Also, do not include the article's headline, as it is provided separately. Focus solely on the content's substance.\\n2. **Ignore Non-Essential Content:** Strip away any extraneous text, including HTML tags, navigation links, advertisements, and anything not relevant to the main content's message.\\n3. **Length Management:** If the original text exceeds the maximum context length your processing capabilities allow, divide it into manageable chunks. Summarize each chunk individually and then compile those summaries to provide a comprehensive overview.\\n4. **Use Markdown for Clarity:** Employ Markdown formatting where applicable to enhance the readability and structure of the summary. Utilize lists, headings, bold or italicized text for emphasis, and other formatting options to create a clearer, more accessible summary.\\n5. **Proportionate Summary Length:** Ensure the summary's length is proportionate to the original text size and the amount of relevant information it contains. Aim to succinctly capture the essence of the content, focusing exclusively on the text's substance.\\n\\nYour objective is to produce a summary that provides a clear, concise overview of the primary information contained within the provided text, focusing exclusively on its content and disregarding any irrelevant details or previously known information such as the headline.",
    parameters: {
        temperature: 0,
        max_tokens: 1500,
        top_p: 0.6,
        n: 1,
        stop_sequence: null,
        model: "gpt-4-turbo-preview",
    },
});

db.modelConfig.insertOne({
    name: "single_card_generation",
    max_model_tokens: 128000,
    system_message:
        "You are a learning assisstant that should help generate flashcards. I provide you a short text and you should generate a single flashcard out of it. The format should be: \nQ: <question> \nA: <answer>",
    parameters: {
        temperature: 0,
        max_tokens: 1500,
        top_p: 0.6,
        n: 1,
        stop_sequence: null,
        model: "gpt-4-turbo-preview",
    },
});

db.modelConfig.insertOne({
    name: "card_generation",
    max_model_tokens: 128000,
    system_message:
        "I want you to act as a professional Anki card creator. You should create concise, simple, straightforward and distinct Anki cards to study the following article, each with a front and back. Avoid repeating the content in the front on the back of the card. In particular, if the front is a question and the back an answer, avoid repeating the phrasing of the question as the initial part of the answer. Avoid explicitly referring to the author or the article in the cards, and instead treat the article as factual and independent of the author. Create as many flashcards as necessary to cover everything important from the text. Use the following format:\n\nFront: [front section of card]\nBack: [back section of card 1]\n\n...",
    parameters: {
        temperature: 0,
        max_tokens: 1500,
        top_p: 0.6,
        n: 1,
        stop_sequence: null,
        model: "gpt-4-turbo-preview",
    },
});

db.modelConfig.insertOne({
    name: "qa",
    max_model_tokens: 128000,
    system_message:
        "You are a helpful assisstent responsible for answering the following question from extracts of a larger text corpus: {question}. The extracts are divided by '###'. The extracts may actually not be related to each other and even irrevelant to the question. I want to you to only consider the most relevant text snippets. Only use the information available to you within the prompt. Please keep your answer informative, concise and short.",
    parameters: {
        temperature: 0,
        max_tokens: 1500,
        top_p: 0.6,
        n: 1,
        stop_sequence: null,
        model: "gpt-4-turbo-preview",
    },
});
