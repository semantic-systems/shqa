import llms


def parser(question, q_type= 1):
    prompt_kg_kg_bridge = f"""Convert question -> HQ-expresion: question is the multi-hop complex question. And the HQ-expression contains operators and elements. Each element is a natural question. Operator is from [JOIN, AND] and each of them is a binary operator, which means it contains two elements. JOIN(KGQA2(a) ; KGQA1(b)) operator is for linear-chain reasoning that question a contains the placeholder (e.g. Ans#1) of question b's answer. Placeholder is to represent the answer from previous question. AND(KGQA2(a) ; KGQA1(b)) operator is for intersection reasoning that question a and b can be processed parallel. 
            JOIN and AND can be compositioned, like JOIN(KGQA2(c), JOIN(KGQA2(b), KGQA1(a))), AND(KGQA2(c), JOIN(KGQA2(b), KGQA1(a))). Which composition to use, please follow the demo examples. 
            For example:
            question: What is the average two years citedness of the author who has worked on Emergent nature inspired algorithms for multi-objective optimization in the year 2013?
            HQ-expression: JOIN( KGQA2( WWhat is the average two years citedness of Ans#1 ) , KGQA1( the author who has worked on Emergent nature inspired algorithms for multi-objective optimization in the year 2013 ) )
            question: What is the cited by count of the author of 'Beyond Boundaries: EL over structured and unstructured data'?
            HQ-expression: JOIN( KGQA2( What is the cited by count of Ans#1 ) , KGQA1( Who is the author of 'Beyond Boundaries: EL over structured and unstructured data' ) )
            question: How many publications does the author of Blind UWB timing with a dirty template have?
            HQ-expression: JOIN( KGQA2( How many publications does Ans#1 have ) , KGQA1( Who is the author of Blind UWB timing with a dirty template ) )
            question: What is the i10Index of the writer who worked with Jennifer Widom on 'Deriving Incremental Production Rules for Deductive Data'?
            HQ-expression: JOIN( KGQA2( What is the i10Index of Ans#1 ) , KGQA1( Who is the writer who worked with Jennifer Widom on 'Deriving Incremental Production Rules for Deductive Data' ) )
            question: How many articles are attributed to the affiliation in which the author of 'William Stetson Merrill and bricolage for information studies' is working?
            HQ-expression: JOIN( KGQA2( How many articles are attributed to Ans#2 ) , JOIN( KGQA2( What is the affiliation in which Ans#1 working ) , KGQA1( Who is the author of 'William Stetson Merrill and bricolage for information studies' ) ) )
            question: What is the institute type of the author who published the article 'Designing Novel Visualization and Interaction Techniques that Scale from Small to Jumbo Displays'?
            HQ-expression: JOIN( KGQA2( What is the institute type of Ans#2 ) , JOIN( KGQA2( What is the institute of Ans#1 ) , KGQA1( Who is the author who published the article 'Designing Novel Visualization and Interaction Techniques that Scale from Small to Jumbo Displays' ) ) )
            question: How many citations does the institution where the article 'Organizing Usability Work to Fit the Full Product Range' author is affiliated with have?
            HQ-expression: JOIN( KGQA2( How many citations does Ans#2 have ) , JOIN( KGQA2( What is the institution where Ans#1 is affiliated with ) , KGQA1( the article 'Organizing Usability Work to Fit the Full Product Range' author is ) ) )
            question: What is the institute type of the organization where the author of the 'Information Factorization in Connectionist Models of Perception' paper works?
            HQ-expression: JOIN( KGQA2( What is the institute type of Ans#2 ) , JOIN( KGQA2( What is the organization where Ans#1 works ) , KGQA1( Who is the author of the 'Information Factorization in Connectionist Models of Perception' paper ) ) )

            Given question: {question}, 
            HQ-expression:

    """
    prompt_kg_text = f"""Convert question -> HQ-expresion: question is the multi-hop complex question. And the HQ-expression contains operators and elements. Each element is a natural question. Operator is from [JOIN, AND] and each of them is a binary operator, which means it contains two elements. JOIN(TextQA(a) ; KGQA1(b)) operator is for linear-chain reasoning that question a contains the placeholder (e.g. Ans#1) of question b's answer. Placeholder is to represent the answer from previous question. AND(TextQA(a) ; KGQA1(b)) operator is for intersection reasoning that question a and b can be processed parallel. 
                JOIN and AND can be compositioned, like JOIN(TextQA(c), JOIN(KGQA2(b), KGQA1(a))), AND(TextQA(c), JOIN(KGQA2(b), KGQA1(a))). Which composition to use, please follow the demo examples. 
                For example:
                question: In which year did the writer of 'Nonlinear Instability in Dissipative Finite Difference Schemes' obtain his DPhil degree?
                HQ-expression: JOIN( TextQA( In which year did Ans#1 obtain his DPhil degree ) , KGQA1( who is the writer of 'Nonlinear Instability in Dissipative Finite Difference Schemes' ) )
                question: What award did the mathematician who authored 'The curse of dimensionality in operator learning' receive in 2020?
                HQ-expression: JOIN( TextQA( What award did the mathematician Ans#1 receive in 2020 ) , KGQA1( who authored 'The curse of dimensionality in operator learning' ) )
                question: Which start-up company is founded by the author of Efficient relaxed-Jacobi smoothers for multigrid on parallel computers?
                HQ-expression: JOIN( TextQA( Which start-up company is founded by Ans#1 ) , KGQA1( Who is the author of Efficient relaxed-Jacobi smoothers for multigrid on parallel computers ) )
                question: When was the establishment year of the college where the author Geoffrey G. Parker is associated with?
                HQ-expression: JOIN( TextQA( When was the establishment year of Ans#1 ) , KGQA2( What is the college where the author Geoffrey G. Parker is associated with ) )
                question: Where is the main campus of Randall Berry's affiliation located?
                HQ-expression: JOIN( TextQA( Where is the main campus of Ans#2 located ) , KGQA2( What is Randall Berry's affiliation ) )
                question: Who is the current Chancellor of the institution affiliated with the contributor of 'Bimanual Input for Tablet Devices with Pressure and Multi-Touch Gestures'?
                HQ-expression: JOIN( TextQA( Who is the current Chancellor of Ans#2 ) , JOIN( KGQA2( What is the institution Ans#1 affiliated ) , KGQA1( Who is the contributor of 'Bimanual Input for Tablet Devices with Pressure and Multi-Touch Gestures' ) ) )
                question: How many Nobel Prize winners are affiliated with the academic institution of the researcher who published 'A polygonal approach to hidden-line and hidden-surface elimination'
                HQ-expression: JOIN( TextQA( How many Nobel Prize winners are affiliated with Ans#2 ) , JOIN( KGQA2( What is the academic institution of Ans#1 ) , KGQA1( the researcher who published 'A polygonal approach to hidden-line and hidden-surface elimination' is ) ) )
                question: What is the motto of the academic institution where the author of 'Model Selection Criteria for Learning Belief Nets: An Empirical Comparison' is affiliated with?
                HQ-expression: JOIN( TextQA( What is the motto of Ans#2 ) , JOIN( KGQA2( What is the academic institution where Ans#1 affiliated with ) , KGQA1( Who is the author of 'Model Selection Criteria for Learning Belief Nets: An Empirical Comparison' ) ) )
                question: What is the name of the author who published the article 'A Novel Approach to Real-Time RTI Based Distributed Simulation System'?
                HQ-expression: KGQA1( What is the name of the author who published the article 'A Novel Approach to Real-Time RTI Based Distributed Simulation System' ) 
                question: What is the academic institution where the author Andrew M. Stuart is affiliated with?
                HQ-expression: KGQA2( What is the academic institution where the author Andrew M. Stuart is affiliated with )
                Given question: {question}, 
                HQ-expression:

        """
    prompt_kg_kg_comparison = f"""Convert question -> HQ-expresion: question is the multi-hop complex question. And the HQ-expression contains operators and elements. Each element is a natural question. Operator is from [JOIN, AND, COMP_>, COMP_<, COMP_=, UNION] and each of them is a binary operator, which means it contains two elements. JOIN(KGQA2(a) ; KGQA1(b)) operator is for linear-chain reasoning that question a contains the placeholder (e.g. Ans#1) of question b's answer. Placeholder is to represent the answer from previous question. AND(KGQA2(a) ; KGQA1(b)) operator is for intersection reasoning that question a and b can be processed parallel. COMP_>((a), (b)) operator is for comparison reasoning that compares a is greater than b. COMP_<((a), (b)) operator is for comparison reasoning that compares a is less than b. COMP_=((a), (b)) operator is for comparison reasoning that cpmpares a is equal to b. 
                COMP_>, COMP_<, COMP_= and JOIN can be compositioned, like COMP_>(JOIN((KGQA2(b), KGQA2(a))), COMP_<(JOIN((KGQA2(b), KGQA2(a))), COMP_=(JOIN((KGQA2(b), KGQA2(a))), COMP_>(JOIN(KGQA2(b), KGQA1(a)), JOIN(KGQA2(d), KGQA1(c))), COMP_<(JOIN(KGQA2(b), KGQA1(a)), JOIN(KGQA2(d), KGQA1(c))), COMP_=(JOIN(KGQA2(b), KGQA1(a)), JOIN(KGQA2(d), KGQA1(c))), COMP_>(JOIN(KGQA2(c), JOIN(KGQA2(b), KGQA1(a))), JOIN(KGQA2(f), JOIN(KGQA2(e), KGQA1(d)))), COMP_<(JOIN(KGQA2(c), JOIN(KGQA2(b), KGQA1(a))), JOIN(KGQA2(f), JOIN(KGQA2(e), KGQA1(d)))), COMP_=(JOIN(KGQA2(c), JOIN(KGQA2(b), KGQA1(a))), JOIN(KGQA2(f), JOIN(KGQA2(e), KGQA1(d)))). Which composition to use, please follow the demo examples. 
                For example:
                question: Whose institute has a higher number of publications cited, the institute of the writer of 'An efficient processor allocation scheme for mesh connected parallel computers' or 'Convex Optimization with Abstract Linear Operators' creator affiliation?
                HQ-expression: COMP_>( JOIN( KGQA2( what is the number of publications cited of Ans#4), JOIN( KGQA2( what is the institute of Ans#3 ), KGQA1( who is the writer of 'An efficient processor allocation scheme for mesh connected parallel computers' ))), JOIN(KGQA2( what is the number of publications cited of Ans#2 ), JOIN(KGQA2( what is the affiliation of Ans#1), KGQA1( who is 'Convex Optimization with Abstract Linear Operators' creator ))))
                question: Whose institute has a less number of publications cited, the institute of the writer of 'An efficient processor allocation scheme for mesh connected parallel computers' or 'Convex Optimization with Abstract Linear Operators' creator affiliation?
                HQ-expression: COMP_<( JOIN( KGQA2( what is the number of publications cited of Ans#4), JOIN( KGQA2( what is the institute of Ans#3 ), KGQA1( who is the writer of 'An efficient processor allocation scheme for mesh connected parallel computers' ))), JOIN(KGQA2( what is the number of publications cited of Ans#2 ), JOIN(KGQA2( what is the affiliation of Ans#1), KGQA1( who is 'Convex Optimization with Abstract Linear Operators' creator ))))
                question: What is the name of the author who has more publications cited by count: Klara Nahrstedt or Amparo Alonso-Betanzos?
                HQ-expression: COMP_>( KGQA2( what is the publications cited by count of Klara Nahrstedt ), KGQA2( what is the publications cited by count of Amparo Alonso-Betanzos))
                question: What is the name of the author who has fewer citations: Klara Nahrstedt or Amparo Alonso-Betanzos?
                HQ-expression: COMP_<( KGQA2( what is the number of citations of Klara Nahrstedt ), KGQA2( what is the number of citations of Amparo Alonso-Betanzos))
                question: In terms of works count, who has a higher number, the author of Describing Datasets in Wikidata or the creator of Site percolation on pseudo-random graphs?
                HQ-expression: COMP_>( JOIN( KGQA2( what is the works count of Ans#2 ), KGQA1( who is the author of Describing Datasets in Wikidata )), JOIN(KGQA2(  what is the works count of Ans#1 ), KGQA1( who is the creator of Site percolation on pseudo-random graphs ) ) )
                question: Comparing the hIndex of the author who published 'ECCB 2014: The 13th European Conference on Computational Biology' with the author of 'Stabilization of a nonlinear structural acoustic interaction', who has a smaller value?
                HQ-expression: COMP_<( JOIN( KGQA2( what is the hIndex of Ans#2 ), KGQA1( the author who published 'ECCB 2014: The 13th European Conference on Computational Biology' is ) ), JOIN( KGQA2( what is the hIndex of Ans#1 ), KGQA1( who is the author of 'Stabilization of a nonlinear structural acoustic interaction' )))
                question: Whose institute has more publications, the author of ISMB/ECCB 2015 or the creator of How to eliminate flutter in flow structure interactions?
                HQ_expression: COMP_>( JOIN( KGQA2( what is the publication count of Ans#4 ), JOIN( KGQA2( what is the institute of Ans#3 ), KGQA1( the author of ISMB/ECCB 2015 is ) ) ), JOIN( KGQA2( what is the publication count of Ans#2 ), JOIN(KGQA2( what is the institute of Ans#1 ), KGQA1( who is the creator of How to eliminate flutter in flow structure interactions ) ) ) )
                question: Whose institute has fewer publication citations, California Institute of Technology or the researcher behind Harold's purple crayon rendered in haptics institute?
                HQ-expression: COMP_<( KGQA2( what is the publication citations of California Institute of Technology ), JOIN( KGQA2(  what is the publication citations of Ans#2 ), JOIN(KGQA2( what is the institute of Ans#1 ), KGQA1( who is the researcher behind Harold's purple crayon rendered in haptics )))
                question: In terms of twoYearMeanCitedness, who has a lower value, author of 'Response to \"The physics of ghost imaging - nonlocal interference or local intensity fluctuation correlation?\"' or 'The coordination dynamics of mobile conjugate reinforcement' author?
                HQ-expression: COMP_<(JOIN(KGQA2( what is the twoYearMeanCitedness of Ans#2 ), KGQA1( who is the author of 'Response to \"The physics of ghost imaging - nonlocal interference or local intensity fluctuation correlation?\"' )), JOIN(KGQA2(  what is the twoYearMeanCitedness of Ans#1 ), KGQA1( who is 'The coordination dynamics of mobile conjugate reinforcement' author ) ) ) 
                question: Whose institute has more publication citations, the author of 'A comparative study of approaches to compute the field distribution of deep brain stimulation in the Hemiparkinson rat model' or the author associated with University of Rostock?
                HQ-expression: COMP_>( JOIN( KGQA2( what is the publication citations of Ans#2 ), JOIN( KGQA2( what is the institute of Ans#1 ), KGQA1( who is the author of 'A comparative study of approaches to compute the field distribution of deep brain stimulation in the Hemiparkinson rat model' ) ) ), KGQA2( what is the publiation citation of University of Rostock ) )
                question: Whose institute has fewer publication citations, the author of 'A comparative study of approaches to compute the field distribution of deep brain stimulation in the Hemiparkinson rat model' or the author associated with University of Rostock?
                HQ-expression: COMP_<( JOIN( KGQA2( what is the publication citations of Ans#2 ), JOIN( KGQA2( what is the institute of Ans#1 ), KGQA1( who is the author of 'A comparative study of approaches to compute the field distribution of deep brain stimulation in the Hemiparkinson rat model' ) ) ), KGQA2( what is the publiation citation of University of Rostock ) )
                question: Which institute has more publications, American University in Cairo or University of Cambridge?
                HQ-expression: COMP_>( KGQA2( what is the number of publications of American University in Cairo ), ( what is the number of publications of University of Cambridge ) )
                question: Which author has less publications cited by count, Neil D. Lawrence or Moustafa Youssef?
                HQ-expression: COMP_<( KGQA2( what is the publications cited by count of Neil D. Lawrence ), ( what is the publications cited by count of Moustafa Youssef ) )
                question: Between American University in Cairo and University of Cambridge, which institute has an education institution type?
                HQ-expression: JOIN( KGQA2( which institute has an education institution type Ans#1 or Ans#2 ), UNION(KGQA2( American University in Cairo institution type is ), KGQA2( what is the institution type of University of Cambridge ) ) )
                question: Which author has fewer publications cited, the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' or 'Optimal Current Waveforms for Switched-Reluctance Motors'?
                HQ-expression: COMP_<(JOIN( KGQA2( what is the number of publications cited of Ans#2), KGQA1( who is the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' ) ), JOIN( KGQA2 ( what is the number of publications cited of Ans#1 ), KGQA1( who is the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' ) ) ) 
                question: Which author has more i10Index, the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' or 'Optimal Current Waveforms for Switched-Reluctance Motors'?
                HQ-expression: COMP_>(JOIN( KGQA2( what is i10Index of Ans#2), KGQA1( who is the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' ) ), JOIN( KGQA2 ( what is the i10Index of Ans#1 ) , KGQA1( who is the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' ) ) ) 
                question: Whose institute has more publications, the author of Trees and Semantics or Approximate Regular Expression Pattern Matching with Concave Gap Penalties writer's affiliation?
                HQ-expression: COMP_>( JOIN( KGQA2( what is the number of publications of Ans#4 ), JOIN( KGQA2( what is the affiliation of Ans#3 ), KGQA1( who is the author of Trees and Semantics ) ) ), JOIN( KGQA2( what is the number of publications of Ans#2 ), JOIN( KGQA2( what is the affiliation of Ans#1 ), KGQA1( who is Approximate Regular Expression Pattern Matching with Concave Gap Penalties writer ) ) ) )
                question: Whose institute has less citation, the author of Trees and Semantics or Approximate Regular Expression Pattern Matching with Concave Gap Penalties writer's affiliation?
                HQ-expression: COMP_<( JOIN( KGQA2( what is the number of citations of Ans#4 ), JOIN( KGQA2( what is the affiliation of Ans#3 ), KGQA1( who is the author of Trees and Semantics ) ) ), JOIN( KGQA2( what is the number of citations of Ans#2 ), JOIN( KGQA2( what is the affiliation of Ans#1 ), KGQA1( who is Approximate Regular Expression Pattern Matching with Concave Gap Penalties writer ) ) ) )

                Given question: {question}, 
                HQ-expression:

            """
    prompt = prompt_kg_text
    prompt_mapping = {
        2: prompt_kg_kg_bridge,
        3: prompt_kg_kg_comparison
    }
    prompt = prompt_mapping.get(q_type, prompt)

    hq_expression = llms.chatgpt(prompt, 1)
    # hq_expression = llms.llama(prompt)
    return hq_expression


if __name__ == "__main__":
    question = "Who has higher citations, the author of 'An Efficient Rate and Power Allocation Algorithm for Multiuser OFDM Systems'or the author of the paper 'Concurrent Program Schemes and Their Logics'?"
    question = "How many Nobel Prize winners are affiliated with the academic institution of the researcher who published The Dynamics of the Theta Method?"
    question = "Whose institute has a higher number of publications cited, the institute of the writer of 'An efficient processor allocation scheme for mesh connected parallel computers' or 'Convex Optimization with Abstract Linear Operators' creator affiliation?"
    question = "Which author has fewer publications cited, the creator of 'Dynamic Real-Time Task Scheduling on Hypercubes' or 'Optimal Current Waveforms for Switched-Reluctance Motors'?"
    question = "In terms of works count, who has more publications, the author who wrote 'The Oberon System' or the researcher behind 'FastR: Fast Database Search Tool for Non-Coding RNA'?"
    question = "Which author is affiliated with the institute that has fewer publications, the creator of the Oberon System or the author of FastR?"
    question = "Between the authors of Logic and Learning: Turing's legacy and Evaluation of Digital Library Impact and User Communities by Analysis of Usage Patterns, who has a higher i10Index?"
    question = "Which institute has fewer publications, the affiliation of the writer of 'Space-Time Interference Alignment and Degree-of-Freedom Regions for the MISO Broadcast Channel With Periodic CSI Feedback' or the author of 'Interactive Message-Locked Encryption and Secure Deduplication'?"
    question = "Whose university has more publications cited by, the creator of 'A Novel Lane Departure Warning System for Improving Road Safety' or the author of 'Chaotic signals and systems for communications'?"
    #cquestion = "when is the birth date of writer of Introduction to Python programming?"
    hq_expression = parser(question)
    print(hq_expression["hq_expression"])
