import pandas as pd
import streamlit as st
import json

# Load the DataFrame (assuming it's already created or loaded)
llms = {
    'claude-3.5-sonnet': 'claude',
    'mixtral-8x7B': 'mixtral',
    'llama-3-70b': 'll70b',
    'llama-3-8b': 'll8b',
    'phi-3-mini': 'phi'
}
splits = ['User_1', 'User_2', 'User_3', 'User_4', 'User_5']

def update_json(filename, question_index, response, model):
    try:
        with open(f'output/{filename}.json', 'r') as f:
            data = [json.loads(line) for line in f]
    except FileNotFoundError:
        data = []

    # Ensure data has enough elements
    while len(data) <= question_index:
        data.append({})
        
    # Update the data
    if 'human_eval' not in data[question_index]:
        data[question_index]['human_eval'] = {}
    
    if isinstance(data[question_index]['human_eval'], dict):
        data[question_index]['human_eval'][model] = response
    else:
        # If 'human_eval' is not a dict, replace it with a new dict
        data[question_index]['human_eval'] = {model: response}

    # Write the updated data back to the file
    with open(f'output/{filename}.json', 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

# Streamlit app
def main():
    st.title('Question Answering')

    # Create a sidebar
    st.sidebar.title('Sidebar')

    # Add dropdown lists to the sidebar
    selected_split = st.sidebar.selectbox('Select split:', splits)
    filename = 'split' + selected_split[-2:]
    model = st.sidebar.selectbox('Select LLM:', list(llms.keys()))

    # Load the DataFrame based on the selected split
    df = pd.read_csv(f'splits/{filename}.csv')

    # Initialize session state for responses if not exist
    if 'responses' not in st.session_state:
        st.session_state.responses = [{} for _ in range(len(df))]

    # Create a form
    for i, (_, row) in enumerate(df.iterrows()):
        question = row['questions']
        answer = row['answers']
        prediction = row[llms[model]]  # Use the column name from the llms dictionary

        st.subheader(f"Question {i+1}")
        st.markdown(question.replace('\n', '<br><br>'), unsafe_allow_html=True)
        st.markdown("**Prediction:**")
        st.markdown(prediction)
        st.markdown("**Ground truth:**")
        st.markdown(answer)

        # Display "Yes" and "No" radio buttons
        user_response = st.radio(
            'Does the prediction and ground truth match?',
            ('', 'Yes', 'No'),
            key=f'response_{i}_{model}',
            index=0 if model not in st.session_state.responses[i] else (['Yes', 'No'].index(st.session_state.responses[i][model]) + 1)
        )

        # Update session state and JSON file when radio button is changed
        if model not in st.session_state.responses[i] or user_response != st.session_state.responses[i][model]:
            if user_response:  # Only update if a selection is made
                st.session_state.responses[i][model] = user_response
                update_json(filename, i, user_response, model)
                st.success(f"Response for Question {i+1} updated for {model}!")

    # Display completion message when all questions are answered for the current model
    if all(model in response and response[model] != '' for response in st.session_state.responses):
        st.success(f"All questions have been answered for {model}!")

if __name__ == '__main__':
    main()