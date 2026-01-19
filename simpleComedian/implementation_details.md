Model: gemma_27b
Gemini API key: AIzaSyCHOT98OXqydAPksLXnWT8Pdws5pTm6ejw

Use modular programming each module showing sepration of concerns with proper docstring for the module. Print in terminal for ease of debugging

# Iteration one (Direct Prompting)

1. First identify the appropriate model name from gemini and verify the response
2. Make a task-a parser module, the enties in the task are mixed so if headline column is filled call headline_generator and if word1 and word2 columns are filled call inclusion_generator
3. Write headline_generator.py which will have the module which calls for news headline generation, make sure the ouptut follows a fixed structure so that it is parsable and joke can be extracted and output tsv can be filled. Simlarly make inclusion_generator.py
For now they simply call gemma27b through gemini api with a good prompt and verify the output structure and return a single joke string satisfying the constraints
4. The parser module has functions to fill the output into the ouput folder which is a copy of the data folder with all the same tsv file
5. Make a main.py which runs all these modules.

Input: data folder, Output: task-a-en.tsv filled in output folder satisfyying task constraints