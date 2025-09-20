import streamlit as st
import json
from quiz_generator import QuizGenerator

# Initialize the quiz generator
@st.cache_resource
def get_quiz_generator():
    return QuizGenerator()

def main():
    st.title("📚 Educational Assignment & Quiz Generator")
    st.markdown("Generate assignments and quizzes from any document or topic using AI")
    
    # Initialize quiz generator
    quiz_gen = get_quiz_generator()
    
    # Input section
    st.header("📝 Input Content")
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "Document Upload"],
        horizontal=True
    )
    
    content = ""
    
    if input_method == "Text Input":
        content = st.text_area(
            "Enter your document content or topic:",
            height=200,
            placeholder="Paste your document content here or describe a topic you want to create assignments about..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=['txt', 'md'],
            help="Currently supports text (.txt) and markdown (.md) files"
        )
        
        if uploaded_file is not None:
            try:
                content = str(uploaded_file.read(), "utf-8")
                st.success(f"Document loaded successfully! ({len(content)} characters)")
                with st.expander("Preview uploaded content"):
                    st.text(content[:500] + "..." if len(content) > 500 else content)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Generation section
    if st.button("🎯 Generate Assignments & Quiz", type="primary", disabled=not content.strip()):
        if not content.strip():
            st.warning("Please provide some content to generate assignments from.")
            return
            
        with st.spinner("Generating educational content..."):
            try:
                # Generate assignments and quiz
                result = quiz_gen.generate_educational_content(content)
                
                if result:
                    # Store in session state for persistence
                    st.session_state.generated_content = result
                    st.success("Content generated successfully!")
                else:
                    st.error("Failed to generate content. Please try again.")
                    
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
    
    # Display generated content
    if hasattr(st.session_state, 'generated_content') and st.session_state.generated_content:
        result = st.session_state.generated_content
        
        st.divider()
        
        # Assignment Questions Section
        st.header("📋 Assignment Questions")
        st.markdown("*Essay prompts and discussion questions*")
        
        for i, assignment in enumerate(result.get('assignments', []), 1):
            with st.container():
                st.subheader(f"Assignment {i}")
                st.write(assignment['question'])
                if 'guidance' in assignment:
                    with st.expander("📖 Guidance & Tips"):
                        st.write(assignment['guidance'])
                st.divider()
        
        # Quiz Section
        st.header("🧠 Multiple Choice Quiz")
        st.markdown("*Test your understanding with these questions*")
        
        quiz_answers = {}
        
        for i, question in enumerate(result.get('quiz', []), 1):
            with st.container():
                st.subheader(f"Question {i}")
                st.write(question['question'])
                
                # Create radio buttons for options
                answer_key = f"quiz_{i}"
                selected_option = st.radio(
                    "Choose your answer:",
                    question['options'],
                    key=answer_key,
                    index=None
                )
                
                if selected_option:
                    quiz_answers[i] = {
                        'selected': selected_option,
                        'correct': question['correct_answer'],
                        'is_correct': selected_option == question['correct_answer']
                    }
                
                st.divider()
        
        # Quiz Results
        if quiz_answers and len(quiz_answers) == len(result.get('quiz', [])):
            st.header("📊 Quiz Results")
            
            correct_count = sum(1 for answer in quiz_answers.values() if answer['is_correct'])
            total_questions = len(quiz_answers)
            score_percentage = (correct_count / total_questions) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Correct Answers", f"{correct_count}/{total_questions}")
            with col2:
                st.metric("Score", f"{score_percentage:.1f}%")
            with col3:
                if score_percentage >= 80:
                    st.success("Excellent! 🎉")
                elif score_percentage >= 60:
                    st.info("Good job! 👍")
                else:
                    st.warning("Keep studying! 📚")
            
            # Detailed feedback
            st.subheader("Answer Review")
            for i, answer_data in quiz_answers.items():
                question_data = result['quiz'][i-1]
                
                if answer_data['is_correct']:
                    st.success(f"Question {i}: Correct! ✅")
                else:
                    st.error(f"Question {i}: Incorrect ❌")
                    st.write(f"Your answer: {answer_data['selected']}")
                    st.write(f"Correct answer: {answer_data['correct']}")
                
                if 'explanation' in question_data:
                    with st.expander(f"Explanation for Question {i}"):
                        st.write(question_data['explanation'])

if __name__ == "__main__":
    main()
